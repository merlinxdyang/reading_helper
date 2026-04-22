#!/usr/bin/env python3
"""Prepare an English reading source for the english-reading-layers skill."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
import zipfile
from html import unescape
from pathlib import Path
from xml.etree import ElementTree as ET


WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]*")
ACRONYM_RE = re.compile(r"\b[A-Z]{2,}(?:-[A-Z0-9]+)*\b")
TITLE_PHRASE_RE = re.compile(r"\b(?:[A-Z][a-z]+(?:[ -]+)){1,5}[A-Z][a-z]+\b")

COMMON_WORDS = {
    "about", "after", "again", "against", "also", "among", "because", "before",
    "between", "could", "during", "first", "found", "from", "have", "however",
    "into", "more", "most", "other", "over", "people", "same", "should", "some",
    "such", "than", "their", "there", "these", "they", "this", "through", "under",
    "using", "very", "were", "what", "when", "where", "which", "while", "with",
    "would", "your",
}

ADVANCED_SUFFIXES = (
    "tion", "sion", "ment", "ance", "ence", "ity", "ism", "ive", "ous",
    "ate", "ize", "ise", "ary", "ory", "ial", "ic", "al",
)


def slugify(text: str, max_len: int = 72) -> str:
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "-", text)
    text = re.sub(r"-+", "-", text).strip("-")
    return (text[:max_len].strip("-") or "english-reading")


def clean_text(text: str) -> str:
    text = unescape(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"(?<=\w)-\n(?=\w)", "", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_paragraphs(text: str) -> list[str]:
    blocks = [re.sub(r"\s+", " ", b).strip() for b in re.split(r"\n\s*\n", text)]
    return [b for b in blocks if b]


def read_text_file(path: Path) -> tuple[str, list[dict]]:
    text = clean_text(path.read_text(encoding="utf-8", errors="replace"))
    return text, [{"kind": "text", "note": "read as UTF-8 text"}]


def read_docx(path: Path) -> tuple[str, list[dict]]:
    notes = [{"kind": "docx", "note": "extracted Word document paragraphs"}]
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    for para in root.findall(".//w:p", ns):
        texts = [node.text or "" for node in para.findall(".//w:t", ns)]
        line = "".join(texts).strip()
        if line:
            paragraphs.append(line)
    return clean_text("\n\n".join(paragraphs)), notes


def read_pdf(path: Path) -> tuple[str, list[dict]]:
    notes: list[dict] = []
    pages: list[str] = []
    try:
        import pypdf  # type: ignore

        reader = pypdf.PdfReader(str(path))
        for i, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            if page_text.strip():
                pages.append(f"[p.{i}]\n{page_text}")
        notes.append({"kind": "pdf", "note": "extracted with pypdf"})
    except Exception as exc:
        notes.append({"kind": "pdf", "note": f"pypdf unavailable or failed: {exc}"})
        try:
            import pdfplumber  # type: ignore

            with pdfplumber.open(str(path)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    page_text = page.extract_text() or ""
                    if page_text.strip():
                        pages.append(f"[p.{i}]\n{page_text}")
            notes.append({"kind": "pdf", "note": "extracted with pdfplumber"})
        except Exception as exc2:
            raise SystemExit(
                "Could not extract PDF text. Install pypdf/pdfplumber or run OCR first. "
                f"Details: {exc2}"
            ) from exc2
    return clean_text("\n\n".join(pages)), notes


def read_source(path: Path) -> tuple[str, list[dict]]:
    suffix = path.suffix.lower()
    if suffix in {".txt", ".md", ".markdown"}:
        return read_text_file(path)
    if suffix == ".docx":
        return read_docx(path)
    if suffix == ".pdf":
        return read_pdf(path)
    raise SystemExit(f"Unsupported input type: {suffix}. Use PDF, DOCX, MD, or TXT.")


def infer_title(path: Path, text: str, explicit: str | None) -> str:
    if explicit:
        return explicit.strip()
    for line in text.splitlines():
        line = line.strip("# ").strip()
        if 5 <= len(line) <= 140 and len(WORD_RE.findall(line)) >= 2:
            return line
    return path.stem.replace("_", " ").replace("-", " ").strip().title()


def paragraph_location(text: str, index: int) -> str:
    page_match = re.search(r"\[p\.(\d+)\]", text[:120])
    if page_match:
        return f"p.{page_match.group(1)} / ¶{index}"
    return f"¶{index}"


def build_paragraphs(text: str) -> list[dict]:
    paragraphs = []
    heading_path: list[str] = []
    for block in split_paragraphs(text):
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", block)
        if heading_match:
            level = len(heading_match.group(1))
            heading = heading_match.group(2).strip()
            heading_path = heading_path[: level - 1] + [heading]
            continue
        clean_block = re.sub(r"^\[p\.\d+\]\s*", "", block).strip()
        if not clean_block:
            continue
        idx = len(paragraphs) + 1
        paragraphs.append(
            {
                "id": f"p{idx:04d}",
                "location": paragraph_location(block, idx),
                "heading_path": heading_path[:],
                "text": clean_block,
            }
        )
    return paragraphs


def estimate_reading_minutes(word_count: int) -> int:
    return max(1, round(word_count / 180))


def candidate_terms(text: str) -> list[dict]:
    seen: set[str] = set()
    terms: list[dict] = []
    for pattern, reason in ((ACRONYM_RE, "acronym"), (TITLE_PHRASE_RE, "capitalized phrase")):
        for match in pattern.finditer(text):
            term = match.group(0).strip()
            key = term.lower()
            if key not in seen and len(term) <= 80:
                seen.add(key)
                terms.append({"term": term, "reason": reason})
    return terms[:200]


def candidate_words(text: str) -> list[dict]:
    counts: dict[str, int] = {}
    for raw in WORD_RE.findall(text):
        word = raw.lower().strip("'")
        if len(word) < 7 or word in COMMON_WORDS:
            continue
        if word.endswith("'s"):
            word = word[:-2]
        counts[word] = counts.get(word, 0) + 1
    scored = []
    for word, count in counts.items():
        score = count
        if len(word) >= 10:
            score += 2
        if word.endswith(ADVANCED_SUFFIXES):
            score += 2
        scored.append((score, word, count))
    scored.sort(reverse=True)
    return [{"word": word, "count": count, "reason": "heuristic advanced candidate"} for _, word, count in scored[:300]]


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_starter_files(package: Path, meta: dict) -> None:
    index = f"""# {meta["title"]}

- Source: {meta["source"]}
- Generated: {meta["generated_at"]}
- Domain: {meta["domain"]}
- Article type: {meta["article_type"]}
- Word count: {meta["word_count"]}
- Estimated reading time: {meta["estimated_reading_minutes"]} minutes

## Layers

- [Layer 1: Readable bilingual guide](L1_readable.md)
- [Layer 2: Classroom presentation](L2_presentation.md)
- [Layer 3: Glossary](L3_glossary.md) / [JSON](L3_glossary.json)
- [Layer 4: Vocabulary](L4_vocabulary.md) / [JSON](L4_vocabulary.json)
"""
    (package / "index.md").write_text(index, encoding="utf-8")
    for filename, title in (
        ("L1_readable.md", "Layer 1: Readable Bilingual Guide"),
        ("L2_presentation.md", "Layer 2: Classroom Presentation"),
        ("L3_glossary.md", "Layer 3: Glossary"),
        ("L4_vocabulary.md", "Layer 4: Vocabulary"),
    ):
        path = package / filename
        if not path.exists():
            path.write_text(f"# {title}\n\nTODO\n", encoding="utf-8")
    if not (package / "L3_glossary.json").exists():
        write_json(package / "L3_glossary.json", {"source": meta["source"], "generated_at": meta["generated_at"], "domain": meta["domain"], "terms": []})
    if not (package / "L4_vocabulary.json").exists():
        write_json(package / "L4_vocabulary.json", {"source": meta["source"], "generated_at": meta["generated_at"], "total_count": 0, "words": []})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path, help="Input PDF, DOCX, Markdown, or text file")
    parser.add_argument("--out-root", type=Path, default=Path.cwd(), help="Directory where the package folder is created")
    parser.add_argument("--title", help="Override inferred title")
    parser.add_argument("--date", help="YYYYMMDD folder prefix; defaults to today")
    args = parser.parse_args()

    source = args.source.expanduser().resolve()
    if not source.exists():
        raise SystemExit(f"Input file not found: {source}")

    text, notes = read_source(source)
    title = infer_title(source, text, args.title)
    today = args.date or dt.datetime.now().strftime("%Y%m%d")
    generated_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    package = args.out_root.expanduser().resolve() / f"{today}_{slugify(title)}"
    work = package / "_work"
    work.mkdir(parents=True, exist_ok=True)

    paragraphs = build_paragraphs(text)
    word_count = len(WORD_RE.findall(text))
    meta = {
        "source": source.name,
        "source_path": str(source),
        "title": title,
        "generated_at": generated_at,
        "domain": "undetermined",
        "article_type": "undetermined",
        "word_count": word_count,
        "estimated_reading_minutes": estimate_reading_minutes(word_count),
        "extraction_notes": notes,
        "layers": {
            "readable": "L1_readable.md",
            "presentation": "L2_presentation.md",
            "glossary_md": "L3_glossary.md",
            "glossary_json": "L3_glossary.json",
            "vocabulary_md": "L4_vocabulary.md",
            "vocabulary_json": "L4_vocabulary.json",
        },
    }
    doc = {
        "meta": meta,
        "paragraphs": paragraphs,
        "candidate_terms": candidate_terms(text),
        "candidate_words": candidate_words(text),
    }

    write_json(work / "doc.json", doc)
    write_json(package / "_meta.json", meta)
    write_starter_files(package, meta)
    print(package)
    return 0


if __name__ == "__main__":
    sys.exit(main())
