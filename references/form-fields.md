# Form-field & table reference

Notes the skill can consult when a PDF's layout is ambiguous.

## Common fillable-form field types

| PDF field type | Meaning              | Value shape          |
|----------------|----------------------|----------------------|
| `/Tx`          | Text field           | string               |
| `/Btn`         | Checkbox / radio     | `/On` `/Off` or name |
| `/Ch`          | Choice (dropdown)    | string               |
| `/Sig`         | Signature            | usually empty        |

## Table-alignment tips

- If columns merge in the output, the PDF likely uses whitespace rather than
  ruled lines — switch the extractor to a layout-aware mode.
- Right-aligned numeric columns can shift; trust the header row to fix column
  boundaries.
- Multi-line cells appear as separate rows — re-join rows that share the same
  leading key column.
