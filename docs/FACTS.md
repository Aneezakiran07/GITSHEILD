# Facts

Things we discovered, each with a date, a source and an author tag.

Rules: never delete another person's entry, append only in your own section, record only what came from a real output, and never invent numbers. If a fact turns out to be wrong, add a new entry that corrects it.

Format: `- YYYY-MM-DD | fact | source: notebook, command output or document | A or B`

## Person A

### Data source and download

- 2026-11-05 | The data source is Samsung CredData. Labels come as one CSV per repo in the meta folder. | source: CredData repository | A
- 2026-11-05 | The meta columns are Id, FileID, Domain, RepoName, FilePath, LineStart, LineEnd, GroundTruth, ValueStart, ValueEnd, CryptographyKey, PredefinedPattern, Category. | source: meta CSV files | A
- 2026-11-05 | download_data.py must run on Linux because some generated filenames are invalid on NTFS. It was run in a Linux VM. | source: download_data.py run in the VM | A
- 2026-11-05 | One download run crashed because GitHub reset the connection while fetching tensorflow. A rerun with --jobs 4 resumed and finished, because the script reuses finished checkouts. | source: download_data.py output in the VM | A
- 2026-11-05 | The snapshot and meta folder have 337 repos. The extract also has 337 distinct RepoName values. | source: VM folder listing, and a pandas count on the extract | A
- 2026-11-05 | The CredData README says 297 repos, 11,408 files, 73,842 labeled lines and 4,583 real credentials (about 6 percent). The downloaded data does not match, so the README may describe an older release. The cause is unverified. | source: CredData README compared with the extract | A

### Extract

- 2026-11-05 | Only the extracted lines are moved to Windows. src/extract_lines.py reads each label, takes the line text and the value from the downloaded code, and writes data/raw/credata_raw_extract.csv with the meta columns plus RepoId, FileExt, LineText, Value and Found. | source: src/extract_lines.py | A
- 2026-11-05 | The extraction found 10,812 code files. | source: src/extract_lines.py output in the VM | A
- 2026-11-05 | The extract is 37,745,332 bytes (about 36 MB), which is under the 90 MB limit. | source: ls on data/raw | A
- 2026-11-05 | The extract has 67,896 rows and 18 columns. GroundTruth counts are T 15,753, F 48,061, X 4,082. T is 23.2 percent of rows. | source: pandas count on the extract | A
- 2026-11-05 | 557 rows have Found equal to 0 (0.82 percent): F 410, T 60, X 87. All of them have empty LineText. | source: pandas count on the extract | A
- 2026-11-05 | LineText is empty on 667 rows, not only the 557 with Found equal to 0. The other 110 rows have Found equal to 1 and point at a blank line: F 65, T 33, X 12. Counting whitespace only lines, the number with Found equal to 1 is 113. Dropping rows where Found is 0 does not remove these. | source: pandas count on the extract | A
- 2026-11-05 | The extract uses LF line endings only, with 80,672 LF bytes and no CRLF. 1,349 rows have a newline inside LineText. | source: byte count and pandas count on the extract | A

### Labels and columns

- 2026-11-05 | The CredData documentation defines T as looks like a real credential, F as a false positive, and X as a test value, example or placeholder. It groups labels as True (T) versus False (F and X). | source: CredData documentation | A
- 2026-11-05 | Secret values in CredData were replaced with random look alikes, so only context features (variable name, file type, path, length, character mix) are meaningful. | source: CredData documentation | A
- 2026-11-05 | Multi line credentials exist, where LineEnd is greater than LineStart. There are 1,351 such rows: T 1,273, F 78, X 0. No row has LineEnd below LineStart. | source: CredData documentation, and a pandas count on the extract | A
- 2026-11-05 | For some False rows ValueStart and ValueEnd are empty or minus one, meaning the whole line is marked. | source: CredData documentation | A
- 2026-11-05 | In the extract no ValueStart or ValueEnd is negative. Empty offsets are not limited to False rows. ValueStart is empty on 33,571 rows (F 32,568, T 1,003) and ValueEnd on 33,777 rows (F 32,650, T 1,127). 206 rows have a ValueStart but no ValueEnd. | source: pandas count on the extract | A
- 2026-11-05 | Among the 33,631 single line rows that have Found equal to 1 and both offsets, ValueEnd is past the end of the line on 212 rows, and Value is empty on 167 rows (T 80, F 52, X 35). The cause is unverified. The labels and the extracted lines may be misaligned for some files. | source: pandas count on the extract | A
- 2026-11-05 | Category can hold several values separated by a colon. 4,084 rows do. No row has an empty Category. | source: CredData documentation, and a pandas count on the extract | A
- 2026-11-05 | The dataset documentation does not say how duplicates are handled, so we must check ourselves. | source: CredData documentation | A

### Repository

- 2026-11-05 | LineText contains text shaped like real credentials: 1,271 rows match a private key header, 390 an AWS key id, 22 a Google API key, 10 a Slack token and 1 a GitHub token. These are regex counts and the values should be look alikes, but GitHub push protection may still block a push that contains them. | source: regex count on the extract | A
- 2026-11-05 | The GitHub repository is public, because the API answers without a login. | source: GitHub API status 200 for Aneezakiran07/GITSHEILD | A
- 2026-11-05 | GitHub push protection rejected a push containing the extract. It flagged AWS access key ids and a Grafana service account token, and reported 18 more detections. | source: git push output | A
- 2026-11-05 | Id is unique in the extract, across all 67,896 rows, and is never empty. | source: pandas count on the extract | A
- 2026-11-05 | 4 Value cells contain text such as NA that pandas reads as missing by default. A default read also turns the 667 empty LineText cells into NaN. | source: pandas read of the extract with and without keep_default_na=False | A
- 2026-11-05 | 23 RepoName values and 406 FileID values contain only digits or a number in e notation, so they could be read as numbers. | source: regex count on the distinct values in the extract | A
- 2026-11-08 | 267 found rows are suspect: 212 have ValueEnd past the end of the line (161 of them also have ValueStart past it) and 113 point at a blank line, with 58 in both groups. By label: F 112, T 114, X 41. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Counting offsets in UTF 8 bytes explains none of the 212 rows, and extra line break characters such as form feed or the Unicode line separator do not appear in the suspect files. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | 78 FileID values appear in more than one repository, always at the same path inside each repository. 1,602 rows use them. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | All 557 rows with Found equal to 0, and 264 of the 267 suspect rows, use a shared FileID. This corrects the earlier entry that guessed the cause was unverified. src/extract_lines.py finds a file by FileID alone, so labels for a shared FileID were read from only one repository's copy. | source: notebooks/01_cleaning.ipynb and src/extract_lines.py | A
- 2026-11-08 | On a small test set where two repos share a FileID, the old src/extract_lines.py read the first repo's label from the second repo's copy of the file. The fixed script reads each repo's own copy. | source: old and new src/extract_lines.py run on a test set | A
- 2026-11-08 | Dropping rows that use a shared FileID removes 1,602 rows (F 1,137, T 283, X 182) and leaves 66,294 rows in 335 of 337 repositories. Every remaining row has Found equal to 1. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | After that, 3 single line rows still have a value past the end of the line and no row points at a blank line. Dropping the 3 leaves 66,291 rows. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Empty cells in the kept rows: ValueStart 32,692, ValueEnd 32,893, Value 33,176, CryptographyKey 65,237, PredefinedPattern 65,614 and FileExt 1,056. No other column has empty cells. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Id, LineStart, LineEnd, ValueStart and ValueEnd hold only whole numbers. Domain has Github on 38 rows next to GitHub on the rest. FileExt has no upper case letters and Category has no empty parts. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | ValueEnd is before ValueStart on 10 rows, all multi line. ValueEnd equals ValueStart on 15 rows, and 201 rows have a ValueStart but no ValueEnd. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | There are no exact duplicate rows and no line labeled twice with the same offsets. 4,945 rows share a line with another label, across 1,875 lines, and the labels disagree on 339 of those lines. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | 319 line texts appear in more than one repository, covering 1,420 rows, and 407 line texts have more than one label, covering 1,161 rows. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Some PredefinedPattern notes such as example, fake-for-test-but-valid and let-it-be-true describe the label itself. | source: pandas count on the kept rows | A
- 2026-11-08 | The cleaned file has 66,291 rows: label 1 on 15,470 (23.34 percent) and label 0 on 50,821. It reads back unchanged with the agreed read settings. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Line length, value length, line number and lines spanned are all strongly skewed. Line length has a median of 58 characters and a maximum of 711,242. Line number has a median of 255 and a maximum of 917,380. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Rows above the box plot fence (third quartile plus 1.5 times the interquartile range): line length 9,995 rows (15.08 percent), value length 1,481 (4.47 percent of rows with a value), line number 11,793 (17.79 percent) and lines spanned 1,347 (2.03 percent). Real secrets are 64.7 percent of the rows above the fence for value length and 94.4 percent for lines spanned, against 23.3 percent overall. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | 247 rows have a line longer than 10,000 characters, in 20 repositories, mostly txt, js and json files. No value is longer than its line. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | The largest repository holds 15.4 percent of rows and 50.6 percent of its rows are real secrets. The 5 largest hold 33.32 percent. The median repository has 69 rows. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | There are 219 file extensions, and 98 of them have fewer than 10 rows, covering 282 rows. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-08 | Cleaning removes 1,605 of 67,896 rows (2.36 percent): 1,602 for shared FileID values and 3 for values past the line. | source: notebooks/01_cleaning.ipynb | A
- 2026-11-09 | The old VAR_NAME pattern in src/features.py took time that grows with the square of the run length on long runs of name characters: 17 seconds for 20,000 characters and 33 seconds for 40,000. build_features did not finish on the cleaned file within 10 minutes. | source: timing runs of re.search and build_features | A
- 2026-11-09 | The new VAR_NAME pattern finds the same name as the old one on all 66,044 cleaned rows with lines up to 10,000 characters, and runs on all 66,291 rows in 0.1 seconds. | source: comparison of str.extract with both patterns | A
- 2026-11-09 | Correction to the two entries above: the 10 minute run was stuck on another command and never reached build_features. The old pattern finishes on all 247 cleaned rows with lines over 10,000 characters in under 0.1 seconds, and build_features with the old pattern takes 1.9 seconds on the whole cleaned file, giving 66,291 rows and 39 columns. The slow case only appears on long made up runs of name characters, so the old pattern is kept. | source: timing run of the old pattern and of build_features | A
- 2026-11-09 | build_features on the cleaned file gives 39 feature columns with no missing values: 28 flags that only hold 0 and 1, and 11 numeric features (value_len, value_entropy, four value ratios, line_len, line_number, lines_spanned, var_name_len and path_depth). | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | With GroupShuffleSplit at test_size 0.2 over seeds 0 to 199, the test set holds from 8.94 to 44.39 percent of rows, because it picks 20 percent of repositories and repository sizes differ a lot. | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | Seed 65 gives train 268 repositories and 53,056 rows (80.03 percent, label 1 23.36 percent) and test 67 repositories and 13,235 rows (19.97 percent, label 1 23.26 percent). No repository is in both, and the largest repository is in train. X is 10.36 percent of test rows against 4.76 percent of train rows. | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | After the split, 98 distinct line texts appear in both train and test, on 360 train rows and 148 test rows (1.12 percent of test rows). None of those 148 test rows has label 1. | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | Skew on the train set before and after log1p: value_len 33.94 to 0.34, line_len 66.12 to 1.80, line_number 8.56 to 0.51, lines_spanned 14.86 to 8.60 and var_name_len 3.10 to minus 0.57. lines_spanned stays skewed because 97.74 percent of train rows span one line. | source: notebooks/03_preprocessing.ipynb and a pandas count on the train rows | A
- 2026-11-09 | The most common value length in train is 36 characters, on 5,464 rows, followed by 32, 64 and 48. | source: pandas count on the train rows | A
- 2026-11-09 | Min max scaling of raw line_len on the train set puts the median at 0.00007 and 99.44 percent of train rows below 0.01. | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | After the log transform and a StandardScaler fitted on train, test means range from minus 0.322 (line_number) to 0.379 (path_depth) and test standard deviations from 0.695 (line_number) to 1.424 (path_depth). | source: notebooks/03_preprocessing.ipynb | A
- 2026-11-09 | 03_preprocessing writes features_train.csv (53,056 rows, 43 columns), features_test.csv (13,235 rows, 43 columns), repo_split.csv (335 repositories) and scaler_params.csv to data/processed. No Id is in both feature files and together they cover all 66,291 cleaned rows. | source: notebooks/03_preprocessing.ipynb | A

## Person B

