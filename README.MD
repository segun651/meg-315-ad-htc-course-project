# AD-HTC Fuel-Enhanced Gas Cycle Simulator 
**A Course Project for Energhx Research Group, University of Lagos**

##  Overview
This repository contains a Python-based thermodynamic simulator for an integrated **Anaerobic Digestion (AD)** and **Hydrothermal Carbonization (HTC)** power cycle. The tool is designed to analyze "Fuel-Enhanced" gas cycles by calculating state properties and visualizing energy flows.

##  Key Features
- **Interactive UI/UX:** Built with Streamlit for real-time parameter adjustment.
- **Accurate Thermodynamics:** Uses the `pyromat` library for real-gas and steam table data.
- **Visual Analytics:** 
  - **h-s Chart:** Visualizes the Rankine (Steam) cycle against the vapor dome.
  - **T-H Chart:** Displays the temperature-heat rate relationship for process gas cooling.
- **Biogas Modeling:** Calculates turbine inlet temperatures based on Biogas LHV.

##  Installation & Usage
1. **Clone the repository:**
   ```bash
   git clone https://github.com
  
2. **Install dependencies:**
   pip install streamlit numpy matplotlib pyromat

3. **Run the application:**
bash
streamlit run app.py
