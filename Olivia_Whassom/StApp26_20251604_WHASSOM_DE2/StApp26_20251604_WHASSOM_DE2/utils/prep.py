import re
import unicodedata
import numpy as np
import pandas as pd

from utils.config import SOURCE_LABELS, RENEWABLE, FOSSIL


def _clean_name(c):
    c = unicodedata.normalize("NFKD", str(c)).encode("ascii", "ignore").decode()
    c = re.sub(r"\(.*?\)", "", c)  # remove the unit, "Production solaire (GWh)" becomes "Production solaire"
    return c.strip().lower().replace(" ", "_")


def clean_raw(df_raw):
    """Rename columns, parse dates, return a wide dataframe (one row per region and month)."""
    df = df_raw.copy()
    df.columns = [_clean_name(c) for c in df.columns]

    month_col = next((c for c in df.columns if c.startswith("mois") or c == "month" or c == "date"), None)
    code_col = next((c for c in df.columns if "code" in c and "insee" in c), None)
    region_col = next((c for c in df.columns if c.startswith("region") and "code" not in c), None)
    if month_col is None or code_col is None or region_col is None:
        raise ValueError("unexpected columns in the csv: " + ", ".join(df.columns))

    prod_cols = [c for c in df.columns if c.startswith("production_") and "total" not in c]
    if not prod_cols:
        raise ValueError("no production_ columns found: " + ", ".join(df.columns))

    out = pd.DataFrame()
    dates = pd.to_datetime(df[month_col], errors="coerce", utc=True).dt.tz_localize(None)
    out["month"] = dates.dt.to_period("M").dt.to_timestamp()
    out["code"] = df[code_col].astype(str).str.replace(".0", "", regex=False).str.strip().str.zfill(2)
    out["region"] = df[region_col].astype(str).str.strip()
    for c in prod_cols:
        key = c.replace("production_", "")
        label = SOURCE_LABELS.get(key, key.replace("_", " ").title())
        out[label] = pd.to_numeric(df[c], errors="coerce")
    return out


def to_long(wide):
    source_cols = [c for c in wide.columns if c not in ("month", "code", "region")]
    long = wide.melt(
        id_vars=["month", "code", "region"],
        value_vars=source_cols,
        var_name="source",
        value_name="gwh",
    )
    long["year"] = long["month"].dt.year
    long["month_num"] = long["month"].dt.month

    def group(s):
        if s in RENEWABLE:
            return "Renewable"
        if s in FOSSIL:
            return "Thermal (gas, coal, oil)"
        return s  # nuclear stays nuclear

    long["group"] = long["source"].map(group)
    return long


def make_tables(df_raw):
    wide = clean_raw(df_raw)
    # drop rows that are broken (no date) and exact duplicates
    wide = wide.dropna(subset=["month"])
    wide = wide.drop_duplicates(subset=["month", "code"], keep="last").sort_values(["month", "code"])
    long = to_long(wide)
    # a few monthly values are negative (probably plants that used more than they produced).
    # They make some shares go above 100 %, so for the mix they are set to 0 (counted in the quality report)
    n_negative = int((long["gwh"] < 0).sum())
    long["gwh"] = long["gwh"].fillna(0.0).clip(lower=0.0)

    months_per_year = long.groupby("year")["month_num"].nunique()
    full_years = months_per_year[months_per_year == 12].index.tolist()

    return {
        "wide": wide,
        "long": long,
        "full_years": full_years,
        "sources": sorted(long["source"].unique()),
        "n_negative": n_negative,
    }


def add_shares(df, by):
    """df is long format. returns total per `by` + share of the groups."""
    tot = df.groupby(by + ["group"], as_index=False)["gwh"].sum()
    wide = tot.pivot_table(index=by, columns="group", values="gwh", fill_value=0).reset_index()
    for g in ["Renewable", "Nuclear", "Thermal (gas, coal, oil)"]:
        if g not in wide.columns:
            wide[g] = 0.0
    wide["total"] = wide[["Renewable", "Nuclear", "Thermal (gas, coal, oil)"]].sum(axis=1)
    wide["renew_share"] = np.where(wide["total"] > 0, 100 * wide["Renewable"] / wide["total"], np.nan)
    wide["nuclear_share"] = np.where(wide["total"] > 0, 100 * wide["Nuclear"] / wide["total"], np.nan)
    wide["thermal_share"] = np.where(wide["total"] > 0, 100 * wide["Thermal (gas, coal, oil)"] / wide["total"], np.nan)
    return wide


def quality_report(df_raw, tables):
    wide = tables["wide"]
    long = tables["long"]
    rows = []

    rows.append(("Rows in raw file", len(df_raw), "info"))
    rows.append(("Rows after cleaning", len(wide), "info"))
    dup = int(wide.duplicated(subset=["month", "code"]).sum())
    rows.append(("Duplicated (month, region) pairs after cleaning", dup, "OK" if dup == 0 else "Check"))

    raw_dup = int(df_raw.duplicated().sum())
    rows.append(("Fully duplicated rows in raw file", raw_dup, "OK" if raw_dup == 0 else "Check"))

    n_missing = int(wide[tables["sources"]].isna().sum().sum())
    # a region with no value at all for a source (for every month) most likely has no such plant
    months_per_reg = wide.groupby("code").size().min()
    structural = 0
    for src in tables["sources"]:
        structural += int(wide.groupby("code")[src].apply(lambda x: x.isna().all()).sum()) * int(months_per_reg)
    if n_missing == 0:
        miss_status = "OK"
    else:
        miss_status = "Explained" if structural == n_missing else "Check"
    rows.append(("Missing production values (before filling with 0)", n_missing, miss_status))
    if n_missing > 0:
        rows.append(("... of which in regions with no value at all for a source (probably no plant)", structural, "info"))

    neg = tables["n_negative"]
    rows.append(("Negative production values (set to 0 for the mix)", neg, "OK" if neg == 0 else "Handled"))

    n_reg = wide["code"].nunique()
    rows.append(("Number of regions", n_reg, "OK" if n_reg >= 12 else "Check"))

    per_region = wide.groupby("code")["month"].nunique()
    same = per_region.nunique() == 1
    rows.append(("Same number of months for every region", "yes" if same else "no", "OK" if same else "Check"))

    all_months = pd.date_range(wide["month"].min(), wide["month"].max(), freq="MS")
    missing_months = len(set(all_months) - set(wide["month"].unique()))
    rows.append(("Months missing in the time range", missing_months, "OK" if missing_months == 0 else "Check"))

    partial = [int(y) for y in sorted(long["year"].unique()) if y not in tables["full_years"]]
    rows.append(("Incomplete years", ", ".join(map(str, partial)) if partial else "none", "Check" if partial else "OK"))

    out = pd.DataFrame(rows, columns=["Check", "Result", "Status"])
    out["Result"] = out["Result"].astype(str)
    return out


def missing_by_column(df_raw):
    m = df_raw.isna().sum().reset_index()
    m.columns = ["column", "missing_values"]
    m["share_pct"] = (100 * m["missing_values"] / max(len(df_raw), 1)).round(2)
    return m
