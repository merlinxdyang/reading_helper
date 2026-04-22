# Output Contract

Use this contract when generating or reviewing an `english-reading-layers` package.

## Folder

Required final files:

```text
[YYYYMMDD]_[article-title-slug]/
├── index.md
├── L1_readable.md
├── L2_presentation.md
├── L3_glossary.md
├── L3_glossary.json
├── L4_vocabulary.md
├── L4_vocabulary.json
└── _meta.json
```

The preparation script may also create `_work/doc.json`; keep it unless the user asks for a clean final-only folder.

## index.md

Include:

- Source title, original filename or pasted-text label, generated timestamp.
- Detected or inferred domain, article type, word count, reading-time estimate.
- Links to the four layers and both JSON files.
- Short note on extraction quality if page numbers, tables, formulas, or figures are incomplete.

## _meta.json

Required fields:

```json
{
  "source": "...",
  "title": "...",
  "generated_at": "...",
  "domain": "...",
  "article_type": "...",
  "word_count": 0,
  "estimated_reading_minutes": 0,
  "extraction_notes": [],
  "layers": {
    "readable": "L1_readable.md",
    "presentation": "L2_presentation.md",
    "glossary_md": "L3_glossary.md",
    "glossary_json": "L3_glossary.json",
    "vocabulary_md": "L4_vocabulary.md",
    "vocabulary_json": "L4_vocabulary.json"
  }
}
```

## L1_readable.md

Required structure:

1. Title and source note.
2. Three guide cards:
   - `文章讲什么`
   - `为什么重要`
   - `读完你会知道什么`
3. Section-by-section content:
   - Chinese TL;DR for each major section.
   - Paragraph-level original English.
   - Natural Chinese explanation.
   - Difficulty notes only where useful.
4. Links from first-use terms to `L3_glossary.md` anchors.

Do not translate code blocks or formulas. Explain them after the original if needed.

## L2_presentation.md

Make it Marp-compatible:

```markdown
---
marp: true
title: "..."
---

# English Title
# 中文标题

Speaker notes...

---
```

Required sections:

- Cover.
- Background and motivation.
- Key claims.
- Methodology/evidence if present.
- Findings/implications.
- Critical discussion.
- Q&A rehearsal.

Each slide should include bilingual title and bilingual bullets. Speaker notes should be useful for a 15-20 minute report; avoid script bloat.

## L3_glossary.json

Required shape:

```json
{
  "source": "original filename",
  "generated_at": "ISO-8601 timestamp",
  "domain": "detected discipline",
  "terms": [
    {
      "term_en": "...",
      "abbr": "...",
      "term_zh": "...",
      "definition": "...",
      "context_quote": "...",
      "location": "§2.3 / p.5",
      "domain_tags": ["..."],
      "related": {
        "synonym": [],
        "antonym": [],
        "hypernym": [],
        "hyponym": []
      }
    }
  ]
}
```

`abbr` may be an empty string. `related` arrays may be empty, but keys must exist.

## L3_glossary.md

Include two views:

- Alphabetical index.
- Thematic clusters.

Each entry should include the source quote and location. Keep quotes short: one sentence or the smallest meaningful clause.

## L4_vocabulary.json

Required shape:

```json
{
  "source": "original filename",
  "generated_at": "ISO-8601 timestamp",
  "total_count": 0,
  "words": [
    {
      "word": "ubiquitous",
      "pos": "adj.",
      "ipa": "/juːˈbɪkwɪtəs/",
      "meaning_zh": "无处不在的；普遍存在的",
      "synonyms_en": [
        {"word": "pervasive", "note": "formal; sometimes negative"},
        {"word": "omnipresent", "note": "literary/written"},
        {"word": "widespread", "note": "neutral; common"}
      ],
      "context_sentence": "...",
      "location": "§1 / p.2",
      "level": {"cefr": "C1", "ielts": 7.5}
    }
  ]
}
```

`total_count` must equal `len(words)`. Vocabulary words must not duplicate glossary terms after lowercasing and simple punctuation stripping.

## L4_vocabulary.md

Include:

- Alphabetical vocabulary table.
- Difficulty-grouped view: C1, C2, IELTS 7.0, IELTS 7.5+.
- Short usage notes where synonyms differ in register, collocation, or sentiment.

## Quality Rules

- Make student-facing explanations concrete and readable. Avoid academic paraphrase that preserves the original difficulty.
- Preserve source meaning; flag uncertainty instead of inventing claims.
- Keep location citations consistent with `doc.json`.
- Use estimated difficulty labels honestly; write `estimated` in notes if no external lexical database was used.
- Avoid glossary/vocabulary overlap.
- Validate JSON before finishing.
