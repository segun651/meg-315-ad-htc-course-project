import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pyromat as pm

# Initialize thermodynamics libraries
pm.config["unit_pressure"] = "bar"
pm.config["unit_temperature"] = "K"
air = pm.get("ig.air")
steam = pm.get("mp.H2O")

st.set_page_config(page_title="Energhx AD-HTC Simulator", layout="wide")
st.title("AD-HTC Fuel-Enhanced Gas Cycle Analysis")
st.markdown("©2025 Energhx Research Group - Faculty of Engineering, University of Lagos")

# --- UI: Input Parameters ---
with st.sidebar:
    st.header("1. AD-HTC Feedstock Inputs")
    biogas_lhv = st.number_input("Biogas LHV (kJ/kg)", value=20000)
    m_fuel = st.number_input("Fuel Mass Flow (kg/s)", value=0.5, step=0.1)
    
    st.header("2. Gas Cycle (Brayton)")
    p1 = st.number_input("Inlet Pressure P1 (bar)", value=1.01)
    t1 = st.number_input("Inlet Temp T1 (K)", value=300.0)
    rp = st.slider("Pressure Ratio (rp)", 5, 20, 10)
    eta_c = st.slider("Compressor Efficiency", 0.7, 0.95, 0.85)
    eta_t_gas = st.slider("Gas Turbine Efficiency", 0.7, 0.95, 0.88)

    st.header("3. Steam Cycle (Rankine)")
    p_boiler = st.number_input("Boiler Pressure (bar)", value=40.0)
    t_boiler = st.number_input("Boiler Temp (K)", value=700.0)
    p_cond = st.number_input("Condenser Pressure (bar)", value=0.1)
    eta_t_steam = st.slider("Steam Turbine Efficiency", 0.7, 0.95, 0.85)

if st.button("ANALYZE SYSTEM"):
    try:
        # ==========================================
        # BRAYTON CYCLE CALCULATIONS
        # ==========================================
        # State 1: Inlet
        s1 = air.s(T=t1, p=p1)[0]
        h1 = air.h(T=t1, p=p1)[0]

        # State 2: Compressor Exit
        p2 = p1 * rp
        s2s = s1
        t2s = air.T_s(s=s2s, p=p2)[0]
        h2s = air.h(T=t2s, p=p2)[0]
        h2 = h1 + (h2s - h1) / eta_c
        t2 = air.T_h(h=h2, p=p2)[0]

        # State 3: Combustion (Fuel Enhanced via AD Biogas)
        m_air = 15.0  # Constant Air-Fuel Ratio assumption
        h3 = (m_air * h2 + m_fuel * biogas_lhv) / (m_air + m_fuel)
        p3 = p2
        t3 = air.T_h(h=h3, p=p3)[0]

        # State 4: Turbine Exit
        p4 = p1
        s3 = air.s(T=t3, p=p3)[0]
        t4s = air.T_s(s=s3, p=p4)[0]
        h4s = air.h(T=t4s, p=p4)[0]
        h4 = h3 - eta_t_gas * (h3 - h4s)
        t4 = air.T_h(h=h4, p=p4)[0]

        # ==========================================
        # STEAM CYCLE (RANKINE)
        # ==========================================
        # State 1s: Pump Inlet (Saturated Liquid)
        h1s = steam.h(p=p_cond, x=0)[0]
        s1s = steam.s(p=p_cond, x=0)[0]
        
        # State 3s: Boiler Exit (Superheated Steam)
        h3s = steam.h(p=p_boiler, T=t_boiler)[0]
        s3s = steam.s(p=p_boiler, T=t_boiler)[0]
        
        # State 4s: Turbine Exit (Isentropic Expansion)
        s4s_ideal = s3s
        # x() is the correct method for quality in pyromat
        x4s = steam.x(s=s4s_ideal, p=p_cond)[0] 
        h4s_ideal = steam.h(p=p_cond, x=x4s)[0]
        h4s_actual = h3s - eta_t_steam * (h3s - h4s_ideal)
        s4s_actual = steam.s(h=h4s_actual, p=p_cond)[0]

        # ==========================================
        # RESULTS DISPLAY
        # ==========================================
        st.header("Performance Results")
        res1, res2 = st.columns(2)
        res1.metric("Gas Cycle Work", f"{(h3-h4)-(h2-h1):.2f} kJ/kg")
        res2.metric("Steam Cycle Work", f"{h3s-h4s_actual:.2f} kJ/kg")

        # ==========================================
        # VISUALIZATION: h-s and T-H Charts
        # ==========================================
        col_a, col_b = st.columns(2)

        with col_a:
            st.subheader("h-s Chart (Steam Cycle)")
            # Plot Vapor Dome
            p_crit = 220.6
            p_range = np.logspace(np.log10(p_cond), np.log10(p_crit), 50)
            sf = [steam.s(p=pp, x=0)[0] for pp in p_range]
            sg = [steam.s(p=pp, x=1)[0] for pp in p_range]
            hf = [steam.h(p=pp, x=0)[0] for pp in p_range]
            hg = [steam.h(p=pp, x=1)[0] for pp in p_range]

            fig_hs, ax_hs = plt.subplots()
            ax_hs.plot(sf, hf, 'k--', alpha=0.5, label="Saturation Line")
            ax_hs.plot(sg, hg, 'k--', alpha=0.5)
            # Plot Cycle Points
            s_pts = [s1s, s3s, s4s_actual, s1s]
            h_pts = [h1s, h3s, h4s_actual, h1s]
            ax_hs.plot(s_pts, h_pts, 'ro-', linewidth=2, label="Rankine Cycle")
            ax_hs.set_xlabel("Entropy (s) [kJ/kg*K]")
            ax_hs.set_ylabel("Enthalpy (h) [kJ/kg]")
            ax_hs.legend()
            st.pyplot(fig_hs)

        with col_b:
            st.subheader("T-H Chart (Process Heat)")
            # H_dot = mass_flow * enthalpy_change
            t_stack = 450.0 
            H_gas_total = (m_air + m_fuel) * (h4 - air.h(T=t_stack, p=p4)[0])
            
            fig_th, ax_th = plt.subplots()
            # Red line: Cooling Gas Exhaust
            ax_th.plot([0, H_gas_total], [t4, t_stack], 'r', linewidth=3, label="Gas Exhaust Cooling")
            # Blue line: Heating Steam (Simplified pinch-point visualization)
            ax_th.plot([0, H_gas_total*0.7], [350, t_boiler], 'b', linewidth=3, label="Steam Heating")
            ax_th.set_xlabel("Cumulative Heat Rate (H_dot) [kW]")
            ax_th.set_ylabel("Temperature (T) [K]")
            ax_th.legend()
            st.pyplot(fig_th)

        st.success("Analysis Complete. Ready for submission to Energhx.")

    except Exception as e:
        st.error(f"Thermodynamic Error: {e}")
