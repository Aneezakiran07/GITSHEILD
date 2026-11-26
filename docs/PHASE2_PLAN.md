# Phase 2 plan and work split

Phase 2 is due 28 Nov 2026. This file says who does what in Phase 2, why the split is fair, and the order the work has to happen in. It is a proposal from Person A until Person B approves it in the pull request.

## What Phase 2 has to deliver

1. Logistic regression, random forest and XGBoost, each trained with class weights.
2. Threshold tuning.
3. SHAP explanations.
4. Two baselines: a regex only scanner and CredSweeper.
5. A pre-commit hook that scans staged lines with the chosen model.
6. README and INSIGHTS updated with the Phase 2 results.

What Phase 1 already gives us:

- The split by repository (`repo_split.csv`, seed 65, see docs/DECISIONS.md).
- The scaled feature tables `features_train.csv` and `features_test.csv`, and the scaler in `scaler_params.csv`. All of them are in data/processed and stay out of git.
- `src/features.py`, which builds every feature from a single row.

Modelling can start straight from these files. Nobody should split, scale or build features again.

## The split

### Person A (Aneeza): models and explanation

Owns `notebooks/04_models.ipynb` and `notebooks/05_explain.ipynb`.

**04_models**

- Train logistic regression, random forest and XGBoost with class weights on `features_train.csv`.
- Tune settings with cross-validation grouped by `RepoId` (GroupKFold) on the train set only, so a repository never appears on both sides of a fold.
- Pick the decision threshold from the out-of-fold cross-validation predictions, never from the test set. Choose the threshold rule (for example, best F1, or a minimum recall) before looking at the test scores.
- Score the test set once, at the end, with the chosen settings and threshold.
- Report test scores two extra ways, as promised in docs/DECISIONS.md:
  - with and without `value_empty` (a possible leak flagged by B)
  - with and without the 1.12 percent of test rows whose line text also appears in train
- Save the chosen model and its threshold in `models/` (ignored by git) by 21 Nov, in the format agreed on 18 Nov.

**05_explain**

- SHAP values for the chosen model on the test set: a summary plot and a few single row examples, showing only feature values, never `LineText` or `Value`.
- An error analysis that compares false positives on F rows with false positives on X rows, using `GroundTruth`, as decided by B in Phase 1.
- Error rates by file type and by test, example and mock paths, to see where the model fails.

### Person B (Fatima): baselines, hook and write-up

Owns `notebooks/06_baselines.ipynb`, `src/hook.py`, README and INSIGHTS, and keeps owning `src/features.py`.

**06_baselines**

- A regex only baseline: flag a line when it matches simple secret patterns (keywords such as password, secret, token or key next to an assignment, plus known key formats). Score it on the same test repositories from `repo_split.csv`.
- A CredSweeper baseline on the same test lines. CredSweeper scans files, so the test lines will probably need to be written to temporary files first.
- Note in the notebook that CredSweeper comes from the team that built CredData and its ML part may have been trained on this data, so a very high score from it may not be a fair comparison.
- A comparison table of precision, recall and F1 for both baselines. A adds the model rows once the model is saved.

**src/hook.py**

- A pre-commit hook that reads the added lines from `git diff --cached`, builds the same features as `src/features.py`, applies the same log1p and the saved `scaler_params.csv`, and blocks the commit when the model score is above the saved threshold.
- The hook does not have an annotated `Value`, so it needs its own way to find the likely value, for example the text after `=` or `:`, maybe with its quotes removed. This must be agreed with A first (see below), because it may change which features the model can use.
- Build it against a stand-in model first, so the work is not blocked, and switch to the real model once A saves it.
- Short install and usage instructions in the README.

**README and INSIGHTS**

- Add a Phase 2 section to the README: the models, the baselines, the results table, the hook and how to run everything.
- Add Phase 2 insights to INSIGHTS, using numbers from the notebooks only.

### Shared

- Each person reviews the other person's pull requests.
- Each person runs their own notebooks from top to bottom with `jupyter nbconvert --to notebook --execute --inplace` before their final commit.
- Each person appends their facts and decisions to their own section of docs/FACTS.md and docs/DECISIONS.md, in the same commit as the work.
- Add `xgboost`, `shap` and `credsweeper` to requirements.txt with exact versions. Whoever first installs a package adds it.

## Why this split is fair

| | Person A | Person B |
|---|---|---|
| Deliverables | 2 notebooks | 1 notebook, 1 script, README and INSIGHTS |
| Hardest part | Grouped cross-validation, threshold tuning and SHAP | Value extraction and feature parity in the hook |
| Waits on the other person | No | Only to switch the hook from the stand-in model to the real one |
| Rough effort | 3 to 4 working days | 3 to 4 working days |

- **Both people get real data science work.** A does the modelling and its explanation. B does the baselines that the models are judged against.
- **Both people get real engineering work.** A handles leak-free cross-validation and saving the model. B builds a working tool that has to match the training features exactly.
- **Nobody is stuck waiting.** An earlier draft gave SHAP and the error analysis to B, which put all of B's late work behind A's model. With SHAP moved to A, B can start the baselines and the hook straight away.
- **Ownership stays clean.** Every notebook and script has one owner, as the git rules require, and `features.py` stays with the person who wrote it.
- **The commit history shows both people.** Both people commit small pieces every working day on their own branch, so the history shows when the work really happened.

## Timeline

All work is finished by 25 Nov. 26 Nov is for the write-up and the final run, 27 Nov is spare time for anything that slips, and on 28 Nov we only submit.

| Date | Person A | Person B | Checkpoint at the end of the day |
|---|---|---|---|
| 18 Nov | Agree the two decisions below. Share `credata_raw_extract.csv` and `credata_clean.csv` with B. Install xgboost and shap and add them to requirements.txt | Agree the two decisions below. Install CredSweeper and add it to requirements.txt | Both decisions written in docs/DECISIONS.md. B can open the data |
| 19 Nov | 04_models: load the tables, set up GroupKFold, logistic regression | 06_baselines: regex baseline scored on the test repositories | Logistic regression cross-validation scores exist. Regex scores exist |
| 20 Nov | 04_models: random forest and XGBoost with small search grids | 06_baselines: CredSweeper runs on the test lines | All three models have cross-validation scores. CredSweeper runs, or the fallback is used |
| 21 Nov | 04_models: choose the model and threshold, save `models/gitguard_model.joblib` | 06_baselines: comparison table. src/hook.py: read staged lines | **The real model file is saved.** Baselines are done |
| 22 Nov | 04_models: test scores, including the with and without versions | src/hook.py: features, scaling and the stand-in model | 04_models pull request opened |
| 23 Nov | 05_explain: SHAP summary plot | src/hook.py: switch to the real model, test it on a demo commit | The hook blocks a fake secret and lets a normal line through |
| 24 Nov | 05_explain: error analysis by F and X, by file type and by path | 06_baselines pull request opened, add the model rows A gives | 05_explain pull request opened |
| 25 Nov | Review B's pull requests. Fix review comments | Review A's pull requests. Fix review comments. Hook pull request opened | **Freeze: no new features or analyses after today.** Everything is merged into main |
| 26 Nov | Run 01 to 05 from top to bottom on main. Send B the final numbers | README and INSIGHTS Phase 2 sections, using A's final numbers. Run 06 from top to bottom | README and INSIGHTS merged |
| 27 Nov | Spare day. Final check on a fresh clone of main | Spare day. Final check on a fresh clone of main | The submission checklist below is all ticked |
| 28 Nov | Submit | Submit | Done |

## Making sure we finish by 28 Nov

### Must have and nice to have

If time runs short, finish every must-have item before starting any nice-to-have item.

**Must have**

- The three models with class weights, cross-validation grouped by repository, a tuned threshold and test scores.
- Test scores with and without `value_empty`, because docs/DECISIONS.md promises it and it is cheap to run.
- The regex baseline, and CredSweeper or a written reason why it could not run.
- A SHAP summary plot for the chosen model.
- A hook that runs on a real commit and blocks a fake secret.
- README and INSIGHTS Phase 2 sections, and every notebook run from top to bottom.

**Nice to have**

- Test scores with and without the rows whose line text also appears in train.
- SHAP examples for single rows.
- Error rates by file type and by path.
- An install script for the hook, and colours or tidy messages in its output.

### Fallbacks for the risky parts

| Risk | Signal | Fallback |
|---|---|---|
| CredSweeper will not install or run on Windows | Not running by the end of 20 Nov | Run it once in the Linux VM on the test lines only and save its predictions as a CSV. If that also fails, report the regex baseline only and say why in the notebook and README |
| Model tuning is slow | One model's search takes more than about an hour | Use a smaller grid or a random search with a fixed number of tries, and write down the setting used |
| The model is late | No model file by the end of 21 Nov | A saves the logistic regression model straight away as a temporary model, so B can finish the hook. The final model replaces it later with the same file format |
| The hook cannot find values well | The demo commit gives wrong scores on 23 Nov | A trains one extra model on line and path features only, and the hook uses that one. Report both models |
| SHAP is slow on the tree models | The summary plot takes too long to make | Use TreeExplainer on a random sample of test rows with a fixed seed, and say so in the notebook |
| A pull request waits for review | No review within one day | Message the other person. A review that waits past 25 Nov blocks the freeze, so reviews come before new work |

### Daily check

At the end of each working day, each person sends the other a short message with three lines: what is done, what is next, and what is blocking. Each person also updates their own section of docs/PROGRESS.md in a small commit. If a checkpoint in the timeline is missed, use the fallback for it the next morning instead of waiting.

### Submission checklist (27 Nov)

- [ ] main has every pull request merged and nothing is left only on aneeza or fatima.
- [ ] A fresh clone of main, with the data files copied in, runs every notebook from top to bottom without errors.
- [ ] requirements.txt has every package with an exact version.
- [ ] The README says how to run each notebook and how to install and use the hook.
- [ ] Every number in the README and INSIGHTS matches a notebook output.
- [ ] docs/FACTS.md and docs/DECISIONS.md have the Phase 2 entries from both people.
- [ ] No notebook output shows `LineText` or `Value`.
- [ ] No data files or model files are tracked in git.
- [ ] docs/PROGRESS.md shows every Phase 2 item as Done.

## Two decisions needed before work starts

1. **Model file format.** A proposal: one joblib file holding the model, the feature column order and the threshold, saved as `models/gitguard_model.joblib`. B's hook loads only this file and `scaler_params.csv`.
2. **Value extraction in the hook.** Choose the rule the hook uses to find the value in a line. If the rule is very different from how the annotated `Value` looks, A should also train one model on line and path features only and compare it, so the hook does not depend on features it cannot build well.

Write both decisions in docs/DECISIONS.md once they are agreed, on 18 Nov at the latest.
