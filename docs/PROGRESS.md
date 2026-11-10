# Phase 1 progress

Phase 1 is due 10 Nov 2026. Phase 2 is due 28 Nov 2026.

Rules: update only your own section. Status is one of Not started, In progress or Done.

## Person A

- [x] notebooks/01_cleaning: missing values, duplicates, outliers, inconsistent formats. Owner: A. Status: Done
- [x] Fix src/extract_lines.py to find files by repository and FileID. Owner: A. Status: Done
- [x] Decide whether to make the extract again in the Linux VM. Not needed, the 1,602 rows with a shared FileID stay dropped for both phases (see docs/DECISIONS.md). Owner: A. Status: Done
- [x] Cleaned dataset or a script that makes it. Owner: A. Status: Done
- [x] notebooks/03_preprocessing: split by repository, log transform and scaling fitted on train. Owner: A. Status: Done
- [x] notebooks/01_cleaning and notebooks/03_preprocessing run from top to bottom. Owner: A. Status: Done

## Person B

- [x] src/features.py. Owner: B. Status: Done
- [x] notebooks/02_eda: EDA with clear visualizations. Owner: B. Status: Done
- [x] images with a short note on what each tells us. Owner: B. Status: Done
- [x] INSIGHTS: written insights. Owner: B. Status: Done
- [x] README.md: title, description, problem statement, dataset details, cleaning summary, key findings, how to run. Owner: B. Status: Done

## Shared

- [x] requirements.txt with Phase 1 packages. Owner: A. Status: Done
- [x] Commit src/extract_lines.py. Owner: A. Status: Done
- [ ] Share data/raw/credata_raw_extract.csv with the other person privately. Owner: A. Status: Not started
- [ ] Every notebook run from top to bottom before the final commit. Owner: each notebook's owner. Status: Not started
- [ ] Add the instructor Rebelhere as a collaborator if the repo becomes private. The repo is public now. Owner: not assigned yet. Status: Not started
- [x] docs folder. Owner: A. Status: Done
- [x] Cleaned data format in docs/CLEANED_DATA.md. Owner: A. Status: Done

## Open questions

- Duplicate policy. Resolved by A on 2026-11-08, see docs/DECISIONS.md
- Outlier policy. Resolved by A on 2026-11-08, see docs/DECISIONS.md
- Whether F and X differ in meaning for modeling. Both are label 0. The test set has a larger share of X than train, see docs/FACTS.md
- What to do with the 110 rows that have Found equal to 1 and blank LineText (see docs/FACTS.md). Resolved by A on 2026-11-08, they use shared FileID values and are dropped
- Whether the rows where ValueEnd is past the end of the line are misaligned labels (see docs/FACTS.md). Resolved by A on 2026-11-08, nearly all use shared FileID values and are dropped
