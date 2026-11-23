# storygraph-fetch-util

Download StoryGraph data from archive.org. Standard library only (Python 3.8+).

## Usage

### As a library

```python
from fetch_storygraph import fetch_stories, fetch_graphs

day    = fetch_stories("2026-10-01", "day")    # dict (same JSON the Stories view uses)
week   = fetch_stories("2026-10-01", "week")
month  = fetch_stories("2026-10-01", "month")
year   = fetch_stories("2026-10-01", "year")
graphs = fetch_graphs("2026-10-01")            # list of graph snapshots for that day
```

### From the command line

Writes JSON to stdout, or to a file with `-o`:

```sh
python fetch_storygraph.py 2026-10-01 day -o stories.json
python fetch_storygraph.py 2026-10-01 graphs -o graphs.json
```

## Schemas

### `fetch_stories(date, level) -> dict`

One file per time window (day / week / month / year) holding every article in that window.

```jsonc
{
  "params": {
    "date": "2026-10-01",              // start of the window
    "time_interval": "days",           // "days" | "weeks" | "months" | "years"
    "topic_model": "localnews/...",    // model used to assign `topic`
    "total_articles_processed": 92,
    "noise_articles": 39,              // articles with cluster_id == null
    "total_left": 12,
    "total_center": 24,
    "total_right": 56
  },
  "articles": [
    {
      "cluster_id": 3,                 // int | null. HDBSCAN cluster; null = noise
      "representativeness": 0.91,      // float | null. Cosine similarity to the cluster
                                       //   centroid; the top article labels the cluster
      "topic": "Politics & Government",
      "entities": [                    // named entities (spaCy labels: PERSON, ORG,
        {"entity": "Jerome Powell", "class": "PERSON"}   //   GPE, NORP, LOC, FAC, ...)
      ],
      "title": "...",
      "published": "...",              // string; format varies by source
                                       //   (ISO 8601 or RFC 2822)
      "link": "https://...",
      "favicon": "https://...",        // may be ""
      "image": "https://...",          // str | null
      "leaning": "center",             // "left" | "center" | "right"
      "publisher": "reuters"
    }
  ]
}
```

### `fetch_graphs(date) -> list[dict]`

One entry per graph snapshot taken during the day (roughly every 10-15 minutes).
Nodes are articles; links connect similar articles; connected components are stories.

```jsonc
[
  {
    "timestamp": "2026-10-01T00:03:44.609240Z",
    "config": "/files/config/polar-media-consensus-graph/<hash>/",
    "ner-version": "Spacy 3.2.1",
    "nodes": [
      {
        "id": "politicususa.com-1",
        "title": "...",
        "published": "Wed, 30 Sep 2026 19:32:57 GMT",
        "link": "https://...",
        "rss-uri-m": "",
        "summary": "...",
        "text": "...",                   // article body (may be truncated)
        "content": "...",                // present on some nodes only
        "favicon": "",
        "extraction-time": "2026-10-01T00:13:32.666981",
        "entities": [                    // spaCy labels plus TOP_10_TERM and TITLE
          {"entity": "Trump", "class": "ORG"}
        ],
        "node-details": {
          "type": "left",                // political leaning
          "color": "blue",
          "annotation": "polarity",
          "connected-comp-type": ""
        }
      }
    ],
    "links": [
      {"source": 16, "target": 17,       // indices into "nodes"
       "sim": 0.43,                      // similarity score
       "rank": 1}
    ],
    "connected-comps": [
      {
        "nodes": [16, 17],               // indices into "nodes"
        "avg-degree": 1.0,
        "density": 1.0,
        "unique-source-count": 1,
        "node-details": {"annotation": "polarity",
                         "connected-comp-type": "cluster", "color": "red"}
      }
    ]
  }
]
```
