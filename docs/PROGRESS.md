# Phase 1 progress

Phase 1 is due 10 Nov 2026. Phase 2 is due 28 Nov 2026.

Rules: update only your own section. Status is one of Not started, In progress or Done.

## Person A

- [x] notebooks/01_cleaning: missing values, duplicates, outliers, inconsistent formats. Owner: A. Status: Done
- [ ] Fix src/extract_lines.py to find files by repository and FileID, then make the extract again in the Linux VM. Owner: A. Status: In progress
- [x] Cleaned dataset or a script that makes it. Owner: A. Status: Done
- [ ] notebooks/03_preprocessing: normalization or scaling. Owner: A. Status: Not started

## Person B

- [ ] src/features.py. Owner: B. Status: Not started
- [ ] notebooks/02_eda: EDA with clear visualizations. Owner: B. Status: Not started
- [ ] images with a short note on what each tells us. Owner: B. Status: Not started
- [ ] INSIGHTS: written insights. Owner: B. Status: Not started
- [ ] README.md: title, description, problem statement, dataset details, cleaning summary, key findings, how to run. Owner: B. Status: Not started

## Shared

- [x] requirements.txt with Phase 1 packages. Owner: A. Status: Done
- [x] Commit src/extract_lines.py. Owner: A. Status: Done
- [ ] Share data/raw/credata_raw_extract.csv with the other person privately. Owner: A. Status: Not started
- [ ] Every notebook run from top to bottom before the final commit. Owner: each notebook's owner. Status: Not started
- [ ] Add the instructor Rebelhere as a collaborator if the repo becomes private. The repo is public now. Owner: not assigned yet. Status: Not started
- [x] docs folder. Owner: A. Status: Done
- [x] Cleaned data format in docs/CLEANED_DATA.md. Owner: A. Status: Done

## Open questions

- Duplicate policy
- Outlier policy
- Whether F and X differ in meaning for modeling
- What to do with the 110 rows that have Found equal to 1 and blank LineText (see docs/FACTS.md)
- Whether the rows where ValueEnd is past the end of the line are misaligned labels (see docs/FACTS.md)
