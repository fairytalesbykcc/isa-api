#!/usr/bin/env python3
"""Verify customized ISA-Tab assay files against this repo's isatools validator.

Usage:
    python verify_assay.py <path-to-investigation-file-or-directory>

Examples:
    python verify_assay.py isa-example/
    python verify_assay.py isa-example/i_Investigation.txt

Prints the STUDY ASSAYS declarations, the assay table header columns, flags assay
files on disk that are not declared (silently skipped by the validator), then the
validator report split into assay-file issues (rule codes from DEFAULT_ASSAY_RULES)
and investigation/cross-file issues.

Single-file mode (no investigation file needed):
    python verify_assay.py path/to/a_assay.txt

Runs only the checks that do not need the investigation context: 4014 header
structure and 4007 empty factor values.
"""

import glob
import os
import sys

# Assay-table rule codes (isatools/isatab/validate/rules/defaults.py,
# DEFAULT_ASSAY_RULES) plus the emission codes those rules actually use.
ASSAY_CODES = {
    "0000",   # check_sample_names (assay-level; reported as warning code 1003)
    "1003",   # sample in assay but not in study (warning from rule 0000)
    "4014",   # header labels and ordering
    "4007",   # empty factor value cells
    "4003",   # required columns/cells (config)
    "4008",
    "4010",   # required column missing / cell empty (config)
    "4011",   # cell value data types
    "4012",   # required cell empty
    "4013",   # duplicated required column
    "1099",   # unit fields
    "4009",   # protocol fields / REF placement
    "3010",   # ontology field structure
    "5001",   # study group count (info)
    "5002",   # study group size mismatch
}
CROSS_FILE_CODES = {
    "0006",   # table file declared but missing on disk (study)
    "0008",   # assay file declared but missing on disk
    "4002",   # measurement/technology pair has no config
    "1003",   # samples used in assay not declared in study (also assay-level)
    "1013",   # samples used in assay not declared in study (error, inv-level)
    "1007",   # protocol used but not declared
    "1019",
    "1008",   # factor used but not declared
    "1021",
    "1009",   # protocol parameter not declared
    "1020",
    "1010",
    "1011",
    "1012",
    "3008",   # ontology term source declarations
}


def find_investigation_file(target):
    if os.path.isfile(target):
        return target
    hits = sorted(glob.glob(os.path.join(target, "i_*.txt")))
    if not hits:
        hits = sorted(glob.glob(os.path.join(target, "*.isa")))
    return hits[0] if hits else None


def parse_study_assays(i_file):
    """Extract STUDY ASSAYS rows: list of (measurement, technology, platform, filename)."""
    lines = []
    with open(i_file, encoding="utf-8", errors="replace") as fp:
        for line in fp:
            parts = [p.strip().strip('"') for p in line.rstrip("\r\n").split("\t")]
            while parts and parts[-1] == "":
                parts.pop()
            lines.append(parts)

    assays = []
    in_assays = False
    block = []

    def flush(block):
        row = {}
        for parts in block:
            if parts and len(parts) > 1:
                row[parts[0]] = parts[1:]
        if not row:
            return
        n = max((len(v) for v in row.values()), default=0)
        mt = row.get("Study Assay Measurement Type", [])
        tt = row.get("Study Assay Technology Type", [])
        pf = row.get("Study Assay Technology Platform", [])
        fn = row.get("Study Assay File Name", [])

        def pick(lst, idx):
            return lst[idx] if idx < len(lst) else ""

        for j in range(n):
            assays.append((pick(mt, j), pick(tt, j), pick(pf, j), pick(fn, j)))

    for parts in lines:
        label = parts[0] if parts else ""
        if label == "STUDY ASSAYS":
            flush(block)
            block = []
            in_assays = True
            continue
        if in_assays and label.isupper() and label != "STUDY ASSAYS":
            flush(block)
            block = []
            in_assays = False
            continue
        if in_assays:
            block.append(parts)
    if in_assays:
        flush(block)
    return assays


def print_assay_info(i_file):
    vdir = os.path.dirname(os.path.abspath(i_file))
    assays = parse_study_assays(i_file)
    declared = {fn for _, _, _, fn in assays if fn}

    print("STUDY ASSAYS declarations ({} assay row(s)):".format(len([a for a in assays if a[3]])))
    for mt, tt, pf, fn in assays:
        print("  measurement='{}' technology='{}' platform='{}' file='{}'".format(mt, tt, pf, fn))
    print()

    on_disk = sorted(glob.glob(os.path.join(vdir, "a_*.txt")))
    for a_file in on_disk:
        base = os.path.basename(a_file)
        flag = "" if base in declared else "  <-- NOT declared in STUDY ASSAYS (validator skips it!)"
        with open(a_file, encoding="utf-8", errors="replace") as fp:
            header = fp.readline().rstrip("\r\n").split("\t")
        print("Header of {} ({} columns):{}".format(base, len(header), flag))
        for i, col in enumerate(c.strip('"') for c in header):
            print("  {:>2}: {}".format(i, col))
        print()
    return declared


def check_single_file(path):
    """Standalone structural checks on one assay file (rules 4014 and 4007)."""
    base = os.path.basename(path)
    if not base.startswith("a_"):
        print("Note: assay files are conventionally named a_*.txt: {}".format(base))
    with open(path, encoding="utf-8", errors="replace") as fp:
        header = fp.readline().rstrip("\r\n").split("\t")
    print("Header of {} ({} columns):".format(base, len(header)))
    for i, col in enumerate(c.strip('"') for c in header):
        print("  {:>2}: {}".format(i, col))
    print()

    try:
        from isatools.isatab.load import load_table
        from isatools.isatab.validate.rules.rules_40xx import check_factor_value_presence, load_table_checks
        from isatools.isatab.validate.store import validator as message_handler
    except ImportError:
        print("isatools is not importable. Activate the repo venv first:")
        print("  source .venv/bin/activate")
        return 2

    message_handler.reset_store()
    with open(path, encoding="utf-8") as fp:
        try:
            table = load_table(fp)
        except Exception as e:
            print("[E] [4014] Table could not be parsed: {}".format(e))
            return 1
    table.filename = base

    try:
        load_table_checks(table, base)  # rule 4014: header labels and ordering
        check_factor_value_presence(table)  # rule 4007: empty factor value cells
    except (IndexError, KeyError) as e:
        message_handler.add_error(
            message="Unrecognised header",
            supplemental="No recognised node column ({}) in {}".format(e, base),
            code=4014,
        )

    errors = message_handler.errors
    warnings = message_handler.warnings
    print("=" * 70)
    print("STRUCTURAL ERRORS (blocking): {}".format(len(errors)))
    for e in errors:
        print("  [E] [{}] {} -- {}".format(code_of(e), e.get("message", ""), e.get("supplemental", "")))
    print("STRUCTURAL WARNINGS: {}".format(len(warnings)))
    for w in warnings:
        print("  [W] [{}] {} -- {}".format(code_of(w), w.get("message", ""), w.get("supplemental", "")))
    print("=" * 70)
    print("Standalone mode: only rules 4014 + 4007 ran. For the full assay rule set,")
    print("declare the file in STUDY ASSAYS and run this against the investigation file.")
    return 1 if errors else 0


def code_of(message_dict):
    return str(message_dict.get("code", "")).strip()


def summarise(items):
    out = {"assay": [], "cross": [], "other": []}
    for item in items:
        code = code_of(item)
        entry = "[{}] {} -- {}".format(code, item.get("message", ""), item.get("supplemental", ""))
        if code in CROSS_FILE_CODES or " of investigation file" in item.get("supplemental", ""):
            out["cross"].append(entry)
        elif code in ASSAY_CODES:
            out["assay"].append(entry)
        else:
            out["other"].append(entry)
    return out


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2

    target = argv[1]
    if os.path.isfile(target) and not os.path.basename(target).startswith("i_"):
        # Single-file mode: standalone structural checks on one assay table.
        return check_single_file(target)

    i_file = find_investigation_file(target)
    if i_file is None:
        print("No investigation file found at: {}".format(target))
        return 2

    print("Investigation file: {}".format(i_file))
    print_assay_info(i_file)

    try:
        from isatools import isatab
    except ImportError:
        print("isatools is not importable. Activate the repo venv first:")
        print("  source .venv/bin/activate")
        return 2

    with open(i_file, encoding="utf-8") as fp:
        report = isatab.validate(fp)

    errors = report.get("errors", [])
    warnings = report.get("warnings", [])

    split_errors = summarise(errors)
    split_warnings = summarise(warnings)

    print("=" * 70)
    print("ASSAY FILE ERRORS (blocking): {}".format(len(split_errors["assay"])))
    for line in split_errors["assay"]:
        print("  [E] " + line)
    print("CROSS-FILE/DECLARATION ERRORS: {}".format(len(split_errors["cross"])))
    for line in split_errors["cross"]:
        print("  [E] " + line)
    print("OTHER ERRORS: {}".format(len(split_errors["other"])))
    for line in split_errors["other"]:
        print("  [E] " + line)
    print("-" * 70)
    print("ASSAY FILE WARNINGS: {}".format(len(split_warnings["assay"])))
    for line in split_warnings["assay"]:
        print("  [W] " + line)
    print("CROSS-FILE/DECLARATION WARNINGS: {}".format(len(split_warnings["cross"])))
    for line in split_warnings["cross"]:
        print("  [W] " + line)
    print("OTHER WARNINGS: {}".format(len(split_warnings["other"])))
    for line in split_warnings["other"]:
        print("  [W] " + line)
    print("=" * 70)
    print("Total: {} error(s), {} warning(s)".format(len(errors), len(warnings)))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
