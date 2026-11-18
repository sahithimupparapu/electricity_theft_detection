
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Electricity Analytics",
    page_icon="⚡",
    layout="wide"
)

# ---------- DESIGN ----------
st.markdown("""
<style>
.stApp {
    background-color: #f3f7fc;
}
[data-testid="stSidebar"] {
    background-color: #102b46;
}
[data-testid="stSidebar"] * {
    color: white !important;
}
h1, h2, h3 {
    color: #123456;
}
.metric-card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    border-left: 5px solid #1687d9;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
}
.hero {
    background: linear-gradient(120deg,#102b46,#176da5);
    padding: 35px;
    border-radius: 16px;
    color: white;
}
.hero h1, .hero p {
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
st.sidebar.title("⚡ POWER ANALYTICS")
st.sidebar.caption("Electricity Intelligence System")

page = st.sidebar.radio(
    "NAVIGATION",
    [
        "Home",
        "Project Overview",
        "Dataset",
        "Consumption Analysis",
        "Anomaly Detection",
        "Comparison",
        "Conclusion & References"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Upload Dataset")

uploaded = st.sidebar.file_uploader(
    "Choose electricity CSV",
    type=["csv"]
)

# ---------- DATA ----------
if uploaded is None:
    st.markdown("""
    <div class="hero">
        <h1>Electricity Consumption Analytics</h1>
        <p>Smart data analysis and statistical anomaly detection</p>
    </div>
    """, unsafe_allow_html=True)

    st.info("Upload your electricity analysis CSV from the sidebar to access the dashboard.")
    st.stop()

try:
    df = pd.read_csv(uploaded)
except Exception as e:
    st.error(f"Could not read the CSV: {e}")
    st.stop()

required = [
    "FLAG", "Average_Consumption",
    "Zero_Consumption_Percentage",
    "IQR_Anomaly", "Z_Anomaly"
]

missing = [c for c in required if c not in df.columns]

if missing:
    st.error("Missing columns: " + ", ".join(missing))
    st.stop()

df["FLAG"] = pd.to_numeric(df["FLAG"], errors="coerce")
df["Average_Consumption"] = pd.to_numeric(
    df["Average_Consumption"], errors="coerce"
)
df["Zero_Consumption_Percentage"] = pd.to_numeric(
    df["Zero_Consumption_Percentage"], errors="coerce"
)

def convert_boolean(series):
    return (
        series.astype(str).str.strip().str.lower()
        .map({
            "true": True,
            "false": False,
            "1": True,
            "0": False
        })
    )

df["IQR_Anomaly"] = convert_boolean(df["IQR_Anomaly"])
df["Z_Anomaly"] = convert_boolean(df["Z_Anomaly"])

df = df.dropna(subset=required).copy()

if df.empty:
    st.error("No valid records found in this dataset.")
    st.stop()

total = len(df)
iqr_count = int(df["IQR_Anomaly"].sum())
z_count = int(df["Z_Anomaly"].sum())
flag_count = int((df["FLAG"] == 1).sum())

# ---------- HOME ----------
if page == "Home":

    st.markdown("""
    <div class="hero">
        <h1>⚡ Electricity Consumption & Theft Detection</h1>
        <p>Intelligent analysis of electricity consumption
        patterns using statistical anomaly detection.</p>
    </div>
    """, unsafe_allow_html=True)
                	
    st.write("")
    st.subheader("Dashboard Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Consumers", f"{total:,}")
    c2.metric("IQR Anomalies", f"{iqr_count:,}")
    c3.metric("Z-score Anomalies", f"{z_count:,}")
    c4.metric("Supplied FLAG = 1", f"{flag_count:,}")

    st.markdown("---")
    st.subheader("About the Project")

    st.write("""
    Electricity theft and unusual consumption patterns can
    create financial losses and affect power distribution systems.

    This project analyses smart meter electricity data and uses
    statistical methods to identify unusual consumption behaviour.
    """)

    a, b = st.columns(2)

    with a:
        st.markdown("### Technologies Used")
        st.write("- Python")
        st.write("- Pandas and NumPy")
        st.write("- Matplotlib and Plotly")
        st.write("- Streamlit")

    with b:
        st.markdown("### Detection Techniques")
        st.write("- Interquartile Range (IQR)")
        st.write("- Z-score method")
        st.write("- Statistical comparison")

# ---------- PROJECT OVERVIEW ----------
elif page == "Project Overview":

    st.title("Project Overview")
    st.subheader("Abstract")

    st.write("""
    This project focuses on analysing electricity consumption
    data to identify unusual patterns that may indicate abnormal
    usage or potential non-technical losses.

    Statistical anomaly detection techniques, including the
    Interquartile Range (IQR) and Z-score methods, are used
    to examine consumer-level electricity consumption.

    The results are presented through an interactive dashboard
    to support data exploration and further investigation.
    """)

    st.subheader("Objectives")

    objectives = [
        "Analyse electricity consumption patterns.",
        "Prepare and examine smart meter data.",
        "Identify unusual consumption using IQR.",
        "Identify extreme values using Z-score.",
        "Visualise and compare detection results."
    ]

    for item in objectives:
        st.markdown("✓ " + item)

    st.subheader("Methodology")

    steps = [
        "Data Collection",
        "Data Preprocessing",
        "Feature Extraction",
        "Anomaly Detection",
        "Result Analysis",
        "Data Visualization"
    ]

    st.write(" → ".join(steps))

# ---------- DATASET ----------
elif page == "Dataset":

    st.title("Dataset Explorer")

    c1, c2 = st.columns(2)
    c1.metric("Total Records", f"{total:,}")
    c2.metric("Total Columns", f"{df.shape[1]}")

    st.subheader("Dataset Preview")
    st.dataframe(df.head(100), use_container_width=True)

    st.subheader("Statistical Summary")
    st.dataframe(df.describe(), use_container_width=True)

    st.download_button(
        "Download Dataset",
        df.to_csv(index=False),
        "electricity_dataset.csv",
        "text/csv"
    )

# ---------- CONSUMPTION ----------
elif page == "Consumption Analysis":

    st.title("Electricity Consumption Analysis")

    values = df["Average_Consumption"].clip(lower=0)

    st.subheader("Consumption Distribution")

    fig = px.histogram(
        x=np.log1p(values),
        nbins=50,
        labels={"x": "log(1 + Average Consumption)"},
        title="Distribution of Average Consumption"
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Consumption by Supplied FLAG")

    box = df.copy()
    box["Log_Consumption"] = np.log1p(
        box["Average_Consumption"].clip(lower=0)
    )

    fig = px.box(
        box,
        x="FLAG",
        y="Log_Consumption",
        points=False,
        title="Consumption Comparison by FLAG",
        labels={
            "FLAG": "Supplied FLAG",
            "Log_Consumption": "log(1 + Average Consumption)"
        }
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Zero Consumption Percentage")

    zero = df.groupby("FLAG")[
        "Zero_Consumption_Percentage"
    ].mean().reset_index()

    fig = px.bar(
        zero,
        x="FLAG",
        y="Zero_Consumption_Percentage",
        text_auto=".2f",
        title="Mean Zero-Consumption Percentage by FLAG"
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# ---------- ANOMALY ----------
elif page == "Anomaly Detection":

    st.title("Anomaly Detection")

    c1, c2 = st.columns(2)
    c1.metric("IQR Detected", f"{iqr_count:,}")
    c2.metric("Z-score Detected", f"{z_count:,}")

    fig = px.bar(
        x=["IQR", "Z-score"],
        y=[iqr_count, z_count],
        text=[iqr_count, z_count],
        title="Anomaly Counts by Detection Method",
        labels={"x": "Method", "y": "Number of Consumers"}
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    method = st.selectbox(
        "Select Detection Method",
        ["IQR", "Z-score"]
    )

    col = "IQR_Anomaly" if method == "IQR" else "Z_Anomaly"
    anomalies = df[df[col] == True]

    st.subheader(f"{method} Anomaly Records")
    st.write(f"Total detected: {len(anomalies):,}")

    st.dataframe(anomalies, use_container_width=True)

    st.download_button(
        "Download Anomaly Records",
        anomalies.to_csv(index=False),
        f"{method.lower()}_anomalies.csv",
        "text/csv"
    )

# ---------- COMPARISON ----------
elif page == "Comparison":

    st.title("Results & Comparison")

    grouped = df.groupby("FLAG").agg(
        IQR=("IQR_Anomaly", "sum"),
        Z_score=("Z_Anomaly", "sum")
    ).reset_index()

    st.subheader("Anomalies by Supplied FLAG")

    fig = px.bar(
        grouped,
        x="FLAG",
        y=["IQR", "Z_score"],
        barmode="group",
        title="Comparison of Detection Methods"
    )

    fig.update_layout(template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(grouped, use_container_width=True)

    overlap = int(
        (df["IQR_Anomaly"] & df["Z_Anomaly"]).sum()
    )

    unique = int(
        (df["IQR_Anomaly"] | df["Z_Anomaly"]).sum()
    )

    c1, c2 = st.columns(2)
    c1.metric("Overlapping Anomalies", f"{overlap:,}")
    c2.metric("Unique Combined Anomalies", f"{unique:,}")

    st.info("""
    The supplied FLAG values are used as comparison labels.
    A statistical anomaly does not independently confirm
    electricity theft.
    """)

# ---------- CONCLUSION ----------
elif page == "Conclusion & References":

    st.title("Conclusion")

    st.write("""
    The project analyses electricity consumption patterns using
    statistical anomaly detection techniques.

    The IQR and Z-score methods identify unusual consumer-level
    readings. The results provide a basis for further examination
    of abnormal electricity consumption.

    Statistical anomalies should be investigated further before
    being classified as confirmed electricity theft.
    """)

    st.subheader("Key Findings")

    st.write(f"- Total valid consumers: {total:,}")
    st.write(f"- IQR anomalies: {iqr_count:,}")
    st.write(f"- Z-score anomalies: {z_count:,}")

    st.markdown("---")

    st.subheader("References")

    references = [
        "Oprea et al. (2021). Anomaly Detection with Machine Learning Algorithms and Big Data in Electricity Consumption. Sustainability.",
        "Himeur et al. (2021). Artificial Intelligence Based Anomaly Detection of Energy Consumption in Buildings: A Review. Applied Energy.",
        "Zangrando et al. (2022). Anomaly detection in quasi-periodic energy consumption data series. Energy Informatics.",
        "Villar-Rodriguez et al. (2017). Detection of non-technical losses in smart meter data. Energy."
    ]

    for ref in references:
        st.markdown("- " + ref)

st.sidebar.markdown("---")
st.sidebar.caption("Electricity Analytics | Academic Project")
