"""Pre-commit hook that blocks commits whose added lines look like real secrets

Usage
    python src/hook.py                 scan the staged lines of the repository in the current folder
    python src/hook.py --install       install the hook in the repository in the current folder
    python src/hook.py --check "line"  score one line, for testing
    python src/hook.py --scan FILE     score every line of a file, for testing without quoting problems
"""
import argparse
import re
import stat
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
from features import ROOT, build_features  # noqa: E402

MODEL_PATH = ROOT / "models" / "gitguard_model.joblib"
SCALER_PATH = ROOT / "data" / "processed" / "scaler_params.csv"

# The value rule agreed in docs/DECISIONS.md, the first of these signs on the line starts the value
VALUE_SIGN = re.compile(r":=|=>|=|:")
QUOTES = "\"'`"

# A changed file header and a hunk header in the output of git diff
FILE_HEADER = re.compile(r"^\+\+\+ b/(.*)$")
HUNK_HEADER = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")

# Files and lines that are never secrets: lockfile hashes, notebook images and lines marked by hand
SKIP_FILES = re.compile(r"(?:^|/)(?:package-lock\.json|yarn\.lock|pnpm-lock\.yaml|poetry\.lock|Pipfile\.lock"
                        r"|Cargo\.lock|composer\.lock|go\.sum)$")
SKIP_LINE = re.compile(r"\"image/[a-z0-9+.\-]+\"\s*:|gitsheild:allow")

# Private keys were labeled as one block from the BEGIN line to the END line, so the hook joins them the same way
KEY_BEGIN = re.compile(r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY")
KEY_END = re.compile(r"-----END [A-Z0-9 ]*PRIVATE KEY")


def extract_value(line):
    # Text after the first sign, trimmed, without a trailing comma or semicolon, cut at the matching quote
    match = VALUE_SIGN.search(line)
    if not match:
        return ""
    value = line[match.end():].strip()
    while value and value[-1] in ",;":
        value = value[:-1].rstrip()
    if value and value[0] in QUOTES:
        end = value.find(value[0], 1)
        value = value[1:end] if end != -1 else value[1:]
    return value


def training_path(path):
    # CredData keeps the folders but renames every file to an 8 character id under data/<repo>/
    # and puts files from the repository root in a folder named _, so real paths are shaped the same way
    parts = Path(path).as_posix().split("/")
    folders = parts[:-1] or ["_"]
    suffix = Path(parts[-1]).suffix
    return "/".join(["data", "00000000", *folders, "00000000" + suffix])


def staged_lines():
    # Every added line in the staged changes, with its file path and its line number in the new file
    diff = subprocess.run(
        ["git", "diff", "--cached", "--unified=0", "--no-color", "--diff-filter=ACM"],
        capture_output=True, text=True, encoding="utf-8", errors="replace", check=True,
    ).stdout
    rows, path, number = [], None, 0
    for line in diff.splitlines():
        file_match = FILE_HEADER.match(line)
        if file_match:
            path = file_match.group(1)
            continue
        hunk_match = HUNK_HEADER.match(line)
        if hunk_match:
            number = int(hunk_match.group(1))
            continue
        if path and line.startswith("+") and not line.startswith("+++"):
            rows.append({"path": path, "line_number": number, "end_number": number, "text": line[1:]})
            number += 1
    return join_key_blocks(rows)


def join_key_blocks(rows):
    # Joins the added lines of a private key into one row that spans from its BEGIN line to its END line
    joined, i = [], 0
    while i < len(rows):
        row = rows[i]
        if KEY_BEGIN.search(row["text"]):
            j = i
            while (j + 1 < len(rows) and not KEY_END.search(rows[j]["text"])
                   and rows[j + 1]["path"] == row["path"]
                   and rows[j + 1]["line_number"] == rows[j]["line_number"] + 1):
                j += 1
            block = rows[i:j + 1]
            joined.append({**row, "end_number": block[-1]["line_number"],
                           "text": "\n".join(r["text"] for r in block)})
            i = j + 1
        else:
            joined.append(row)
            i += 1
    return joined


def to_frame(rows):
    # Builds the columns that src/features.py reads, in the same shape as the cleaned data
    frame = pd.DataFrame(rows, columns=["path", "line_number", "end_number", "text"])
    return pd.DataFrame({
        "LineText": frame["text"],
        "Value": frame["text"].map(extract_value),
        "LineStart": frame["line_number"].astype(str),
        "LineEnd": frame["end_number"].astype(str),
        "FilePath": frame["path"].map(training_path),
        "FileExt": frame["path"].map(lambda p: Path(p).suffix.lstrip(".").lower()),
    })


def scale(features, scaler_path=SCALER_PATH):
    # Applies log1p where scaler_params.csv says so, then the train mean and scale
    params = pd.read_csv(scaler_path)
    scaled = features.astype(float)
    for row in params.itertuples():
        column = scaled[row.feature]
        if str(row.log1p) == "True":
            column = np.log1p(column)
        scaled[row.feature] = (column - row.mean) / row.scale
    return scaled


def score(rows, model_path=MODEL_PATH, scaler_path=SCALER_PATH):
    # Returns the rows with a score and a flag, using the model, feature order and threshold in the model file
    import joblib

    bundle = joblib.load(model_path)
    frame = to_frame(rows)
    features = scale(build_features(frame), scaler_path)[bundle["features"]]
    result = pd.DataFrame(rows)
    result["score"] = bundle["model"].predict_proba(features)[:, 1]
    result["flagged"] = result["score"] >= bundle["threshold"]
    return result, bundle


def preview(text):
    # Shows where the line is without printing the whole secret again
    value = extract_value(text) or text.strip().splitlines()[0]
    return value[:4] + "*" * min(max(len(value) - 4, 0), 12)


def repo_relative(path):
    # Paths in a commit are relative to the repository, so a scanned file is made relative to the current folder
    try:
        return Path(path).resolve().relative_to(Path.cwd().resolve()).as_posix()
    except ValueError:
        return Path(path).name


def install():
    # Writes .git/hooks/pre-commit in the repository in the current folder
    git_dir = subprocess.run(["git", "rev-parse", "--git-dir"], capture_output=True, text=True, check=True).stdout.strip()
    hook_path = Path(git_dir) / "hooks" / "pre-commit"
    python = Path(sys.executable).as_posix()
    script = Path(__file__).resolve().as_posix()
    hook_path.write_text(f'#!/bin/sh\n"{python}" "{script}"\n', encoding="utf-8", newline="\n")
    hook_path.chmod(hook_path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("installed", hook_path)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--install", action="store_true", help="install the hook in the current repository")
    parser.add_argument("--check", metavar="LINE", help="score one line instead of the staged changes")
    parser.add_argument("--scan", metavar="FILE", help="score every line of a file instead of the staged changes")
    parser.add_argument("--path", default="config.py", help="file path used with --check")
    args = parser.parse_args()

    if args.install:
        install()
        return 0

    if args.check is not None:
        rows = [{"path": args.path, "line_number": 1, "end_number": 1, "text": args.check}]
    elif args.scan is not None:
        text = Path(args.scan).read_text(encoding="utf-8", errors="replace")
        rows = join_key_blocks([{"path": repo_relative(args.scan), "line_number": n, "end_number": n, "text": line}
                                for n, line in enumerate(text.splitlines(), start=1)])
    else:
        rows = staged_lines()
    rows = [r for r in rows if r["text"].strip() and not SKIP_FILES.search(r["path"])
            and not SKIP_LINE.search(r["text"])]
    if not rows:
        if args.check is not None:
            print("skipped, this line or file is never scanned")
        return 0

    result, bundle = score(rows)
    if args.check is not None:
        print(f"score {result['score'].iloc[0]:.4f}, threshold {bundle['threshold']:.4f}, "
              f"{'flagged' if result['flagged'].iloc[0] else 'not flagged'}")
        return 0

    if args.scan is not None:
        for row in result.itertuples():
            print(f"  line {row.line_number}  score {row.score:.4f}  {'flagged' if row.flagged else 'ok'}")

    flagged = result[result["flagged"]]
    if flagged.empty:
        return 0
    print(f"GITSHEILD: {len(flagged)} added line(s) look like real secrets ({bundle['name']}, threshold {bundle['threshold']:.4f})")
    for row in flagged.itertuples():
        print(f"  {row.path}:{row.line_number}  score {row.score:.2f}  {preview(row.text)}")
    print("Remove the secret, add the comment gitsheild:allow to the line, or commit with --no-verify if you are sure it is not one.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
