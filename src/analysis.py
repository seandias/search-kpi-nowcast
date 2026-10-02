"""Does Google search interest predict a company's reported operating KPI?

Run from the repo root:
    python src/analysis.py duolingo
    python src/analysis.py --all        # every company, plus outputs/summary.md

Each company lives in companies/<name>/ with:
    config.json         name, ticker, KPI label, search term
    kpi.csv             quarter, quarter_end, value, source (from the company's filings)
    google_trends.csv   weekly search interest (from src/fetch_trends.py)

Approach
- KPIs and search interest both trend, so correlating raw levels would look
  great and mean nothing. We compare year-over-year (YoY) growth rates, which
  also removes seasonality.
- Walk-forward test: for each quarter, fit on earlier quarters only, then
  predict that quarter, which is what an analyst could have known before the
  earnings release.
- Benchmark: a naive forecast that assumes YoY growth stays the same as last
  quarter. A signal is only useful if it beats this.
- Nowcast: predict the latest completed quarter before the company reports it.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

COMPANIES = Path("companies")
OUT = Path("outputs")
MIN_TRAIN = 6  # quarters needed before the first out-of-sample prediction


def load_config(slug):
    return json.loads((COMPANIES / slug / "config.json").read_text())


def load_trends(path):
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


def build_quarterly(slug):
    kpi = pd.read_csv(COMPANIES / slug / "kpi.csv")
    kpi["period"] = pd.PeriodIndex(kpi["quarter"], freq="Q")
    kpi = kpi.set_index("period")["value"]

    trends = load_trends(COMPANIES / slug / "google_trends.csv")
    tq = trends.groupby(trends.index.to_period("Q")).agg(["mean", "count"])
    tq = tq[tq["count"] >= 10]["mean"]  # drop partial quarters at the edges of the window

    idx = pd.period_range(min(kpi.index.min(), tq.index.min()), max(kpi.index.max(), tq.index.max()), freq="Q")
    df = pd.DataFrame(index=idx)
    df["kpi"] = kpi
    df["trends"] = tq
    df["kpi_yoy"] = df["kpi"] / df["kpi"].shift(4) - 1
    df["trends_yoy"] = df["trends"] / df["trends"].shift(4) - 1
    df["kpi_prev_year"] = df["kpi"].shift(4)
    return df


def _change_slope(train):
    d = train[["kpi_yoy", "trends_yoy"]].diff().dropna()
    return np.polyfit(d["trends_yoy"], d["kpi_yoy"], 1)[0] if len(d) >= 3 else 0.0


def walk_forward(df):
    data = df.dropna(subset=["kpi_yoy", "trends_yoy"])
    rows = []
    for i in range(MIN_TRAIN, len(data)):
        train, test = data.iloc[:i], data.iloc[i]
        b, a = np.polyfit(train["trends_yoy"], train["kpi_yoy"], 1)
        level_g = a + b * test["trends_yoy"]
        naive_g = train["kpi_yoy"].iloc[-1]
        # Change model: last quarter's growth, nudged by how much search growth moved since then.
        change_g = naive_g + _change_slope(train) * (test["trends_yoy"] - train["trends_yoy"].iloc[-1])
        base = test["kpi_prev_year"]
        rows.append({
            "quarter": str(data.index[i]),
            "actual": test["kpi"],
            "naive": base * (1 + naive_g),
            "change_model": base * (1 + change_g),
            "level_model": base * (1 + level_g),
            "actual_yoy": test["kpi_yoy"],
            "naive_yoy": naive_g,
            "change_yoy": change_g,
            "level_yoy": level_g,
        })
    return pd.DataFrame(rows)


def nowcast(df):
    """Predict the most recent quarter that has Trends data but no reported KPI yet."""
    data = df.dropna(subset=["kpi_yoy", "trends_yoy"])
    pending = df[df["kpi"].isna() & df["trends_yoy"].notna() & df["kpi_prev_year"].notna()]
    if pending.empty:
        return None
    q = pending.index[-1]
    base, tr = df.loc[q, "kpi_prev_year"], df.loc[q, "trends_yoy"]
    b, a = np.polyfit(data["trends_yoy"], data["kpi_yoy"], 1)
    naive_g = data["kpi_yoy"].iloc[-1]
    change_g = naive_g + _change_slope(data) * (tr - data["trends_yoy"].iloc[-1])
    level_g = a + b * tr
    return {"quarter": str(q), "trends_yoy": tr,
            "naive": base * (1 + naive_g), "naive_yoy": naive_g,
            "change_model": base * (1 + change_g), "change_yoy": change_g,
            "level_model": base * (1 + level_g), "level_yoy": level_g}


def metrics(df, wf):
    data = df.dropna(subset=["kpi_yoy", "trends_yoy"])
    mae = {m: (wf[m] - wf["actual"]).abs().mean() for m in ["naive", "change_model", "level_model"]}
    hit = (np.sign(wf["change_yoy"] - wf["naive_yoy"]) == np.sign(wf["actual_yoy"] - wf["naive_yoy"])).mean()
    return {"n": len(data), "first": str(data.index[0]), "last": str(data.index[-1]),
            "corr": data["kpi_yoy"].corr(data["trends_yoy"]), "tested": len(wf), "mae": mae, "hit": hit}


def charts(slug, cfg, df, wf):
    out = OUT / slug
    out.mkdir(parents=True, exist_ok=True)
    data = df.dropna(subset=["kpi_yoy", "trends_yoy"])
    labels = [str(p) for p in data.index]
    short = cfg["kpi_short"]

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(labels, data["kpi_yoy"] * 100, marker="o", label=f"Reported {short} growth (YoY)")
    ax.plot(labels, data["trends_yoy"] * 100, marker="s", label=f'Google searches for "{cfg["search_term"]}" (YoY)')
    ax.axhline(0, color="grey", lw=0.8)
    ax.set_ylabel("Year-over-year change (%)")
    ax.set_title(f"{cfg['name']}: search interest vs reported {short}")
    ax.legend(); ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(out / "growth_vs_search.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(wf["quarter"], wf["actual"], marker="o", lw=2, label=f"Reported {short}")
    ax.plot(wf["quarter"], wf["naive"], marker="^", ls=":", label="Naive benchmark (same growth as last quarter)")
    ax.plot(wf["quarter"], wf["change_model"], marker="D", ls="-.", label="Search-change model")
    ax.plot(wf["quarter"], wf["level_model"], marker="s", ls="--", label="Search-level model")
    ax.set_ylabel(f"{short} ({cfg['kpi_unit']})")
    ax.set_title(f"{cfg['name']}: out-of-sample forecasts, using only earlier quarters")
    ax.legend(); ax.tick_params(axis="x", rotation=45)
    fig.tight_layout(); fig.savefig(out / "walk_forward.png", dpi=150); plt.close(fig)


def run(slug):
    cfg = load_config(slug)
    df = build_quarterly(slug)
    wf = walk_forward(df)
    m = metrics(df, wf)
    nc = nowcast(df)
    charts(slug, cfg, df, wf)

    u, short, base = "M", cfg["kpi_short"], m["mae"]["naive"]
    vs = lambda k: f"{(m['mae'][k] / base - 1) * 100:+.0f}% vs benchmark"
    lines = [
        f"# {cfg['name']} ({cfg['ticker']}): search interest vs {cfg['kpi_name'].lower()}", "",
        f"- Quarters with both series (YoY): {m['n']} ({m['first']} to {m['last']})",
        f"- Correlation of YoY growth, search vs {short}: {m['corr']:.2f}",
        f"- Out-of-sample quarters tested: {m['tested']}",
        f"- Mean absolute error, naive benchmark: {base:.2f}{u}",
        f"- Mean absolute error, search-change model: {m['mae']['change_model']:.2f}{u} ({vs('change_model')})",
        f"- Mean absolute error, search-level model: {m['mae']['level_model']:.2f}{u} ({vs('level_model')})",
        f"- Search-change model called acceleration vs deceleration correctly: {m['hit']:.0%} of quarters",
        "", "## Walk-forward detail", "",
        wf.assign(**{c: wf[c].map("{:.1%}".format) for c in ["actual_yoy", "naive_yoy", "change_yoy", "level_yoy"]},
                  **{c: wf[c].round(1) for c in ["actual", "naive", "change_model", "level_model"]}).to_markdown(index=False),
    ]
    if nc:
        lines += ["", f"## Nowcast for {nc['quarter']} (not yet reported)", "",
                  f"- Search interest YoY: {nc['trends_yoy']:+.1%}",
                  f"- Naive benchmark: {nc['naive']:.1f}{u} ({nc['naive_yoy']:.1%} YoY)",
                  f"- Search-change model: {nc['change_model']:.1f}{u} ({nc['change_yoy']:.1%} YoY)",
                  f"- Search-level model: {nc['level_model']:.1f}{u} ({nc['level_yoy']:.1%} YoY)"]
    text = "\n".join(lines)
    (OUT / slug / "results.md").write_text(text)
    print(text, "\n")
    return cfg, m, nc


def summary(results):
    rows = []
    for slug, (cfg, m, nc) in results.items():
        base = m["mae"]["naive"]
        rows.append({
            "Company": cfg["name"], "KPI": cfg["kpi_short"], "Quarters tested": m["tested"],
            "YoY correlation": f"{m['corr']:.2f}",
            "Search-change vs benchmark": f"{(m['mae']['change_model'] / base - 1) * 100:+.0f}%",
            "Search-level vs benchmark": f"{(m['mae']['level_model'] / base - 1) * 100:+.0f}%",
            "Beats benchmark?": "Yes" if min(m["mae"]["change_model"], m["mae"]["level_model"]) < base else "No",
        })
    text = "# Summary across companies\n\nNegative % means lower error than the naive benchmark (better).\n\n" \
        + pd.DataFrame(rows).to_markdown(index=False)
    (OUT / "summary.md").write_text(text)
    print(text)


def main():
    args = sys.argv[1:]
    if not args:
        raise SystemExit("Usage: python src/analysis.py <company> | --all")
    if args == ["--all"]:
        slugs = sorted(p.name for p in COMPANIES.iterdir() if (p / "google_trends.csv").exists())
        missing = sorted(p.name for p in COMPANIES.iterdir() if (p / "config.json").exists() and p.name not in slugs)
        if missing:
            print(f"Skipping (no google_trends.csv yet, run fetch_trends.py): {', '.join(missing)}\n")
    else:
        slugs = args
    results = {s: run(s) for s in slugs}
    if len(results) > 1:
        summary(results)


if __name__ == "__main__":
    main()
