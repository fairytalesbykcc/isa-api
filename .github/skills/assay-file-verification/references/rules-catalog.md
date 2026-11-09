# Assay File Validation Rules Catalog

Grounded in `isatools/isatab/validate/` of this repository.
Assay-table rules run in this order (see `rules/defaults.py`, `DEFAULT_ASSAY_RULES`):

`4014, 4007, 4003, 4011, 1099, 4009, 3010, 0000, 5001`

The assay-table config is selected per assay row of STUDY ASSAYS by
`(Study Assay Measurement Type.lower(), Study Assay Technology Type.lower())`
(`rules/core.py::ISAAssayValidator`). If the pair matches no loaded config,
rule 4002 errors and no assay-table rules can run — see
[config-table.md](./config-table.md).

## Assay-table rules

### 4014 — Unrecognised header / structural order (`rules_40xx.py::load_table_checks`)
**Severity:** Error (Warning when a bracketed label name `[]` is empty).

Checks every column label and the column grouping after each node:
- Node labels allowed in assay files: `Sample Name`, `Extract Name`,
  `Labeled Extract Name`, `Protocol REF` and the data-file labels
  `Raw Data File`, `Raw Spectral Data File`, `Free Induction Decay Data File`,
  `Image File`, `Derived Data File`, `Derived Spectral Data File`,
  `Derived Array Data File`, `Derived Array Data Matrix File`, `Array Data File`,
  `Protein Assignment File`, `Peptide Assignment File`,
  `Post Translational Modification Assignment File`, `Acquisition Parameter Data File`,
  `Metabolite Assignment File`, `Metabolite Identification File`.
- Indexed columns (`Raw Data File.1`) are normalised before checking.
- Bracketed labels must match `Characteristics[...]`, `Factor Value[...]`,
  `Parameter Value[...]`, `Comment[...]` with a non-empty name inside the brackets.
- After `Sample Name` / `Extract Name` / `Labeled Extract Name`: only
  `Characteristics[...]`, `Comment[...]`, `Term Source REF`, `Term Accession
  Number`, `Unit` (`Factor Value[...]` is additionally allowed after `Sample Name`;
  `Label` must directly follow `Labeled Extract Name`).
- After `Protocol REF`: only `Parameter Value[...]`, `Comment[...]`, `Date`,
  `Performer`, ontology qualifiers, `Unit`, and the assay annotation columns
  `Assay Name`, `MS Assay Name`, `NMR Assay Name`, `Hybridization Assay Name`,
  `Array Design REF`, `Scan Name`, `Normalization Name`, `Data Transformation Name`.
- After a data-file column: only `Comment[...]`.

**Fix:** rename/reorder columns; remove unrecognised labels; fill empty bracket names.

### 4007 — Factor value presence (`rules_40xx.py::check_factor_value_presence`)
**Severity:** Warning. No empty cells in any `Factor Value[...]` column of the assay table.
**Fix:** fill each row's factor values.

### 4003 / 4010 / 4012 / 4013 — Required fields (`rules_40xx.py::check_required_fields`)
**Severity:** Warning.
Every config field with `is-required="true"` for the assay's table config
(e.g. `Sample Name`, `Extract Name`, `Assay Name`/`... Assay Name`, the assay's
data-file column in `transcription_seq`-style configs) must exist exactly once and
have non-empty cells.
**Fix:** add the missing column, remove duplicates, fill the required cells.

### 4011 — Field value data types (`rules_40xx.py::check_field_values`)
**Severity:** Warning. Cell values must match the config data type:
`Boolean` (`true`/`false` only), `Date` (ISO8601), `Integer`, `Double`,
`List` (cell must equal one of the config `list_values`, case-insensitive).
Ontology-term fields are skipped here (structure is checked by 3010).
**Fix:** correct the cell format/value.

### 1099 — Unit fields (`rules_10xx.py::check_unit_field`)
**Severity:** Warning. `Unit` columns must be followed by `Term Source REF` /
`Term Accession Number` when the unit is ontology-annotated, and numeric cells with
units must be parseable.
**Fix:** add the qualifier triple after `Unit`; ensure value cells are numeric.

### 4009 — Protocol fields (`rules_40xx.py::check_protocol_fields`)
**Severity:** Warning.
- The last `Protocol REF` column must be followed by a material or data node.
- Protocols used between two node columns must be declared in STUDY PROTOCOLS
  (name → type mapping comes from the investigation file of the parent study).
- For config-covered node pairs, every `protocol-field` expected by the assay
  config must appear between the nodes, in config order (e.g. in
  `transcription_seq.xml`: `nucleic acid extraction` between `Sample Name` and
  `Extract Name`; `library construction`, `nucleic acid sequencing` further down).
- Protocol-type matching is case-sensitive against the config
  (`protocol-type="nucleic acid extraction"` etc.).

**Fix:** declare missing protocols in the investigation file; fix column order;
match protocol types (case) to the config.

### 3010 — Ontology fields (`rules_30xx.py::check_ontology_fields`)
**Severity:** Warning. For each annotated column the pair `Term Source REF`,
`Term Accession Number` must immediately follow it; term sources must be declared
in ONTOLOGY SOURCE REFERENCE; accession must not appear without a source.
**Fix:** reorder/add the qualifier columns; declare missing term sources (rule 3008).

### 0000 → 1003 — Samples declared in study (`rules_00xx.py::check_sample_names`)
**Severity:** Warning (code 1003). Every `Sample Name` in the assay table must
exist in the `Sample Name` column of the study file the assay belongs to.
**Fix:** fix the sample name in the assay file or add the sample to the study file.

### 5001 — Study groups (`rules_50xx.py::check_study_groups`)
**Severity:** Info / Warning. Reports group count from `Factor Value` columns in
the assay table; warning if it differs from `Comment[Number of Study Groups]`.

## Investigation-level rules that reference assay files

| Code | Rule | What it checks |
|------|------|----------------|
| 0006 / 0008 | `rules_00xx.py::check_table_files_read` | File named in `Study Assay File Name` exists on disk (Error). Empty filenames are skipped. |
| 4002 | `rules_40xx.py::check_measurement_technology_types` | (Measurement, technology) pair of the STUDY ASSAYS row matches a loaded config (Error). |
| 1003 → 1013 | `rules_10xx.py::check_samples_not_declared_in_study_used_in_assay` | Assay `Sample Name`s ⊆ study `Sample Name`s (Error 1013). |
| 1007 / 1019 | `rules_10xx.py::check_protocol_usage` | Every `Protocol REF` value used in the assay file is declared in STUDY PROTOCOLS (Error). |
| 1008 / 1021 | `rules_10xx.py::check_study_factor_usage` | Every `Factor Value[X]` name X used in the assay file is declared in STUDY FACTORS (Error). Also warns about declared-but-unused factors. |
| 1009 / 1020 | `rules_10xx.py::check_protocol_parameter_usage` | `Parameter Value[...]` names used in the assay file are declared as `Study Protocol Parameter Name` for the corresponding protocol. |
| 3008 | `rules_30xx.py::check_ontology_sources` | Term sources referenced are declared in ONTOLOGY SOURCE REFERENCE. |
| 3001 | `rules_30xx.py::check_date_formats` | Dates are ISO8601. |

## Silent gaps (validator never reports these)

- **Assay file on disk but not declared**: `validate()` only iterates
  `Study Assay File Name` values from STUDY ASSAYS. An undeclared `a_*.txt` is
  silently ignored — `verify_assay.py` flags it.
- **Unknown (measurement, technology) pair**: rule 4002 errors and the assay
  table is not loaded, so no 40xx assay-table checks run for it.
- **Empty STUDY ASSAYS rows** (`""` filename) are skipped but the section itself
  must exist in the investigation file or parsing fails
  ("Expected: STUDY ASSAYS section").

## Canonical assay file layout

From the assay config XMLs (e.g. `transcription_seq.xml`; equivalent to
`isatools/isatab/dump/write.py::write_assay_table_files`):

```
Sample Name  Characteristics[...]*  Comment[...]*  Factor Value[...]*
Protocol REF (extraction)  Parameter Value[...]*  (Date?)  (Performer?)  Comment[...]*
Extract Name  Characteristics[...]*  Comment[...]*
[Protocol REF (labeling)  Parameter Value[...]*  Comment[...]*
 Labeled Extract Name  Label  Term Source REF  Term Accession Number]
Protocol REF (assay)  Parameter Value[...]*  Comment[...]*
Assay Name / MS Assay Name / ...  (Scan Name)  (Normalization Name)  (Array Design REF)
Raw Data File | Array Data File | ...  Comment[...]*
[Protocol REF (data transformation)  Parameter Value[...]*  Comment[...]*
 Derived Data File | Derived Array Data File | ...]
```

Qualifier columns go right after the annotated value column:
`Term Source REF`, `Term Accession Number` (ontology values) or
`Unit`, `Term Source REF`, `Term Accession Number` (numeric values with unit).
`Characteristics[Material Type]` is abbreviated to `Material Type`.
