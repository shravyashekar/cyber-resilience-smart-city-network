"""Cyber Resilience Smart City Network: a fictional city drill demonstration."""
from html import escape

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benchmark_data import evaluate_labeled_csv, preview_csv
from anomaly_detector import classification_metrics
from network_topology import SERVICES
from simulation import run_simulation

st.set_page_config(
    page_title="Cyber Resilience Smart City Network",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.session_state.setdefault("light_theme", False)
st.toggle("Light theme", key="light_theme", help="Switch the dashboard to a light color scheme.")

st.markdown("""
<style>
html, body, [class*="css"] {font-family:Segoe UI,Arial,sans-serif;background:#07111f;color:#edf4ff}
.stApp {background:radial-gradient(ellipse at 8% 0%,#122b45 0%,#07111f 58%)}
[data-testid="stSidebar"] {background:#0b1928;border-right:1px solid #23364d}
.block-container {padding-top:2.2rem;max-width:1400px;position:relative}
.st-key-light_theme {position:absolute !important;top:4rem !important;right:0 !important;width:auto !important;z-index:1000}
[data-testid="stHeader"] {background:transparent !important}
[data-testid="stToolbar"], [data-testid="stDecoration"] {display:none !important}
.brand-tag {color:#60d7c2;font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase}
.hero {font-size:42px;font-weight:800;letter-spacing:-1.3px;margin:2px 0 0}
.subtitle {color:#a9bbcf;font-size:16px;margin:4px 0 20px}
.result-box {padding:18px 20px;border-radius:15px;background:linear-gradient(135deg,#123148,#102236);border:1px solid #2a4d63;margin:8px 0 18px}
.result-title {font-size:20px;font-weight:750;margin-bottom:5px;color:#f3f8ff}
.result-copy {color:#b4c5d8;font-size:14px;line-height:1.5}
.result-pill {display:inline-block;padding:5px 10px;margin-top:9px;border-radius:999px;background:#173c3b;color:#7ce0c9;font-size:12px;font-weight:700}
.flow-grid {display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px;margin:8px 0 18px}
.flow-card {min-height:130px;padding:16px;background:linear-gradient(150deg,#12263c,#0d1b2b);border:1px solid #243951;border-radius:15px}
.flow-num {font-size:11px;font-weight:700;color:#60d7c2;letter-spacing:1.4px}
.flow-icon {font-size:24px;margin:9px 0 5px}
.flow-title {font-size:15px;font-weight:700;color:#edf4ff;margin-bottom:5px}
.flow-copy {font-size:12px;line-height:1.45;color:#a9bbcf}
.tier-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:8px 0 18px}
.tier-card {padding:15px 16px;border-radius:14px;background:#102236;border:1px solid #28445d}
.tier-title {font-size:14px;font-weight:800;color:#edf4ff}
.tier-services {font-size:12px;color:#a9bbcf;line-height:1.5;margin-top:7px}
.tier-action {font-size:12px;font-weight:700;color:#60d7c2;margin-top:8px}
.service-grid {display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px;margin:12px 0 26px}
.service-card {min-height:168px;padding:18px;background:linear-gradient(150deg,#142b42,#0d1b2b);border:1px solid #28445d;border-radius:16px}
.service-head {display:flex;align-items:center;gap:14px;margin-bottom:15px}
.service-icon {display:flex;flex:0 0 56px;align-items:center;justify-content:center;width:56px;height:56px;border-radius:16px;background:#1c3850;font-size:32px}
.service-title-wrap {min-width:0;flex:1}
.service-name {font-size:17px;font-weight:750;color:#edf4ff;line-height:1.25}
.service-kind {font-size:12px;color:#9fb3c9;margin-top:4px}
.tier-badge {flex:0 0 auto;padding:5px 8px;border-radius:8px;background:#20364b;color:#bad0e4;font-size:10px;font-weight:700;white-space:nowrap}
.service-states {display:grid;grid-template-columns:1fr 1fr;gap:10px}
.state-box {min-width:0;padding:10px 11px;border-radius:10px;background:#0c1928;border:1px solid #20364b}
.state-label {color:#8fa8c1;font-size:10px;font-weight:700;letter-spacing:.07em;text-transform:uppercase}
.state-value {font-size:13px;font-weight:700;line-height:1.3;margin-top:5px;overflow-wrap:anywhere}
.status-ok {color:#7ce0c9}
.status-alert {color:#ffbd99}
.status-fallback {color:#f1d37d}
@media(max-width:900px){.service-grid{grid-template-columns:1fr}}
@media(max-width:900px){.tier-grid{grid-template-columns:1fr}}
[data-testid="stMetric"] {background:linear-gradient(145deg,#12263c,#0d1b2b);border:1px solid #243951;padding:15px 17px;border-radius:14px}
[data-testid="stMetricLabel"] {color:#a9bbcf}
[data-testid="stMetricValue"] {font-weight:750}
[data-testid="stPlotlyChart"] {background:#0c1928;border:1px solid #21364c;border-radius:16px;padding:8px}
div.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background:linear-gradient(90deg,#e94f61,#ff775f);border:0;border-radius:10px;font-weight:700;min-height:46px
}
div.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {border:0;filter:brightness(1.08)}
@media(max-width:900px){.flow-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.hero{font-size:34px}}
</style>
""", unsafe_allow_html=True)

if st.session_state["light_theme"]:
    st.markdown("""
    <style>
    html, body, [class*="css"] {background:#f4f7fb !important;color:#1f2937 !important}
    .stApp {background:#f4f7fb !important;color:#1f2937 !important}
    [data-testid="stSidebar"] {background:#eaf0f6 !important;border-right:1px solid #d5dee8}
    [data-testid="stHeader"] {background:rgba(244,247,251,.95) !important}
    h1, h2, h3, h4, p, label, li, [data-testid="stMarkdownContainer"] {color:#1f2937}
    .brand-tag, .flow-num, .tier-action {color:#087f72}
    .subtitle, .flow-copy, .tier-services, .service-kind, .state-label,
    [data-testid="stMetricLabel"] {color:#526174 !important}
    .result-box {background:linear-gradient(135deg,#e4f1f5,#eef4fa);border-color:#c5d8e2}
    .result-title, .flow-title, .tier-title, .service-name {color:#172b3b !important}
    .result-copy {color:#40566a !important}
    .result-pill {background:#d9f3eb;color:#08765e}
    .flow-card, .tier-card, .service-card, [data-testid="stMetric"] {
        background:#ffffff !important;border-color:#d5e0ea !important
    }
    .service-icon, .tier-badge {background:#e7eef5;color:#334b61}
    .state-box {background:#f5f8fb;border-color:#d8e1ea}
    .state-value {color:#26384a}
    .status-ok {color:#08765e}
    .status-alert {color:#b5472e}
    .status-fallback {color:#8a6500}
    [data-testid="stPlotlyChart"] {background:#ffffff;border-color:#d5e0ea}
    [data-testid="stDataFrame"], [data-testid="stTable"] {background:#ffffff;color:#1f2937}
    [data-testid="stMetricDelta"] {
        background:#d9f3eb !important;color:#08765e !important
    }
    [data-testid="stMetricDelta"] * {color:#08765e !important}
    [data-testid="stMetricDelta"] svg {fill:#08765e !important}
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) {
        background:#e9f7ef !important;border:1px solid #a8d7b6 !important
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) {
        background:#eaf4fc !important;border:1px solid #b6d6ef !important
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) {
        background:#fff6dc !important;border:1px solid #ebd48a !important
    }
    [data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) {
        background:#fff0f0 !important;border:1px solid #efb4b4 !important
    }
    [data-testid="stAlertContentSuccess"], [data-testid="stAlertContentSuccess"] * {color:#176b3a !important}
    [data-testid="stAlertContentInfo"], [data-testid="stAlertContentInfo"] * {color:#175a8c !important}
    [data-testid="stAlertContentWarning"], [data-testid="stAlertContentWarning"] * {color:#704d00 !important}
    [data-testid="stAlertContentError"], [data-testid="stAlertContentError"] * {color:#9b1c1c !important}
    [data-testid^="stAlertContent"] svg {fill:currentColor !important}
    [data-baseweb="select"] > div, [data-baseweb="input"] > div,
    [data-testid="stFileUploaderDropzone"] {
        background:#ffffff !important;color:#1f2937 !important;border-color:#cbd5e1 !important
    }
    [data-testid="stTabs"] button {color:#334155}
    div.stButton > button[kind="primary"],
    div[data-testid="stFormSubmitButton"] > button[kind="primary"] {color:#ffffff}
    </style>
    """, unsafe_allow_html=True)

EVENTS = {
    "Denial of Service": "DoS",
    "Port scanning": "Port Scan",
    "Suspicious software activity": "Malware-like",
    "Normal day": "Normal",
}
EVENT_LABELS = {value: key for key, value in EVENTS.items()}

st.sidebar.markdown('<div class="brand-tag">SMART CITY RESILIENCE · CITY DRILL</div>', unsafe_allow_html=True)
st.sidebar.title("Set up a drill")
event_label = st.sidebar.selectbox("What should happen?", list(EVENTS))
event = EVENTS[event_label]
data_source = st.sidebar.radio("Traffic data", ["Generated demo data", "Labeled public CSV"])
uploaded_csv = None
preview_frame = None
label_column = None
normal_label = None
if data_source == "Labeled public CSV":
    uploaded_csv = st.sidebar.file_uploader(
        "Upload a labeled network-flow CSV",
        type=["csv"],
        help="The app reads at most 50,000 rows for this evaluation.",
    )
    if uploaded_csv is not None:
        try:
            preview_frame, label_options = preview_csv(uploaded_csv.getvalue())
            if not label_options:
                label_options = list(preview_frame.columns)
            label_column = st.sidebar.selectbox(
                "Which column has the traffic labels?", label_options
            )
            label_values = sorted(
                preview_frame[label_column].dropna().astype(str).str.strip().unique().tolist()
            )
            likely_normal = next(
                (value for value in label_values
                 if value.casefold() in ("benign", "normal", "benign traffic", "0")),
                label_values[0],
            )
            normal_label = st.sidebar.selectbox(
                "Which label means normal traffic?",
                label_values,
                index=label_values.index(likely_normal),
            )
        except Exception as exc:
            st.sidebar.error(f"Could not read that CSV: {exc}")
with st.sidebar.expander("More options"):
    rows = st.slider(
        "Generated sample records", 100, 1000, 300, 50,
        disabled=data_source != "Generated demo data",
    )
    seed = st.number_input(
        "Repeatable run number", min_value=0, max_value=99999, value=17, step=1
    )
st.sidebar.caption("City services and recovery actions are simulated. Uploaded CSV traffic is used only for offline detector evaluation.")

st.markdown('<div class="brand-tag">INTERACTIVE CITY RESILIENCE DEMO</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero">Cyber Resilience Smart City Network</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">See how a smart city can spot trouble and keep essential services running.</div>', unsafe_allow_html=True)

st.markdown("**City service for this drill**")
with st.form("city_drill_form"):
    service_col, run_col = st.columns([0.68, 0.32])
    with service_col:
        service = st.selectbox(
            "City service for this drill",
            list(SERVICES),
            key="selected_service",
            label_visibility="collapsed",
        )
    with run_col:
        run = st.form_submit_button(
            "▶  Run city drill", type="primary", use_container_width=True
        )

st.subheader("How it works")
st.markdown("""
<div class="flow-grid">
  <div class="flow-card"><div class="flow-num">01 · TRAFFIC</div><div class="flow-icon">📡</div><div class="flow-title">Load traffic</div><div class="flow-copy">Generate mixed normal and incident records, or evaluate a labeled network-flow CSV.</div></div>
  <div class="flow-card"><div class="flow-num">02 · IDS</div><div class="flow-icon">🧠</div><div class="flow-title">Detect unusual patterns</div><div class="flow-copy">Isolation Forest learns from normal traffic and predicts which records are anomalous.</div></div>
  <div class="flow-card"><div class="flow-num">03 · RISK</div><div class="flow-icon">⚖️</div><div class="flow-title">Assess city risk</div><div class="flow-copy">Combine threat severity, service criticality, and civic impact into a transparent 0–100 score.</div></div>
  <div class="flow-card"><div class="flow-num">04 · RESPOND</div><div class="flow-icon">🛡️</div><div class="flow-title">Recover and verify</div><div class="flow-copy">Use the service tier and risk score to choose failover, safe fallback, monitoring, or isolation.</div></div>
</div>
""", unsafe_allow_html=True)

st.subheader("City-service tiers")
st.markdown("""
<div class="tier-grid">
  <div class="tier-card"><div class="tier-title">🔴 Tier 1 · Essential services</div><div class="tier-services">Hospital · Emergency Dispatch · Power Grid</div><div class="tier-action">Risk ≥ 70: isolate and fail over; otherwise use safe fallback.</div></div>
  <div class="tier-card"><div class="tier-title">🟡 Tier 2 · High-priority services</div><div class="tier-services">Traffic Control · Water Supply</div><div class="tier-action">Risk ≥ 55: use safe fallback; otherwise monitor.</div></div>
  <div class="tier-card"><div class="tier-title">🟢 Tier 3 · Lower-priority service</div><div class="tier-services">Public Display</div><div class="tier-action">Risk ≥ 55: isolate; otherwise monitor with backup on standby.</div></div>
</div>
""", unsafe_allow_html=True)

if "result" not in st.session_state or run:
    with st.spinner("Running the city drill…"):
        data, before, after, actions = run_simulation(event, service, int(rows), int(seed))
        benchmark_metrics = None
        dataset_name = "Generated demo data"
        if data_source == "Labeled public CSV" and uploaded_csv is not None and label_column and normal_label is not None:
            try:
                external_frame, benchmark_metrics = evaluate_labeled_csv(
                    preview_frame, label_column, normal_label, int(seed)
                )
                external_frame["scenario"] = event
                data = external_frame
                dataset_name = uploaded_csv.name
            except Exception as exc:
                st.error(f"CSV evaluation could not run: {exc}. Showing generated demo data instead.")
        elif data_source == "Labeled public CSV":
            st.warning("Upload a labeled CSV, choose its label column and normal label, then run the drill.")
        st.session_state.result = (data, before, after, actions, event, service, benchmark_metrics, dataset_name)
data, before, after, actions, run_event, run_service, benchmark_metrics, dataset_name = st.session_state.result
# Show the last completed run. Changing controls alone does not imply a run happened.
run_label = EVENT_LABELS[run_event]

anomalies = int(data["detected_anomaly"].sum())
ratio = anomalies / max(len(data), 1)
prediction_metrics = classification_metrics(data["is_anomaly"], data["detected_anomaly"])
if benchmark_metrics:
    result_title = "Public dataset evaluation complete"
    result_copy = (f"The detector was evaluated on {benchmark_metrics['rows_evaluated']:,} held-out rows from {escape(dataset_name)}. "
                   f"The city response panel separately demonstrates the selected {run_label.lower()} policy for {run_service}.")
    result_pill = "Labeled CSV · held-out evaluation"
elif run_event == "Normal":
    result_title = "Routine day simulated"
    result_copy = f"The detector marked {anomalies} of {len(data)} records as unusual. No service was isolated in this normal-day drill."
    result_pill = "No response action taken"
elif actions["critical_services_reachable"]:
    result_title = f"{run_label} drill complete"
    if actions["response_taken"]:
        result_copy = (f"{run_label} activity was simulated for {run_service}. The Tier {actions['tier']} "
                       f"plan used {actions['response_mode'].lower()}, then checked critical-service connectivity.")
        result_pill = "Recovery check passed"
    else:
        result_copy = (f"{run_label} activity was simulated for {run_service}. Risk is below its response "
                       "threshold, so the service remains in place for monitoring.")
        result_pill = "Monitor; no disruption"
else:
    result_title = f"{run_label} drill needs attention"
    result_copy = f"The Tier {actions['tier']} plan used {actions['response_mode'].lower()} for {run_service}, but the critical-service connectivity check needs review."
    result_pill = "Recovery check needs review"
st.markdown(f'<div class="result-box"><div class="result-title">{result_title}</div><div class="result-copy">{result_copy}</div><span class="result-pill">{result_pill}</span></div>', unsafe_allow_html=True)

m1, m2, m3 = st.columns(3, gap="medium")
m1.metric("Records evaluated", f"{len(data):,}", dataset_name if benchmark_metrics else None)
m2.metric("Isolation Forest flags", f"{anomalies:,}", f"{ratio:.1%} predicted anomalous")
m3.metric("Risk score", f"{actions['risk_score']}/100", actions["risk_assessment"]["threat_severity"] + " threat")

ids_tab, risk_tab, overview_tab, healing_tab = st.tabs(
    ["Intrusion Detection System", "Risk Assessment", "Network Overview", "Self-Healing"]
)

with overview_tab:
    st.subheader("City services")
    st.caption("Illustrated services with clear status for the city service and its backup. The drill target is marked.")
    icons = {"Hospital": "🏥", "Emergency Dispatch": "🚑", "Traffic Control": "🚦", "Water Supply": "💧", "Power Grid": "⚡", "Public Display": "📣"}
    service_cards = []
    for name, service_details in SERVICES.items():
        primary = after.nodes[name]
        backup = after.nodes[name + " Backup"]
        is_target = name == run_service and bool(actions.get("response_taken"))
        status = primary.get("status", "Active")
        primary_text = ("Isolated for drill" if primary.get("isolated") else
                        "Safe fallback mode" if status.startswith("Safe fallback") else "Running normally")
        primary_class = ("status-alert" if primary.get("isolated") else
                         "status-fallback" if status.startswith("Safe fallback") else "status-ok")
        backup_text = "Active and carrying service" if backup.get("role") == "active-backup" else "Ready on standby"
        tier_badge = f"TIER {service_details['tier']}" + (" · DRILL TARGET" if is_target else "")
        service_cards.append(
            f'<div class="service-card"><div class="service-head">'
            f'<div class="service-icon">{icons[name]}</div>'
            f'<div class="service-title-wrap"><div class="service-name">{name}</div>'
            f'<div class="service-kind">{service_details["criticality"]} priority service</div></div>'
            f'<span class="tier-badge">{tier_badge}</span></div>'
            f'<div class="service-states">'
            f'<div class="state-box"><div class="state-label">City service</div><div class="state-value {primary_class}">{primary_text}</div></div>'
            f'<div class="state-box"><div class="state-label">Backup unit</div><div class="state-value status-ok">{backup_text}</div></div>'
            f'</div></div>'
        )
    st.markdown('<div class="service-grid">' + ''.join(service_cards) + '</div>', unsafe_allow_html=True)

with ids_tab:
    st.subheader("Isolation Forest results")
    st.caption("Flags and percentages below come from Isolation Forest predictions. Ground-truth labels are used only for evaluation metrics.")
    metrics_cols = st.columns(5)
    metrics_cols[0].metric("Normal records", f"{prediction_metrics['normal_records']:,}")
    metrics_cols[1].metric("Anomalous records", f"{prediction_metrics['anomalous_records']:,}")
    detection_rate = prediction_metrics["detection_rate"]
    false_positive_rate = prediction_metrics["false_positive_rate"]
    metrics_cols[2].metric("Detection rate", "N/A" if detection_rate is None else f"{detection_rate:.1%}")
    metrics_cols[3].metric("False positive rate", "N/A" if false_positive_rate is None else f"{false_positive_rate:.1%}")
    metrics_cols[4].metric("Predicted anomalies", f"{anomalies:,}", f"{ratio:.1%} of evaluated rows")
    if benchmark_metrics:
        st.caption(f"Source: {dataset_name}. The model trained on normal-labeled rows and was evaluated on a held-out, stratified sample. Labels identify known dataset classes; a model flag is still not proof of a real-time attack.")
        st.subheader("Held-out evaluation")
        eval_cols = st.columns(5)
        eval_cols[0].metric("Accuracy", f"{benchmark_metrics['accuracy']:.1%}")
        eval_cols[1].metric("Precision", f"{benchmark_metrics['precision']:.1%}")
        eval_cols[2].metric("Recall", f"{benchmark_metrics['recall']:.1%}")
        eval_cols[3].metric("False alarms", f"{benchmark_metrics['false_positives']:,}")
        eval_cols[4].metric("Missed attacks", f"{benchmark_metrics['false_negatives']:,}")
        st.caption(f"{benchmark_metrics['rows_loaded']:,} rows loaded · {benchmark_metrics['rows_evaluated']:,} held out · {benchmark_metrics['feature_count']} numeric features · Normal label: {benchmark_metrics['normal_label']}")
        matrix = pd.DataFrame(
            [[benchmark_metrics["true_negatives"], benchmark_metrics["false_positives"]],
             [benchmark_metrics["false_negatives"], benchmark_metrics["true_positives"]]],
            index=["Actual normal", "Actual attack"], columns=["Predicted normal", "Predicted attack"]
        )
        st.dataframe(matrix, use_container_width=True)
    else:
        st.caption("Generated traffic includes normal and scenario-labeled incident records, except the Normal scenario. A detector flag is a model result, not proof of an attack.")
    chart, table = st.columns([1.2, 1], gap="large")
    with chart:
        hist = go.Figure()
        for label, color in [("Normal", "#60d7c2"), ("Anomaly", "#ff8b5e")]:
            part = data[data.detection == label]
            if not part.empty:
                hist.add_trace(go.Histogram(x=part.anomaly_score, name=label, marker_color=color, opacity=.78, nbinsx=32))
        chart_font_color = "#263547" if st.session_state["light_theme"] else "#b5c7dc"
        hist.update_layout(
            barmode="overlay",
            height=330,
            margin=dict(l=5, r=5, t=15, b=5),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color=chart_font_color),
            xaxis_title="Pattern score",
            yaxis_title="Records",
        )
        st.plotly_chart(hist, use_container_width=True)
    with table:
        summary = data.groupby("detection").size().rename("Records").reset_index().rename(columns={"detection": "Detector result"})
        st.dataframe(summary, hide_index=True, use_container_width=True)
        download_name = "labeled_benchmark_evaluation.csv" if benchmark_metrics else "smart_city_demo_records.csv"
        st.download_button("Download evaluation rows" if benchmark_metrics else "Download demo records", data.to_csv(index=False).encode("utf-8"), download_name, "text/csv")
    with st.expander("View sample records"):
        st.dataframe(data.head(100), use_container_width=True, hide_index=True)

with risk_tab:
    risk = actions["risk_assessment"]
    st.subheader("Transparent risk assessment")
    st.caption("Risk = 50% threat severity + 25% service criticality + 25% civic impact. Each factor is scored from 0 to 100.")
    risk_cols = st.columns(4)
    risk_cols[0].metric("Threat severity", f"{risk['threat_severity_score']}/100", risk["threat_severity"])
    risk_cols[1].metric("Service criticality", f"{risk['service_criticality_score']}/100", f"Tier {actions['tier']}")
    risk_cols[2].metric("Civic impact", f"{risk['civic_impact_score']}/100", run_service)
    risk_cols[3].metric("Combined risk", f"{risk['risk_score']}/100")
    st.progress(risk["risk_score"] / 100)
    st.write(
        f"Calculation: 0.50 × {risk['threat_severity_score']} + "
        f"0.25 × {risk['service_criticality_score']} + "
        f"0.25 × {risk['civic_impact_score']} = **{risk['risk_score']}/100**."
    )
    st.write(f"**Decision:** {actions['response_mode']} — {actions['response_detail']}")
    st.caption("The selected simulated incident supplies threat severity. IDS predictions are evaluated separately and do not automatically trigger recovery.")
    if run_event == "Normal":
        st.info("Normal-day runs have no active threat, so no recovery action is taken; the score still shows the selected service's baseline criticality and civic impact.")
    st.caption("Illustrative classroom score; weights and service impact ratings are documented in README.md, not a validated operational risk standard.")

with healing_tab:
    st.subheader("Tier-aware self-healing")
    st.markdown(f"**Scenario:** {run_label} &nbsp; · &nbsp; **Service:** {run_service} &nbsp; · &nbsp; **Risk:** {actions['risk_score']}/100")
    st.markdown(f"**Tier {actions['tier']} response: {actions['response_mode']}**")
    st.write(actions["response_detail"])
    if actions.get("response_taken"):
        if actions["response_mode"] == "Failover":
            st.success("The affected service was isolated, its backup activated, and service links rerouted.")
        elif actions["response_mode"] == "Safe fallback":
            st.info(f"{run_service} remains available in a reduced safe mode.")
        else:
            st.warning(f"{run_service} was isolated; its backup remains on standby.")
    elif run_event == "Normal":
        st.success("No service isolation or rerouting was needed for this normal-day drill.")
    else:
        st.info("The incident risk is below the selected tier's response threshold; monitoring continues without disruption.")
    if run_event != "Normal":
        if actions["critical_services_reachable"]:
            st.markdown("### ✅ Recovery verification passed")
            st.write("Critical city services remain connected in this simulated network.")
        else:
            st.warning("The critical-service connectivity check needs review.")
    st.caption("The simulation handles one incident and one target service per run. It does not model concurrent incident queues.")

st.caption("Cyber Resilience Smart City Network · Fictional services · Synthetic or locally evaluated labeled traffic")
