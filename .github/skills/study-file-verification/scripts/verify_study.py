#!/usr/bin/env python3
"""Verify a customized ISA-Tab study file against this repo's isatools validator.

Usage:
    python verify_study.py <path-to-investigation-file-or-directory>

Examples:
    python verify_study.py isa-example/
    python verify_study.py isa-example/i_Investigation.txt

Prints the study table header columns, then the validator report split into
study-file issues (rule codes from DEFAULT_STUDY_RULES) and other issues
(investigation-level rules that reference the study file).
"""

import glob
import os
import sys

# Study-table rule codes (isatools/isatab/validate/rules/defaults.py)
# plus related study-group and investigation cross-checks.
STUDY_CODES = {
    "4014",  # header labels and ordering
    "4007",  # empty factor value cells
    "4003",  # required columns/cells (config)
    "4008",
    "4010",
    "4011",  # cell value data types
    "1099",  # unit fields
    "4009",  # protocol fields / REF placement
    "3010",  # ontology field structure
    "5001",  # study group count (info)
    "5002",  # study group size mismatch
}
CROSS_FILE_CODES = {
    "0006",   # study file declared but missing on disk
    "1003",   # assay sample not declared in study file
    "1008",   # factor used in study file not declared in investigation
    "1021",
    "1007",   # protocol used but not declared
    "1019",
    "3008",   # ontology term source declarations
}


def find_investigation_file(target):
    if os.path.isfile(target):
        return target
    hits = sorted(glob.glob(os.path.join(target, "i_*.txt")))
    if not hits:
        hits = sorted(glob.glob(os.path.join(target, "*.isa")))
    return hits[0] if hits else None


def print_study_headers(validation_dir):
    study_files = sorted(glob.glob(os.path.join(validation_dir, "s_*.txt")))
    if not study_files:
        print("No study files (s_*.txt) found next to the investigation file.")
        return
    for s_file in study_files:
        with open(s_file, encoding="utf-8") as fp:
            header = fp.readline().rstrip("\r\n").split("\t")
        print("Header of {} ({} columns):".format(os.path.basename(s_file), len(header)))
        for i, col in enumerate(c.strip('"') for c in header):
            print("  {:>2}: {}".format(i, col))
        print()


def code_of(message_dict):
    raw = message_dict.get("code", "")
    # codes may be ints or strings like "4014" / "4003"
    return str(raw).strip()


def summarise(kind, items):
    out = {"study": [], "cross": [], "other": []}
    for item in items:
        code = code_of(item)
        entry = "[{}] {} -- {}".format(code, item.get("message", ""), item.get("supplemental", ""))
        if code in STUDY_CODES and " of investigation file" not in item.get("supplemental", ""):
            # 4003 collides with the investigation-level required-fields check;
            # those supplementals contain "of investigation file".
            out["study"].append(entry)
        elif code in CROSS_FILE_CODES:
            out["cross"].append(entry)
        else:
            out["other"].append(entry)
    return {k: ["[{}] {}".format(kind, e) for e in v] for k, v in out.items()}


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2

    target = argv[1]
    i_file = find_investigation_file(target)
    if i_file is None:
        print("No investigation file found at: {}".format(target))
        return 2

    print("Investigation file: {}".format(i_file))
    print_study_headers(os.path.dirname(os.path.abspath(i_file)))

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

    split_errors = summarise("E", errors)
    split_warnings = summarise("W", warnings)

    print("=" * 70)
    print("STUDY FILE ERRORS (blocking): {}".format(len(split_errors["study"])))
    for line in split_errors["study"]:
        print("  " + line)
    print("CROSS-FILE ERRORS: {}".format(len(split_errors["cross"])))
    for line in split_errors["cross"]:
        print("  " + line)
    print("OTHER ERRORS: {}".format(len(split_errors["other"])))
    for line in split_errors["other"]:
        print("  " + line)
    print("-" * 70)
    print("STUDY FILE WARNINGS: {}".format(len(split_warnings["study"])))
    for line in split_warnings["study"]:
        print("  " + line)
    print("OTHER WARNINGS: {}".format(len(split_warnings["cross"]) + len(split_warnings["other"])))
    for line in split_warnings["cross"] + split_warnings["other"]:
        print("  " + line)
    print("=" * 70)
    print("Total: {} error(s), {} warning(s)".format(len(errors), len(warnings)))

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
