import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ---- PWA: manifest + service worker registration (does not change app logic) ----
st.markdown(
    """
    <link rel="manifest" href="manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', () => {
          navigator.serviceWorker.register('./service-worker.js').catch(e=>console.log('SW registration failed', e));
        });
      }
    </script>
    """,
    unsafe_allow_html=True
)

plt.style.use('dark_background')
sns.set_palette("husl")

COLORS = {
    'primary': '#00D4FF',
    'secondary': '#FF6B6B',
    'accent': '#4ECDC4',
    'warning': '#FFE66D',
    'success': '#95E1D3',
    'background': '#1E1E1E',
    'surface': '#2D2D2D',
    'text': '#FFFFFF'
}

st.set_page_config(layout="wide")

# Display logo centered
st.image("logo.png", width=200)

# Centered multiline title as originally written
st.markdown(
    """
    <div style="text-align: center; color: #00D4FF; line-height: 1.3; margin-top: -20px; margin-bottom: 20px;">
        <h1 style="margin-bottom: 5px;">MAGNUM TECHNOLOGY CENTRE</h1>
        <h3 style="margin-top: 0; margin-bottom: 5px;">DESANDER</h3>
    </div>
    """,
    unsafe_allow_html=True
)

# 📘 User Manual Section
with st.expander("📘 User Manual - How to Use This App", expanded=True):
    st.markdown(
        """
        ### 🔧 Step-by-Step Instructions:
        1. **Obtain Your Data File**  
           - Download the Excel log file from your **PLC (Programmable Logic Controller)** or data logging system.  
           - Ensure the file is in `.xlsx` format and contains columns like `Date`, `time`, `Scaled mass (kg)`, and `Pressure (psi)`.

        2. **Upload the File**  
           - Use the **file uploader** below to upload your Excel sheet.  
           - After uploading, the app will read the data and automatically detect available dates.

        3. **Select the Date**  
           - Use the dropdown to select a specific date to analyze.  
           - The app filters and visualizes data corresponding to your chosen date.

        4. **Explore Visualizations and Insights**  
           - View real-time trends, bar charts, and distributions for scaled mass and pressure.  
           - Understand how pressure and mass change over time.

        5. **Review Summary Statistics**  
           - Scroll down to see metrics like average, max, standard deviation, and change rates.

        > ⚠️ *Ensure your Excel data structure matches the expected format to avoid analysis issues.*
        """,
        unsafe_allow_html=True
    )

# File uploader
uploaded_file = st.file_uploader("📁 Upload an Excel file", type=["xlsx"])

if uploaded_file is None:
    st.warning("⚠️ Please upload a file to continue.")
    st.stop()

@st.cache_data
def load_data(file):
    return pd.read_excel(file)

df = load_data(uploaded_file)

# Parse date and extract unique
df['date_parsed'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
unique_dates = sorted(df['date_parsed'].dropna().dt.date.unique())

# Date selector
selected_date = st.selectbox("📅 Select a date to view:", unique_dates)

# Data preparation
def prepare_data(df, selected_date):
    selected_datetime = pd.to_datetime(selected_date)
    filtered_df = df[df['date_parsed'] == selected_datetime].copy()
    if filtered_df.empty:
        return None
    filtered_df = filtered_df[filtered_df['Scaled mass (kg)'] >= 0]
    min_time_sec = filtered_df['time'].min()
    filtered_df['shifted_time_sec'] = filtered_df['time'] - min_time_sec
    base_time = pd.Timestamp.combine(selected_datetime, pd.to_datetime("09:00:00").time())
    filtered_df['datetime'] = base_time + pd.to_timedelta(filtered_df['shifted_time_sec'], unit='s')
    filtered_df['time_bin'] = filtered_df['datetime'].dt.floor('10min')
    agg_df = filtered_df.groupby('time_bin').agg({
        'Scaled mass (kg)': 'mean',
        'Pressure (psi)': 'mean'
    }).reset_index()
    agg_df['Scaled mass change'] = agg_df['Scaled mass (kg)'].diff().fillna(0)
    agg_df['Pressure change'] = agg_df['Pressure (psi)'].diff().fillna(0)
    agg_df['Mass velocity'] = agg_df['Scaled mass change'] / 10
    agg_df['Pressure velocity'] = agg_df['Pressure change'] / 10
    return agg_df

agg_df = prepare_data(df, selected_date)

if agg_df is None:
    st.error("❌ No data available for the selected date.")
    st.stop()

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("📊 Avg Mass", f"{agg_df['Scaled mass (kg)'].mean():.1f} kg")
col2.metric("📈 Max Mass", f"{agg_df['Scaled mass (kg)'].max():.1f} kg")
col3.metric("⚡ Avg Pressure", f"{agg_df['Pressure (psi)'].mean():.1f} psi")
col4.metric("🔺 Max Pressure", f"{agg_df['Pressure (psi)'].max():.1f} psi")

agg_df['time_str'] = agg_df['time_bin'].dt.strftime('%H:%M')

# Line chart
fig1, ax1 = plt.subplots(figsize=(12, 5))
ax1.plot(agg_df['time_str'], agg_df['Scaled mass (kg)'], label='Scaled Mass (kg)', color=COLORS['primary'], marker='o')
ax1.set_xlabel("Time (HH:MM)")
ax1.set_ylabel("Scaled Mass (kg)", color=COLORS['primary'])
ax1.tick_params(axis='y', labelcolor=COLORS['primary'])
ax1.set_xticks(agg_df.index[::max(1, len(agg_df)//10)])
ax1.set_xticklabels(agg_df['time_str'][::max(1, len(agg_df)//10)], rotation=45)

ax2 = ax1.twinx()
ax2.plot(agg_df['time_str'], agg_df['Pressure (psi)'], label='Pressure (psi)', color=COLORS['secondary'], marker='^')
ax2.set_ylabel("Pressure (psi)", color=COLORS['secondary'])
ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])

ax1.set_title("📈 Real-Time Trends")
fig1.tight_layout()
st.pyplot(fig1)

# Bar chart
fig2, ax3 = plt.subplots(figsize=(12, 5))
x = np.arange(len(agg_df))
width = 0.35
ax3.bar(x - width/2, agg_df['Scaled mass change'], width, label='Mass Change', color=COLORS['accent'])
ax4 = ax3.twinx()
ax4.bar(x + width/2, agg_df['Pressure change'], width, label='Pressure Change', color=COLORS['warning'])

ax3.set_xlabel("Time (HH:MM)")
ax3.set_ylabel("Mass Change (kg)", color=COLORS['accent'])
ax4.set_ylabel("Pressure Change (psi)", color=COLORS['warning'])
ax3.set_xticks(x[::max(1, len(x)//10)])
ax3.set_xticklabels(agg_df['time_str'][::max(1, len(x)//10)], rotation=45)

fig2.suptitle("📊 Pressure and Scaled Mass Relationship wrt time")
fig2.tight_layout()
st.pyplot(fig2)

# Histogram
fig3, (ax5, ax6) = plt.subplots(1, 2, figsize=(16, 5))
sns.histplot(agg_df['Scaled mass (kg)'], kde=True, ax=ax5, color=COLORS['primary'])
ax5.set_title("📊 Scaled Mass Distribution")
ax5.set_xlabel("Scaled Mass (kg)")
sns.histplot(agg_df['Pressure (psi)'], kde=True, ax=ax6, color=COLORS['secondary'])
ax6.set_title("📊 Pressure Distribution")
ax6.set_xlabel("Pressure (psi)")

fig3.tight_layout()
st.pyplot(fig3)

# Summary Stats
st.subheader("📋 Summary Statistics")
st.write(f"🔢 Total Data Points: {len(agg_df)}")
st.write(f"📈 Average Scaled Mass: {agg_df['Scaled mass (kg)'].mean():.2f} kg")
st.write(f"📊 Mass Std Dev: {agg_df['Scaled mass (kg)'].std():.2f} kg")
st.write(f"⚡ Average Pressure: {agg_df['Pressure (psi)'].mean():.2f} psi")
st.write(f"📊 Pressure Std Dev: {agg_df['Pressure (psi)'].std():.2f} psi")
st.write(f"🔄 Max Mass Change: {agg_df['Scaled mass change'].abs().max():.2f} kg")
st.write(f"🔄 Max Pressure Change: {agg_df['Pressure change'].abs().max():.2f} psi")
