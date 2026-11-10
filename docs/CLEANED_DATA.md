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

Each row is one labeled line. Id is the row key and is unique. Rows where Found is 0 are removed, along with every row that uses a FileID shared by several repositories. The 3 single line rows whose value ends past the line are also removed. No rows are removed as duplicates or outliers. The reasons are in docs/DECISIONS.md.

## Preprocessed files for Phase 2

notebooks/03_preprocessing.ipynb reads the cleaned file and writes these files to data/processed. They stay out of git like the cleaned file.

| File | Content |
| --- | --- |
| features_train.csv | Train rows with Id, RepoId, GroundTruth, label and the 39 features from src/features.py, numeric features log transformed where listed and scaled |
| features_test.csv | Test rows in the same format, scaled with the scaler fitted on train |
| repo_split.csv | RepoId and split, train or test, for every repository |
| scaler_params.csv | For each numeric feature, whether log1p was applied and the train mean and scale |

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
