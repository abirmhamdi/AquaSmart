"""
AquaSmart -- ML / FL / FL+SMPC comparison dashboard.
Subject section 4.6: "Developper un dashboard simple, de preference avec
Streamlit... Afficher un apercu du dataset... Visualiser les predictions...
Comparer graphiquement les performances des modeles ML... Comparer les
approches Centralized ML, Local ML, FL et FL+SMPC... Afficher l'impact de
SMPC sur precision, temps d'execution et cout de communication."

Run with:  streamlit run dashboard/app.py
"""
import json
import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from fl_smpc.data import load_all_clients, FEATURE_COLS, TARGET_COL  # noqa: E402

RESULTS_DIR = os.path.join(ROOT, "fl_smpc", "results")
COMPARISON_PATH = os.path.join(RESULTS_DIR, "comparison_results.json")
ML_PATH = os.path.join(RESULTS_DIR, "ml_comparison.json")

_LOGO = os.path.join(ROOT, "aqua_smart", "frontend", "static", "img", "favicon.png")
st.set_page_config(
    page_title="AquaSmart. Dashboard",
    page_icon=Image.open(_LOGO) if os.path.exists(_LOGO) else None,   # the AquaSmart logo instead of an emoji
    layout="wide",
)


@st.cache_data
def get_clients():
    return load_all_clients(sample_cap=3000)


@st.cache_data
def get_pooled(_clients):
    return pd.concat(_clients.values(), ignore_index=True)


def load_json(path):
    if not os.path.exists(path):
        return None
    with open(path) as f:
        return json.load(f)


def grouped_bar_chart(df, cols, title, higher_is_better=None):
    """Matplotlib grouped bar chart -- one group of bars per metric, one
    colour per model, value labels on top of every bar."""
    models = df["model"].tolist()
    n_models, n_metrics = len(models), len(cols)
    x = np.arange(n_metrics)
    width = 0.8 / n_models
    fig, ax = plt.subplots(figsize=(9, 4.5))
    colors = plt.cm.tab10(np.linspace(0, 1, n_models))
    for i, (model, color) in enumerate(zip(models, colors)):
        vals = df.loc[df["model"] == model, cols].values.flatten()
        bars = ax.bar(x + i * width - 0.4 + width / 2, vals, width, label=model, color=color)
        for b, v in zip(bars, vals):
            ax.annotate(f"{v:.2f}", (b.get_x() + b.get_width() / 2, b.get_height()),
                        ha="center", va="bottom", fontsize=8)
    ax.set_xticks(x)
    ax.set_xticklabels([c.upper().replace("R2", "R\u00b2") for c in cols])
    ax.set_ylabel("Score")
    ax.set_title(title)
    ax.legend(loc="upper right", fontsize=8)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    fig.tight_layout()
    return fig


def feed_ration_histogram(values, bin_width=0.5, zoom_until=10.0, x_max=15.0, squeeze=0.4):
    """Histogram of the feed-ration target on piecewise axes, so the dense part is easy to read:
      x: 0-10 g drawn at full width, 10-15 g squeezed to `squeeze` of its normal width
      y: counts 0-4k drawn at full height (expanded), 4k-6k at 35%, 6k and above at 8% (compressed)
    All bins have the same real width, so bar heights stay comparable. Hover shows the real
    count. Rows above x_max are not drawn; their number is returned for a caption."""
    vals = np.asarray(values, dtype=float)
    edges = np.arange(0, x_max + bin_width, bin_width)
    counts, _ = np.histogram(vals, bins=edges)
    n_above = int((vals > x_max).sum())

    def warp(v, knee, k):
        v = np.asarray(v, dtype=float)
        return np.where(v <= knee, v, knee + (v - knee) * k)

    # y axis: piecewise-linear map  real count -> drawn height
    y_knots = [0, 4000, 6000, 12000, 10_000_000]
    y_slopes = [1.0, 0.35, 0.08, 0.08]
    y_pos = [0.0]
    for i, k in enumerate(y_slopes):
        y_pos.append(y_pos[-1] + (y_knots[i + 1] - y_knots[i]) * k)

    def warp_y(v):
        return np.interp(np.asarray(v, dtype=float), y_knots, y_pos)

    left, right = edges[:-1], edges[1:]
    wl, wr = warp(left, zoom_until, squeeze), warp(right, zoom_until, squeeze)
    fig = go.Figure(go.Bar(
        x=(wl + wr) / 2, y=warp_y(counts), width=(wr - wl),
        customdata=np.column_stack([left, right, counts]),
        hovertemplate="%{customdata[0]:.1f} to %{customdata[1]:.1f} g<br>count: %{customdata[2]:,.0f}<extra></extra>",
        marker_line_width=0.5, marker_line_color="rgba(0,0,0,0.35)",
    ))
    x_ticks = list(range(0, int(zoom_until) + 1)) + [12.5, 15]
    fig.update_xaxes(
        tickvals=[float(warp(t, zoom_until, squeeze)) for t in x_ticks],
        ticktext=[str(t) for t in x_ticks],
        title="feed_ration_g (g per fish)  |  0-10 expanded, 10-15 compressed",
    )
    top = int(np.ceil(counts.max() / 2000.0) * 2000) if counts.max() > 0 else 4000
    top = max(top, 4000)
    y_ticks = [0, 1000, 2000, 3000, 4000, 6000] + ([12000] if top >= 12000 else [])  # few labels in the compressed zone
    fig.update_yaxes(
        tickvals=[float(warp_y(t)) for t in y_ticks],
        ticktext=[f"{t // 1000}k" if t else "0" for t in y_ticks],
        title="count  |  0-4k expanded, 6k-12k compressed",
        range=[0, float(warp_y(top))],
    )
    fig.add_vline(x=zoom_until, line_dash="dot", line_color="gray",
                  annotation_text="x scale compressed", annotation_position="top right")
    if counts.max() > 4000:
        fig.add_hline(y=float(warp_y(4000)), line_dash="dot", line_color="gray",
                      annotation_text="y: compression starts (4k)", annotation_position="top right")
    fig.update_layout(title="Derived feed_ration_g target distribution", bargap=0)
    return fig, n_above


# ── Floating header bar: centered title + section tabs ───────────────────
PAGE_DATA = "Dataset Overview"
PAGE_ML = "ML Model Leaderboard"
PAGE_CMP = "Approach Comparison"   # = Centralized vs Local vs FL vs FL+SMPC
SECTIONS = [PAGE_DATA, PAGE_ML, PAGE_CMP]

HEADER_CSS = """
<style>
/* keep Streamlit's own header (it holds the show/hide sidebar button) but make it see-through, icons in white */
[data-testid="stHeader"] { background: transparent !important; }
[data-testid="stHeader"] button, [data-testid="stHeader"] svg { color: #ffffff !important; }
[data-testid="stMainBlockContainer"] { padding: 0 2rem 3rem 2rem !important; max-width: 100% !important; }

/* the element that only carries this CSS takes no space (the styles still apply) */
[data-testid="stElementContainer"]:has(style) { display: none; }

/* title bar: centered, sticks to the top while the page scrolls */
[data-testid="stMainBlockContainer"] > [data-testid="stVerticalBlock"] > *:has(.st-key-topbar) {
    position: sticky; top: 0; z-index: 1000;
}
.st-key-topbar {
    width: calc(100% + 4rem) !important; max-width: none !important; margin: 0 -2rem 1rem -2rem;
    padding: 0 4rem; min-height: 64px; align-items: center; justify-content: center;
    background: linear-gradient(90deg, #0a2f3d 0%, #0e5a6b 50%, #0a2f3d 100%);
    border-bottom: 2px solid #22d3ee; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.35);
}
.aqs-title { text-align: center; color: #ffffff; font-size: 1.7rem; font-weight: 700; letter-spacing: 0.3px; line-height: 1.2; }

/* the button that re-opens a hidden sidebar must stay clearly visible on the dark bar */
[data-testid="stExpandSidebarButton"] { background: rgba(255, 255, 255, 0.2) !important; border-radius: 8px; opacity: 1 !important; }
[data-testid="stExpandSidebarButton"] svg, [data-testid="stExpandSidebarButton"] * { color: #ffffff !important; opacity: 1 !important; }

/* sidebar navigation: the selected section is highlighted (round radio dot hidden) */
[data-testid="stSidebar"] label[data-testid="stRadioOption"] > div > div:first-child,
[data-testid="stSidebar"] label[data-baseweb="radio"] > div:first-child { display: none; }
[data-testid="stSidebar"] [role="radiogroup"] { gap: 0.35rem; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"], [data-testid="stSidebar"] label[data-baseweb="radio"] {
    padding: 0.5rem 0.8rem; border-radius: 8px; width: 100%; cursor: pointer;
}
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked),
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) { background: #22d3ee; }
[data-testid="stSidebar"] label[data-testid="stRadioOption"]:has(input:checked) p,
[data-testid="stSidebar"] label[data-baseweb="radio"]:has(input:checked) p { color: #04222b; font-weight: 700; }
</style>
"""
st.markdown(HEADER_CSS, unsafe_allow_html=True)   # style only; kept outside the bar

with st.container(key="topbar"):
    st.markdown('<div class="aqs-title">AquaSmart: Secure feeding-ration prediction</div>', unsafe_allow_html=True)

# navigation lives in the left sidebar (collapsible with the arrow at the top)
page = st.sidebar.radio("Section", SECTIONS, key="section")

clients = get_clients()
pooled = get_pooled(clients)

# ─────────────────────────────────────────────────────────────────────────
if page == PAGE_DATA:
    st.header("Dataset overview")
    st.write(
        f"**{len(clients)} ponds** loaded from `dataset/*.csv` (each pond = one independent "
        f"farm / FL client), **{len(pooled):,} rows** after cleaning."
    )

    sizes = pd.DataFrame({"pond": list(clients.keys()), "rows": [len(v) for v in clients.values()]})
    c1, c2 = st.columns([1, 1])
    with c1:
        st.plotly_chart(px.bar(sizes, x="pond", y="rows", title="Rows per pond (client)"),
                         use_container_width=True)
    with c2:
        hist_fig, n_above = feed_ration_histogram(pooled[TARGET_COL])
        st.plotly_chart(hist_fig, use_container_width=True)
        st.caption(f"{n_above:,} rows ({n_above / len(pooled):.1%}) have a ration above 15 g "
                   "and are not drawn.")

    st.subheader("Sensor feature distributions")
    feat_pick = st.multiselect(
        "Features", ["temperature", "dissolved_oxygen", "ph", "turbidity", "ammonia", "nitrate"],
        default=["temperature", "dissolved_oxygen", "ph"],
    )
    if feat_pick:
        fig = go.Figure()
        for f in feat_pick:
            fig.add_trace(go.Box(y=pooled[f], name=f))
        fig.update_layout(title="Boxplots of raw sensor readings across all ponds")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Correlation matrix")
    corr = pooled[FEATURE_COLS].corr()
    st.plotly_chart(px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1),
                     use_container_width=True)

    with st.expander("Raw sample rows"):
        st.dataframe(pooled.sample(min(200, len(pooled))))

# ─────────────────────────────────────────────────────────────────────────
elif page == PAGE_ML:
    st.header("ML model comparison (subject 4.3)")
    ml = load_json(ML_PATH)
    if ml is None:
        st.warning("No results yet -- run `python -m fl_smpc.experiments.ml_models` first.")
    else:
        st.caption(f"Target: `{ml['target']}` | train={ml['n_train']:,} | test={ml['n_test']:,}")
        df = pd.DataFrame(ml["leaderboard"])

        st.subheader("Models comparison")
        st.pyplot(grouped_bar_chart(df, ["mae", "rmse", "r2"], "Model Comparison"))
        st.caption("Lower is better for MAE/RMSE, higher is better for R2.")

        st.dataframe(df.set_index("model").style.format(
            {"mae": "{:.4f}", "rmse": "{:.4f}", "r2": "{:.4f}", "train_time_sec": "{:.2f}"}))
        st.info(
            "Linear/Ridge stay close together (both linear); Random Forest / XGBoost capture the "
            "threshold-style non-linearities in the feeding rules and win on RMSE/R2. The base "
            "model used later for the FL and FL+SMPC simulation is still Ridge -- FedAvg-style "
            "aggregation only works cleanly on parametric models."
        )

        st.subheader("Visualise predictions: predicted vs. actual")
        pick = st.selectbox("Model", df["model"].tolist(), index=0)
        samp = ml["prediction_samples"][pick]
        pred_df = pd.DataFrame({"Actual (g)": samp["y_true"], "Predicted (g)": samp["y_pred"]})
        fig = px.scatter(pred_df, x="Actual (g)", y="Predicted (g)", opacity=0.5,
                          title=f"{pick}: predicted vs. actual feed ration (test set sample)")
        lim = max(pred_df.max().max(), 1)
        fig.add_trace(go.Scatter(x=[0, lim], y=[0, lim], mode="lines",
                                  line=dict(dash="dash", color="gray"), name="perfect prediction"))
        st.plotly_chart(fig, use_container_width=True)

# ─────────────────────────────────────────────────────────────────────────
elif page == PAGE_CMP:
    st.header("Approach comparison: Centralized vs Local vs FL vs FL+SMPC")
    res = load_json(COMPARISON_PATH)
    if res is None:
        st.warning("No results yet -- run `python -m fl_smpc.run_experiments` first.")
    else:
        keys = ["centralized", "local", "federated", "smpc"]
        rows = []
        for k in keys:
            r = res[k]
            rows.append({
                "Approach": r["approach"], "MAE": r["metrics"]["mae"], "RMSE": r["metrics"]["rmse"],
                "R2": r["metrics"]["r2"], "Time (s)": r["time_sec"], "Messages": r["n_messages"],
                "Comm. (KB)": r["comm_bytes"] / 1024, "Confidentiality": r["confidentiality"],
            })
        df = pd.DataFrame(rows)
        st.dataframe(df.set_index("Approach").style.format(
            {"MAE": "{:.3f}", "RMSE": "{:.3f}", "R2": "{:.3f}", "Time (s)": "{:.3f}", "Comm. (KB)": "{:.1f}"}))

        c1, c2 = st.columns(2)
        with c1:
            st.plotly_chart(px.bar(df, x="Approach", y="RMSE", color="Confidentiality",
                                    title="Accuracy (RMSE, lower is better)"), use_container_width=True)
        with c2:
            st.plotly_chart(px.bar(df, x="Approach", y="Comm. (KB)", color="Confidentiality",
                                    title="Communication cost"), use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            st.plotly_chart(px.bar(df, x="Approach", y="Time (s)", color="Confidentiality",
                                    title="Execution time"), use_container_width=True)
        with c4:
            conf_order = {"Low": 1, "Medium": 2, "High": 3}
            df["Confidentiality level"] = df["Confidentiality"].map(conf_order)
            st.plotly_chart(px.bar(df, x="Approach", y="Confidentiality level",
                                    title="Confidentiality (qualitative, higher = safer)",
                                    color="Confidentiality"), use_container_width=True)

        st.subheader("FL vs FL+SMPC convergence over rounds")
        hist_fl = pd.DataFrame(res["federated"]["history"])
        hist_smpc = pd.DataFrame(res["smpc"]["history"])
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=hist_fl["round"], y=hist_fl["rmse"], name="FL (FedAvg)"))
        fig.add_trace(go.Scatter(x=hist_smpc["round"], y=hist_smpc["rmse"], name="FL + SMPC",
                                  line=dict(dash="dash")))
        fig.update_layout(title="Global model RMSE per communication round", xaxis_title="Round", yaxis_title="RMSE")
        st.plotly_chart(fig, use_container_width=True)
        st.caption(
            "The two curves sit on top of each other: pairwise additive masking is designed so the "
            "masks cancel exactly once the server sums the weighted updates -- FL+SMPC reaches the "
            "same model as plain FL, at the cost of extra handshake messages "
            f"({res['smpc']['smpc_handshake_messages']} total) and "
            f"{res['smpc']['smpc_overhead_sec']*1000:.1f} ms of masking compute."
        )

        with st.expander("What each approach's confidentiality note actually means"):
            for k in keys:
                r = res[k]
                st.markdown(f"**{r['approach']}** ({r['confidentiality']}): {r['confidentiality_note']}")
