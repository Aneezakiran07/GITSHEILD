"""GitShield website: paste a line of code or upload a file and see whether it holds a real secret

Run from the repository root with
    streamlit run app/app.py
"""
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from features import build_features  # noqa: E402
from hook import (  # noqa: E402
    MODEL_PATH, SCALER_PATH, SKIP_FILES, SKIP_LINE, extract_value, join_key_blocks, preview, scale, to_frame,
)

# Plain names for the features, shown next to the SHAP reasons
FEATURE_NAMES = {
    "value_len": "length of the value",
    "value_entropy": "randomness (entropy) of the value",
    "value_digit_ratio": "share of digits in the value",
    "value_upper_ratio": "share of upper case letters in the value",
    "value_lower_ratio": "share of lower case letters in the value",
    "value_symbol_ratio": "share of symbols in the value",
    "line_len": "length of the line",
    "line_number": "line number in the file",
    "lines_spanned": "number of lines the candidate spans",
    "var_name_len": "length of the variable name",
    "path_depth": "depth of the file path",
}

EXAMPLES = {
    "Hard coded password": ('DB_PASSWORD = "Xk9pQ2vL8mN4rT7wZ1yB6cF3"', "config/settings.py"),
    "Password read from the environment": ('db_password = os.environ["DB_PASSWORD"]', "app/config.py"),
    "Test password in a test file": ('password = "test1234"', "tests/test_login.py"),
    "Normal code": ("total = price * quantity", "src/cart.py"),
}


@st.cache_resource
def load_model():
    # Loads the model once per session, with the explainer used for the reasons
    bundle = joblib.load(MODEL_PATH)
    return bundle, shap.TreeExplainer(bundle["model"])


def score_rows(rows):
    # Scores rows exactly as src/hook.py does and also returns the SHAP values
    bundle, explainer = load_model()
    features = scale(build_features(to_frame(rows)), SCALER_PATH)[bundle["features"]]
    scores = bundle["model"].predict_proba(features)[:, 1]
    return scores, features, explainer.shap_values(features), bundle


def describe(feature, value):
    # Turns one feature and its scaled value into a short readable phrase
    if feature in FEATURE_NAMES:
        level = "high" if value > 0.5 else "low" if value < -0.5 else "average"
        return f"{FEATURE_NAMES[feature]} is {level}"
    words = feature.replace("name_has_", "variable name contains ").replace("line_has_", "line contains ")
    words = words.replace("path_has_", "path contains a ").replace("ext_", "file type is ").replace("_", " ")
    return words if value >= 0.5 else f"not: {words}"


st.set_page_config(page_title="GitShield", page_icon="🛡️", layout="centered")
st.title("GitShield")
st.write(
    "GitShield tells real leaked credentials apart from false alarms in source code. "
    "It uses the same XGBoost model and the same features as the pre-commit hook in `src/hook.py`, "
    "trained on Samsung CredData and tested on 67 repositories it never saw "
    "(precision 0.857, recall 0.929, F1 0.891 with annotated values)."
)

if not MODEL_PATH.exists() or not SCALER_PATH.exists():
    st.error("The model file or the scaler file is missing. Run notebooks 03 and 04 first, see the README.")
    st.stop()

bundle, _ = load_model()
threshold = bundle["threshold"]

tab_line, tab_file = st.tabs(["Check a line", "Scan a file"])

with tab_line:
    example = st.selectbox("Start from an example, or type your own line below", ["(none)"] + list(EXAMPLES))
    default_line, default_path = EXAMPLES.get(example, ("", "src/config.py"))
    line = st.text_input("Line of code", value=default_line)
    path = st.text_input("File path in the repository", value=default_path,
                         help="The path matters: the model looks at the file type and at folder names such as test or docs.")

    if st.button("Check line", type="primary") and line.strip():
        if SKIP_FILES.search(path) or SKIP_LINE.search(line):
            st.info("This line or file is never scanned (lockfiles, notebook images and lines marked gitsheild:allow).")
        else:
            rows = [{"path": path, "line_number": 1, "end_number": 1, "text": line}]
            scores, features, shap_values, _ = score_rows(rows)
            score = float(scores[0])
            if score >= threshold:
                st.error(f"Looks like a real secret: score {score:.3f}, threshold {threshold:.3f}")
            else:
                st.success(f"Looks safe: score {score:.3f}, threshold {threshold:.3f}")
            st.progress(min(max(score, 0.0), 1.0))
            value = extract_value(line)
            st.caption(f"Value found by the hook's rule: `{preview(line)}`" if value else "No value found on this line.")

            st.subheader("Why")
            contributions = pd.Series(shap_values[0], index=features.columns)
            top = contributions.reindex(contributions.abs().sort_values(ascending=False).index).head(6)
            reasons = pd.DataFrame({
                "reason": [describe(f, features.iloc[0][f]) for f in top.index],
                "effect": ["toward a real secret" if v > 0 else "toward a false alarm" for v in top.values],
                "strength": np.round(np.abs(top.values), 2),
            })
            st.dataframe(reasons, hide_index=True, width="stretch")
            st.caption("Strength is the SHAP contribution on the log odds scale. Larger means a bigger push.")

with tab_file:
    upload = st.file_uploader("Upload a source or config file", type=None)
    upload_path = st.text_input("Path of this file in the repository", value="",
                                help="Leave empty to use the uploaded file name.")
    if upload is not None and st.button("Scan file", type="primary"):
        text = upload.getvalue().decode("utf-8", errors="replace")
        file_path = upload_path.strip() or upload.name
        if SKIP_FILES.search(file_path):
            st.info("This file is never scanned (lockfiles).")
        else:
            rows = join_key_blocks([{"path": file_path, "line_number": n, "end_number": n, "text": t}
                                    for n, t in enumerate(text.splitlines(), start=1)])
            rows = [r for r in rows if r["text"].strip() and not SKIP_LINE.search(r["text"])]
            if not rows:
                st.info("The file has no lines to scan.")
            else:
                scores, _, _, _ = score_rows(rows)
                result = pd.DataFrame({
                    "line": [r["line_number"] for r in rows],
                    "score": np.round(scores, 3),
                    "masked value": [preview(r["text"]) for r in rows],
                })
                flagged = result[result["score"] >= threshold]
                if flagged.empty:
                    st.success(f"No line looks like a real secret ({len(rows)} lines scanned).")
                else:
                    st.error(f"{len(flagged)} of {len(rows)} lines look like real secrets.")
                    st.dataframe(flagged.sort_values("score", ascending=False), hide_index=True, width="stretch")
                with st.expander("Scores of all lines"):
                    st.dataframe(result, hide_index=True, width="stretch")

st.divider()
st.caption(
    "Values are masked in all outputs. Scores are the model's probability that a line holds a real secret. "
    "The model is a course project and will miss some secrets and flag some safe lines, see the README for its limits."
)
