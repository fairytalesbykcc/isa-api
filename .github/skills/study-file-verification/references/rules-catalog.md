# Study File Validation Rules Catalog

Grounded in `isatools/isatab/validate/` of this repository.
Study-table rules run in this order (see `rules/defaults.py`, `DEFAULT_STUDY_RULES`):

`4014, 4007, 4003, 4011, 1099, 4009, 3010, 5001` (+ copies 4008/4010, 5002 warning)

## Study-table rules

### 4014 — Unrecognised header / structural order (`rules_40xx.py::load_table_checks`)
**Severity:** Error (Warning when a bracketed label name `[]` is empty).

Checks every column label:
- Node labels allowed: `Source Name`, `Sample Name`, `Protocol REF` (+ assay-only
  nodes such as `Extract Name`, data file columns — those must NOT appear in a study file).
- Indexed columns (`Label.0`) are normalised before checking.
- Bracketed labels must match `Characteristics[...]`, `Factor Value[...]`,
  `Parameter Value[...]`, `Comment[...]` with a non-empty name inside the brackets.
- After `Source Name` / `Sample Name`: only `Characteristics[...]`, `Factor Value[...]`,
  `Comment[...]`, `Term Source REF`, `Term Accession Number`, `Unit`.
- After `Protocol REF`: only `Parameter Value[...]`, `Comment[...]`, `Date`,
  `Performer`, `Term Source REF`, `Term Accession Number`, `Unit`
  (plus assay-file annotation columns such as `Assay Name` — not valid in study files).

**Fix:** rename/reorder columns; remove unrecognised labels; fill empty bracket names.

### 4007 — Factor value presence (`rules_40xx.py::check_factor_value_presence`)
**Severity:** Warning. No empty cells in any `Factor Value[...]` column.
**Fix:** fill each sample row's factor values.

### 4003 / 4008 / 4010 — Required fields (`rules_40xx.py::check_required_fields`, `check_investigation_against_config`)
**Severity:** Error (investigation sections) / Warning (missing/multiple table columns).
Required columns come from the XML config (`studySample.xml` for study tables):
`Source Name`, `Protocol REF` (sample collection), `Sample Name` are required.
**Fix:** add the missing column, remove duplicate columns, fill empty required cells.

### 4011 — Field value data types (`rules_40xx.py::check_field_values`)
**Severity:** Warning. Cell values must match the config data type:
`Date` (ISO8601), `Integer`, `Double`, `Boolean`, `List` (allowed values from config).
**Fix:** correct the cell format (e.g. `2016-01-01`, not `Jan 2016`).

### 1099 — Unit fields (`rules_10xx.py::check_unit_field`)
**Severity:** Warning. `Unit` columns must be followed by `Term Source REF` /
`Term Accession Number` when the unit is ontology-annotated, and numeric cells with
units must be parseable.
**Fix:** add the qualifier triple after `Unit`; ensure value cells are numeric.

### 4009 — Protocol fields (`rules_40xx.py::check_protocol_fields`)
**Severity:** Warning.
- Last `Protocol REF` column must be followed by a material/data node (`Sample Name`).
- Protocols referenced between two node columns must exist in STUDY PROTOCOLS
  (name → type mapping from the investigation file).
- For config-covered sections, all protocol types expected by config appear in order.
**Fix:** declare missing protocols in the investigation file; fix column order.

### 3010 — Ontology fields (`rules_30xx.py::check_ontology_fields`)
**Severity:** Warning. For each annotated column the pair
`Term Source REF`, `Term Accession Number` must immediately follow it; the term source
must be declared in ONTOLOGY SOURCE REFERENCE; accession should not appear without a source.
**Fix:** reorder/add the qualifier columns; declare missing term sources (rule 3008).

### 5001 / 5002 — Study groups (`rules_50xx.py::check_study_groups`)
**Severity:** Info / Warning. The number of study groups (combinations of
`Factor Value` columns) is reported; warning if it differs from
`Comment[Number of Study Groups]` in the STUDY section of the investigation file.
**Fix:** update the comment or correct factor values.

## Investigation-level rules that reference the study file

| Code | Rule | What it checks |
|------|------|----------------|
| 0006 | `rules_00xx.py::check_table_files_read` | The file named in `Study File Name` exists (Error). |
| 1003 | `rules_00xx.py::check_sample_names` / `rules_10xx.py` (1013) | Every `Sample Name` used in assay files is declared in the study file (Warning/Error). |
| 1008 / 1021 | `rules_10xx.py::check_study_factor_usage` | Every `Factor Value[X]` name X is declared in STUDY FACTORS (Error). |
| 1007 / 1019 | `rules_10xx.py::check_protocol_usage` | Every `Protocol REF` value is declared in STUDY PROTOCOLS (Warning). |
| 1009 / 1020 | `rules_10xx.py::check_protocol_parameter_usage` | `Parameter Value[...]` names match declared protocol parameters. |
| 1010–1012 | `rules_10xx.py` | Protocol names/params and factor names are declared consistently. |
| 3001 | `rules_30xx.py::check_date_formats` | Dates are ISO8601. |
| 3008 | `rules_30xx.py::check_ontology_sources` | Term sources referenced are declared in ONTOLOGY SOURCE REFERENCE. |

## Canonical study file layout

From `isatools/isatab/dump/write.py::write_study_table_files`
(equivalent to `studySample.xml` config):

```
Source Name  Characteristics[...]*  Comment[...]*
Protocol REF  Parameter Value[...]*  (Date?)  (Performer?)  Comment[...]*
Sample Name  Characteristics[...]*  Comment[...]*  Factor Value[...]*
```

Qualifier columns inserted right after an annotated value column:
`Term Source REF`, `Term Accession Number` (ontology values) or
`Unit`, `Term Source REF`, `Term Accession Number` (numeric values with unit).
`Characteristics[Material Type]` is abbreviated to `Material Type`.
