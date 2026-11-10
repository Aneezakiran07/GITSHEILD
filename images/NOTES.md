# Image notes

Every image is made by `notebooks/02_eda.ipynb` from the cleaned data (66,291 rows). Label 1 means a real credential (T), label 0 a false positive (F) or a test value (X). The dashed line in the share charts is the overall share of real secrets, 23.34 percent.

| Image | What it tells us |
| --- | --- |
| 01_class_balance.png | Real credentials are 23.34 percent of rows (T 15,470, F 46,924, X 3,897), so the classes are imbalanced. |
| 02_repositories.png | The median repository has 69 rows, the 5 largest hold 33.32 percent of rows, and 24 of 335 repositories have no real secret, so the split by repository must be checked for size and label share. |
| 03_file_types.png | Key files (56.2 percent) and doc or text files (43.6 percent) hold real secrets far more often than source code (15.3 percent) or scripts (12.5 percent). |
| 04_categories.png | Fixed format categories such as Bearer Authorization, PEM Private Key, AWS Client ID and JSON Web Token are mostly real, while generic ones such as Password, Key and API are mostly false positives. |
| 05_value_length_entropy.png | Real values are longer (median 36 against 18 characters) and more random (entropy 3.74 against 3.24). Most not real rows have no value at all (62.5 percent against 9.0 percent). |
| 06_value_char_mix.png | Real values have more digits (39.1 against 22.9 percent) and fewer symbols (3.8 against 12.7 percent), and upper case does not differ. |
| 07_line_features.png | Real secrets sit on slightly longer lines, the line number barely differs, and multi line labels are almost all real. |
| 08_keywords.png | A private key header is 93.2 percent real and secret in the variable name 43.8 percent, but password and token are at or below the overall share. |
| 09_path_words.png | Test and mock paths have more real secrets (36.9 and 40.8 percent), not fewer, so ignoring test folders would miss real credentials. |
| 10_f_vs_x.png | F and X differ: F mostly has no value, while X has short, low entropy values, is often named like a password and sits in test paths like T. |
| 11_correlation.png | The value measures are the most linked with the label, and value length with entropy (0.971) and lines spanned with multi line (1.0) carry the same information. |
