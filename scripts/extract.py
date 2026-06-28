#!/usr/bin/env python3
"""Extract text, tables, or form-field values from a PDF.

Uses pypdf for text and form fields, and pdfplumber for tables. Install with:
    pip install pypdf pdfplumber
"""

import argparse
import json
import sys


def extract_text(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    return "\n\n".join(page.extract_text() or "" for page in reader.pages)


def extract_fields(path):
    from pypdf import PdfReader

    reader = PdfReader(path)
    fields = reader.get_fields() or {}
    return {name: (f.get("/V") if hasattr(f, "get") else None)
            for name, f in fields.items()}


def _clean_rows(rows):
    """Normalize cells and drop fully-empty rows.

    pdfplumber yields None for empty cells; the text strategy also emits blank
    spacer rows between content rows. Returns None if nothing survives.
    """
    cleaned = []
    for row in rows:
        cells = [(cell or "").strip() for cell in row]
        if any(cells):
            cleaned.append(cells)
    return cleaned or None


def extract_tables(path, strategy="lines", bbox=None, columns=None):
    """Return a list of tables, one per detected table, each a list of rows.

    strategy selects how pdfplumber finds table boundaries:
      "lines" - use ruled lines drawn in the PDF (default; best for bordered
                tables)
      "text"  - infer columns/rows from text alignment (use for borderless
                tables laid out with whitespace)

    bbox, if given, is a (x0, top, x1, bottom) tuple in PDF points; only that
    region of each page is scanned. The text strategy treats a whole page as
    one table and splits prose into bogus columns, so cropping to just the
    table is the reliable way to use it on a mixed-content page.

    columns, if given, is a sorted list of x-coordinates (PDF points) for the
    column boundary lines, including the outer left/right edges. It pins the
    column positions exactly instead of inferring them, which fixes borderless
    headers whose wide words straddle an inferred edge. When set, columns are
    assigned by bucketing each word's center between the boundaries (see
    _extract_by_columns); pdfplumber's intersection model is bypassed.
    """
    import pdfplumber

    table_settings = {
        "vertical_strategy": strategy,
        "horizontal_strategy": strategy,
    }
    if strategy == "text":
        # Group characters into words before inferring column edges, and only
        # draw an edge where several words actually line up. This cuts the
        # mid-word column splits the bare text strategy produces.
        table_settings.update(
            {
                "text_x_tolerance": 3,
                "text_y_tolerance": 3,
                "min_words_vertical": 2,
                "min_words_horizontal": 1,
            }
        )

    tables = []
    with pdfplumber.open(path) as pdf:
        for page_number, page in enumerate(pdf.pages, start=1):
            region = page.crop(bbox) if bbox else page
            if columns:
                rows = _extract_by_columns(region, columns)
                if rows:
                    tables.append(
                        {"page": page_number, "index": 0, "rows": rows}
                    )
                continue
            for table_index, table in enumerate(
                region.extract_tables(table_settings)
            ):
                rows = _clean_rows(table)
                if rows is None:
                    continue
                tables.append(
                    {
                        "page": page_number,
                        "index": table_index,
                        "rows": rows,
                    }
                )
    return tables


def _extract_by_columns(region, columns, y_tolerance=3):
    """Split words in `region` into a grid using explicit column boundaries.

    Words are grouped into rows by their vertical position, then each word is
    placed in the column whose [left, right) boundary span contains the word's
    horizontal center. Words outside the outer boundaries are ignored. Returns a
    list of rows (each a list of column strings), or None if no words fall in
    range.
    """
    left, right = columns[0], columns[-1]
    n_cols = len(columns) - 1

    def column_of(word):
        center = (word["x0"] + word["x1"]) / 2
        if center < left or center >= right:
            return None
        for i in range(n_cols):
            if columns[i] <= center < columns[i + 1]:
                return i
        return None

    # Bucket words into rows keyed by their top coordinate (within tolerance).
    rows_by_top = []  # list of [top, {col_index: [words]}]
    for word in sorted(region.extract_words(), key=lambda w: (w["top"], w["x0"])):
        col = column_of(word)
        if col is None:
            continue
        for entry in rows_by_top:
            if abs(entry[0] - word["top"]) <= y_tolerance:
                entry[1].setdefault(col, []).append(word)
                break
        else:
            rows_by_top.append([word["top"], {col: [word]}])

    rows = []
    for _, cols in sorted(rows_by_top, key=lambda e: e[0]):
        row = [""] * n_cols
        for col, words in cols.items():
            row[col] = " ".join(w["text"] for w in words)
        rows.append(row)
    return rows or None


def _parse_bbox(text):
    parts = [p.strip() for p in text.split(",")]
    if len(parts) != 4:
        raise argparse.ArgumentTypeError(
            "--bbox expects 'x0,top,x1,bottom' (four numbers in PDF points)"
        )
    try:
        return tuple(float(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError("--bbox values must be numbers")


def _parse_columns(text):
    parts = [p.strip() for p in text.split(",") if p.strip()]
    if len(parts) < 2:
        raise argparse.ArgumentTypeError(
            "--columns expects at least two x-coordinates (the outer edges)"
        )
    try:
        return sorted(float(p) for p in parts)
    except ValueError:
        raise argparse.ArgumentTypeError("--columns values must be numbers")


def main():
    parser = argparse.ArgumentParser(description="Extract content from a PDF.")
    parser.add_argument("path", help="Path to the PDF file")
    parser.add_argument(
        "--mode",
        choices=["text", "fields", "tables"],
        default="text",
        help="What to extract (default: text)",
    )
    parser.add_argument(
        "--table-strategy",
        choices=["lines", "text"],
        default="lines",
        help=(
            "How to detect tables in --mode tables: 'lines' for ruled/bordered "
            "tables (default), 'text' for borderless tables aligned with "
            "whitespace"
        ),
    )
    parser.add_argument(
        "--bbox",
        type=_parse_bbox,
        default=None,
        metavar="x0,top,x1,bottom",
        help=(
            "Crop each page to this region (PDF points, top-left origin) before "
            "extracting tables. Strongly recommended with --table-strategy text "
            "to isolate the table from surrounding prose"
        ),
    )
    parser.add_argument(
        "--columns",
        type=_parse_columns,
        default=None,
        metavar="x0,x1,x2,...",
        help=(
            "Explicit column boundary x-coordinates (PDF points), including the "
            "outer left/right edges. Pins columns exactly for borderless tables "
            "whose headers straddle an inferred edge; rows are still inferred. "
            "Pair with --bbox to also bound the rows"
        ),
    )
    args = parser.parse_args()

    if args.mode == "text":
        print(extract_text(args.path))
    elif args.mode == "fields":
        print(json.dumps(extract_fields(args.path), indent=2))
    elif args.mode == "tables":
        print(json.dumps(
            extract_tables(
                args.path, args.table_strategy, args.bbox, args.columns
            ),
            indent=2,
        ))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001 - surface a clean error to the caller
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
