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

## Person B

