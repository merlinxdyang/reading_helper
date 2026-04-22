# Reading Helper

`reading_helper` is a Codex skill for turning an assigned English reading into four study-ready layers:

1. **Undergraduate-readable bilingual guide** - paragraph-level English original with natural Chinese explanation.
2. **Classroom presentation version** - bilingual Marp-compatible outline for a 15-20 minute report.
3. **Terminology glossary** - reusable discipline terms in Markdown and JSON.
4. **Advanced vocabulary bank** - non-terminology C1+/IELTS 7+ words in Markdown and JSON.

The goal is simple: help students understand a difficult English reading now, and keep terms and vocabulary searchable later.

## Repository Structure

```text
.
├── SKILL.md
├── agents/
│   └── openai.yaml
├── references/
│   └── output-contract.md
└── scripts/
    ├── prepare_reading_source.py
    └── validate_reading_package.py
```

## What It Produces

For each source reading, the skill creates a package like this:

```text
[YYYYMMDD]_[article-title-slug]/
├── index.md
├── L1_readable.md
├── L2_presentation.md
├── L3_glossary.md
├── L3_glossary.json
├── L4_vocabulary.md
├── L4_vocabulary.json
├── _meta.json
└── _work/
    └── doc.json
```

Supported source formats:

- PDF
- DOCX
- Markdown
- TXT
- pasted English text saved as TXT

## Install as a Codex Skill

Clone or copy this repository into your Codex skills directory:

```bash
mkdir -p ~/.codex/skills
cd ~/.codex/skills
git clone https://github.com/merlinxdyang/reading_helper.git english-reading-layers
```

Then invoke it in Codex with:

```text
Use $english-reading-layers to process this reading: /path/to/article.pdf
```

## Quick Start Without Codex

Prepare an input file into the standard package structure:

```bash
python3 scripts/prepare_reading_source.py /path/to/article.pdf --out-root ./outputs
```

This creates `_work/doc.json`, `_meta.json`, and starter layer files. The actual layer writing is intended for Codex or another LLM following `SKILL.md` and `references/output-contract.md`.

Validate a completed package:

```bash
python3 scripts/validate_reading_package.py ./outputs/20260422_article-title
```

The validator checks required files, JSON structure, glossary/vocabulary separation, synonym counts, and unfinished `TODO` placeholders.

## Notes

- PDF extraction uses `pypdf` first and falls back to `pdfplumber` if available.
- Vocabulary levels are estimates unless an external lexical database is used.
- Glossary terms and vocabulary words are intentionally separated to avoid duplicate study entries.
- `L2_presentation.md` is Marp-compatible, so it can be converted to slides with Marp tooling.

## License

No license has been specified yet.
