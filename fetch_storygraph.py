"""Download StoryGraph data from archive.org. Standard library only (Python 3.8+).

See README.md for usage and the schemas of the returned data.
"""

import argparse
import datetime as dt
import gzip
import json
import urllib.request

BASE = "https://archive.org/download/storygraph-data-usa-{y}-{m}/{d}/"


def _get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "storygraph-fetch"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw = resp.read()
    try:
        return gzip.decompress(raw)
    except OSError:  # not gzipped
        return raw


def stories_url(date, level="day"):
    """Build the archive.org URL for a stories file. date: 'YYYY-MM-DD' or datetime.date."""
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)

    if level == "day":
        name = f"stories-day-{date:%Y-%m-%d}.json.gz"
    elif level == "week":
        # Weekly files live under the Monday of the ISO week.
        week_num = date.isocalendar()[1]
        date = date - dt.timedelta(days=date.weekday())
        name = f"stories-week-{date:%Y-%m}-w{week_num:02d}.json.gz"
    elif level == "month":
        name = f"stories-month-{date:%Y-%m}.json.gz"
    elif level == "year":
        name = f"stories-year-{date:%Y}.json.gz"
    else:
        raise ValueError("level must be one of: day, week, month, year")

    return BASE.format(y=f"{date:%Y}", m=f"{date:%m}", d=f"{date:%d}") + name


def fetch_stories(date, level="day"):
    """Fetch the aggregated stories/articles JSON for a day, week, month, or year."""
    return json.loads(_get(stories_url(date, level)))


def fetch_graphs(date):
    """Fetch every graph snapshot for a day (the Storygraph view's data), as a list of dicts."""
    if isinstance(date, str):
        date = dt.date.fromisoformat(date)
    url = BASE.format(y=f"{date:%Y}", m=f"{date:%m}", d=f"{date:%d}") + f"graphs-{date:%Y-%m-%d}.jsonl.gz"
    text = _get(url).decode("utf-8")
    return [json.loads(line) for line in text.splitlines() if line.strip()]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="Download StoryGraph data from archive.org")
    p.add_argument("date", help="YYYY-MM-DD")
    p.add_argument("kind", choices=["day", "week", "month", "year", "graphs"])
    p.add_argument("-o", "--out", help="output file (default: stdout)")
    args = p.parse_args()

    data = fetch_graphs(args.date) if args.kind == "graphs" else fetch_stories(args.date, args.kind)
    out = json.dumps(data, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        print(out)

