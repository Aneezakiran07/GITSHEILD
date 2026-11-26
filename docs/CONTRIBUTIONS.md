# Contributions

GitShield was built by a team of two. Each notebook and script has one owner, as recorded in the repository layout in the README and in `docs/PHASE2_PLAN.md`. Both members reviewed each other's numbers and recorded their facts and decisions in their own sections of `docs/FACTS.md` and `docs/DECISIONS.md`.

## Aneeza Kiran (Person A)

- Data extraction from Samsung CredData (`src/extract_lines.py`), including the fix for FileIDs shared between repositories.
- Cleaning (`notebooks/01_cleaning.ipynb`) and the cleaned data format (`docs/CLEANED_DATA.md`).
- Preprocessing (`notebooks/03_preprocessing.ipynb`): the split by repository, the log transform and the scaler fitted on train.
- Modelling (`notebooks/04_models.ipynb`): grouped cross validation, logistic regression, random forest and XGBoost on three feature sets, threshold selection, test scores, confusion matrices and precision recall curves, and the saved hook model.
- Explanation (`notebooks/05_explain.ipynb`): SHAP, error analysis by GroundTruth, file type, path and repository, and comparison of errors with the baselines.
- The model file format and the hook's value rule, agreed with Fatima.
- The Streamlit website (`app/app.py`) and its deployment.
- The Phase 2 plan, the architecture document and the security analysis.

## Fatima Kashif (Person B)

- Feature engineering (`src/features.py`): value, line, variable name, path and file type features.
- Exploratory data analysis (`notebooks/02_eda.ipynb`), the charts in `images` and `INSIGHTS.md`.
- Baselines (`notebooks/06_baselines.ipynb`): the regex scanner, CredSweeper with and without its ML filter, the comparison table and chart, and the evaluation of the hook on the test lines.
- The pre-commit hook (`src/hook.py`): reading staged lines, the path rewrite, joining private key blocks, skipping known noise, masked output and installation.
- The README and the written insights for both phases.
