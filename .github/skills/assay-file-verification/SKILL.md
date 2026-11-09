---
name: assay-file-verification
description: 'Verify a customized ISA-Tab assay file (a_*.txt) against the isatools validation rules in isatools/isatab/validate. Use when: checking an assay file before committing, debugging validation errors/warnings by rule code, reviewing assay column headers and node/process ordering, verifying the STUDY ASSAYS declaration (measurement type, technology type, filename) in the investigation file matches the assay table configuration, checking Sample Name values against the study files, or auditing data file columns and ontology qualifiers.'
---

# Assay File Verification

Verifies customized ISA-Tab assay files (`a_*.txt`) using the exact rules implemented in
`isatools/isatab/validate` (this repo), plus a manual checklist for issues the validator
can only warn about — or skips silently.

## When to Use

- You created or edited an assay file and want to confirm it is valid ISA-Tab.
- The validator reported errors/warnings and you need to map rule codes to fixes.
- You declared a new assay in STUDY ASSAYS and want to confirm the
  (measurement type, technology type) pair resolves to a loaded table config.
- You changed headers or added `Extract Name`, `Labeled Extract Name`, data file,
  `Parameter Value[...]`, or `Comment[...]` columns and want to confirm structure.

## Rule Codes (assay tables)

The assay validator (`isatools/isatab/validate/rules/defaults.py`,
`DEFAULT_ASSAY_RULES = ("4014", "4007", "4003", "4011", "1099", "4009", "3010", "0000", "5001")`)
runs, in order, once per assay declared in STUDY ASSAYS:

| Code | Check | Severity |
|------|-------|----------|
| 4014 | Header labels recognised and correctly ordered/grouped | Error (Warning if a bracketed label name is missing) |
| 4007 | No empty cells in `Factor Value[...]` columns | Warning |
| 4003 | Required columns from the assay table config present/non-duplicated | Warning (codes 4010/4013) |
| 4011 | Cell values match config data types (boolean, date, integer, double, list) | Warning |
| 1099 | Unit fields are valid | Warning |
| 4009 | Last `Protocol REF` followed by material/data node; protocol types match config order | Warning |
| 3010 | Ontology fields: `Term Source REF`/`Term Accession Number` follow annotated columns | Warning |
| 0000 | Every `Sample Name` in the assay file exists in the study file | Warning (emitted as code 1003) |
| 5001 | Study group count | Info |

The assay config is selected by `(Study Assay Measurement Type, Study Assay Technology Type)`
from the STUDY ASSAYS row (both lowercased) — see
[config-table.md](./references/config-table.md).

Investigation-level rules that also touch assay files: 0006/0008 (assay file exists),
4002 (measurement/technology pair has a config), 1003/1013 (samples declared in study),
1007/1019 (protocols declared), 1008/1021 (factors declared), 1009/1020 (parameters used
declared), 3008 (ontology sources).

Full per-rule detail: [rules catalog](./references/rules-catalog.md).

## Procedure

1. **Run the bundled checker** (uses this repo's own validator):

   `python .github/skills/assay-file-verification/scripts/verify_assay.py <dir-or-i_file>`

   Full mode prints the STUDY ASSAYS declarations, the assay file header columns,
   then errors/warnings grouped as assay-file issues vs. investigation/cross-file
   issues, each tagged with its rule code.

   **Single-file mode** (before the assay is wired into STUDY ASSAYS):

   `python .github/skills/assay-file-verification/scripts/verify_assay.py a_myassay.txt`

   runs only the investigation-independent checks (4014 structure, 4007 empty
   factor values). Re-run in full mode after declaring the assay.

2. **Read the report by rule code.** Fix errors first: 4002 (unknown
   measurement/technology pair — no assay rules can run without a config), 4014
   (structural), 0008/0006 (assay file declared but missing on disk), 1013/1003
   (samples not in study file), 1008/1007-style declaration mismatches. Warnings
   (4007, 4010–4013, 4011, 1099, 3010, etc.) don't block loading but fix before committing.

3. **Manual header checklist** (mirror of rule 4014 `load_table_checks`):
   - First column is `Sample Name`; the table is a chain of
     `material node → Protocol REF(s) → material/data node` to the final data file column.
   - Assay-only nodes never appear in study files: `Extract Name`,
     `Labeled Extract Name` (followed by `Label`), and data file columns
     (`Raw Data File`, `Raw Spectral Data File`, `Image File`, `Derived Data File`,
     `Array Data File`, `Metabolite Assignment File`, etc.).
   - After `Sample Name`/`Extract Name`/`Labeled Extract Name`: only
     `Characteristics[...]`, `Factor Value[...]` (samples only), `Comment[...]`, and
     qualifiers `Term Source REF`, `Term Accession Number`, `Unit`.
   - After `Protocol REF`: only `Parameter Value[...]`, `Date`, `Performer`,
     `Comment[...]`, qualifiers, and assay annotation columns `Assay Name`,
     `MS Assay Name`, `NMR Assay Name`, `Hybridization Assay Name`,
     `Array Design REF`, `Scan Name`, `Normalization Name`, `Data Transformation Name`.
   - After a data file column: only `Comment[...]`.
   - Every bracketed label has a non-empty name; qualifier triples appear in order
     (value, `Term Source REF`, `Term Accession Number`; `Unit` first for unit values).
   - The final protocol group must be followed by a data/material node (rule 4009).
   - The protocol type sequence between nodes must match the config's
     `protocol-field` order (see config-table.md), e.g. for sequencing assays:
     extraction → (labeling) → assay (sequence? no — library construction/sequencing).

4. **Cross-file consistency** (investigation rules):
   - The STUDY ASSAYS row exists and its measurement/technology pair resolves to a
     config (rule 4002) — use exact term-labels from config-table.md (case-insensitive).
   - Every `Sample Name` in the assay file is defined in the study `Sample Name`
     column (rules 1013/0000→1003). Names must match exactly.
   - Every `Protocol REF` value is declared in the study's STUDY PROTOCOLS
     `Study Protocol Name` (rule 1007); parameter names used in
     `Parameter Value[...]` belong to that protocol's declared parameters where
     applicable (rule 1009).
   - Every `Factor Value[X]` name X is declared in STUDY FACTORS (rule 1008).
   - Every `Term Source REF` value exists in ONTOLOGY SOURCE REFERENCE (rule 3008).
   - `Study Assay File Name` equals the on-disk `a_*.txt` filename (rule 0008/0006).

5. **Silent gaps the validator will NOT report** (check manually):
   - An `a_*.txt` file on disk that is NOT listed in STUDY ASSAYS is never validated.
   - STUDY ASSAYS rows with an empty `Study Assay File Name` are skipped entirely —
     but the STUDY ASSAYS section itself must exist (even with empty values) for the
     investigation parser.
   - If the (measurement, technology) pair has no config (rule 4002), assay-table
     rules effectively cannot run — fix the declaration first.

6. **Report results.** State: errors found (blocking), warnings (non-blocking), and the
   exact cell/column/row from the supplemental message for each finding.

## Resources

- [verify_assay.py](./scripts/verify_assay.py) — runs the isatools validator and dumps
  STUDY ASSAYS declarations + assay headers
- [rules-catalog.md](./references/rules-catalog.md) — rule codes, code locations, fixes
- [config-table.md](./references/config-table.md) — (measurement, technology) → config
  mapping and canonical assay layout
