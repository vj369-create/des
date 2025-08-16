import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

st.set_page_config(page_title="Industrial Dashboard", layout="wide")

st.title("📊 Industrial Dashboard")

# File uploader
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

# Date picker
selected_date = st.date_input("Select a date")

if uploaded_file is not None:
    # Load Excel
    df = pd.read_excel(uploaded_file)

    # Try to parse a 'date' column if exists
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        filtered = df[df["date"].dt.date == selected_date]
    else:
        filtered = df  # fallback if no date column

    st.subheader("📈 Data Preview")
    st.write(filtered.head())

    # Example plot
    if not filtered.empty:
        fig, ax = plt.subplots(figsize=(8, 4))
        filtered.iloc[:, 1].plot(kind="line", ax=ax, marker="o")
        ax.set_title(f"Dashboard for {selected_date}")
        ax.set_ylabel("Value")
        st.pyplot(fig)
    else:
        st.warning("No data available for this date.")

# Inject PWA manifest + service worker
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register("service-worker.js");
      }
    </script>
    """, unsafe_allow_html=True
)
