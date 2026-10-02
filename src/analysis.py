"""Does Google search interest in "Duolingo" predict its reported daily active users (DAUs)?

Run from the repo root:  python src/analysis.py

Approach
- Both series trend strongly upward, so correlating raw levels would look great
  and mean nothing. Instead we compare year-over-year (YoY) growth rates, which
  also removes seasonality (January resolutions, summer dips).
- Walk-forward test: for each quarter, fit a one-variable regression on earlier
  quarters only, then predict that quarter. This mimics what an analyst could
  actually have known before the earnings release.
- Benchmark: a naive forecast that assumes YoY growth stays the same as last
  quarter. The signal is only useful if it beats this.
- Nowcast: predict the latest completed quarter before Duolingo reports it.
"""
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

DATA = Path("data")
OUT = Path("outputs")
MIN_TRAIN = 6  # quarters needed before the first out-of-sample prediction


def load_trends(path=DATA / "google_trends.csv"):
    """Read either the pytrends CSV or the CSV downloaded from trends.google.com."""
    raw = path.read_text(encoding="utf-8-sig").splitlines()
    # The manual download starts with "Category: ..." and a blank line before the header.
    start = next(i for i, line in enumerate(raw) if line.lower().startswith(("date", "week", "month")))
    df = pd.read_csv(path, skiprows=start, encoding="utf-8-sig")
    df.columns = ["date", "interest"] + list(df.columns[2:])
    df = df[["date", "interest"]]
    df["interest"] = pd.to_numeric(df["interest"].astype(str).str.replace("<1", "0.5"), errors="coerce")
    df["date"] = pd.to_datetime(df["date"])
    return df.dropna().set_index("date")["interest"]


def build_quarterly():
    dau = pd.read_csv(DATA / "duolingo_dau.csv")
    dau["period"] = pd.PeriodIndex(dau["quarter"], freq="Q")
    dau = dau.set_index("period")["dau_millions"]

    trends = load_trends()
    tq = trends.groupby(trends.index.to_period("Q")).agg(["mean", "count"])
    tq = tq[tq["count"] >= 10]["mean"]  # drop partial quarters at the edges of the window

    idx = pd.period_range(min(dau.index.min(), tq.index.min()), max(dau.index.max(), tq.index.max()), freq="Q")
    df = pd.DataFrame(index=idx)
    df["dau"] = dau
    df["trends"] = tq
    df["dau_yoy"] = df["dau"] / df["dau"].shift(4) - 1
    df["trends_yoy"] = df["trends"] / df["trends"].shift(4) - 1
    df["dau_prev_year"] = df["dau"].shift(4)
    return df


def walk_forward(df):
    data = df.dropna(subset=["dau_yoy", "trends_yoy"])
    rows = []
    for i in range(MIN_TRAIN, len(data)):
        train, test = data.iloc[:i], data.iloc[i]
        b, a = np.polyfit(train["trends_yoy"], train["dau_yoy"], 1)
        pred_g = a + b * test["trends_yoy"]
        naive_g = train["dau_yoy"].iloc[-1]
        # Change model: last quarter's growth, nudged by how much search growth moved since then.
        dtr = train[["dau_yoy", "trends_yoy"]].diff().dropna()
        bd = np.polyfit(dtr["trends_yoy"], dtr["dau_yoy"], 1)[0] if len(dtr) >= 3 else 0.0
        change_g = naive_g + bd * (test["trends_yoy"] - train["trends_yoy"].iloc[-1])
        rows.append({
            "quarter": str(data.index[i]),
            "actual_dau": test["dau"],
            "pred_dau": test["dau_prev_year"] * (1 + pred_g),
            "naive_dau": test["dau_prev_year"] * (1 + naive_g),
            "change_dau": test["dau_prev_year"] * (1 + change_g),
            "actual_yoy": test["dau_yoy"],
            "pred_yoy": pred_g,
            "naive_yoy": naive_g,
            "change_yoy": change_g,
        })
    return pd.DataFrame(rows)


def nowcast(df):
    """Predict the most recent quarter that has Trends data but no reported DAUs yet."""
    data = df.dropna(subset=["dau_yoy", "trends_yoy"])
    pending = df[df["dau"].isna() & df["trends_yoy"].notna() & df["dau_prev_year"].notna()]
    if pending.empty:
        return None
    q = pending.index[-1]
    b, a = np.polyfit(data["trends_yoy"], data["dau_yoy"], 1)
    g = a + b * df.loc[q, "trends_yoy"]
    resid = data["dau_yoy"] - (a + b * data["trends_yoy"])
    d = data[["dau_yoy", "trends_yoy"]].diff().dropna()
    bd = np.polyfit(d["trends_yoy"], d["dau_yoy"], 1)[0]
    gc = data["dau_yoy"].iloc[-1] + bd * (df.loc[q, "trends_yoy"] - data["trends_yoy"].iloc[-1])
    return {"change_yoy": gc, "change_dau": df.loc[q, "dau_prev_year"] * (1 + gc),"quarter": str(q), "pred_yoy": g, "pred_dau": df.loc[q, "dau_prev_year"] * (1 + g),
            "band_dau": df.loc[q, "dau_prev_year"] * resid.std(ddof=2),
            "trends_yoy": df.loc[q, "trends_yoy"], "slope": b}


def charts(df, wf):
    OUT.mkdir(exist_ok=True)
    data = df.dropna(subset=["dau_yoy", "trends_yoy"])
    labels = [str(p) for p in data.index]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(labels, data["dau_yoy"] * 100, marker="o", label="Reported DAU growth (YoY)")
    ax.plot(labels, data["trends_yoy"] * 100, marker="s", label='Google searches for "Duolingo" (YoY)')
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_ylabel("Year-over-year change (%)")
    ax.set_title("Search interest vs reported user growth")
    ax.legend(); ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(OUT / "growth_vs_search.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(wf["quarter"], wf["actual_dau"], marker="o", lw=2, label="Reported DAUs")
    ax.plot(wf["quarter"], wf["pred_dau"], marker="s", ls="--", label="Search-level model")
    ax.plot(wf["quarter"], wf["change_dau"], marker="D", ls="-.", label="Search-change model")
    ax.plot(wf["quarter"], wf["naive_dau"], marker="^", ls=":", label="Naive forecast (same growth as last quarter)")
    ax.set_ylabel("DAUs (millions)")
    ax.set_title("Out-of-sample forecasts, made using only earlier quarters")
    ax.legend(); ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(OUT / "walk_forward.png", dpi=150); plt.close(fig)


def main():
    df = build_quarterly()
    data = df.dropna(subset=["dau_yoy", "trends_yoy"])
    corr = data["dau_yoy"].corr(data["trends_yoy"])
    wf = walk_forward(df)
    mae_model = (wf["pred_dau"] - wf["actual_dau"]).abs().mean()
    mae_naive = (wf["naive_dau"] - wf["actual_dau"]).abs().mean()
    mae_change = (wf["change_dau"] - wf["actual_dau"]).abs().mean()
    hit = (np.sign(wf["change_yoy"] - wf["naive_yoy"]) == np.sign(wf["actual_yoy"] - wf["naive_yoy"])).mean()
    nc = nowcast(df)
    charts(df, wf)

    lines = [
        "# Results", "",
        f"- Quarters with both series (YoY): {len(data)} ({data.index[0]} to {data.index[-1]})",
        f"- Correlation of YoY growth, search vs DAUs: {corr:.2f}",
        f"- Out-of-sample quarters tested: {len(wf)}",
        f"- Mean absolute error, naive forecast (benchmark): {mae_naive:.2f}M DAUs",
        f"- Mean absolute error, search-level model: {mae_model:.2f}M DAUs "
        f"({(mae_model / mae_naive - 1) * 100:+.0f}% vs benchmark)",
        f"- Mean absolute error, search-change model: {mae_change:.2f}M DAUs "
        f"({(mae_change / mae_naive - 1) * 100:+.0f}% vs benchmark)",
        f"- Search-change model called acceleration vs deceleration correctly: {hit:.0%} of quarters",
        "", "## Walk-forward detail", "",
        wf.assign(**{c: wf[c].map("{:.1%}".format) for c in ["actual_yoy", "pred_yoy", "naive_yoy", "change_yoy"]},
                  **{c: wf[c].round(1) for c in ["actual_dau", "pred_dau", "naive_dau", "change_dau"]}).to_markdown(index=False),
    ]
    if nc:
        lines += ["", f"## Nowcast for {nc['quarter']} (not yet reported)", "",
                  f"- Search interest YoY: {nc['trends_yoy']:+.1%}",
                  f"- Predicted DAUs: {nc['pred_dau']:.1f}M (about ±{nc['band_dau']:.1f}M), "
                  f"implying {nc['pred_yoy']:.1%} YoY growth (search-level model)",
                  f"- Predicted DAUs: {nc['change_dau']:.1f}M, implying {nc['change_yoy']:.1%} YoY growth (search-change model)"]
    text = "\n".join(lines)
    OUT.mkdir(exist_ok=True)
    (OUT / "results.md").write_text(text)
    print(text)


if __name__ == "__main__":
    main()
