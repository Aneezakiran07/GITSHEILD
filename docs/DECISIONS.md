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

## Person B

| Date | Decision | Reason | Author |
| --- | --- | --- | --- |
