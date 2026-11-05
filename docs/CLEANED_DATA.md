# Cleaned data format

This is the agreement between notebooks/01_cleaning.ipynb (Person A) and the work that reads its output, src/features.py and notebooks/02_eda.ipynb (Person B).

## File

- Path: data/processed/credata_clean.csv
- Made by: notebooks/01_cleaning.ipynb
- Not tracked by git, because it holds the same lines GitHub push protection rejected. Run the notebook to make it, or get a copy from Person A.
- Encoding: UTF-8, with a header row and no index column.

## How to read it

```python
df = pd.read_csv("data/processed/credata_clean.csv", dtype=str, keep_default_na=False)
df["label"] = df["label"].astype(int)
```

Use these read settings for the raw extract too. Without keep_default_na=False, empty cells become NaN and text such as NA in Value is read as missing. dtype=str keeps ids such as 00408ef6 as text.

## Rows

Each row is one labeled line. Id is the row key and is unique. Rows where Found is 0 are removed. The other removal rules follow the open questions in docs/PROGRESS.md and will be recorded in docs/DECISIONS.md.

## Columns

Columns keep the same names as the raw extract, so code written against the raw extract keeps working.

| Column | Meaning |
| --- | --- |
| label | Target. 1 when GroundTruth is T, 0 when it is F or X. New column |
| GroundTruth | Original value T, F or X, kept so EDA can compare F with X |
| Id | Unique row key |
| RepoId | Repository, used as the group for the train and test split |
| RepoName | Repository name from the labels |
| FileID | File id from the labels |
| Domain | Domain from the labels |
| FilePath | File path from the labels |
| FileExt | File extension, empty when the file has none |
| LineStart | First labeled line |
| LineEnd | Last labeled line, greater than LineStart for multi line rows |
| ValueStart | Start of the value in the line, may be empty |
| ValueEnd | End of the value in the line, may be empty |
| CryptographyKey | Value from the labels |
| PredefinedPattern | Value from the labels |
| Category | One or more categories separated by a colon |
| LineText | Text of the labeled line or lines, may contain newlines |
| Value | Value text taken from the line, may be empty |

Found is removed because it would always be 1.

## Changes

Person A may add columns. To rename or remove a column, Person A agrees it with Person B and records it in docs/DECISIONS.md.

## Before the cleaned file exists

Person B can work on the raw extract using the read settings above, after dropping rows where Found is 0 and making label from GroundTruth.
