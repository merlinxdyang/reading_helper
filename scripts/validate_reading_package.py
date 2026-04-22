#!/usr/bin/env python3
"""Validate an english-reading-layers output package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


REQUIRED_FILES = [
    "index.md",
    "L1_readable.md",
    "L2_presentation.md",
    "L3_glossary.md",
    "L3_glossary.json",
    "L4_vocabulary.md",
    "L4_vocabulary.json",
    "_meta.json",
]

GLOSSARY_TERM_FIELDS = {
    "term_en",
    "abbr",
    "term_zh",
    "definition",
    "context_quote",
    "location",
    "domain_tags",
    "related",
}

VOCAB_FIELDS = {
    "word",
    "pos",
    "ipa",
    "meaning_zh",
    "synonyms_en",
    "context_sentence",
    "location",
    "level",
}


def load_json(path: Path) -> dict:
    try:
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)
    except Exception as exc:
        raise ValueError(f"{path.name} is not valid JSON: {exc}") from exc


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.lower())


def validate(package: Path) -> list[str]:
    errors: list[str] = []
    for filename in REQUIRED_FILES:
        path = package / filename
        if not path.exists():
            errors.append(f"missing required file: {filename}")
        elif path.stat().st_size == 0:
            errors.append(f"empty required file: {filename}")
        elif path.suffix.lower() == ".md":
            text = path.read_text(encoding="utf-8", errors="replace")
            if re.search(r"(?m)^\s*TODO\s*$", text):
                errors.append(f"unfinished placeholder in: {filename}")

    if errors:
        return errors

    meta = load_json(package / "_meta.json")
    for field in ("source", "title", "generated_at", "domain", "article_type", "word_count", "estimated_reading_minutes", "layers"):
        if field not in meta:
            errors.append(f"_meta.json missing field: {field}")

    glossary = load_json(package / "L3_glossary.json")
    for field in ("source", "generated_at", "domain", "terms"):
        if field not in glossary:
            errors.append(f"L3_glossary.json missing field: {field}")
    if not isinstance(glossary.get("terms", []), list):
        errors.append("L3_glossary.json terms must be a list")

    glossary_keys: set[str] = set()
    for i, term in enumerate(glossary.get("terms", [])):
        missing = GLOSSARY_TERM_FIELDS - set(term)
        if missing:
            errors.append(f"L3_glossary.json terms[{i}] missing fields: {sorted(missing)}")
        if "term_en" in term:
            glossary_keys.add(normalize_key(str(term["term_en"])))
        related = term.get("related", {})
        for key in ("synonym", "antonym", "hypernym", "hyponym"):
            if key not in related:
                errors.append(f"L3_glossary.json terms[{i}].related missing key: {key}")

    vocab = load_json(package / "L4_vocabulary.json")
    for field in ("source", "generated_at", "total_count", "words"):
        if field not in vocab:
            errors.append(f"L4_vocabulary.json missing field: {field}")
    words = vocab.get("words", [])
    if not isinstance(words, list):
        errors.append("L4_vocabulary.json words must be a list")
        words = []
    if vocab.get("total_count") != len(words):
        errors.append("L4_vocabulary.json total_count must equal len(words)")

    seen_words: set[str] = set()
    for i, word in enumerate(words):
        missing = VOCAB_FIELDS - set(word)
        if missing:
            errors.append(f"L4_vocabulary.json words[{i}] missing fields: {sorted(missing)}")
        key = normalize_key(str(word.get("word", "")))
        if not key:
            errors.append(f"L4_vocabulary.json words[{i}] has empty word")
        if key in seen_words:
            errors.append(f"L4_vocabulary.json duplicate word: {word.get('word')}")
        seen_words.add(key)
        if key in glossary_keys:
            errors.append(f"vocabulary duplicates glossary term: {word.get('word')}")
        synonyms = word.get("synonyms_en", [])
        if not isinstance(synonyms, list) or not (2 <= len(synonyms) <= 4):
            errors.append(f"L4_vocabulary.json words[{i}].synonyms_en must contain 2-4 items")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    package = args.package.expanduser().resolve()
    if not package.is_dir():
        raise SystemExit(f"Not a directory: {package}")
    errors = validate(package)
    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print("Validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
