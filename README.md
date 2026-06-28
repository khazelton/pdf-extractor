# pdf-extractor skill

Extract text, tables, and form-field values from PDF files. Bordered tables,
borderless (whitespace-aligned) tables, and fillable AcroForm fields are all
supported.

## Install

### Claude Code (CLI)

Unzip into one of:

- `~/.claude/skills/` — available in every project
- `<repo>/.claude/skills/` — scoped to one project (commit it to share via git)

The archive already contains a top-level `pdf-extractor/` folder, so extract it
into the `skills/` directory itself. If you don't have an `unzip` binary, use
Python's built-in extractor (works anywhere Python is installed):

```bash
unzip pdf-extractor-skill.zip -d ~/.claude/skills/
# or, no unzip binary needed:
python3 -m zipfile -e pdf-extractor-skill.zip ~/.claude/skills/
```

Then install the Python dependencies:

```bash
uv pip install -r ~/.claude/skills/pdf-extractor/requirements.txt
# or with plain pip:
pip install -r ~/.claude/skills/pdf-extractor/requirements.txt
```

Invoke with `/pdf-extractor`, or just ask Claude to pull data out of a PDF and
it will trigger automatically.

### claude.ai

Upload the zip via **Settings → Capabilities/Features → Skills**. Note that
claude.ai runs skills in a restricted sandbox, so the script's local Python
execution may behave differently than in Claude Code.

## Using the script directly

```bash
python scripts/extract.py <file.pdf> --mode text
python scripts/extract.py <file.pdf> --mode fields
python scripts/extract.py <file.pdf> --mode tables --table-strategy lines
python scripts/extract.py <file.pdf> --mode tables --table-strategy text \
    --bbox "x0,top,x1,bottom"
python scripts/extract.py <file.pdf> --mode tables \
    --bbox "x0,top,x1,bottom" --columns "x0,x1,...,xN"
```

| Flag | Purpose |
|------|---------|
| `--mode text\|fields\|tables` | What to extract (default: `text`) |
| `--table-strategy lines\|text` | `lines` for bordered tables (default), `text` for borderless |
| `--bbox "x0,top,x1,bottom"` | Crop to a region (PDF points, top-left origin) — recommended with `text` |
| `--columns "x0,x1,...,xN"` | Pin exact column edges; best paired with `--bbox` |

Coordinates are in PDF points. Find them with pdfplumber's
`page.extract_words()` (each word has `x0`/`x1`/`top`/`bottom`).

## Contents

```
pdf-extractor/
├── SKILL.md              # skill definition (frontmatter + instructions)
├── README.md             # this file
├── requirements.txt      # Python dependencies
├── scripts/
│   └── extract.py        # the extractor CLI
├── references/
│   └── form-fields.md    # field-type & table-alignment reference
└── examples/
    ├── README.md         # runnable commands + expected output
    ├── sample.pdf        # text + bordered + borderless tables
    └── form.pdf          # two fillable form fields
```
