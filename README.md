# GlobalNews — Global News Crawling & Big Data Analysis System
# GlobalNews — 글로벌 뉴스 크롤링 & 빅데이터 분석 시스템

> **112 international news sites, 14 languages, 4,230+ articles/day**
> **8-stage NLP pipeline + 7-module insight analytics + evidence-based future intelligence**
>
> **112개 국제 뉴스 사이트, 14개 언어, 일일 4,230건 이상 수집**
> **8단계 NLP 파이프라인 + 7모듈 통찰 분석 + 증거 기반 미래 인텔리전스**

| | EN | KO |
|---|---|---|
| **What it does** | Crawls 112 news sites daily, runs 56 NLP techniques, produces geopolitical/economic/entity intelligence with risk alerts | 112개 뉴스 사이트를 매일 크롤링, 56개 NLP 기법 적용, 지정학/경제/엔티티 인텔리전스 + 리스크 경보 생산 |
| **Output** | Parquet (ZSTD) + SQLite (FTS5) + Evidence-based intelligence + Automated risk alerts | Parquet (ZSTD) + SQLite (FTS5) + 증거 기반 인텔리전스 + 자동 리스크 경보 |
| **Languages** | English, Korean, Spanish, German, Swedish, Japanese, Russian, Italian, Portuguese, Polish, Czech, French, Norwegian, Mongolian | 영어, 한국어, 스페인어, 독일어, 스웨덴어, 일본어, 러시아어, 이탈리아어, 포르투갈어, 폴란드어, 체코어, 프랑스어, 노르웨이어, 몽골어 |
| **Performance** | 4,230 articles/day, ~5h crawling, ~73min analysis, NER 79%, 7,635 findings | 일일 4,230건, 크롤링 ~5시간, 분석 ~73분, NER 정확도 79%, 7,635 발견 |
| **Stack** | Python 3.13, SBERT, BERTopic, spaCy, Kiwi, Davlan XLM-RoBERTa, mDeBERTa, PyArrow, DuckDB | |
| **Framework** | Born from [AgenticWorkflow](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md) (parent organism — DNA inheritance) | [AgenticWorkflow](AGENTICWORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md) 프레임워크(만능줄기세포)로부터 탄생 — DNA 유전 |

---

## Quick Start / 빠른 시작

```bash
# 1. Clone and setup / 클론 및 설정
git clone https://github.com/idoforgod/GlobalNews-Crawling-AgenticWorkflow.git
cd GlobalNews-Crawling-AgenticWorkflow

# 2. Create venv / 가상환경 생성 (Python 3.12-3.13 required / 필수, spaCy는 3.14 비호환)
python3.13 -m venv .venv && source .venv/bin/activate

# 3. Install dependencies / 의존성 설치
pip install -r requirements.txt
python -m spacy download en_core_web_sm

# 4. Verify environment / 환경 검증
.venv/bin/python scripts/preflight_check.py --project-dir . --mode full --json

# 5. Run full pipeline / 전체 파이프라인 실행 (crawl 112 sites + 8-stage NLP analysis)
.venv/bin/python main.py --mode full --date $(date +%Y-%m-%d)

# 6. Run insight analytics / 통찰 분석 실행 (7 modules + evidence-based intelligence)
.venv/bin/python main.py --mode insight --window 30 --end-date $(date +%Y-%m-%d)
```

### Claude Code Users / Claude Code 사용자

Just type **"start"** or **"시작하자"**. The system auto-routes to the right mode.
**"start"** 또는 **"시작하자"**라고 입력하면 자동으로 적절한 모드로 실행됩니다.

| Say this / 입력 | What happens / 동작 |
|----------|-------------|
| "시작하자" / "start" | Full pipeline (crawl + analyze) / 전체 파이프라인 |
| "통찰 분석" / "run insights" | Workflow B (7-module insight analytics) / 빅데이터 통찰 분석 |
| "크롤링 해줘" / "crawl" | Crawling only / 크롤링만 |
| "상태 확인" / "status" | Show results / 결과 조회 |

---

## What This System Produces / 이 시스템이 생산하는 것

### Workflow A: Daily Collection & Analysis (~5 hours) / 일일 수집 & 분석

```
112 news sites (14 languages) / 112개 뉴스 사이트 (14개 언어)
    │
    ▼ Crawling / 크롤링: 4-Level retry (max 90 attempts / 최대 90회 재시도),
    │           5-worker parallel / 5개 병렬 워커, Never-Abandon policy
    │
    ▼ 4,230 articles/day / 일일 4,230건 (raw JSONL, 16 MB)
    │
    ▼ 8-Stage NLP Pipeline (73 min / 73분):
    │
    │  Stage 1: Preprocessing / 전처리            Kiwi (Korean) + spaCy (English)
    │  Stage 2: Feature Extraction / 피처 추출    SBERT 384-dim + TF-IDF + Multilingual NER
    │  Stage 3: Article Analysis / 기사 분석      Sentiment / 감성 + Plutchik 8 Emotions / 8감정 + STEEPS
    │  Stage 4: Aggregation / 집계               BERTopic + HDBSCAN + Entity Networks / 엔티티 네트워크
    │  Stage 5: Time Series / 시계열             STL Decomposition / 분해 + PELT Changepoints / 변화점
    │  Stage 6: Cross Analysis / 교차 분석       Granger Causality / 인과관계 + PCMCI
    │  Stage 7: Signal Classification / 신호 분류 5-Layer (Fad → Singularity)
    │  Stage 8: Data Output / 출력              Parquet + SQLite FTS5 + DuckDB
    │
    ▼ Output / 산출물: data/output/YYYY-MM-DD/
       ├── analysis.parquet   (7.8 MB, 4,230 rows, 21 columns)
       ├── topics.parquet     (52 topics / 52개 토픽)
       ├── signals.parquet    (5-Layer classification / 5계층 분류)
       └── index.sqlite       (27 MB, full-text search / 전문 검색)
```

### Workflow B: Insight Analytics (~60 seconds) / 통찰 분석

Accumulated data (7-40 day window) is analyzed by 7 modules.
축적된 데이터(7~40일 윈도우)를 7개 모듈이 교차 분석합니다.

| Module / 모듈 | Analysis / 분석 | Key Metrics / 핵심 지표 | Future Prediction / 미래 예측 활용 |
|--------|----------|-------------|----------------------|
| **M1** Cross-Lingual / 교차언어 | Information asymmetry across 14 languages / 14개 언어 간 정보 비대칭 | JSD divergence, Wasserstein sentiment bias, filter bubble index / JSD 비대칭, 감성편향, 필터버블 | Diplomatic conflict precursor / 외교 갈등 선행지표 |
| **M2** Narrative / 내러티브 | Frame evolution + information flow / 프레임 진화 + 정보 흐름 | Changepoint detection, HHI voice dominance, media health / 변화점, 음성지배, 미디어 건강도 | Propaganda detection / 여론 조작 탐지 |
| **M3** Entity / 엔티티 | Entity trajectories + hidden connections / 궤적 + 숨은 연결 | Burst/plateau classification, Jaccard links / 폭발/정체 분류, 연결 | Predict next newsmakers / 다음 뉴스 주인공 예측 |
| **M4** Temporal / 시간 패턴 | Information velocity + attention decay / 전파 속도 + 관심 감쇠 | Cascade, velocity matrix, cyclicality / 캐스케이드, 속도행렬, 주기성 | News lifecycle prediction / 뉴스 수명 예측 |
| **M5** Geopolitical / 지정학 | Bilateral relations + soft power / 양자관계 + 소프트파워 | BRI index (414 pairs), conflict/cooperation ratio / BRI 지수, 갈등/협력 비율 | Track relationship changes / 관계 악화·개선 추적 |
| **M6** Economic / 경제 | EPU uncertainty + sector sentiment / 불확실성 + 섹터 감성 | Multilingual EPU (12 languages), 5-sector momentum / 12언어 EPU, 5섹터 모멘텀 | Economic crisis early warning / 경제 위기 조기 경보 |
| **M7** Synthesis + Intelligence / 종합 + 인텔리전스 | **Evidence-based future intelligence** / **증거 기반 미래 인텔리전스** | Entity profiles (100), pair tensions (224), evidence articles (255), risk alerts / 엔티티 프로파일, 양자긴장, 증거기사, 경보 | **Actionable predictions with evidence** / **증거 기반 행동 가능한 예측** |

### M7 Intelligence — Evidence-Based Outputs / M7 인텔리전스 — 증거 기반 산출물

The system matches **raw article content with NLP analysis results** to produce actionable intelligence.
기사 원문과 NLP 분석 결과를 **자동 매칭**하여 행동 가능한 인텔리전스를 생산합니다.

| Output / 산출물 | What It Contains / 내용 | Example / 예시 |
|--------|-----------------|---------|
| `entity_profiles.parquet` | Per-entity sentiment profile / 엔티티별 감성 프로파일 | "Iran: 496 mentions, avg sentiment -0.232, neg 38%" |
| `pair_tensions.parquet` | Bilateral tension tracking / 양자관계 긴장 추적 | "Iran+Israel: 143 co-occurrences, avg -0.306" |
| `evidence_articles.parquet` | Best evidence articles per topic / 토픽별 최우수 증거 기사 | Actual titles, bodies, sources matched to insights / 실제 기사 본문 매칭 |
| `risk_alerts.parquet` | Automated threshold-based alerts / 임계점 자동 경보 | "EPU > 0.4 + all sectors negative = crisis precursor / 위기 전조" |

**Alert Thresholds / 경보 임계점** (configurable in / 설정 가능: `data/config/insights.yaml`):

| Alert / 경보 | Threshold / 임계점 | Meaning / 의미 |
|-------|-----------|---------|
| Crisis Sentiment / 위기 감성 | < -0.40 | Entity pair extreme → military escalation / 군사적 확대 임박 |
| EPU Critical / EPU 위기 | > 0.40 | Economic uncertainty → crisis precursor / 경제 위기 전조 |
| Burst Chaos / 버스트 카오스 | > 80% | 80%+ entities in burst → chaos phase / 카오스 국면 |
| Global Polarization / 글로벌 분극화 | > 50% | Conflict-dominant pairs exceed 50% / 갈등 양자쌍 50% 초과 |

---

## Latest Results (2026-04-07) / 최신 실행 결과

| Metric / 지표 | Value / 값 |
|--------|-------|
| Articles collected / 수집 기사 | **4,230** (16 MB JSONL) |
| Active sites / 활성 사이트 | **111/112** |
| Languages / 언어 | **14** |
| NER extraction rate / NER 추출률 | **79% (person), 89% (org), 85% (location)** |
| Sentiment distribution / 감성 분포 | Negative 40%, Neutral 33%, Positive 27% |
| Topics discovered / 토픽 발견 | **52** |
| Crawl time / 크롤링 시간 | **~5 hours** (was 12.5h / 이전 12.5시간에서 최적화) |
| Analysis time / 분석 시간 | **73 minutes** (8 stages / 8단계) |
| Insight findings / 통찰 발견 | **7,635** |
| Risk alerts / 리스크 경보 | **2 triggered / 2건 발동** (sector_all_negative, EPU warning) |
| Peak memory / 최대 메모리 | 19.76 GB |

**Top entities / 상위 엔티티**: Iran (4,084), Israel (2,596), US (2,448), Trump (2,431), AI (1,729)

---

## Multilingual NLP Models / 다국어 NLP 모델

| Task / 작업 | Model / 모델 | Languages / 언어 | Note / 비고 |
|------|-------|-----------|----------|
| NER | `Davlan/xlm-roberta-base-ner-hrl` | ar, de, en, es, fr, it, lv, nl, pt, zh + cross-lingual | 79% (Korean via transfer / 한국어 교차이전) |
| Sentiment (EN) / 감성 (영어) | `cardiffnlp/twitter-roberta-base-sentiment-latest` | English | Production |
| Sentiment (KO) / 감성 (한국어) | `monologg/kobert` + mDeBERTa fallback | Korean | Production |
| Sentiment (Multi) / 감성 (다국어) | `twitter-xlm-roberta-base-sentiment-multilingual` + `mDeBERTa-v3-base-mnli-xnli` | 8+ languages | Production |
| Emotions / 감정 | `facebook/bart-large-mnli` (zero-shot) | Multilingual / 다국어 | Plutchik 8 dimensions / 8차원 |
| STEEPS | `MoritzLaurer/mDeBERTa-v3-base-mnli-xnli` (zero-shot) | Multilingual / 다국어 | 6 categories / 6분류 |
| Embeddings / 임베딩 | `paraphrase-multilingual-MiniLM-L12-v2` | 50+ languages | 384-dim |
| Topics / 토픽 | BERTopic + HDBSCAN | Language-agnostic / 언어 무관 | 52 topics |

All models are **automatically downloaded** on first run. No API keys required (Claude API = $0).
모든 모델은 첫 실행 시 **자동 다운로드**됩니다. API 키 불필요 (Claude API = $0).

---

## Crawling Engine / 크롤링 엔진

**4-Level Retry Architecture** — up to 90 automatic recovery attempts per article:
**4-Level 재시도 아키텍처** — 기사당 최대 90회 자동 복구:

| Level | Target / 대상 | Retries / 재시도 | Strategy / 전략 |
|-------|--------|---------|----------|
| L1 NetworkGuard | HTTP request / 요청 | 5x | Exponential backoff 1-60s / 지수 백오프 |
| L2 Strategy / 전략 | Extraction mode / 추출 방식 | 2x | Standard → TotalWar escalation / 에스컬레이션 |
| L3 Crawler / 크롤러 | Crawl rounds / 라운드 | 1-3x | Adaptive / 적응형 (small / 소규모: 1, large / 대규모: 3) |
| L4 Pipeline / 파이프라인 | Full restart / 전체 재시작 | 3x | Re-run failed sites only / 실패 사이트만 재실행 |
| **Total / 합계** | | **5 x 2 x 3 x 3 = 90** | + Never-Abandon extra passes / 추가 패스 |

**Additional features / 추가 기능**:
- **5-Worker ThreadPoolExecutor**: 5 sites crawled simultaneously / 5개 사이트 동시 크롤링
- **SiteDeadline Fairness Yield**: Max 900s per site, prevents starvation / 사이트당 최대 900초, 기아 방지
- **3-Level Deduplication / 3단계 중복제거**: URL normalization → Title Jaccard → SimHash
- **DynamicBypassEngine**: 7 block types, 12 strategies, 5-tier escalation / 7개 차단 유형, 12개 전략, 5단계 에스컬레이션
- **Sitemap Capping**: Max 50 child sitemaps to prevent hour-long scans / 최대 50개로 제한하여 장시간 스캔 방지

---

## Project Structure / 프로젝트 구조

```
GlobalNews-Crawling-AgenticWorkflow/
├── main.py                         CLI entry point / 진입점 (crawl/analyze/insight/status)
├── dashboard.py                    Streamlit dashboard / 대시보드 (6 tabs / 6개 탭)
│
├── src/                            Core source / 핵심 소스 (183 modules, ~55,900 LOC)
│   ├── crawling/                   Crawling engine / 크롤링 엔진 + 116 site adapters / 어댑터
│   ├── analysis/                   8-stage NLP pipeline / 8단계 NLP 파이프라인
│   ├── insights/                   Workflow B (M1-M7 + M7 intelligence / 인텔리전스)
│   ├── storage/                    Parquet + SQLite I/O
│   ├── config/                     Constants + configuration / 상수 + 설정
│   └── utils/                      Logging, error handling / 로깅, 에러 처리
│
├── data/config/                    Configuration (tracked) / 설정 (추적됨)
│   ├── sources.yaml                112 site definitions / 사이트 정의 (groups A-J)
│   ├── pipeline.yaml               8-stage pipeline config / 파이프라인 설정
│   └── insights.yaml               Workflow B config + alert thresholds / 통찰 설정 + 경보 임계점
│
├── data/                           Runtime data (gitignored) / 런타임 데이터 (git 미추적)
│   ├── raw/YYYY-MM-DD/             Raw JSONL articles / 원시 기사
│   ├── processed/                  Preprocessed Parquet / 전처리
│   ├── features/                   NER, embeddings, TF-IDF
│   ├── analysis/                   Topics, networks, timeseries / 토픽, 네트워크, 시계열
│   ├── output/YYYY-MM-DD/          Final output / 최종 산출물: Parquet + SQLite
│   └── insights/{run_id}/          Workflow B outputs + intelligence / 통찰 + 인텔리전스
│
├── scripts/                        Operations scripts / 운영 스크립트 (34)
├── tests/                          Tests / 테스트 (60 files, 2,708 tests)
├── .claude/                        AI agent infrastructure / AI 에이전트 인프라
│   ├── agents/                     36 specialized sub-agents / 전문 서브에이전트
│   ├── skills/                     6 reusable skills / 재사용 스킬
│   ├── hooks/scripts/              25 automation hooks / 자동화 훅 (P1 validation, safety)
│   └── commands/                   7 slash commands / 슬래시 명령
│
├── GLOBALNEWS-*.md                 [Child] System documentation / [자식] 시스템 문서
├── AGENTICWORKFLOW-*.md            [Parent] Framework documentation / [부모] 프레임워크 문서
├── DECISION-LOG.md                 Architecture Decision Records / 설계 결정 기록 (ADR-001~070)
└── soul.md                         DNA inheritance philosophy / DNA 유전 철학
```

---

## Reproducibility / 재현 가능성

All gitignored files are **automatically regenerated**.
gitignore된 파일은 모두 **자동 재생성**됩니다.

| What's gitignored / git 미추적 | How to reproduce / 재생성 방법 |
|-------------------|-----------------|
| `.venv/` | `python3.13 -m venv .venv && pip install -r requirements.txt` |
| NLP models / NLP 모델 | Auto-downloaded on first run / 첫 실행 시 자동 다운로드 (~2 GB) |
| `data/raw/` | Re-run crawling / 크롤링 재실행: `main.py --mode crawl` |
| `data/processed/`, `features/`, `analysis/`, `output/` | Re-run analysis / 분석 재실행: `main.py --mode analyze` |
| `data/insights/` | Re-run insights / 통찰 재실행: `main.py --mode insight` |
| `data/dedup.sqlite` | Auto-created on crawl / 크롤링 시 자동 생성 |

**Everything needed to reproduce results is in the repository.**
**결과 재현에 필요한 모든 것이 저장소에 포함되어 있습니다**: 소스 코드, 설정, 사이트 정의, 파이프라인 설정, 경보 임계점.

---

## Data Querying / 데이터 쿼리

```python
# DuckDB — instant SQL on Parquet / Parquet에 즉시 SQL
import duckdb
duckdb.sql("""
    SELECT source, sentiment_label, COUNT(*) as n
    FROM 'data/output/2026-04-07/analysis.parquet'
    GROUP BY ALL ORDER BY n DESC
""")

# SQLite FTS5 — full-text search / 전문 검색
import sqlite3
conn = sqlite3.connect('data/output/2026-04-07/index.sqlite')
conn.execute("SELECT * FROM articles_fts WHERE articles_fts MATCH 'Iran AND nuclear'").fetchall()

# Pandas — analysis / 분석
import pandas as pd
df = pd.read_parquet('data/output/2026-04-07/analysis.parquet')
df.groupby('topic_label')['sentiment_score'].mean().sort_values()

# Intelligence — entity profiles / 인텔리전스 — 엔티티 프로파일
profiles = pd.read_parquet('data/insights/quarterly-2026-Q2/synthesis/intelligence/entity_profiles.parquet')
profiles.nlargest(10, 'mention_count')[['entity', 'mention_count', 'avg_sentiment', 'neg_ratio']]

# Risk alerts / 리스크 경보
alerts = pd.read_parquet('data/insights/quarterly-2026-Q2/synthesis/intelligence/risk_alerts.parquet')
alerts[alerts['triggered'] == True]
```

---

## Documentation Guide / 문서 가이드

| Document / 문서 | Content / 내용 | Audience / 대상 |
|----------|---------|----------|
| **README.md** (this file / 이 문서) | Project overview, quick start / 프로젝트 개요, 빠른 시작 | First-time visitors / 처음 방문자 |
| [GLOBALNEWS-README.md](GLOBALNEWS-README.md) | Detailed system specs / 시스템 상세 스펙 | System evaluators / 시스템 평가자 |
| [GLOBALNEWS-ARCHITECTURE-AND-PHILOSOPHY.md](GLOBALNEWS-ARCHITECTURE-AND-PHILOSOPHY.md) | Design philosophy, architecture / 설계 철학, 아키텍처 | Developers / 개발자 |
| [GLOBALNEWS-USER-MANUAL.md](GLOBALNEWS-USER-MANUAL.md) | Operations guide, CLI, intelligence / 운영 가이드, 인텔리전스 해석 | Operators & analysts / 운영자·분석가 |
| [DECISION-LOG.md](DECISION-LOG.md) | Architecture Decision Records / 설계 결정 기록 (ADR-001~070) | Architects / 아키텍트 |

---

## Tests / 테스트

```bash
pytest                            # All 2,708 tests / 전체 테스트
pytest tests/crawling/            # Crawling tests / 크롤링 테스트 (1,233)
pytest tests/unit/                # Unit tests / 단위 테스트
pytest -m "not slow"              # Skip NLP model loading / NLP 모델 로딩 스킵 (fast)
```

---

## License / 라이선스

MIT License. See / 참조: [COPYRIGHT.md](COPYRIGHT.md).
