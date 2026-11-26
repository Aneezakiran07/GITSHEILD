# Security analysis

This document discusses what GitShield protects against, how well it works, how it can be evaded or bypassed, how fast it is, and what we learned. Every number comes from the notebooks or from the checks listed at the end.

## Threat model

**The risk.** Developers commit credentials into source code by accident: passwords, API keys, tokens and private keys. Once pushed, a secret stays in the git history and is exposed to everyone with read access, including the public for open source repositories. The usual fix, rotating the credential, is slow and often forgotten.

**What GitShield defends.** It stops a credential before it enters the history, at commit time on the developer's machine. It is aimed at honest mistakes, not at an insider who wants to leak a secret on purpose, since such a person can bypass any client side check.

**Why a model and not only rules.** Keyword and pattern scanners find nearly every secret but raise so many false alarms that developers learn to ignore or disable them. GitShield uses the context of a candidate line (the shape of the value, the line, the variable name, the path and the file type) to decide whether it is a real credential, so that a warning is worth reading.

## Detection results

All scores are on 13,235 labeled lines from 67 repositories that were never used in training (`notebooks/04_models.ipynb`, `notebooks/06_baselines.ipynb`).

| Scanner | Precision | Recall | F1 | False alarms |
| --- | --- | --- | --- | --- |
| Regex scanner | 0.2651 | 0.6049 | 0.3686 | 5,162 |
| CredSweeper 1.19.6, rules only | 0.4414 | 0.9932 | 0.6112 | 3,869 |
| **GitShield model, annotated value** | **0.8565** | **0.9288** | **0.8912** | **479** |
| GitShield through the hook (value found by the hook's rule) | 0.6929 | 0.7147 | 0.7037 | 975 |

- The model finds 2,859 of 3,078 real secrets and raises 479 false alarms, against 5,162 for the regex scanner. Through the hook it finds 2,200 and raises 975, still far fewer than either rule scanner. A developer sees about one tenth of the warnings while more than nine in ten real secrets are still caught.
- CredSweeper with its ML filter scores F1 0.9824, but it comes from the team that built CredData and has most likely been trained on these labels, so it is not a fair comparison.
- Cross validation average precision is 0.9072 (standard deviation 0.0325), lower than on the test set (0.9468). Scores vary strongly between repositories, so the cross validation number is the safer expectation for a new codebase.

## Where it fails

From `notebooks/05_explain.ipynb`:

- **Missed secrets are concentrated.** The 219 missed real secrets come from 28 of the 67 test repositories, and one repository holds 74 of them. A team whose secrets look unusual can see a much lower detection rate than the average.
- **Test passwords cause false alarms.** 13.71 percent of test and example values (X rows) are flagged. They are short values named like a password, often in test folders, and look like real passwords to the model.
- **The runtime value rule is the weak link.** On annotated data the model scores F1 0.891, through the hook 0.704. The hook's simple rule finds exactly the annotated value on 49.93 percent of single line test rows that have one, and the model loses 677 real secrets this way, mostly in config (307) and code (280) files.

## Attacks and edge cases tried against the hook

We scored hand written lines with `src/hook.py` (all values are made up). The threshold is 0.4158.

| Case | Score | Result |
| --- | --- | --- |
| Hard coded password in `config/settings.py` | 0.989 | blocked |
| Same value, variable named `x` (no keyword) | 0.993 | blocked |
| Value split into two concatenated strings | 0.964 | blocked |
| Value base64 encoded | 0.984 | blocked |
| Value hex encoded | 0.962 | blocked |
| API key in a JSON config | 0.963 | blocked |
| API key in a YAML file without quotes | 0.937 | blocked |
| Password inside a comment | 0.990 | blocked |
| Database URL with user and password | 0.962 | blocked |
| Same password in a test folder | 0.991 | blocked |
| Same password in a docs file | 0.967 | blocked |
| Short real looking password `Tr0ub4dor` | 0.931 | blocked |
| RSA private key block over 7 lines (joined into one row) | 0.979 | blocked |
| Placeholder `password = "changeme"` | 0.326 | allowed (correct) |
| `password = request.form["password"]` | 0.237 | allowed (correct) |
| `db_password = os.environ["DB_PASSWORD"]` | 0.384 | allowed (correct) |
| `password = os.getenv("DB_PASSWORD")` | 0.654 | blocked (false alarm) |
| Git commit SHA | 0.977 | blocked (false alarm) |
| UUID | 0.846 | blocked (false alarm) |
| SHA-256 checksum | 0.841 | blocked (false alarm) |
| Docker image digest | 0.982 | blocked (false alarm) |

**Findings.** Simple obfuscation (splitting, base64, hex, removing the keyword) does not hide a random looking secret, because the model mainly judges how random the value looks (value entropy holds 29.88 percent of the SHAP importance). The flip side is that random looking non secrets, such as hashes, UUIDs and image digests, are flagged too. CredData only contains lines that a keyword scanner already picked, so the model rarely saw such values during training. A real deployment should allow list these known formats before scoring.

## Bypasses and limits of a client side hook

- **`git commit --no-verify`** skips every pre-commit hook. GitShield cannot prevent this. The hook's message mentions it on purpose, for real false alarms.
- **`gitsheild:allow`** on a line skips it. It is meant for reviewed false alarms but can hide a real secret.
- **The hook must be installed in every clone.** It lives in `.git/hooks`, which git does not copy. A server side check (a CI job or a pre-receive hook running the same `score` function) would close this gap.
- **Only added lines are scanned.** Secrets already in the history are not found, and a secret committed before the hook was installed stays there.
- **Secrets the model has never seen in this form** can score low, as the concentration of misses in a few repositories shows.

## Security of the tool itself

- **No secret values are printed.** The hook and the website show the first four characters followed by stars. Notebook outputs show only ids, counts and scores.
- **No real secrets in the repository.** CredData replaced every secret with a random look alike, the raw and cleaned data stay out of git (GitHub push protection rejects them), and the example password in `app/app.py` and the README is made up. The model file contains trees and thresholds, not training lines.
- **The hook is offline.** It reads the staged diff and the two model files and makes no network calls.
- **The public website is a demo.** Text pasted into https://gitsheild.streamlit.app/ is sent to the hosting server. The app does not save it, but real credentials should never be pasted into any online checker. Use the local hook or `streamlit run app/app.py` for real code.

## Performance

- Scoring 1,000 added lines takes 0.25 seconds, and a single line 0.14 seconds including loading the model, on the development laptop (Windows, Python 3.13). A typical commit adds far fewer lines, so the hook adds well under a second.
- The model file is about 1 MB and the scaler 670 bytes.
- Training all three models with grouped cross validation on three feature sets takes about 5 to 10 minutes, and SHAP on all 13,235 test rows about 25 seconds.

## Lessons

1. **Split by repository or the scores lie.** Rows from one repository share authors and file layouts. With a grouped split, scores still varied from 0.59 to 0.99 average precision between folds for logistic regression, which a random split would have hidden.
2. **Watch for labeling leaks.** An empty value meant the annotator marked the whole line, which a scanner cannot know. We dropped the flag, but the value length carries the same information, so the honest test is the hook, which has to find the value itself.
3. **The gap between a model and a tool is real.** F1 dropped from 0.891 to 0.704 only because the runtime cannot see the annotation. Feature parity between training and runtime had to be checked line for line.
4. **Machine learning and rules complement each other.** CredSweeper's rules find 218 of the model's 219 missed secrets, while the model removes most of the rules' false alarms. A layered scanner beats either alone.
5. **Entropy is powerful but not specific.** It survives obfuscation, but it also flags hashes and UUIDs. Allow lists and more training data from outside keyword scanners would help.

## Recommendations

- Run the same scoring in CI or as a server side hook, so a skipped local hook does not let a secret through.
- Allow list hashes, UUIDs and image digests before scoring.
- Improve the value rule per file type, which is the largest source of missed secrets at runtime.
- When a secret is flagged after it was pushed, rotate it. Removing it from the code does not remove it from the history.

## Sources of the numbers

- Detection results, confusion matrices and thresholds: `notebooks/04_models.ipynb` and `docs/FACTS.md`.
- Errors, SHAP and overlap with the baselines: `notebooks/05_explain.ipynb`.
- Baselines and the hook on the test lines: `notebooks/06_baselines.ipynb`.
- Attacks, edge cases and timings: hand written lines scored with `src.hook.score` on 27 Nov 2026, recorded in `docs/FACTS.md`.
