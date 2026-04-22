---
name: english-reading-layers
description: >-
  Create four study outputs from an English reading material: a bilingual undergraduate-readable guide, a bilingual classroom presentation/Marp outline, a reusable terminology glossary in Markdown and JSON, and a separate advanced vocabulary bank in Markdown and JSON. Use when Codex is asked to help students understand assigned English readings, convert PDF/DOCX/Markdown/TXT/pasted English materials into Chinese-English learning aids, prepare classroom reports, extract academic terms, or build searchable term/vocabulary indexes for future study.
---

# English Reading Layers

Turn one English source into a complete study package:

1. `L1_readable.md` - bilingual undergraduate-readable version.
2. `L2_presentation.md` - bilingual 15-20 minute classroom report, Marp-compatible.
3. `L3_glossary.md` and `L3_glossary.json` - reusable discipline glossary.
4. `L4_vocabulary.md` and `L4_vocabulary.json` - advanced non-terminology vocabulary bank.

Use this skill to produce all four layers by default. Do not ask which layer to make unless the user explicitly requests a subset.

## Workflow

1. **Normalize the source.**
   - For a local file, run `scripts/prepare_reading_source.py <input-file> --out-root <output-root>`.
   - For pasted text, save it as a temporary `.txt` source, then run the same script.
   - Keep formulas, code blocks, tables, citations, and quoted source sentences intact.
   - If PDF extraction is poor, use a stronger PDF/OCR workflow before generating layers.

2. **Read the intermediate `doc.json`.**
   - Use `_work/doc.json` as the shared source of truth for title, sections, paragraphs, locations, word count, and candidate terms/words.
   - Do not repeatedly parse the original source once `doc.json` is available.

3. **Generate Layer 1.**
   - Begin with three short guide cards: what the article says, why it matters, and what the student will know after reading.
   - For each major section, add a 2-3 sentence Chinese TL;DR.
   - Provide paragraph-level English original plus natural Chinese explanation. Translate meaning, not word order.
   - Add concise difficulty notes for abstract concepts, methods, metaphors, or dense argument transitions.
   - Mark first appearances of glossary terms with links to `L3_glossary.md`.

4. **Generate Layer 2.**
   - Extract the argument skeleton: thesis, arguments, evidence, conclusion.
   - Write a Marp-compatible slide deck outline with bilingual slide titles and bilingual bullet points.
   - Include speaker notes for each slide: 60-90 seconds, Chinese first unless the user asks otherwise, with useful English phrasing.
   - Add visual suggestions where a figure, table, timeline, flowchart, or comparison matrix would help.
   - Include 3-5 likely Q&A questions with suggested answers.

5. **Generate Layer 3.**
   - Include discipline terms, acronyms, defined phrases, theory names, methods, named metrics, and high-value noun phrases.
   - Exclude ordinary difficult words that are not field concepts; those belong in Layer 4.
   - For each term, provide English term, abbreviation expansion if any, Chinese translation and common variants, one-sentence definition, source context quote, location, domain tags, and related concepts.
   - Output both human-readable Markdown and machine-readable JSON.

6. **Generate Layer 4.**
   - Include advanced general vocabulary estimated at CEFR C1+ or IELTS 7+.
   - Exclude Layer 3 terms, proper names, places, organizations, numbers, units, formulas, and code identifiers.
   - Lemmatize and deduplicate by dictionary headword.
   - For each word, provide part of speech, US IPA when available, Chinese meaning based on the source context, 2-4 English synonyms with register notes, source sentence, location, and estimated difficulty.
   - Output both Markdown and JSON.

7. **Package and validate.**
   - Final folder name: `[YYYYMMDD]_[article-title-slug]/`.
   - Required files: `index.md`, `L1_readable.md`, `L2_presentation.md`, `L3_glossary.md`, `L3_glossary.json`, `L4_vocabulary.md`, `L4_vocabulary.json`, `_meta.json`.
   - Run `scripts/validate_reading_package.py <package-folder>` before finishing.
   - Report any extraction limits, uncertain vocabulary levels, or missing page numbers.

## Output Contract

Read `references/output-contract.md` when generating or reviewing package contents. It defines required file structures, JSON fields, quality checks, and validation expectations.

## Defaults

- Produce all layers in one pass.
- Use bilingual Chinese-English output for Layers 1 and 2.
- Use Markdown plus JSON for Layers 3 and 4.
- Keep terms and vocabulary separate; glossary terms must not appear as vocabulary entries.
- Treat CEFR and IELTS levels as estimates unless a real lexical database is available.
- Use source locations from `doc.json`; if page numbers are unavailable, cite section and paragraph ids.
- Prefer concise study usefulness over exhaustive translation.
