# Insights

## Phase 1: the data

Findings from `notebooks/02_eda.ipynb` on the cleaned CredData file (66,291 rows in 335 repositories) and the 39 features from `src/features.py`. Every number comes from the notebook output. Charts are in `images`, with a note on each in `images/NOTES.md`.

### 1. The classes are imbalanced

Real credentials (T) are 15,470 rows, or 23.34 percent. The negative class is mostly false positives (F, 46,924 rows) with a small group of test values and placeholders (X, 3,897 rows). Phase 2 needs class weights or a similar fix, and should report precision and recall rather than accuracy.

### 2. The shape of the value is the strongest signal

The values in CredData are random look alikes, yet they still differ by label. On rows that have a value, real values are longer (median 36 against 18 characters), more random (entropy 3.74 against 3.24 bits per character), richer in digits (39.1 against 22.9 percent) and poorer in symbols (3.8 against 12.7 percent). Value length (0.531), digit ratio (0.528) and entropy (0.504) have the highest rank correlation with the label. This suggests the replacement kept the length and character classes of the original secrets.

### 3. Whether a value exists may leak the labeling process

62.5 percent of the not real rows have no value, against 9.0 percent of the real rows, and almost all of these are F (67.7 percent of F rows, 0.1 percent of X rows). An empty value usually means the annotator marked the whole line instead of a value, which is a labeling habit rather than something in the code. A real scanner always has a candidate value, so `value_empty`, and the value measures that are 0 when it is 1, may make a model look better than it is. Phase 2 should compare a model with and without them, and also on rows that have a value only.

### 4. Keywords alone do not separate real from fake

CredData's candidates were found by keyword scanners, so most rows already contain a keyword. Password in the variable name is 22.6 percent real and token 17.5 percent, at or below the overall share. Two flags do stand out: a private key header (93.2 percent real, 1,305 rows) and secret in the variable name (43.8 percent, 3,367 rows). An assignment appears on 64,562 rows, so that flag is almost constant.

### 5. Test folders contain real secrets

36.9 percent of rows in test paths and 40.8 percent in mock paths are real, against 23.34 percent overall, and 73.1 percent of all real secrets sit in a test path. The common scanner rule of skipping test folders would therefore miss many credentials that CredData labels as real. Example and doc paths are close to the overall share.

### 6. Text files and specific formats hold the real secrets

Key files are 56.2 percent real (306 rows) and doc or text files 43.6 percent (14,340 rows), while source code is only 15.3 percent (28,773 rows). Categories with a fixed format are almost always real (Bearer Authorization 100 percent, PEM Private Key 94.4, AWS Client ID 86.5, JSON Web Token 74.6), while generic ones are mostly not (Password 19.3, Key 17.3, API 6.0). Category is not used as a feature, because a scanner would not know it for new code.

### 7. F and X are different kinds of negatives

X almost always has a value, but it is short (median 7 characters) and low in entropy (2.58). X is often named like a password (35.2 percent against 12.4 percent of F) and, like T, mostly sits in test paths (65.5 percent against 35.8 percent of F). So X looks like a real secret in where it is and what it is called, but not in the value. We keep the agreed binary label, and keep GroundTruth for error analysis in Phase 2, where X rows are likely to be the hardest false positives.

### 8. Some features are redundant

Value length and entropy correlate at 0.971, and both correlate with `value_empty` at about -0.92. Lines spanned and multi line have a rank correlation of 1.0, and both are about 0.9 with the private key header. A model can drop one of each pair. Line number barely differs by label (median 276 against 250), so it is a weak signal.

### 9. Repositories are uneven

The median repository has 69 rows, the 5 largest hold 33.32 percent of rows, and 24 of 335 repositories have no real secret. A split by repository can give train and test sets with very different sizes: across 200 seeds the test set held from 8.94 to 44.39 percent of rows. 03_preprocessing therefore picked seed 65, which gives 268 repositories and 53,056 rows in train (label 1 23.36 percent) and 67 repositories and 13,235 rows in test (label 1 23.26 percent).

The label shares match, but the test set has twice the share of X rows (10.36 against 4.76 percent of train). Section 7 shows X is the negative that looks most like a real secret in its path and name, so Phase 2 should expect more false positives on the test set than on train and report results by GroundTruth.

### Phase 1 limits

- Keyword patterns are simple. key also matches words such as keyboard, and pass matches compass.
- The variable name is only found for the name = value and name: value styles.
- The 1,602 rows with shared FileID values stay dropped for both phases, because their line text was read from the wrong copy of the file. They are 17.67 percent real against 23.34 percent in the kept rows, so the kept data has a slightly higher share of real secrets than the full dataset.
- 148 test rows (1.12 percent) share their line text with train rows. All of them have label 0, so they cannot make finding real secrets look easier.

## Phase 2: models, baselines and the hook

Findings from `notebooks/04_models.ipynb`, `notebooks/05_explain.ipynb` and `notebooks/06_baselines.ipynb`, all on the 13,235 test rows from 67 repositories that were never used in training. The results table is in the README.

### 10. A model on context features beats simple scanners by a wide margin

The hook model (XGBoost without `value_empty`) reaches F1 0.8912 with precision 0.8565 and recall 0.9288. The regex scanner reaches only 0.3686, below the 0.3774 of flagging every line, and CredSweeper's rules alone 0.6112. Random forest is close behind (0.8832) and raises the fewest false alarms on F rows (1.91 percent), while logistic regression is clearly weaker (0.7880), so the signal is not linear.

### 11. Regex flags placeholders more often than real secrets

The regex scanner flags 95.5 percent of X rows (test values and placeholders) but only 60.5 percent of real secrets. A keyword next to an assignment is exactly what a placeholder such as `password = "changeme"` looks like, so keyword rules alone cannot tell real secrets from fake ones. This agrees with insight 4.

### 12. The strongest baseline has probably seen the test labels

CredSweeper with its ML filter reaches F1 0.9824 and flags only 0.7 percent of F rows and 0.4 percent of X rows. It comes from the team that built CredData, and its rules find 99.32 percent of the real secrets, so CredData's candidates were most likely collected with rules like these and its filter trained on the labels. Its score is therefore not a fair comparison, and the regex scanner and CredSweeper's rules are the honest baselines.

### 13. The model and a rule scanner work best together

Of the 219 real secrets the hook model misses, CredSweeper's rules find 218, and no real test secret is missed by the model, regex and CredSweeper's rules together. In the other direction, the model avoids 3,631 of the 3,869 false alarms of CredSweeper's rules. So the model works best as a filter on top of a rule scanner: the rules give the recall and the model removes most of their false alarms.

### 14. The model relies on the shape of the value

SHAP on all test rows shows that `value_entropy` alone holds 29.88 percent of the total importance, and the five largest features hold 60.35 percent, four of them describing the value. This confirms insight 2 from the data: even though the values are random look alikes, their length, randomness and character mix carry most of the signal. `multi_line` is never used, because `lines_spanned` holds the same information (insight 8).

### 15. The hardest false alarms are test passwords

The model's false alarms on X rows have a median value length of 8 and entropy 2.75, against 36 and 3.74 for real secrets found, and 64.36 percent of them have password in the variable name, against 20.32 percent of real secrets found. They look like short test passwords. This is the F and X difference from insight 7, and the reason X is the hardest negative: 13.71 percent of X rows are flagged against 3.31 percent of F rows.

### 16. Test paths raise false alarms but do not hide secrets

The false alarm rate is 6.74 percent in test paths against 2.49 percent in paths with no test, example, mock or doc word, while recall stays between 0.919 and 0.945 in every path group. Insight 5 showed that test folders hold many real secrets, and the model keeps finding them there, at the cost of more false alarms.

### 17. Errors are concentrated in a few repositories

The 219 missed secrets come from 28 of the 67 test repositories, and the five worst hold 71.69 percent of them, one repository alone 74. A score on 67 repositories can therefore move a lot with a different split, which is also why cross validation scores varied by repository (average precision 0.9072, standard deviation 0.0325) and the test average precision (0.9468) is higher than in cross validation.

### 18. The real tool loses about a fifth of its F1

The hook cannot see the annotated value, so it finds the value with a simple rule. On the same test rows F1 drops from 0.8912 to 0.7037: recall on real secrets falls from 92.9 to 71.5 percent, and false alarms on F rows rise from 3.3 to 8.6 percent. The rule finds exactly the annotated value on 49.93 percent of the single line test rows that have one. The 677 secrets lost through the hook sit mostly in config (307) and code (280) files. The model was trained on annotated values, so a model trained on values found by the same rule, or a better value finder, is the clearest way to improve the tool.

### 19. Where the file sits changes the score

Training paths keep their folders but use random file names, so the hook rewrites real paths the same way. The path then changes the score: the same made up placeholder line, `password = "changeme"`, scored 0.33 in `config.py`, `src/config.py` and `src/app/config.py`, but 0.62 four folders deep and 0.50 seven folders deep, both above the threshold. Deeply nested files in a real project can therefore raise more false alarms. Two things also had to be handled for the tool to work on real commits: a private key header scored 0.005 as a single line and 0.98 when joined with its key block, and notebook image lines and lockfile hashes scored as secrets until the hook skipped them.

### Phase 2 limits

- The hook model was trained on annotated values and runs on values found by a rule, which costs about 0.19 F1 (insight 18).
- CredSweeper's score cannot be compared fairly (insight 12).
- The test set has 67 repositories, and a few of them hold most of the errors (insight 17).
- The scores in insight 19 come from one made up line at different paths, not from a measured test.

