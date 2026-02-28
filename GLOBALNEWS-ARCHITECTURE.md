# GlobalNews — 시스템 아키텍처

> 44개 국제 뉴스 사이트를 크롤링하고 56개 NLP 분석 기법으로 처리하는 Staged Monolith 시스템의 기술 아키텍처 문서.

---

## 1. 시스템 개요

### 1.1 아키텍처 유형: Staged Monolith

단일 프로세스 내에서 4개 계층이 순차적으로 실행되는 **Staged Monolith** 아키텍처를 채택했다. 마이크로서비스가 아닌 모놀리스를 선택한 이유:

- **C3 제약** (단일 머신): MacBook M2 Pro에서 전체 파이프라인 실행
- **메모리 제어**: 단계 간 `gc.collect()`로 정밀한 메모리 관리 (피크 ≤ 48GB)
- **데이터 로컬리티**: Parquet 파일이 디스크 위에서 단계 간 직접 전달
- **디버깅 용이**: 단일 프로세스이므로 상태 추적이 단순

```
┌─────────────────────────────────────────────────────────────┐
│                      main.py (CLI)                          │
│            crawl │ analyze │ full │ status                  │
├──────────────────┼──────────────────────────────────────────┤
│                  │                                          │
│   ┌──────────────▼──────────────┐                          │
│   │  Layer 1: CRAWLING ENGINE   │                          │
│   │  44 adapters + anti-block   │                          │
│   │  → data/raw/YYYY-MM-DD/    │                          │
│   └──────────────┬──────────────┘                          │
│                  │ all_articles.jsonl                       │
│   ┌──────────────▼──────────────┐                          │
│   │  Layer 2: ANALYSIS PIPELINE │                          │
│   │  8 stages, 56 techniques   │                          │
│   │  → data/{processed,features,analysis}/                 │
│   └──────────────┬──────────────┘                          │
│                  │ Parquet files                            │
│   ┌──────────────▼──────────────┐                          │
│   │  Layer 3: STORAGE           │                          │
│   │  Parquet ZSTD + SQLite FTS5 │                          │
│   │  → data/output/YYYY-MM-DD/ │                          │
│   └──────────────┬──────────────┘                          │
│                  │                                          │
│   ┌──────────────▼──────────────┐                          │
│   │  Layer 4: PRESENTATION      │                          │
│   │  Streamlit dashboard (6 tabs)│                          │
│   │  + DuckDB/Pandas/FTS5 쿼리  │                          │
│   └─────────────────────────────┘                          │
│                                                             │
│   [Shared] config/ │ utils/ │ constants.py                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 Conductor Pattern (C2)

Claude Code는 데이터를 직접 처리하지 않는다. Python 스크립트를 생성 → Bash로 실행 → 결과 읽기 → 다음 단계 결정하는 **Conductor(지휘자)** 역할만 수행한다.

---

## 2. 크롤링 엔진 (Layer 1)

### 2.1 전체 아키텍처

```
sources.yaml (44 sites)
       │
       ▼
┌──────────────────────────────────────────────────┐
│              CrawlingPipeline                     │
│  ┌────────────┐  ┌───────────────┐               │
│  │ SiteAdapter │  │ NetworkGuard  │               │
│  │ (44개)      │  │ (5-retry HTTP)│               │
│  └──────┬─────┘  └───────┬───────┘               │
│         │                │                        │
│  ┌──────▼────────────────▼───────┐               │
│  │       URL Discovery            │               │
│  │  Tier 1: RSS (feedparser)      │               │
│  │  Tier 2: Sitemap (lxml)        │               │
│  │  Tier 3: DOM (BeautifulSoup)   │               │
│  └──────────────┬─────────────────┘               │
│                 │ DiscoveredURL[]                  │
│  ┌──────────────▼─────────────────┐               │
│  │    Article Extraction           │               │
│  │  Chain: Fundus → Trafilatura    │               │
│  │        → Newspaper4k → CSS     │               │
│  └──────────────┬─────────────────┘               │
│                 │ RawArticle                       │
│  ┌──────────────▼─────────────────┐               │
│  │    Deduplication (3-Level)      │               │
│  │  L1: URL normalize (O(1))      │               │
│  │  L2: Title Jaccard (≥0.8)      │               │
│  │  L3: SimHash Hamming (≤10bit)  │               │
│  └──────────────┬─────────────────┘               │
│                 ▼                                  │
│     data/raw/YYYY-MM-DD/all_articles.jsonl        │
└──────────────────────────────────────────────────┘
```

### 2.2 사이트 어댑터 시스템

44개 사이트 각각에 대한 전용 어댑터가 `src/crawling/adapters/`에 구현되어 있다.

**기반 클래스**: `BaseSiteAdapter` (450+ lines)

핵심 속성: SITE_ID, SITE_NAME, SITE_URL, LANGUAGE, GROUP, RSS_URLS, SITEMAP_URL, TITLE_CSS, BODY_CSS, DATE_CSS, AUTHOR_CSS, ANTI_BLOCK_TIER, UA_TIER, RATE_LIMIT_SECONDS, PAYWALL_TYPE 등.

**어댑터 그룹**:

| 그룹 | 디렉터리 | 사이트 수 | 특징 |
|------|---------|----------|------|
| Korean Major | `kr_major/` | 11 | 네이버 연동, Kiwi 토크나이저, 한국어 날짜 파싱 |
| Korean Tech | `kr_tech/` | 8 | 기술 뉴스, 간단한 구조, RSS 중심 |
| English | `english/` | 12 | 페이월 사이트(NYT, FT, WSJ) 포함 |
| Multilingual | `multilingual/` | 13 | CJK 인코딩, RTL(아랍/히브리), 다중 언어 |

### 2.3 4-Level 재시도 시스템

```
Level 1: NetworkGuard ×5 (HTTP 재시도, 지수 백오프 base=2s, max=30s)
Level 2: Standard → TotalWar ×2 (undetected-chromedriver 전환)
Level 3: Crawler ×3 (라운드, 딜레이 [30s, 60s, 120s])
Level 4: Pipeline ×3 (전체 재시작, [60s, 120s, 300s])
─────────────────────────────────────
이론적 최대: 5 × 2 × 3 × 3 = 90회 자동 시도
Tier 6: Claude Code 인터랙티브 분석으로 에스컬레이션
```

### 2.4 안티블록 시스템

**7가지 차단 유형 진단** (BlockDetector):
IP Block, UA Filter, Rate Limit, CAPTCHA, JS Challenge, Fingerprint, Geo-Block

**6-Tier 에스컬레이션**:
Tier 1 (딜레이+UA) → Tier 2 (세션/쿠키) → Tier 3 (Playwright) → Tier 4 (Patchright+핑거프린트) → Tier 5 (프록시) → Tier 6 (수동 분석)

**Circuit Breaker**: CLOSED →(5연속 실패)→ OPEN →(300초 대기)→ HALF_OPEN →(성공)→ CLOSED

### 2.5 중복 제거 (3-Level)

| Level | 방법 | 기준 |
|-------|------|------|
| L1 | URL 정규화 + 정확 매칭 | 쿼리 파라미터 제거, 프로토콜 정규화 |
| L2 | 제목 유사도 | Jaccard ≥ 0.8 + Levenshtein ≤ 0.2 |
| L3 | SimHash 본문 핑거프린트 | 64bit 해밍 거리 ≤ 10 |

저장소: `data/dedup.sqlite` (크로스-런 지속)

### 2.6 데이터 계약 (RawArticle)

```python
@dataclass(frozen=True)
class RawArticle:
    url: str                    # 원본 URL (필수)
    title: str                  # 제목 (필수)
    body: str                   # 본문 (필수)
    source_id: str              # 사이트 ID (필수)
    source_name: str            # 사이트 이름
    language: str               # ISO 639-1
    published_at: datetime      # 발행일시
    crawled_at: datetime        # 크롤링일시
    author: str | None          # 저자
    category: str | None        # 카테고리
    content_hash: str           # SHA-256 본문 해시
    crawl_tier: int             # 사용된 티어 (1-6)
    crawl_method: str           # RSS/Sitemap/DOM/Playwright
```

---

## 3. 분석 파이프라인 (Layer 2)

### 3.1 8단계 파이프라인 흐름

```
all_articles.jsonl
  │
  ▼
Stage 1 (전처리) → articles.parquet
  │
  ▼
Stage 2 (피처) → embeddings/tfidf/ner.parquet
  │
  ▼
Stage 3 (기사 분석) → article_analysis.parquet + mood_trajectory.parquet
  │
  ▼
Stage 4 (집계) → topics/networks/dtm/aux_clusters.parquet
  │
  ├─────────────────────────────────────┐
  ▼                                     ▼
Stage 5 (시계열, 독립)              Stage 6 (교차분석, 독립)
→ timeseries.parquet                → cross_analysis.parquet
  │                                     │
  └──────────────┬──────────────────────┘
                 ▼
Stage 7 (신호 분류) → signals.parquet
  │
  ▼
Stage 8 (출력) → analysis.parquet + index.sqlite + checksums.md5
```

### 3.2 단계별 상세

#### Stage 1: 전처리 (T01-T06) — ~1.0 GB

| 기법 | 라이브러리 |
|------|----------|
| T01 한국어 형태소 | kiwipiepy (singleton) |
| T02 영어 레마타이제이션 | spaCy en_core_web_sm |
| T03 문장 분리 | Kiwi (ko) / spaCy (en) |
| T04 언어 감지 | langdetect |
| T05 텍스트 정규화 | NFKC + 공백 |
| T06 불용어 제거 | 커스텀 (ko) + spaCy (en) |

입력: JSONL → 출력: `articles.parquet` (12 columns)

#### Stage 2: 피처 추출 (T07-T12) — ~2.4 GB

| 기법 | 라이브러리 |
|------|----------|
| T07 SBERT 임베딩 | sentence-transformers (384-dim) |
| T08 TF-IDF | sklearn (10,000 features, ngram 1-2) |
| T09 NER | xlm-roberta / spaCy |
| T10 키워드 | keybert (SBERT 공유) |
| T12 단어 통계 | custom |

출력: `embeddings.parquet`, `tfidf.parquet`, `ner.parquet`

#### Stage 3: 기사 분석 (T13-T19, T49) — ~1.8 GB

| 기법 | 라이브러리 |
|------|----------|
| T13 한국어 감성 | KoBERT (F1=94%) |
| T14 영어 감성 | cardiffnlp/twitter-roberta |
| T15 8차원 감정 | BART-MNLI / KcELECTRA |
| T16 STEEPS 분류 | BART-MNLI zero-shot |
| T17 논조 감지 | BART-MNLI zero-shot |
| T18 Social Mood Index | 집계 공식 |
| T19 감정 궤적 | 7일 이동 델타 |
| T49 내러티브 추출 | BART-MNLI zero-shot |

출력: `article_analysis.parquet` (13 columns) + `mood_trajectory.parquet`

#### Stage 4: 집계 (T21-T28) — ~1.5 GB

| 기법 | 라이브러리 |
|------|----------|
| T21 BERTopic | BERTopic + Model2Vec (CPU 500x) |
| T22 동적 토픽 | BERTopic topics_over_time |
| T23 HDBSCAN | hdbscan (cosine) |
| T24 NMF | sklearn |
| T25 LDA | sklearn |
| T26 k-means | sklearn (silhouette 최적화) |
| T27 계층적 클러스터링 | scipy Ward |
| T28 Louvain 커뮤니티 | python-louvain |

출력: `topics.parquet`, `networks.parquet`, `dtm.parquet`, `aux_clusters.parquet`

#### Stage 5: 시계열 (T29-T36) — ~0.5 GB (독립)

| 기법 | 라이브러리 |
|------|----------|
| T29 STL 분해 | statsmodels (주기=7) |
| T30 Kleinberg 버스트 | custom automaton |
| T31 PELT 변화점 | ruptures (RBF, BIC) |
| T32 Prophet 예측 | prophet (7d + 30d) |
| T33 웨이블릿 | pywt (Daubechies-4) |
| T34 ARIMA | statsmodels (grid search) |
| T35 이동평균 교차 | pandas (3d vs 14d) |
| T36 계절성 | scipy periodogram |

출력: `timeseries.parquet` (17 columns)

#### Stage 6: 교차 분석 (T37-T46, T20, T50) — ~0.8 GB (독립)

| 기법 | 라이브러리 |
|------|----------|
| T37 Granger 인과관계 | statsmodels |
| T38 PCMCI 인과 추론 | tigramite (ParCorr) |
| T39 공출현 네트워크 | networkx |
| T40 지식 그래프 | networkx (NER 기반) |
| T41 중심성 분석 | networkx (degree, betweenness, PageRank) |
| T42 네트워크 진화 | networkx |
| T43 교차 언어 토픽 정렬 | SBERT multilingual centroid |
| T44 프레임 분석 | sklearn TF-IDF KL divergence |
| T45 의제 설정 | scipy 교차 상관 |
| T46 시간적 정렬 | DTW |
| T20 GraphRAG | networkx |
| T50 모순 감지 | SBERT + NLI |

출력: `cross_analysis.parquet`

#### Stage 7: 신호 분류 (T47-T55) — ~0.5 GB

| 기법 | 라이브러리 |
|------|----------|
| T47 LOF 이상치 | sklearn |
| T48 Isolation Forest | sklearn |
| T51 Z-score | scipy |
| T52 엔트로피 변화 | scipy |
| T53 Zipf 편차 | custom |
| T54 생존 분석 | lifelines (Kaplan-Meier) |
| T55 KL 다이버전스 | scipy |
| BERTrend | custom (토픽 생애주기) |
| Singularity | weighted composite (7 지표) |

**5-Layer 신호 계층**:

| Layer | 기간 | 특성 |
|-------|------|------|
| L1 Fad | < 1주 | 급등-급락, burst_score 높음 |
| L2 Short-term | 1-4주 | 안정적 성장 후 정체 |
| L3 Mid-term | 1-6개월 | 변화점 + 트렌드 기울기 |
| L4 Long-term | 6개월+ | 다중 소스 + 구조적 변화 |
| L5 Singularity | 12개월+ | 패러다임 전환, 3개 독립 경로 중 2개 필요 |

Singularity 3경로: (1) OOD (LOF+IF), (2) 변화점+BERTrend, (3) Zipf+KL — threshold=0.65

출력: `signals.parquet` (12 columns)

#### Stage 8: 출력 (T56) — ~0.5 GB

1. **analysis.parquet 병합** (21 columns): 5개 소스 조인 → ZSTD 압축
2. **signals.parquet 최종화**: 스키마 검증
3. **topics.parquet 복사**: ZSTD
4. **SQLite 인덱스**: FTS5 + vec + signals_index + topics_index
5. **DuckDB 검증**: 모든 Parquet 읽기 확인
6. **품질 검증**: 중복 ID, 임베딩 차원(384), NOT NULL

### 3.3 메모리 관리

- **MAX_MEMORY_GB**: 48.0 GB
- **gc.collect()**: 모든 단계 사이 강제 실행
- **모델 라이프사이클**: 순차 로드/언로드 (concurrent 금지)
- **Kiwi singleton**: 필수 (재로딩 시 +125MB 누수)
- **SBERT 공유**: KeyBERT + BERTopic이 동일 인스턴스 사용

### 3.4 날짜별 경로 변환

모든 상수 경로(`DATA_PROCESSED_DIR / "articles.parquet"`)는 `_remap_path()`를 통해 날짜별 파티션으로 변환:

```
constants: data/processed/articles.parquet
→ runtime: data/processed/2026-02-27/articles.parquet
```

---

## 4. 데이터 아키텍처

### 4.1 날짜별 파티션

```
data/
├── raw/YYYY-MM-DD/              # 원시 JSONL
│   ├── all_articles.jsonl
│   ├── crawl_report.json
│   ├── .crawl_state.json        # 재개 체크포인트
│   └── backup/                  # 롤링 백업
├── processed/YYYY-MM-DD/        # Stage 1 출력
│   └── articles.parquet
├── features/YYYY-MM-DD/         # Stage 2 출력
│   ├── embeddings.parquet
│   ├── tfidf.parquet
│   └── ner.parquet
├── analysis/YYYY-MM-DD/         # Stage 3-6 출력
│   ├── article_analysis.parquet
│   ├── topics.parquet
│   ├── networks.parquet
│   ├── timeseries.parquet
│   ├── cross_analysis.parquet
│   ├── dtm.parquet
│   ├── aux_clusters.parquet
│   └── mood_trajectory.parquet
├── output/YYYY-MM-DD/           # Stage 7-8 최종 출력
│   ├── analysis.parquet         # 21 columns 병합
│   ├── signals.parquet          # 12 columns 신호
│   ├── topics.parquet           # 7 columns 토픽
│   ├── index.sqlite             # FTS5 + vec
│   └── checksums.md5
├── models/                      # ML 모델 캐시
├── logs/                        # 로그 (daily/weekly/archive/alerts)
└── dedup.sqlite                 # 전역 중복 제거 DB
```

### 4.2 Parquet 스키마

**ARTICLES (12 columns)**: article_id, url, title, body, source, category, language, published_at, crawled_at, author, word_count, content_hash

**ANALYSIS (21 columns)**: article_id, sentiment_label, sentiment_score, emotion_{joy,trust,fear,surprise,sadness,disgust,anger,anticipation}, topic_id, topic_label, topic_probability, steeps_category, importance_score, keywords, entities_{person,org,location}, embedding

**SIGNALS (12 columns)**: signal_id, signal_layer, signal_label, detected_at, topic_ids, article_ids, burst_score, changepoint_significance, novelty_score, singularity_composite, evidence_summary, confidence

**Parquet 설정**: ZSTD level 3, 원자적 쓰기 (임시 파일 + rename)

### 4.3 SQLite 인덱스

```sql
articles_fts     -- FTS5 (title + body + keywords)
signals_index    -- topic_id + layer + confidence
topics_index     -- topic_label + article_count
crawl_status     -- site_id + crawl_date + article_count
```

---

## 5. Presentation Layer

### 5.1 Streamlit 대시보드 (dashboard.py)

| 탭 | 시각화 |
|---|--------|
| Overview | 기사 수, 소스/그룹/언어별 분포, 일일 볼륨, 파이프라인 상태 |
| Topics | Top 20 토픽, STEEPS 분류, 신뢰도 히스토그램, 토픽 트렌드 |
| Sentiment & Emotions | 감성 파이차트, 8차원 레이더, 소스×감정 히트맵, 무드 궤적 |
| Time Series | 메트릭별 그래프, 이동평균 교차, Prophet 예측+신뢰구간 |
| Word Cloud | 다국어 워드클라우드, 한국어/영어 필터, Top 30 빈도 |
| Article Explorer | 소스/언어/키워드 필터, 정렬, 상세 보기 |

사이드바: 기간(Daily/Monthly/Quarterly/Yearly), 날짜 선택, 교차분석 패널

### 5.2 프로그래매틱 쿼리

- **DuckDB**: `SELECT ... FROM read_parquet('data/output/YYYY-MM-DD/analysis.parquet')`
- **Pandas**: `pd.read_parquet('data/output/YYYY-MM-DD/analysis.parquet')`
- **SQLite FTS5**: `SELECT * FROM articles_fts WHERE articles_fts MATCH 'query'`

---

## 6. 설정 시스템

### 6.1 sources.yaml

44개 사이트 설정. 각 사이트: meta (name, url, language, group, enabled, difficulty_tier), crawl (primary_method, rss_urls, sections, rate_limit_seconds, ua_tier, anti_block_tier), selectors (title_css, body_css, date_css), paywall (type).

### 6.2 pipeline.yaml

8단계 파이프라인 설정. Global (max_memory_gb=10, gc_between_stages, parquet_compression=zstd). 단계별 (enabled, memory_limit_gb, timeout_seconds, models, dependencies).

### 6.3 constants.py (350+ 상수)

경로 27개, 재시도 파라미터 (MAX_RETRIES=5, BACKOFF_MAX=60s), Circuit Breaker (FAILURE_THRESHOLD=5, RECOVERY_TIMEOUT=300s), 크롤링 (LOOKBACK_HOURS=24, MAX_ARTICLES=1000), 분석 (SBERT_DIM=384, TFIDF_MAX=10000), 신호 (CONFIDENCE=0.5, SINGULARITY=0.65).

---

## 7. 운영 인프라

### 7.1 CLI (main.py)

```bash
python3 main.py --mode {crawl|analyze|full|status}
                --date YYYY-MM-DD --sites X,Y --groups A,B
                --stage N --all-stages --dry-run
                --log-level {DEBUG|INFO|WARNING|ERROR}
```

### 7.2 자동화

| 스케줄 | 스크립트 | 역할 |
|--------|---------|------|
| 일일 02:00 | `run_daily.sh` | 전체 파이프라인 (4시간 타임아웃) |
| 주간 일요일 01:00 | `run_weekly_rescan.sh` | 사이트 건강 점검 |
| 월간 1일 03:00 | `archive_old_data.sh` | 30일 이상 데이터 아카이빙 |

### 7.3 Preflight Check

`python3 scripts/preflight_check.py --project-dir . --mode full --json`

Python 3.12+, 20개 의존성, 44개 사이트 설정, 디스크 ≥2GB, spaCy 모델, 네트워크, 디렉터리 구조 검증.

---

## 8. 테스트 인프라

43 파일, ~287 테스트, 18,400 LOC.

| 카테고리 | 파일 수 | 내용 |
|---------|--------|------|
| unit | 23 | 단계별, SOT, 설정, 중복제거 |
| integration | 1 | SOT 전체 라이프사이클 |
| structural | 3 | 에이전트 구조, 사이트 일관성, 플레이북 |
| crawling | 6 | 안티블록, 서킷브레이커, 어댑터 |

---

## 9. 의존성 (44+ packages)

**크롤링** (13): requests, aiohttp, beautifulsoup4, lxml, feedparser, trafilatura, newspaper4k, playwright, patchright, chardet, simhash, datasketch

**NLP** (12): kiwipiepy, spacy, sentence-transformers, transformers (<5.0), torch, bertopic, keybert, langdetect, scikit-learn, hdbscan, setfit, fasttext-wheel

**시계열+네트워크** (9): statsmodels, prophet, ruptures, PyWavelets, lifelines, networkx, python-louvain, tigramite, igraph

**저장+유틸** (10): pyarrow, pandas, duckdb, sqlite-vec, pyyaml, pydantic, python-dateutil, tqdm, structlog, pytest

---

## 10. DNA 유전

부모 [AgenticWorkflow](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md)로부터 유전:

| DNA | 자식 표현 |
|-----|----------|
| 3단계 구조 | Research (4) → Planning (4) → Implementation (12) |
| SOT | `.claude/state.yaml` |
| 4계층 QA | L0 Anti-Skip → L1 Verification → L1.5 pACS → L2 Review |
| Safety Hooks | 위험 명령 차단 |
| Context Preservation | 스냅샷 + KI + RLM |
| P1 Hallucination Prevention | 13개 `validate_*.py` |

**도메인 고유 변이**: 4-Level 재시도 (90회), 44-site Adapter Pattern, 5-Layer Signal Hierarchy, Date-Partitioned Storage

---

## 11. 빌드 히스토리

20단계 워크플로우, 32개 전문 서브에이전트, 6개 에이전트 팀으로 AI가 자동 구축.

| 단계 | 내용 | pACS |
|------|------|------|
| 1-4 | Research (정찰, 기술검증, 실현가능성) | 70-74 |
| 5-8 | Planning (아키텍처, 전략, 설계) | 72-80 |
| 9-12 | Crawling 구현 | 78-82 |
| 13-15 | Analysis 구현 | 80-82 |
| 16-20 | 테스트, 자동화, 문서, 리뷰 | 65-84 |

총 코드: ~41,500 (src) + ~18,400 (tests) = ~59,900 LOC
