from pathlib import Path

import pandas as pd

# Paths are built from this file's location so they work from src, notebooks or the repo root
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "credata_raw_extract.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "credata_clean.csv"


def load_data(path=None, drop_shared_ids=False):
    # Uses the cleaned file when it exists, otherwise the raw extract, as docs/CLEANED_DATA.md allows
    if path is None:
        path = CLEAN_PATH if CLEAN_PATH.exists() else RAW_PATH
    path = Path(path)

    # Every column is text and empty cells stay empty, so ids and values such as NA are not changed
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    # A FileID used by more than one repository may have been read from the wrong copy.
    # Shared ids are found before any row is dropped, so an id stays shared even if one copy was not found
    if drop_shared_ids:
        repos_per_id = df.groupby("FileID")["RepoId"].nunique()
        shared_ids = repos_per_id[repos_per_id > 1].index
        df = df[~df["FileID"].isin(shared_ids)]

    # The raw extract still has rows whose line was not found and no label column yet
    if "Found" in df.columns:
        df = df[df["Found"] == "1"].drop(columns="Found")
    if "label" not in df.columns:
        df["label"] = (df["GroundTruth"] == "T").astype(int)
    else:
        df["label"] = df["label"].astype(int)

    return df.reset_index(drop=True)