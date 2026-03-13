#!/usr/bin/env python3
"""Check crawl progress from background task output and data files.

Tracks: sites with articles, sites with 0 articles, deadline yields
(fairness pauses), and sites currently in progress.
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def main():
    project = Path(__file__).resolve().parent.parent
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    date_str = datetime.now().strftime("%Y-%m-%d")

    print(f"=== CRAWL PROGRESS {datetime.now().strftime('%H:%M:%S')} ===\n")

    # 1. Check articles in JSONL
    jsonl = project / "data" / "raw" / date_str / "all_articles.jsonl"
    article_count = 0
    sources: dict[str, int] = {}
    if jsonl.exists():
        with open(jsonl) as f:
            for line in f:
                article_count += 1
                try:
                    d = json.loads(line)
                    sid = d.get("source_id", "unknown")
                    sources[sid] = sources.get(sid, 0) + 1
                except json.JSONDecodeError:
                    pass

    # 2. Parse background task output for site completions
    completed_with_articles: dict[str, int] = {}
    completed_zero: list[str] = []
    started_sites: set[str] = set()
    skipped_sites: set[str] = set()
    deadline_yields: dict[str, int] = {}  # site -> yield count
    pass_count = 0  # never-abandon pass count

    if output_file and Path(output_file).exists():
        with open(output_file) as f:
            for line in f:
                # crawl_site_complete — check yielded flag
                m = re.search(r'crawl_site_complete\s+site=(\S+)\s+articles=(\d+)', line)
                if m:
                    site, count = m.group(1), int(m.group(2))
                    yielded = 'yielded=True' in line
                    if yielded:
                        # Deadline-yielded: partial crawl, will be retried
                        deadline_yields[site] = deadline_yields.get(site, 0) + 1
                    elif count > 0:
                        completed_with_articles[site] = max(
                            completed_with_articles.get(site, 0), count
                        )
                    else:
                        if site not in completed_zero:
                            completed_zero.append(site)
                    continue
                # site_already_complete
                m = re.search(r'site_already_complete\s+site_id=(\S+)', line)
                if m:
                    site = m.group(1)
                    skipped_sites.add(site)
                    cnt = sources.get(site, 0)
                    if cnt > 0:
                        completed_with_articles[site] = cnt
                    continue
                # deadline yield (fairness pause — site will be retried)
                if 'site_deadline_yield' in line:
                    m = re.search(r'site_id=(\S+)', line)
                    if m:
                        site = m.group(1)
                        deadline_yields[site] = deadline_yields.get(site, 0) + 1
                    continue
                # never-abandon pass
                if 'crawl_never_abandon_pass' in line:
                    m = re.search(r'pass=(\d+)', line)
                    if m:
                        pass_count = max(pass_count, int(m.group(1)))
                    continue
                # crawl_site_start
                m = re.search(r'crawl_site_start\s+site=(\S+)', line)
                if m:
                    started_sites.add(m.group(1))

    all_done = set(completed_with_articles) | set(completed_zero) | skipped_sites
    in_progress = started_sites - all_done

    success_count = len(completed_with_articles)
    zero_count = len([s for s in completed_zero if s not in completed_with_articles])

    print(f"Sites with articles:    {success_count} / 121")
    print(f"Sites with 0 articles:  {zero_count} (extraction failed)")
    print(f"Sites in progress:      {len(in_progress)}")
    print(f"Deadline yields:        {len(deadline_yields)} sites paused for fairness")
    if pass_count > 0:
        print(f"Never-abandon passes:   {pass_count}")
    print(f"Total articles (JSONL): {article_count}")
    print()

    # Top sites by articles
    if sources:
        print("Top sites by articles:")
        for sid, cnt in sorted(sources.items(), key=lambda x: -x[1])[:15]:
            print(f"  {sid:25s} {cnt:4d} articles")
        print()

    # In progress
    if in_progress:
        print(f"Currently crawling ({len(in_progress)}):")
        for s in sorted(in_progress)[:10]:
            yields = deadline_yields.get(s, 0)
            suffix = f" (yielded {yields}x)" if yields else ""
            print(f"  {s}{suffix}")
        if len(in_progress) > 10:
            print(f"  ... and {len(in_progress) - 10} more")
        print()

    # Deadline yields detail
    if deadline_yields:
        active_yields = {s: c for s, c in deadline_yields.items() if s not in all_done}
        done_yields = {s: c for s, c in deadline_yields.items() if s in all_done}
        if active_yields:
            print(f"Sites awaiting retry after yield ({len(active_yields)}):")
            for site, count in sorted(active_yields.items(), key=lambda x: -x[1])[:10]:
                print(f"  {site:25s} {count:3d} yields")
            if len(active_yields) > 10:
                print(f"  ... and {len(active_yields) - 10} more")
            print()
        if done_yields:
            print(f"Sites completed after yield ({len(done_yields)}):")
            for site, count in sorted(done_yields.items(), key=lambda x: -x[1])[:5]:
                articles = completed_with_articles.get(site, 0)
                print(f"  {site:25s} {count:3d} yields → {articles} articles")
            print()

    # Elapsed
    if output_file and Path(output_file).exists():
        stat = Path(output_file).stat()
        elapsed = datetime.now().timestamp() - stat.st_birthtime
        print(f"Elapsed: {elapsed/60:.1f} minutes")


if __name__ == "__main__":
    main()
