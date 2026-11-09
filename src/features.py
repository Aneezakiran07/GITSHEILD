import math
from collections import Counter
from pathlib import Path

import pandas as pd

# Paths are built from this file's location so they work from src, notebooks or the repo root
ROOT = Path(__file__).resolve().parent.parent
RAW_PATH = ROOT / "data" / "raw" / "credata_raw_extract.csv"
CLEAN_PATH = ROOT / "data" / "processed" / "credata_clean.csv"

# Words searched for in the variable name and in the whole line
KEYWORDS = {
    "password": r"pass(?:word|wd)?|pwd",
    "secret": r"secret",
    "token": r"token",
    "key": r"key",
    "auth": r"auth|credential|cred",
}

# Words searched for in the file path, matched as whole parts of the path such as test or tests
PATH_WORDS = {
    "test": r"tests?|testing|spec|specs|unittests?",
    "example": r"examples?|samples?|demos?|tutorials?",
    "mock": r"mocks?|fakes?|dummy|fixtures?|stubs?",
    "doc": r"docs?|documentation|readme",
}

# A fixed list of extension groups, so grouping needs no counts from the data
EXT_GROUPS = {
    "code": {"py", "js", "ts", "jsx", "tsx", "java", "go", "rb", "php", "c", "h", "cpp", "hpp", "cc", "cs",
             "swift", "kt", "scala", "rs", "m", "pl", "lua", "r", "groovy", "dart", "erl", "ex", "exs", "clj", "vue"},
    "config": {"json", "yaml", "yml", "xml", "ini", "cfg", "conf", "config", "toml", "properties", "env",
               "plist", "gradle", "tf", "tfvars", "lock"},
    "script": {"sh", "bash", "zsh", "ps1", "bat", "cmd", "mk", "makefile", "dockerfile"},
    "doc": {"md", "txt", "rst", "html", "htm", "adoc", "tex", "csv", "log"},
    "keyfile": {"pem", "key", "crt", "cer", "p12", "pfx", "pub", "jks", "asc", "gpg", "ppk"},
}

# The first name before an equals sign or a colon, such as db_password in db_password = "..."
VAR_NAME = r"([A-Za-z_][A-Za-z0-9_.\-]*)[\"']?\s*(?::=|=>|=|:)"


def load_data(path=None, drop_shared_ids=False):
    # Uses the cleaned file when it exists, otherwise the raw extract, as docs/CLEANED_DATA.md allows
    if path is None:
        path = CLEAN_PATH if CLEAN_PATH.exists() else RAW_PATH
    path = Path(path)

    # Every column is text and empty cells stay empty, so ids and values such as NA are not changed
    df = pd.read_csv(path, dtype=str, keep_default_na=False)

    # A FileID used by more than one repository may have been read from the wrong copy
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


def shannon_entropy(text):
    # Bits per character, low for repeated or word like text and high for random looking text
    if not text:
        return 0.0
    counts = Counter(text)
    total = len(text)
    return 0.0 - sum(n / total * math.log2(n / total) for n in counts.values())


def value_features(df):
    # Numbers describing the Value text only, so outputs never show the value itself
    value = df["Value"]
    length = value.str.len()
    # Dividing by zero would give NaN for empty values, so empty values get ratios of 0
    safe_length = length.where(length > 0, 1)

    out = pd.DataFrame(index=df.index)
    out["value_len"] = length
    out["value_empty"] = (length == 0).astype(int)
    out["value_entropy"] = value.map(shannon_entropy)
    out["value_digit_ratio"] = value.str.count(r"[0-9]") / safe_length
    out["value_upper_ratio"] = value.str.count(r"[A-Z]") / safe_length
    out["value_lower_ratio"] = value.str.count(r"[a-z]") / safe_length
    # Anything that is not an ASCII letter or digit counts as a symbol, including spaces and non ASCII letters
    out["value_symbol_ratio"] = value.str.count(r"[^A-Za-z0-9]") / safe_length
    return out


def line_features(df):
    # Numbers describing the labeled line and where it sits in the file
    text = df["LineText"]
    lower = text.str.lower()
    line_start = df["LineStart"].astype(int)
    line_end = df["LineEnd"].astype(int)

    out = pd.DataFrame(index=df.index)
    out["line_len"] = text.str.len()
    out["line_number"] = line_start
    out["lines_spanned"] = line_end - line_start + 1
    out["multi_line"] = (line_end > line_start).astype(int)
    out["line_has_assign"] = text.str.contains(r"=|:", regex=True).astype(int)
    out["line_has_quote"] = text.str.contains(r"[\"'`]", regex=True).astype(int)
    out["line_has_url"] = lower.str.contains("://", regex=False).astype(int)
    out["line_is_comment"] = text.str.match(r"\s*(?:#|//|/\*|\*|--(?:\s|$)|;|<!--)").astype(int)
    out["line_has_key_header"] = lower.str.contains(r"-----begin [a-z ]*key", regex=True).astype(int)

    # The variable name is often the strongest hint, so keywords are checked there and in the whole line
    var_name = text.str.extract(VAR_NAME, expand=False).fillna("").str.lower()
    out["var_name_len"] = var_name.str.len()
    for name, pattern in KEYWORDS.items():
        out[f"name_has_{name}"] = var_name.str.contains(pattern, regex=True).astype(int)
        out[f"line_has_{name}"] = lower.str.contains(pattern, regex=True).astype(int)
    return out


def path_features(df):
    # Numbers describing the file path and extension
    path = df["FilePath"].str.lower()
    ext = df["FileExt"].str.lower()

    out = pd.DataFrame(index=df.index)
    for name, words in PATH_WORDS.items():
        # A word counts only when it is a whole part of the path, so latest does not match test
        out[f"path_has_{name}"] = path.str.contains(rf"(?:^|[^a-z])(?:{words})(?:[^a-z]|$)", regex=True).astype(int)
    out["path_depth"] = path.str.count("/")

    group = pd.Series("other", index=df.index)
    for name, extensions in EXT_GROUPS.items():
        group[ext.isin(extensions)] = name
    group[ext == ""] = "none"
    for name in [*EXT_GROUPS, "none", "other"]:
        out[f"ext_{name}"] = (group == name).astype(int)
    return out


def build_features(df):
    # Takes the output of load_data and returns numeric columns with the same rows and index
    # Label, ids, CryptographyKey, PredefinedPattern and Category are left out on purpose
    # Every value is worked out from its own row, so nothing is fitted on the whole data
    return pd.concat([value_features(df), line_features(df), path_features(df)], axis=1)
