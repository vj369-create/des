import streamlit as st

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
w = dyn_load / fork_spacing  # N/mm

# Section Modulus Zx
Z = ((width * height**2) - ((width - 2 * thickness) * (height - 2 * thickness)**2)) / (6 * height)

# Bending Moment
M = (w * fork_spacing**2) / 8  # N.mm

# Bending Stress
stress = M / Z  # MPa

# Output
st.markdown("### 📊 Output")
st.write(f"**Dynamic Load (N):** {dyn_load:.2f}")
st.write(f"**Bending Moment (N·mm):** {M:.2f}")
st.write(f"**Section Modulus (Zx in mm³):** {Z:.2f}")
st.write(f"**Calculated Bending Stress:** {stress:.2f} MPa")
st.write(f"**Yield Strength of Steel:** {yield_strength} MPa")

result = "✅ SAFE under dynamic load." if stress < yield_strength else "❌ NOT SAFE. Redesign required."
st.success(result) if stress < yield_strength else st.error(result)
