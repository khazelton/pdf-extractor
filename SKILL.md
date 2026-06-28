---
name: pdf-extractor
version: 0.1.0
description: Extract text, tables, and form-field values from PDF files. Use when the user wants to pull data out of a PDF, fill a PDF form, or convert PDF content to text/markdown.
---

# PDF Extractor

Extract structured content from PDF files.

## When to use this skill

Use this when the user asks to:
- Pull text or tables out of a PDF
- Read values from a fillable PDF form
- Convert a PDF to markdown or plain text

## Instructions

1. Identify the target PDF path from the user's request.
2. The script depends on `pypdf` and `pdfplumber`, which are installed in a
   venv bundled with this skill. Run the script with the venv interpreter
   (`.venv/bin/python` in the skill directory), not the system `python`.
   If `.venv` is missing, create it once with `uv`:

   ```bash
   uv venv .venv && uv pip install --python .venv -r requirements.txt
   ```

3. For plain text extraction, run the bundled script:

   ```bash
   .venv/bin/python scripts/extract.py <path-to-pdf> --mode text
   ```

4. For form fields, use `--mode fields`. The output is JSON mapping field
   names to values.
5. For tables, use `--mode tables`. By default it detects bordered tables via
   ruled lines. If the table has no borders (columns aligned with whitespace),
   add `--table-strategy text`. On a page that mixes prose and a borderless
   table, also pass `--bbox "x0,top,x1,bottom"` (PDF points, top-left origin)
   to crop to just the table — the text strategy otherwise treats the whole
   page as one table and splits paragraphs into bogus columns. Cross-check
   column alignment against `references/form-fields.md` if the layout looks off.
6. If a borderless table's header still mis-splits (wide header words straddle
   an inferred column edge), pin the columns explicitly with
   `--columns "x0,x1,...,xN"` — the boundary x-coordinates including the outer
   edges. This buckets each word into a column by its center, so headers stay
   intact. Pair it with `--bbox` to also bound the rows (otherwise prose above
   the table gets bucketed in too). To find the coordinates, inspect word
   positions with pdfplumber's `page.extract_words()` (each word has `x0`/`x1`).

## Notes

- If a PDF is scanned (image-only), text extraction will be empty — tell the
  user it needs OCR, which this skill does not perform.
