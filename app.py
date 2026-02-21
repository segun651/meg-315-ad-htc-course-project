import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="AD-HTC Gas Cycle Simulator", layout="wide")

st.title("AD-HTC Fuel-Enhanced Gas Cycle Simulator")
st.write("Simplified Integrated Rankine (Steam) + Brayton (Gas Turbine) Model")

st.header("Input Parameters")

col1, col2 = st.columns(2)

# ---------------------------
# BRAYTON CYCLE INPUTS
# ---------------------------
with col1:
    st.subheader("Brayton Cycle (Gas Turbine)")
    T1 = st.number_input("Compressor Inlet Temperature T1 (K)", value=300.0)
    rp = st.number_input("Compressor Pressure Ratio (rp)", value=8.0)
    T3 = st.number_input("Turbine Inlet Temperature T3 (K)", value=1200.0)
    eta_c = st.number_input("Compressor Efficiency", value=0.85)
    eta_t = st.number_input("Turbine Efficiency", value=0.88)

# ---------------------------
# RANKINE CYCLE INPUTS
# ---------------------------
with col2:
    st.subheader("Rankine Cycle (Steam)")
    T_boiler = st.number_input("Boiler Temperature (K)", value=773.0)
    T_cond = st.number_input("Condenser Temperature (K)", value=313.0)
    eta_t_steam = st.number_input("Steam Turbine Efficiency", value=0.85)

if st.button("Analyze System"):

    # =====================================================
    # BRAYTON CYCLE CALCULATIONS
    # =====================================================

    cp = 1.005  # kJ/kgK (air)
    gamma = 1.4

    # Compressor
    T2s = T1 * rp**((gamma - 1)/gamma)
    T2 = T1 + (T2s - T1)/eta_c

    # Turbine
    T4s = T3 / rp**((gamma - 1)/gamma)
    T4 = T3 - eta_t*(T3 - T4s)

    Wc = cp * (T2 - T1)
    Wt = cp * (T3 - T4)
    W_net_brayton = Wt - Wc
    Q_in_brayton = cp * (T3 - T2)
    eta_brayton = W_net_brayton / Q_in_brayton

    # Enthalpies for plotting (h = cp*T)
    h1 = cp*T1
    h2 = cp*T2
    h3 = cp*T3
    h4 = cp*T4

    # =====================================================
    # RANKINE CYCLE (SIMPLIFIED MODEL)
    # =====================================================

    # Assumptions:
    # Saturated liquid at condenser exit
    # Linear enthalpy approximation

    h_f = 4.18 * (T_cond - 273)       # approx liquid enthalpy
    h_g = 2800                       # approx steam enthalpy at boiler
    h3_steam = h_g
    h4s = h_f + 0.7*(h3_steam - h_f)  # isentropic estimate
    h4 = h3_steam - eta_t_steam*(h3_steam - h4s)

    W_turbine_steam = h3_steam - h4
    Q_boiler = h3_steam - h_f
    eta_rankine = W_turbine_steam / Q_boiler

    # Simplified entropy values for h-s diagram
    s1 = 0.5
    s2 = 0.5
    s3 = 6.5
    s4 = 7.0

    # =====================================================
    # RESULTS DISPLAY
    # =====================================================

    st.header("Results")

    col3, col4 = st.columns(2)

    with col3:
        st.subheader("Brayton Cycle Performance")
        st.write(f"Net Work Output = {W_net_brayton:.2f} kJ/kg")
        st.write(f"Thermal Efficiency = {eta_brayton*100:.2f} %")

    with col4:
        st.subheader("Rankine Cycle Performance")
        st.write(f"Turbine Work = {W_turbine_steam:.2f} kJ/kg")
        st.write(f"Thermal Efficiency = {eta_rankine*100:.2f} %")

    # =====================================================
    # T-h Diagram (Brayton)
    # =====================================================

    st.subheader("T-h Diagram (Brayton Cycle)")

    fig1, ax1 = plt.subplots()
    ax1.plot([h1, h2, h3, h4, h1],
             [T1, T2, T3, T4, T1])
    ax1.set_xlabel("Enthalpy (kJ/kg)")
    ax1.set_ylabel("Temperature (K)")
    ax1.set_title("Brayton Cycle T-h Diagram")
    st.pyplot(fig1)

    # =====================================================
    # h-s Diagram (Rankine)
    # =====================================================

    st.subheader("h-s Diagram (Rankine Cycle)")

    fig2, ax2 = plt.subplots()
    ax2.plot([s1, s2, s3, s4, s1],
             [h_f, h_f, h3_steam, h4, h_f])
    ax2.set_xlabel("Entropy (kJ/kgK)")
    ax2.set_ylabel("Enthalpy (kJ/kg)")
    ax2.set_title("Rankine Cycle h-s Diagram")
    st.pyplot(fig2)

    st.success("Analysis Complete.")