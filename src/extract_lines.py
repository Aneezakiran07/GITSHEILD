import argparse
import csv
import glob
import os
import sys

import pandas as pd


def build_file_index(data_dir):
    # maps each file id to its path on disk so we never depend on the path format in the labels
    index = {}
    for dirpath, _, filenames in os.walk(data_dir):
        for name in filenames:
            stem = name.split(".")[0]
            index[stem] = os.path.join(dirpath, name)
    return index


def read_lines(path, cache):
    # reads a file once and keeps its lines in memory for the other labels of the same file
    if path not in cache:
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as handle:
            text = handle.read()
        cache[path] = text.split("\n")
        if len(cache) > 200:
            cache.pop(next(iter(cache)))
    return cache[path]


def to_int(value):
    # turns a label cell into an integer or returns None when the cell is empty or not a number
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()

    meta_files = sorted(glob.glob(os.path.join(args.root, "meta", "*.csv")))
    if not meta_files:
        sys.exit("no meta csv files found under " + args.root)

    index = build_file_index(os.path.join(args.root, "data"))
    print("files found on disk:", len(index))

    rows = []
    missing_files = 0
    for meta_path in meta_files:
        repo_id = os.path.splitext(os.path.basename(meta_path))[0]
        meta = pd.read_csv(meta_path, dtype=str, keep_default_na=False)
        cache = {}
        for rec in meta.to_dict("records"):
            path = index.get(rec.get("FileID", ""))
            line_start = to_int(rec.get("LineStart"))
            line_end = to_int(rec.get("LineEnd")) or line_start
            line_text = ""
            value = ""
            found = False
            if path and line_start:
                lines = read_lines(path, cache)
                if 1 <= line_start <= len(lines):
                    found = True
                    chunk = lines[line_start - 1 : line_end]
                    line_text = "\n".join(piece.rstrip("\r") for piece in chunk)
                    value_start = to_int(rec.get("ValueStart"))
                    value_end = to_int(rec.get("ValueEnd"))
                    first_line = lines[line_start - 1].rstrip("\r")
                    if value_start is not None and value_end is not None and line_start == line_end:
                        value = first_line[value_start:value_end]
            if not found:
                missing_files += 1
            rec["RepoId"] = repo_id
            rec["FileExt"] = os.path.splitext(path)[1].lstrip(".") if path else ""
            rec["LineText"] = line_text
            rec["Value"] = value
            rec["Found"] = int(found)
            rows.append(rec)

    out = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    out.to_csv(args.out, index=False, quoting=csv.QUOTE_NONNUMERIC)
    print("rows written:", len(out))
    print("rows where the line could not be found:", missing_files)
    print("ground truth counts:")
    print(out["GroundTruth"].value_counts(dropna=False).to_string())
    print("saved to", args.out)


main()
