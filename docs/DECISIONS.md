# Decisions

Rules: never delete another person's entry, append rows only in your own section, and record only reasons that come from real outputs. To change a decision, add a new row that replaces it.

## Person A

| Date | Decision | Reason | Author |
| --- | --- | --- | --- |
| 2026-11-05 | Encode T as 1 and both F and X as 0, and keep the original GroundTruth value in a separate column. | CredData groups labels as True (T) versus False (F and X), and EDA needs to compare F with X. | A |
| 2026-11-05 | Drop rows where Found is 0, and report how many. | These rows have no line text to learn from. There are 557 of them in the current extract. | A |
| 2026-11-05 | Do not use the 73,842 and 6 percent figures from the proposal. Report the measured numbers and state in the README that the downloaded version differs. | The downloaded data does not match those figures. | A |
| 2026-11-05 | Split by repository before scaling, and fit scalers and vectorizers on the train set only. | This stops information from test repositories leaking into training. | A |
| 2026-11-05 | Work happens on Windows. The Linux VM is only used for the download and extraction. | Some generated filenames are invalid on NTFS, so only those two steps need Linux. | A |
| 2026-11-05 | data/raw is ignored by git except data/raw/credata_raw_extract.csv, only if the file is under 90 MB. | The extract is about 36 MB, so it qualifies. Everything else in data/raw stays local. | A |
| 2026-11-05 | One owner per notebook, one branch per person, pull with rebase before pushing, and pull requests reviewed by the other person. | This avoids notebook merge conflicts and gives every change a second reader. | A |
| 2026-11-05 | Keep data/raw/credata_raw_extract.csv out of git and share it privately. This replaces the earlier data/raw decision. | GitHub push protection rejected a push containing the extract, and any cleaned file made from it would contain the same lines. src/extract_lines.py is the script that makes it. | A |
| 2026-11-05 | Pin requirements.txt to the versions installed on the machine used so far, with Phase 1 packages only. | Both people get the same results. XGBoost and SHAP are added when Phase 2 starts. | A |
| 2026-11-05 | The cleaned data is data/processed/credata_clean.csv in the format set out in docs/CLEANED_DATA.md, and it stays out of git. | 02_eda and src/features.py depend on 01_cleaning, and the file holds the same lines push protection rejected. Column names match the raw extract so code can move from one to the other. | A |
| 2026-11-08 | Notebook outputs show counts and offsets only, never LineText or Value. | Notebooks are tracked by git, and GitHub push protection rejects pushes containing the look alike secrets. | A |
| 2026-11-08 | src/extract_lines.py finds each file by its repository folder and FileID together, and prints how many pairs it found more than once. | 78 FileID values appear in more than one repository, and finding files by FileID alone read labels from the wrong copy. | A |
| 2026-11-08 | Drop all 1,602 rows that use a shared FileID instead of making the extract again in the Linux VM. This covers the earlier rule to drop rows where Found is 0, because all 557 of those are among them. | It costs 2.36 percent of rows and lets both people keep the same extract before the Phase 1 deadline. The fixed script can bring the rows back before Phase 2. | A |
| 2026-11-08 | Drop the 3 remaining single line rows whose value ends past the line. | Their labels cannot be checked against the text. | A |
| 2026-11-08 | Do not fill empty cells. | Every empty cell has a meaning, such as the whole line marked or a file with no extension, and a placeholder would hide it. | A |
| 2026-11-08 | Change Domain value Github to GitHub. | It is the only inconsistent spelling found, on 38 rows. | A |
| 2026-11-08 | Leave CryptographyKey and PredefinedPattern as they are and keep them out of model features. | They are sparse annotator notes, and some describe the label itself, which would leak it. | A |
| 2026-11-08 | Drop no rows as duplicates. Keep every label on a shared line and every repeated line text, and check text overlap between train and test in 03_preprocessing. | There are no exact or same offset duplicates. Labels on a shared line mark different values, and repeated texts are separate labels in separate files. | A |
| 2026-11-08 | Write the cleaned file with LF line endings. | It matches the raw extract and is the same file on Windows and Linux. | A |

## Person B

| Date | Decision | Reason | Author |
| --- | --- | --- | --- |
