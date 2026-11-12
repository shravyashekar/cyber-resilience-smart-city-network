"""Cyber Resilience Smart City Network: a fictional city drill demonstration."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from benchmark_data import evaluate_labeled_csv, preview_csv
from network_topology import SERVICES
from simulation import run_simulation

st.set_page_config(page_title="Cyber Resilience Smart City Network", page_icon="🛡️", layout="wide")
st.markdown("""
<style>
html, body, [class*="css"] {font-family:Segoe UI,Arial,sans-serif;background:#07111f;color:#edf4ff}
.stApp {background:radial-gradient(ellipse at 8% 0%,#122b45 0%,#07111f 58%)}
[data-testid="stSidebar"] {background:#0b1928;border-right:1px solid #23364d}
.block-container {padding-top:2.2rem;max-width:1400px}
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
div.stButton > button[kind="primary"] {background:linear-gradient(90deg,#e94f61,#ff775f);border:0;border-radius:10px;font-weight:700;min-height:46px}
div.stButton > button[kind="primary"]:hover {border:0;filter:brightness(1.08)}
@media(max-width:900px){.flow-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.hero{font-size:34px}}
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
service = st.sidebar.selectbox("City service", list(SERVICES))
data_source = st.sidebar.radio("Traffic data", ["Generated demo data", "Labeled public CSV"])
uploaded_csv = None
preview_frame = None
label_column = None
normal_label = None
if data_source == "Labeled public CSV":
    uploaded_csv = st.sidebar.file_uploader("Upload a Kaggle CSV", type=["csv"], help="Use a labeled network-flow CSV. The app reads at most 50,000 rows for this demo.")
    if uploaded_csv is not None:
        try:
            preview_frame, label_options = preview_csv(uploaded_csv.getvalue())
            if not label_options:
                label_options = list(preview_frame.columns)
            label_column = st.sidebar.selectbox("Which column has the traffic labels?", label_options)
            label_values = sorted(preview_frame[label_column].dropna().astype(str).str.strip().unique().tolist())
            likely_normal = next((value for value in label_values if value.casefold() in ("benign", "normal", "benign traffic", "0")), label_values[0])
            normal_label = st.sidebar.selectbox("Which label means normal traffic?", label_values, index=label_values.index(likely_normal))
        except Exception as exc:
            st.sidebar.error(f"Could not read that CSV: {exc}")
with st.sidebar.expander("More options"):
    rows = st.slider("Generated sample records", 100, 1000, 300, 50, disabled=data_source != "Generated demo data")
    seed = st.number_input("Repeatable run number", min_value=0, max_value=99999, value=17, step=1)
run = st.sidebar.button("▶  Run city drill", type="primary", use_container_width=True)
st.sidebar.caption("City services and response are simulated. A labeled CSV can supply the traffic for detector evaluation.")

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

st.markdown('<div class="brand-tag">INTERACTIVE CITY RESILIENCE DEMO</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero">Cyber Resilience Smart City Network</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">See how a smart city can spot trouble and keep essential services running.</div>', unsafe_allow_html=True)

st.subheader("How it works")
if benchmark_metrics:
    input_copy = f"Use up to {benchmark_metrics['rows_loaded']:,} labeled rows from {dataset_name}."
    detection_copy = "Train on normal-labeled rows, then score a held-out sample."
else:
    input_copy = f"Generate pretend {run_label.lower()} activity for {run_service}."
    detection_copy = "Compare the records with generated normal traffic and flag unusual patterns."
protect_copy = {
    "Failover": f"Tier 1: isolate {run_service} and switch its service links to a backup.",
    "Safe fallback": f"Tier 2: keep {run_service} available in a reduced safe mode.",
    "Isolation": f"Tier 3: isolate {run_service}; leave its backup on standby.",
    "No action": "Normal-day drill: no isolation or backup switch is needed.",
}.get(actions.get("response_mode"), "Apply a response based on the selected service tier.")
check_copy = ("Check that important city services remain connected."
              if run_event != "Normal" else "Confirm that all services stay active.")
st.markdown(f"""
<div class="flow-grid">
  <div class="flow-card"><div class="flow-num">01 · INPUT</div><div class="flow-icon">📡</div><div class="flow-title">Load traffic</div><div class="flow-copy">{input_copy}</div></div>
  <div class="flow-card"><div class="flow-num">02 · SCORE</div><div class="flow-icon">🧠</div><div class="flow-title">Score traffic patterns</div><div class="flow-copy">Isolation Forest: {detection_copy}</div></div>
  <div class="flow-card"><div class="flow-num">03 · RESPOND</div><div class="flow-icon">🛡️</div><div class="flow-title">Apply the tier plan</div><div class="flow-copy">{protect_copy}</div></div>
  <div class="flow-card"><div class="flow-num">04 · VERIFY</div><div class="flow-icon">✅</div><div class="flow-title">Check city continuity</div><div class="flow-copy">{check_copy}</div></div>
</div>
""", unsafe_allow_html=True)
st.caption("In this demo, the chosen scenario and service tier select the response. The detector’s score is displayed for analysis; it does not trigger the response automatically.")

st.subheader("Three city-service tiers")
st.markdown("""
<div class="tier-grid">
  <div class="tier-card"><div class="tier-title">🔴 Tier 1 · Keep essential services running</div><div class="tier-services">Hospital · Emergency Dispatch · Power Grid</div><div class="tier-action">Response: isolate affected node, switch to active backup</div></div>
  <div class="tier-card"><div class="tier-title">🟡 Tier 2 · Continue in safe mode</div><div class="tier-services">Traffic Control · Water Supply</div><div class="tier-action">Response: use reduced safe fallback mode</div></div>
  <div class="tier-card"><div class="tier-title">🟢 Tier 3 · Contain lower-priority service</div><div class="tier-services">Public Display</div><div class="tier-action">Response: isolate; leave backup on standby</div></div>
</div>
""", unsafe_allow_html=True)

anomalies = int(data["detected_anomaly"].sum())
ratio = anomalies / max(len(data), 1)
if benchmark_metrics:
    result_title = "Public dataset evaluation complete"
    result_copy = (f"The detector was evaluated on {benchmark_metrics['rows_evaluated']:,} held-out rows from {dataset_name}. "
                   f"The city response panel separately demonstrates the selected {run_label.lower()} policy for {run_service}.")
    result_pill = "Labeled CSV · held-out evaluation"
elif run_event == "Normal":
    result_title = "Routine day simulated"
    result_copy = f"The detector marked {anomalies} of {len(data)} records as unusual. No service was isolated in this normal-day drill."
    result_pill = "No response action taken"
elif actions["critical_services_reachable"]:
    result_title = f"{run_label} drill complete"
    result_copy = f"{run_label} activity was simulated for {run_service}. The Tier {actions['tier']} plan used {actions['response_mode'].lower()}, then checked that critical services remain reachable."
    result_pill = "Recovery check passed"
else:
    result_title = f"{run_label} drill needs attention"
    result_copy = f"The Tier {actions['tier']} plan used {actions['response_mode'].lower()} for {run_service}, but the critical-service connectivity check needs review."
    result_pill = "Recovery check needs review"
st.markdown(f'<div class="result-box"><div class="result-title">{result_title}</div><div class="result-copy">{result_copy}</div><span class="result-pill">{result_pill}</span></div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4, gap="medium")
m1.metric("Rows evaluated" if benchmark_metrics else "Records created", f"{len(data):,}", dataset_name if benchmark_metrics else "made for this demo")
m2.metric("Unusual patterns", f"{anomalies:,}", f"{ratio:.0%} of records")
m3.metric("Response plan", actions.get("response_mode", "None"), f"Tier {actions.get('tier', '—')}")
m4.metric("Civic impact score", str(actions.get("impact_score", "—")), "estimated demo score / 100")

overview, traffic_tab = st.tabs(["City view", "Traffic details"])

with overview:
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

    st.subheader("What the city did")
    st.markdown(f"**Drill:** {run_label} &nbsp; · &nbsp; **Service:** {run_service}")
    if actions.get("response_taken"):
        st.markdown(f"**Tier {actions['tier']} response: {actions['response_mode']}**")
        if actions["response_mode"] == "Failover":
            st.success("The affected device was isolated and its backup is active.")
        elif actions["response_mode"] == "Safe fallback":
            st.info(f"{run_service} continues in a reduced, safer operating mode.")
        else:
            st.warning(f"{run_service} was isolated; its backup remains on standby.")
        if actions["critical_services_reachable"]:
            st.markdown("### ✅ City check passed")
            st.write("Critical city services remain connected in this simulated network.")
        else:
            st.warning("The critical-service connectivity check needs review.")
    else:
        st.success("No service isolation or rerouting was needed for this normal-day drill.")
    st.caption("This is a pretend response in a fictional network, not a change to a real service.")

with traffic_tab:
    st.subheader("Traffic details")
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
        st.caption("Generated demo data: the detector marks records that look different from generated normal activity. A flag is a model result, not proof of an attack.")
    chart, table = st.columns([1.2, 1], gap="large")
    with chart:
        hist = go.Figure()
        for label, color in [("Normal", "#60d7c2"), ("Anomaly", "#ff8b5e")]:
            part = data[data.detection == label]
            if not part.empty:
                hist.add_trace(go.Histogram(x=part.anomaly_score, name=label, marker_color=color, opacity=.78, nbinsx=32))
        hist.update_layout(barmode="overlay", height=330, margin=dict(l=5, r=5, t=15, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#b5c7dc"), xaxis_title="Pattern score", yaxis_title="Records")
        st.plotly_chart(hist, use_container_width=True)
    with table:
        summary = data.groupby("detection").size().rename("Records").reset_index().rename(columns={"detection": "Detector result"})
        st.dataframe(summary, hide_index=True, use_container_width=True)
        download_name = "labeled_benchmark_evaluation.csv" if benchmark_metrics else "smart_city_demo_records.csv"
        st.download_button("Download evaluation rows" if benchmark_metrics else "Download demo records", data.to_csv(index=False).encode("utf-8"), download_name, "text/csv")
    with st.expander("View sample records"):
        st.dataframe(data.head(100), use_container_width=True, hide_index=True)

st.caption("Cyber Resilience Smart City Network · Fictional services · Generated traffic only")
