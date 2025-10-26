# Utility functions for 01_deseq_study.ipynb

# --------- IMPORTS ------------
from pathlib import Path
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
import sys
import requests

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# PyDESeq2
from pydeseq2.dds import DeseqDataSet
from pydeseq2.ds import DeseqStats

# Config reproducible
np.random.seed(16)

# ---------- ENV AND PATHS ------------

# Load environment variables from .env file
repo_root = Path.cwd().parent
load_dotenv(repo_root / ".env")

# Paths
INPUT_DIR = Path(os.getenv("INPUT_DIR"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR"))

# Inputs
RAW_DIR = (repo_root / INPUT_DIR / "raw" / "functional_annotation").resolve()
META_PATH = (repo_root / INPUT_DIR / "metadata" / "metadata.csv").resolve()

# Outputs
analysis_name = "02_deseq_study"
OUT_ROOT = (repo_root / OUTPUT_DIR / analysis_name).resolve()
OUT_CSV = OUT_ROOT / "csv"
OUT_PLOTS = OUT_ROOT / "plots"
for d in [OUT_ROOT, OUT_CSV, OUT_PLOTS]:
    d.mkdir(parents=True, exist_ok=True)

#Check paths
print(f"Repo root: {repo_root}")
print(f"Input dir: {INPUT_DIR}")
print(f"Output dir: {OUTPUT_DIR}")



# ------------ FUNCTIONS ------------

def read_emapper(raw_dir, pattern="ERR*.emapper.annotations"):
    """
    Read all *.emapper.annotations files under `raw_dir` matching `pattern`
    and return a single long DataFrame with columns:
        ['sample_id', 'query', 'KEGG_Module'].
    """
    raw_dir = Path(raw_dir)
    files = sorted(raw_dir.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No files matching '{pattern}' found in {raw_dir}")

    all_dfs = []
    for fp in files:
        m = re.search(r"(ERR\d+)", fp.name, flags=re.I)
        sample_id = m.group(1).upper() if m else fp.stem.split(".")[0]

        header = None
        with open(fp, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line.startswith("#query"):
                    header = line.lstrip("#").strip().split("\t")
                    break
        if header is None:
            print(f"Skipping {fp.name}: no '#query' header found.")
            continue

        df = pd.read_csv(fp, sep="\t", comment="#", names=header, dtype=str, low_memory=False)
        df = df[["query", "KEGG_Module"]].dropna()
        df = df[df["KEGG_Module"] != "-"]
        df["KEGG_Module"] = df["KEGG_Module"].astype(str).str.split(",")
        df = df.explode("KEGG_Module", ignore_index=True)
        df["KEGG_Module"] = df["KEGG_Module"].str.strip()
        df = df[df["KEGG_Module"] != ""]

        df.insert(0, "sample_id", sample_id)
        all_dfs.append(df[["sample_id", "query", "KEGG_Module"]])

    if not all_dfs:
        raise RuntimeError("No valid annotation files could be read.")

    out = pd.concat(all_dfs, ignore_index=True)
    print(f"Loaded {len(files)} files — {out['sample_id'].nunique()} samples, {len(out):,} rows.")
    return out

def summarize_modules(df):
    """
    Return:
      - long_counts: ['sample_id','KEGG_Module','n_proteins'] (#unique queries per module)
      - matrix: samples x modules (counts)
    """
    long_counts = (
        df.groupby(["sample_id", "KEGG_Module"])["query"]
        .nunique()
        .reset_index(name="n_proteins")
    )
    matrix = (
        long_counts
        .pivot(index="sample_id", columns="KEGG_Module", values="n_proteins")
        .fillna(0)
        .astype(int)
    )
    return long_counts, matrix

def fetch_kegg_reference():
    """
    Fetch KEGG module reference (KEGG_Module, Module_name, Module_description).
    """
    url = "https://rest.kegg.jp/list/module"
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    lines = [line.split("\t") for line in r.text.strip().split("\n")]
    df = pd.DataFrame(lines, columns=["KEGG_Module", "Description"])
    df["KEGG_Module"] = df["KEGG_Module"].str.replace("module:", "", regex=False).str.strip()
    df["Module_name"] = df["Description"].str.split(",", n=1).str[0]
    df["Module_description"] = df["Description"]
    return df.drop_duplicates(subset=["KEGG_Module"])

def percent_unmapped(modules, reference_df):
    """
    Percentage of modules in `modules` that are NOT present in the KEGG reference dataframe.
    """
    present = set(modules)
    found = set(reference_df["KEGG_Module"])
    missing = [m for m in present if m not in found]
    return round(100 * len(missing) / len(present), 2) if present else 0.0

def matrix_sparsity(matrix):
    """
    Sparsity (percentage of zeros) in a counts matrix.
    """
    total = matrix.size
    zeros = (matrix == 0).sum().sum()
    return round(100 * zeros / total, 2) if total else 0.0

# Read metadata

def load_metadata(meta_path):
    """
    Load metadata.csv and return DataFrame with columns: ['sample_id', 'group'].
    Expects columns 'NCBI_accession' and 'study_condition'.
    """
    meta = pd.read_csv(meta_path)
    if "NCBI_accession" not in meta.columns or "study_condition" not in meta.columns:
        raise ValueError("Metadata must have columns 'NCBI_accession' and 'study_condition'.")
    meta["sample_id"] = (
        meta["NCBI_accession"].astype(str).str.extract(r"(ERR\d+)", expand=False).str.upper()
    )
    meta["group"] = meta["study_condition"].astype(str).str.strip().str.lower()
    meta = meta.dropna(subset=["sample_id", "group"]).drop_duplicates("sample_id")
    return meta[["sample_id", "group"]]

# Results 

def save_csv(df, out_dir, name):
    """
    Save a DataFrame as CSV inside `out_dir`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{name}.csv"
    df.to_csv(file_path, index=True)
    print(f"CSV saved in: {file_path}")

def save_plot(out_dir, name, dpi=300):
    """
    Save the current Matplotlib figure in `out_dir`.
    """
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{name}.png"
    plt.savefig(file_path, dpi=dpi, bbox_inches="tight")
    plt.close()
    print(f"Figure saved in: {file_path}")