# Examples

Two sample PDFs and the commands that exercise every mode. Run them from the
skill root (the folder containing `scripts/`).

- `sample.pdf` — a title, a paragraph, a **bordered** table, and a
  **borderless** (whitespace-aligned) table.
- `form.pdf` — a fillable AcroForm with two text fields.

## 1. Plain text

```bash
python scripts/extract.py examples/sample.pdf --mode text
```
Prints the document text (title, paragraph, and both tables flattened).

## 2. Bordered table (`lines`)

```bash
python scripts/extract.py examples/sample.pdf --mode tables --table-strategy lines
```
```json
[
  {"page": 1, "index": 0, "rows": [
    ["Product", "Qty", "Revenue"],
    ["Widget", "120", "$1,440"],
    ["Gadget", "75", "$1,125"],
    ["Gizmo", "40", "$800"]
  ]}
]
```

## 3. Borderless table — pinned columns (`--bbox` + `--columns`)

The borderless table sits at roughly x 110–250, y 315–356, with column edges at
110 / 155 / 205 / 250. Pinning the columns keeps the header intact:

```bash
python scripts/extract.py examples/sample.pdf --mode tables \
    --bbox "110,315,250,356" --columns "110,155,205,250"
```
```json
[
  {"page": 1, "index": 0, "rows": [
    ["Region", "Units", "Margin"],
    ["North", "300", "18%"],
    ["South", "210", "22%"],
    ["West", "185", "15%"]
  ]}
]
```

(For a borderless table on a clean page you can skip `--columns` and just use
`--table-strategy text`; the explicit columns are the fix for headers whose
wide words straddle an inferred edge.)

## 4. Form fields

```bash
python scripts/extract.py examples/form.pdf --mode fields
```
```json
{
  "reviewer": "A. Patel",
  "status": "Approved"
}
```

To find `--bbox`/`--columns` coordinates for your own PDFs, inspect word
positions with pdfplumber: `page.extract_words()` gives each word's
`x0`/`x1`/`top`/`bottom`.
