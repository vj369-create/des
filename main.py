import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import io

# App title
st.title("🧮 Skid Beam Bending Stress Calculator")
st.subheader("With Forklift Load & Dynamic Effects")

# Input Section
st.markdown("### 📥 Input Parameters")

load_kg = st.number_input("Enter Load (kg)", min_value=100.0, value=1000.0)
fork_spacing = st.number_input("Forklift Tine Spacing (mm)", min_value=200.0, value=700.0)
daf = st.slider("Dynamic Amplification Factor (DAF)", min_value=1.0, max_value=3.0, value=2.5, step=0.1)
height = st.number_input("RHS Height - Vertical (mm)", min_value=50.0, value=150.0)
width = st.number_input("RHS Width - Horizontal (mm)", min_value=50.0, value=100.0)
thickness = st.number_input("RHS Wall Thickness (mm)", min_value=3.0, value=6.0)

# Constants
g = 9.81  # m/s²
yield_strength = 250  # MPa

# Calculations
load_n = load_kg * g
dyn_load = load_n * daf
w = dyn_load / fork_spacing

# Section modulus Zx
Z = ((width * height*2) - ((width - 2*thickness)(height - 2*thickness)**2)) / (6 * height)
M = (w * fork_spacing**2) / 8
stress = M / Z

# Result section
st.markdown("### 📊 Output")
st.write(f"*Dynamic Load (N):* {dyn_load:.2f}")
st.write(f"*Bending Moment (N·mm):* {M:.2f}")
st.write(f"*Section Modulus (Zx in mm³):* {Z:.2f}")
st.write(f"*Calculated Bending Stress:* {stress:.2f} MPa")
st.write(f"*Yield Strength of Steel:* {yield_strength} MPa")

result = "✅ SAFE under dynamic load." if stress < yield_strength else "❌ NOT SAFE. Redesign required."
st.success(result) if stress < yield_strength else st.error(result)

# Optional Visualization
if st.checkbox("📈 Show Stress vs Yield Strength Plot"):
    fig, ax = plt.subplots()
    ax.bar(["Bending Stress", "Yield Strength"], [stress, yield_strength], color=["#FF6B6B", "#4ECDC4"])
    ax.set_ylabel("Stress (MPa)")
    ax.set_title("Stress Comparison")
    st.pyplot(fig)

# PDF Export Section
st.markdown("### 📄 Export Results as PDF")

def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt="Skid Beam Bending Stress Report", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Load: {load_kg:.2f} kg", ln=True)
    pdf.cell(200, 10, txt=f"Fork Spacing: {fork_spacing:.2f} mm", ln=True)
    pdf.cell(200, 10, txt=f"DAF: {daf}", ln=True)
    pdf.cell(200, 10, txt=f"RHS Dimensions: {height} x {width} x {thickness} mm", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt=f"Dynamic Load: {dyn_load:.2f} N", ln=True)
    pdf.cell(200, 10, txt=f"Bending Moment: {M:.2f} N·mm", ln=True)
    pdf.cell(200, 10, txt=f"Section Modulus Zx: {Z:.2f} mm³", ln=True)
    pdf.cell(200, 10, txt=f"Bending Stress: {stress:.2f} MPa", ln=True)
    pdf.cell(200, 10, txt=f"Yield Strength: {yield_strength} MPa", ln=True)
    pdf.cell(200, 10, txt=f"Result: {result}", ln=True)

    # Convert PDF to bytes
    pdf_bytes = io.BytesIO()
    pdf.output(pdf_bytes)
    pdf_bytes.seek(0)
    return pdf_bytes

pdf_file = create_pdf()

st.download_button(
    label="📥 Download Report as PDF",
    data=pdf_file,
    file_name="skid_bending_report.pdf",
    mime="application/pdf"
)