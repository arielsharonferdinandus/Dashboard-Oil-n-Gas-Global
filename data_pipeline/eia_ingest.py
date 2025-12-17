import pandas as pd
import numpy as np
import requests
from pathlib import Path
import os
import re

BASE_DIR = Path("data")
RAW_DIR = BASE_DIR / "raw"
PROCESSED_DIR = BASE_DIR / "processed"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

EIA_XLS_URL = "https://www.eia.gov/dnav/pet/xls/PET_PRI_SPT_S1_D.xls"
XLS_PATH = RAW_DIR / "PET_PRI_SPT_S1_D.xls"

if not XLS_PATH.exists():
    response = requests.get(EIA_XLS_URL)
    response.raise_for_status()
    XLS_PATH.write_bytes(response.content)

print("Excel source ready:", XLS_PATH)

xls = pd.ExcelFile(XLS_PATH)
xls.sheet_names

def shorten_source_name(label: str) -> str:
    s = label.lower()

    remove = [
        "spot price", "fob", "dollars", "per barrel",
        "price", "u.s.", "us"
    ]
    for r in remove:
        s = s.replace(r, "")

    s = re.sub(r"[(),]", "", s)
    s = re.sub(r"\s+", " ", s).strip()

    if "rwtc" in s:
        return "wti"
    if "rbrte" in s:
        return "brent"
    if "gulf coast" in s:
        return "us_gulf_coast"
    if "new york harbor" in s:
        return "new_york_harbor"
    if "mont belvieu" in s:
        return "mont_belvieu"

    return "_".join(s.split()[:3])

def clean_eia_sheet(sheet_name, fuel_type):
    raw_df = pd.read_excel(XLS_PATH, sheet_name=sheet_name, header=None)

    source_labels = raw_df.iloc[2, 1:].astype(str).tolist()
    print(source_labels)
    # Data starts at row 2
    df = raw_df.iloc[2:].copy()
    df.columns = ["date"] + source_labels
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    result = {}

    for label in source_labels:
        temp = df[["date", label]].copy()
        temp = temp.rename(columns={label: "price"})
        temp["price"] = pd.to_numeric(temp["price"], errors="coerce")

        temp = temp.dropna(subset=["date", "price"])

        short_name = shorten_source_name(label)
        result[short_name] = temp

    return result

fuel_sheets = {
    "Data 1": "Crude Oil",
    "Data 2": "Gasoline",
    "Data 3": "RBOB Gasoline",
    "Data 6": "Jet Fuel",
    "Data 7": "Propane"
}

CSV_DIR = Path("data/csv")
CSV_DIR.mkdir(parents=True, exist_ok=True)

for sheet, fuel in fuel_sheets.items():
    dfs = clean_eia_sheet(sheet, fuel)

    for short_name, df_clean in dfs.items():
        filename = f"{fuel.lower().replace(' ', '_')}_{short_name}.csv"
        output_path = CSV_DIR / filename

        df_clean.to_csv(output_path, index=False)
        print("Saved:", output_path)
