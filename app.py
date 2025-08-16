
import io
import base64
from datetime import datetime
from flask import Flask, render_template, request, send_file
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.gridspec import GridSpec

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

def prepare_data(df, selected_date):
    df = df.copy()
    df['date_parsed'] = pd.to_datetime(df['Date'], format='%d-%m-%Y', errors='coerce')
    filtered_df = df[df['date_parsed'] == selected_date].copy()
    if filtered_df.empty:
        return None
    # Remove negative scaled mass values
    filtered_df = filtered_df[filtered_df['Scaled mass (kg)'] >= 0]
    # Shift time to start at 9:00 AM
    min_time_sec = filtered_df['time'].min()
    filtered_df['shifted_time_sec'] = filtered_df['time'] - min_time_sec
    base_time = pd.Timestamp.combine(selected_date.date(), pd.to_datetime("09:00:00").time())
    filtered_df['datetime'] = base_time + pd.to_timedelta(filtered_df['shifted_time_sec'], unit='s')
    filtered_df['time_bin'] = filtered_df['datetime'].dt.floor('10min')
    # Aggregate
    agg_df = filtered_df.groupby('time_bin').agg({
        'Scaled mass (kg)': 'mean',
        'Pressure (psi)': 'mean'
    }).reset_index()
    # Changes
    agg_df['Scaled mass change'] = agg_df['Scaled mass (kg)'].diff().fillna(0)
    agg_df['Pressure change'] = agg_df['Pressure (psi)'].diff().fillna(0)
    agg_df['Mass velocity'] = agg_df['Scaled mass change'] / 10
    agg_df['Pressure velocity'] = agg_df['Pressure change'] / 10
    return agg_df

def create_header_panel(fig, selected_date, agg_df):
    header_ax = fig.add_subplot(GridSpec(6, 4, figure=fig)[0, :])
    header_ax.set_xlim(0, 10)
    header_ax.set_ylim(0, 1)
    header_ax.axis('off')
    header_rect = Rectangle((0, 0), 10, 1, facecolor=COLORS['surface'], alpha=0.8)
    header_ax.add_patch(header_rect)
    header_ax.text(5, 0.7, '🏭 INDUSTRIAL MONITORING DASHBOARD',
                   fontsize=20, fontweight='bold', ha='center',
                   color=COLORS['primary'])
    header_ax.text(5, 0.3, f"📅 {selected_date.strftime('%A, %B %d, %Y')} | Data Points: {len(agg_df)}",
                   fontsize=12, ha='center', color=COLORS['text'], alpha=0.8)

def create_kpi_cards(fig, agg_df):
    kpi_data = [
        ("📊 Avg Mass", f"{agg_df['Scaled mass (kg)'].mean():.1f} kg", COLORS['primary']),
        ("📈 Max Mass", f"{agg_df['Scaled mass (kg)'].max():.1f} kg", COLORS['success']),
        ("⚡ Avg Pressure", f"{agg_df['Pressure (psi)'].mean():.1f} psi", COLORS['secondary']),
        ("🔺 Max Pressure", f"{agg_df['Pressure (psi)'].max():.1f} psi", COLORS['warning'])
    ]
    for i, (label, value, color) in enumerate(kpi_data):
        ax = fig.add_subplot(GridSpec(6, 4, figure=fig)[1, i])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        card_rect = Rectangle((0.05, 0.1), 0.9, 0.8, facecolor=COLORS['surface'],
                             alpha=0.9, edgecolor=color, linewidth=2)
        ax.add_patch(card_rect)
        ax.text(0.5, 0.65, value, fontsize=14, fontweight='bold',
                ha='center', va='center', color=color)
        ax.text(0.5, 0.35, label, fontsize=10, ha='center', va='center',
                color=COLORS['text'], alpha=0.8)

def create_main_trends_chart(fig, agg_df):
    ax = fig.add_subplot(GridSpec(6, 4, figure=fig)[2:4, :2])
    x = agg_df['time_bin']
    x_labels = x.dt.strftime('%H:%M')
    ax.plot(x, agg_df['Scaled mass (kg)'],
            color=COLORS['primary'], linewidth=3, marker='o', markersize=6,
            label='Scaled Mass (kg)', markerfacecolor='white',
            markeredgecolor=COLORS['primary'], markeredgewidth=2)
    ax.set_xlabel('Time (HH:MM)', color=COLORS['text'], fontsize=11)
    ax.set_ylabel('Scaled Mass (kg)', color=COLORS['primary'], fontsize=11, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=COLORS['primary'])
    ax.tick_params(axis='x', colors=COLORS['text'])
    ax2 = ax.twinx()
    ax2.plot(x, agg_df['Pressure (psi)'],
             color=COLORS['secondary'], linewidth=3, marker='^', markersize=6,
             label='Pressure (psi)', markerfacecolor='white',
             markeredgecolor=COLORS['secondary'], markeredgewidth=2)
    ax2.set_ylabel('Pressure (psi)', color=COLORS['secondary'], fontsize=11, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=COLORS['secondary'])
    ax.set_title('📈 REAL-TIME TRENDS ANALYSIS', fontsize=14, fontweight='bold',
                 color=COLORS['text'], pad=20)
    ax.grid(True, linestyle='--', alpha=0.3, color='white')
    fig.autofmt_xdate(rotation=45)

def create_change_analysis_chart(fig, agg_df):
    ax = fig.add_subplot(GridSpec(6, 4, figure=fig)[2:4, 2:])
    x = agg_df['time_bin']
    x_labels = x.dt.strftime('%H:%M')
    width = 0.35
    x_pos = np.arange(len(x))
    ax.bar(x_pos - width/2, agg_df['Scaled mass change'], width,
           color=COLORS['accent'], alpha=0.8, label='Mass Change',
           edgecolor='white', linewidth=1)
    ax2 = ax.twinx()
    ax2.bar(x_pos + width/2, agg_df['Pressure change'], width,
            color=COLORS['warning'], alpha=0.8, label='Pressure Change',
            edgecolor='white', linewidth=1)
    ax.set_xlabel('Time (HH:MM)', color=COLORS['text'], fontsize=11)
    ax.set_ylabel('Mass Change (kg)', color=COLORS['accent'], fontsize=11, fontweight='bold')
    ax2.set_ylabel('Pressure Change (psi)', color=COLORS['warning'], fontsize=11, fontweight='bold')
    ax.tick_params(axis='y', labelcolor=COLORS['accent'])
    ax2.tick_params(axis='y', labelcolor=COLORS['warning'])
    ax.tick_params(axis='x', colors=COLORS['text'])
    ax.set_title('📊 CHANGE RATE ANALYSIS', fontsize=14, fontweight='bold',
                 color=COLORS['text'], pad=20)
    ax.grid(True, linestyle='--', alpha=0.3, color='white', axis='y')
    step = max(1, len(x_labels) // 8)
    ax.set_xticks(x_pos[::step])
    ax.set_xticklabels(x_labels[::step], rotation=45, ha='right')

def create_distribution_analysis(fig, agg_df):
    from scipy import stats
    ax1 = fig.add_subplot(GridSpec(6, 4, figure=fig)[4:6, 0:2])
    ax1.hist(agg_df['Scaled mass (kg)'], bins=20,
             color=COLORS['primary'], alpha=0.7, edgecolor='white', linewidth=1)
    ax1.set_xlabel('Scaled Mass (kg)', color=COLORS['text'], fontsize=11)
    ax1.set_ylabel('Frequency', color=COLORS['primary'], fontsize=11, fontweight='bold')
    ax1.set_title('📊 MASS DISTRIBUTION', fontsize=12, fontweight='bold', color=COLORS['text'])
    ax1.tick_params(colors=COLORS['text'])
    ax1.grid(True, alpha=0.3, color='white')
    ax2 = fig.add_subplot(GridSpec(6, 4, figure=fig)[4:6, 2:4])
    ax2.hist(agg_df['Pressure (psi)'], bins=20,
             color=COLORS['secondary'], alpha=0.7, edgecolor='white', linewidth=1)
    ax2.set_xlabel('Pressure (psi)', color=COLORS['text'], fontsize=11)
    ax2.set_ylabel('Frequency', color=COLORS['secondary'], fontsize=11, fontweight='bold')
    ax2.set_title('📊 PRESSURE DISTRIBUTION', fontsize=12, fontweight='bold', color=COLORS['text'])
    ax2.tick_params(colors=COLORS['text'])
    ax2.grid(True, alpha=0.3, color='white')

def render_dashboard_image(agg_df, selected_date):
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(20, 12), facecolor=COLORS['background'])
    create_header_panel(fig, selected_date, agg_df)
    create_kpi_cards(fig, agg_df)
    create_main_trends_chart(fig, agg_df)
    create_change_analysis_chart(fig, agg_df)
    create_distribution_analysis(fig, agg_df)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf

app = Flask(__name__, static_folder="static", template_folder="templates")

@app.route('/manifest.json')
def manifest():
    return app.send_static_file('manifest.json')

@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard', methods=['GET'])
def dashboard_query():
    """Optional: supports existing f.xlsx on server via query string date=dd-mm-yyyy"""
    date_str = request.args.get('date')
    if not date_str:
        return render_template('result.html', error="Please provide a date in dd-mm-yyyy format.")
    try:
        selected_date = pd.to_datetime(date_str, format='%d-%m-%Y')
    except ValueError:
        return render_template('result.html', error="Invalid date format. Use dd-mm-yyyy.")
    try:
        df = pd.read_excel('f.xlsx')
    except FileNotFoundError:
        return render_template('result.html', error="Data file 'f.xlsx' not found on the server.")
    agg_df = prepare_data(df, selected_date)
    if agg_df is None or len(agg_df) == 0:
        return render_template('result.html', error="No data available for the selected date.")
    img_buf = render_dashboard_image(agg_df, selected_date)
    import base64
    img_b64 = base64.b64encode(img_buf.getvalue()).decode('utf-8')
    summary = {
        "points": len(agg_df),
        "avg_mass": float(agg_df['Scaled mass (kg)'].mean()),
        "std_mass": float(agg_df['Scaled mass (kg)'].std() or 0),
        "avg_pressure": float(agg_df['Pressure (psi)'].mean()),
        "std_pressure": float(agg_df['Pressure (psi)'].std() or 0),
        "max_mass_change": float(agg_df['Scaled mass change'].abs().max() or 0),
        "max_pressure_change": float(agg_df['Pressure change'].abs().max() or 0),
        "date": selected_date.strftime('%A, %B %d, %Y')
    }
    return render_template('result.html', image_data=img_b64, summary=summary, date=summary["date"])

@app.route('/upload', methods=['POST'])
def upload():
    """Accepts Excel file + date (YYYY-MM-DD from <input type="date">). Returns image."""
    if 'file' not in request.files:
        return "No file uploaded.", 400
    file = request.files['file']
    date_str = request.form.get('date')
    if not date_str:
        return "Date is required.", 400
    try:
        # HTML date picker gives YYYY-MM-DD
        selected_date = pd.to_datetime(date_str, format='%Y-%m-%d')
    except ValueError:
        return "Invalid date format.", 400
    try:
        df = pd.read_excel(file)
    except Exception as e:
        return f"Failed to read Excel: {e}", 400
    agg_df = prepare_data(df, selected_date)
    if agg_df is None or len(agg_df) == 0:
        return "No data for selected date.", 400
    img_buf = render_dashboard_image(agg_df, selected_date)
    img_buf.seek(0)
    return send_file(img_buf, mimetype='image/png', download_name='dashboard.png')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080, debug=False)
