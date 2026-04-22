# Reading Helper / 英文阅读辅助

## 中文说明

`reading_helper` 是一个 Codex skill，用来把老师布置的英文阅读材料一次性转成四层学习资料：

1. **本科生可读版**：保留英文原文，并提供自然中文意译，帮助学生先看懂。
2. **课堂汇报版**：生成适合 15-20 分钟 presentation 的双语 Marp 大纲和讲稿。
3. **术语索引库**：提取学科术语，输出 Markdown 和 JSON，方便长期检索。
4. **生词库**：提取非术语类高级词汇，面向 CEFR C1+ / 雅思 7+，输出 Markdown 和 JSON。

核心目标是：先解决“这篇英文材料看不懂”，再解决“重要术语和生词以后还找得到”。

## English Overview

`reading_helper` is a Codex skill that turns an assigned English reading into four study-ready layers:

1. **Undergraduate-readable bilingual guide**: keeps the English original and adds natural Chinese explanations.
2. **Classroom presentation version**: creates a bilingual Marp-compatible outline and speaker notes for a 15-20 minute report.
3. **Terminology glossary**: extracts reusable discipline terms in Markdown and JSON.
4. **Advanced vocabulary bank**: extracts non-terminology C1+/IELTS 7+ vocabulary in Markdown and JSON.

The goal is to help students understand difficult English readings now, while keeping important terms and vocabulary searchable later.

## 仓库结构 / Repository Structure

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

- `SKILL.md`：Codex skill 的主说明，定义触发场景和完整工作流。
- `agents/openai.yaml`：Codex UI 中显示的 skill 元数据。
- `references/output-contract.md`：四层输出的文件结构、JSON 字段和质量规则。
- `scripts/prepare_reading_source.py`：把 PDF/DOCX/Markdown/TXT 预处理成统一的 `doc.json` 和输出包骨架。
- `scripts/validate_reading_package.py`：检查最终输出包是否完整、JSON 是否合规、术语库和生词库是否重复。

English:

- `SKILL.md`: main Codex skill instructions and workflow.
- `agents/openai.yaml`: skill metadata for Codex UI.
- `references/output-contract.md`: required output structure, JSON fields, and quality rules.
- `scripts/prepare_reading_source.py`: prepares PDF/DOCX/Markdown/TXT sources into `doc.json` and starter output files.
- `scripts/validate_reading_package.py`: validates completed reading packages.

## 输出内容 / What It Produces

每篇阅读材料会生成一个独立文件夹：

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

支持的输入格式：

- PDF
- DOCX
- Markdown
- TXT
- 粘贴文本保存成 TXT

English:

Each source reading becomes a standalone package with the files above. Supported inputs include PDF, DOCX, Markdown, TXT, and pasted text saved as TXT.

## 安装为 Codex Skill / Install as a Codex Skill

把这个仓库克隆到 Codex skills 目录：

```bash
mkdir -p ~/.codex/skills
cd ~/.codex/skills
git clone https://github.com/merlinxdyang/reading_helper.git english-reading-layers
```

然后在 Codex 中这样调用：

```text
Use $english-reading-layers to process this reading: /path/to/article.pdf
```

English:

Clone this repository into your Codex skills directory, then invoke it with `$english-reading-layers` and provide the source reading path.

## 不通过 Codex 直接使用脚本 / Quick Start Without Codex

先把输入材料预处理成标准输出包结构：

```bash
python3 scripts/prepare_reading_source.py /path/to/article.pdf --out-root ./outputs
```

这会生成 `_work/doc.json`、`_meta.json` 和四层输出的起始文件。真正的四层内容撰写仍然建议由 Codex 或其他 LLM 按照 `SKILL.md` 与 `references/output-contract.md` 完成。

完成后校验输出包：

```bash
python3 scripts/validate_reading_package.py ./outputs/20260422_article-title
```

校验器会检查：

- 必需文件是否存在。
- JSON 字段是否完整。
- 术语库和生词库是否重复。
- 每个生词是否有 2-4 个英文近义词。
- Markdown 中是否还残留未完成的 `TODO` 占位符。

English:

Use `prepare_reading_source.py` to create the standard package structure, then use `validate_reading_package.py` to check the completed output. The actual study layers are intended to be written by Codex or another LLM following the skill instructions and output contract.

## 使用说明 / Notes

- PDF 解析优先使用 `pypdf`，失败时会尝试 `pdfplumber`。
- 生词难度等级是估算值，除非接入真实词频或考试词汇数据库。
- 术语库和生词库刻意分离，避免同一个概念在两个学习库中重复出现。
- `L2_presentation.md` 兼容 Marp，可进一步转换为 PPT 或幻灯片。

English:

- PDF extraction uses `pypdf` first and falls back to `pdfplumber` if available.
- Vocabulary difficulty levels are estimates unless an external lexical database is used.
- Glossary terms and vocabulary entries are intentionally separated.
- `L2_presentation.md` is Marp-compatible.

## 许可证 / License

暂未指定许可证。

No license has been specified yet.
