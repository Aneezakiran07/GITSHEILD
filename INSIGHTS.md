# Insights

Findings from `notebooks/02_eda.ipynb` on the cleaned CredData file (66,291 rows in 335 repositories) and the 39 features from `src/features.py`. Every number comes from the notebook output. Charts are in `images`, with a note on each in `images/NOTES.md`.

## 1. The classes are imbalanced

Real credentials (T) are 15,470 rows, or 23.34 percent. The negative class is mostly false positives (F, 46,924 rows) with a small group of test values and placeholders (X, 3,897 rows). Phase 2 needs class weights or a similar fix, and should report precision and recall rather than accuracy.

## 2. The shape of the value is the strongest signal

The values in CredData are random look alikes, yet they still differ by label. On rows that have a value, real values are longer (median 36 against 18 characters), more random (entropy 3.74 against 3.24 bits per character), richer in digits (39.1 against 22.9 percent) and poorer in symbols (3.8 against 12.7 percent). Value length (0.531), digit ratio (0.528) and entropy (0.504) have the highest rank correlation with the label. This suggests the replacement kept the length and character classes of the original secrets.

## 3. Whether a value exists may leak the labeling process

62.5 percent of the not real rows have no value, against 9.0 percent of the real rows, and almost all of these are F (67.7 percent of F rows, 0.1 percent of X rows). An empty value usually means the annotator marked the whole line instead of a value, which is a labeling habit rather than something in the code. A real scanner always has a candidate value, so `value_empty`, and the value measures that are 0 when it is 1, may make a model look better than it is. Phase 2 should compare a model with and without them, and also on rows that have a value only.

## 4. Keywords alone do not separate real from fake

CredData's candidates were found by keyword scanners, so most rows already contain a keyword. Password in the variable name is 22.6 percent real and token 17.5 percent, at or below the overall share. Two flags do stand out: a private key header (93.2 percent real, 1,305 rows) and secret in the variable name (43.8 percent, 3,367 rows). An assignment appears on 64,562 rows, so that flag is almost constant.

## 5. Test folders contain real secrets

36.9 percent of rows in test paths and 40.8 percent in mock paths are real, against 23.34 percent overall, and 73.1 percent of all real secrets sit in a test path. The common scanner rule of skipping test folders would therefore miss many credentials that CredData labels as real. Example and doc paths are close to the overall share.

## 6. Text files and specific formats hold the real secrets

Key files are 56.2 percent real (306 rows) and doc or text files 43.6 percent (14,340 rows), while source code is only 15.3 percent (28,773 rows). Categories with a fixed format are almost always real (Bearer Authorization 100 percent, PEM Private Key 94.4, AWS Client ID 86.5, JSON Web Token 74.6), while generic ones are mostly not (Password 19.3, Key 17.3, API 6.0). Category is not used as a feature, because a scanner would not know it for new code.

## 7. F and X are different kinds of negatives

X almost always has a value, but it is short (median 7 characters) and low in entropy (2.58). X is often named like a password (35.2 percent against 12.4 percent of F) and, like T, mostly sits in test paths (65.5 percent against 35.8 percent of F). So X looks like a real secret in where it is and what it is called, but not in the value. We keep the agreed binary label, and keep GroundTruth for error analysis in Phase 2, where X rows are likely to be the hardest false positives.

## 8. Some features are redundant

Value length and entropy correlate at 0.971, and both correlate with `value_empty` at about -0.92. Lines spanned and multi line have a rank correlation of 1.0, and both are about 0.9 with the private key header. A model can drop one of each pair. Line number barely differs by label (median 276 against 250), so it is a weak signal.

## 9. Repositories are uneven

The median repository has 69 rows, the 5 largest hold 33.32 percent of rows, and 24 of 335 repositories have no real secret. A split by repository can give train and test sets with very different sizes: across 200 seeds the test set held from 8.94 to 44.39 percent of rows. 03_preprocessing therefore picked seed 65, which gives 268 repositories and 53,056 rows in train (label 1 23.36 percent) and 67 repositories and 13,235 rows in test (label 1 23.26 percent).

The label shares match, but the test set has twice the share of X rows (10.36 against 4.76 percent of train). Section 7 shows X is the negative that looks most like a real secret in its path and name, so Phase 2 should expect more false positives on the test set than on train and report results by GroundTruth.

## Limits

- Keyword patterns are simple. key also matches words such as keyboard, and pass matches compass.
- The variable name is only found for the name = value and name: value styles.
- The 1,602 rows with shared FileID values stay dropped for both phases, because their line text was read from the wrong copy of the file. They are 17.67 percent real against 23.34 percent in the kept rows, so the kept data has a slightly higher share of real secrets than the full dataset.
- 148 test rows (1.12 percent) share their line text with train rows. All of them have label 0, so they cannot make finding real secrets look easier.
