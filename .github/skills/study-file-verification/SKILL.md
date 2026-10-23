---
name: study-file-verification
description: 'Verify a customized ISA-Tab study file (s_*.txt) against the isatools validation rules in isatools/isatab/validate. Use when: checking a study file before committing, debugging validation errors/warnings by rule code, reviewing study file column headers and ordering, verifying Factors/Protocols/Ontology Sources declared in the investigation file match what the study table uses, or auditing study groups and factor values.'
---

# Study File Verification

Verifies a customized ISA-Tab study file (`s_*.txt`) using the exact rules implemented in
`isatools/isatab/validate` (this repo), plus a manual checklist for issues the validator
can only warn about.

## When to Use

- You created or edited a study file and want to confirm it is valid ISA-Tab.
- The validator reported errors/warnings and you need to map rule codes to fixes.
- You changed column headers or added `Characteristics[...]`, `Factor Value[...]`,
  `Parameter Value[...]`, or `Comment[...]` columns and want to confirm structure.

## Rule Codes (study tables)

The study validator (`isatools/isatab/validate/rules/defaults.py`,
`DEFAULT_STUDY_RULES = ("4014", "4007", "4003", "4011", "1099", "4009", "3010", "5001")`)
runs, in order:

| Code | Check | Severity |
|------|-------|----------|
| 4014 | Header labels recognised and correctly ordered/grouped | Error (Warning if a bracketed label name is missing) |
| 4007 | No empty cells in `Factor Value[...]` columns | Warning |
| 4003 | Required columns from `studySample.xml` config present/non-empty | Error |
| 4011 | Cell values match config data types (date, integer, double, boolean, list) | Warning |
| 1099 | Unit fields are valid | Warning |
| 4009 | `Protocol REF` followed by material/data node; protocol types declared and in config order | Warning |
| 3010 | Ontology fields: `Term Source REF`/`Term Accession Number` follow annotated columns; sources declared | Warning |
| 5001/5002 | Study group count vs `Comment[Number of Study Groups]` | Info / Warning |

Investigation-level rules that also touch the study file: 0006 (study file exists),
1008/1021 (factors declared in STUDY FACTORS), 1007–1012/1019/1020 (protocols + parameters
declared in STUDY PROTOCOLS), 3001 (ISO8601 dates), 3008 (ontology sources).

Full per-rule detail: [rules catalog](./references/rules-catalog.md).

## Procedure

1. **Run the bundled checker** (uses this repo's own validator):

   `python .github/skills/study-file-verification/scripts/verify_study.py <dir-or-i_file>`

   It prints the study file header columns, then errors/warnings grouped as
   study-file issues vs. investigation/other issues, each tagged with its rule code.

2. **Read the report by rule code.** Errors from code 4014 are structural and block
   everything else — fix them first. Then 1008/1007-style cross-file declaration issues.
   Warnings (4007, 4011, 5002, etc.) do not block loading but should be fixed before committing.

3. **Manual header checklist** (mirror of rule 4014 in `rules_40xx.py`/`load_table_checks`):
   - First column is `Source Name`; table ends with `Sample Name` (plus its bracketed columns).
   - Node columns only: `Source Name`, `Sample Name`, `Protocol REF` (assay-file-only nodes
     like `Extract Name`, data files never appear in a study file).
   - After `Source Name`/`Sample Name`: only `Characteristics[...]`, `Factor Value[...]`
     (samples only), `Comment[...]`, and qualifiers `Term Source REF`, `Term Accession
     Number`, `Unit`.
   - After `Protocol REF`: only `Parameter Value[...]`, `Date`, `Performer`, `Comment[...]`,
     qualifiers. `Sample Name` must directly follow the last protocol group.
   - Every bracketed label has a non-empty name: `Characteristics[Organism]`, not `Characteristics[]`.
   - Qualifier triples appear in order: value column, `Term Source REF`, `Term Accession
     Number` (and `Unit, Term Source REF, Term Accession Number` for unit-valued cells).
   - `Characteristics[Material Type]` is written as plain `Material Type`.

4. **Cross-file consistency** (investigation rules):
   - Every `Factor Value[X]` name X exists in the STUDY FACTORS `Study Factor Name` column.
   - Every `Protocol REF` value exists in STUDY PROTOCOLS `Study Protocol Name`.
   - Every `Term Source REF` value exists in ONTOLOGY SOURCE REFERENCE `Term Source Name`.
   - The study filename matches `Study File Name` in the investigation file (code 0006).
   - `Sample Name` values are unique per row combination and match samples used in assay files (1003).

5. **Report results.** State: errors found (blocking), warnings (non-blocking), and the
   exact cell/column/row location from the supplemental message for each finding.

## Resources

- [verify_study.py](./scripts/verify_study.py) — runs the isatools validator and a header dump
- [rules-catalog.md](./references/rules-catalog.md) — rule codes, code locations, and fixes
