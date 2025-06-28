# Phonepe_Pulse
 📊 --> PhonePe Pulse Data Analysis & Visualization

This project provides an end-to-end data analysis and visualization dashboard based on the [PhonePe Pulse](https://pulse.phonepe.com/) data repository. It includes data extraction, processing, and an interactive visualization interface using Python, PostgreSQL, and Streamlit.

---

## 📌 Table of Contents
	- About the Project
	- Tech Stack
	- Features
	- Data Pipeline
	- Project Structure
	
---

## 🧾 About the Project

The **PhonePe Pulse Data Visualization** project is a deep-dive analysis of digital payment behavior across India using PhonePe transaction data. The aim is to:
- Understand user engagement trends.
- Identify top-performing states, districts, and PIN codes.
- Provide insights into insurance, users strategies and other transaction categories.
- Build a dashboard that allows dynamic exploration of these insights.

---

## 🔧 Tech Stack

| Tool/Library 		| Purpose |
|-----------------------|---------|
| Python       		| Data Processing & Backend Logic |
| PostgreSQL   		| Relational Database |
| Streamlit    		| Dashboard Visualization |
| Plotly & Matplotlob   | Interactive Graphs |
| Pandas       		| Data Wrangling |
| GeoJSON      		| Map Visualization |

---

## ✨ Features

- Interactive dashboard with filters for year, quarter, state, and category.
- Choropleth map of India showing transaction distribution.
- Time-series charts to observe trends over time.
- Ranking tables for top 10 states/districts.
- Data insights into registration, insurance.

---

## 🔁 Data Pipeline

1. **Data Extraction** from PhonePe Pulse GitHub (JSON format).
2. **Transformation** into structured tabular format using Python.
3. **Loading** into PostgreSQL database.
4. **Visualization** through a Streamlit-based web dashboard.

---

## 🗂️ Project Structure 
		phonepe-pulse-project
		
		├──  data
		     └── extracted_data.csv
		
		├──  scripts
		    ├── extract_data.py
		    ├── transform.py
		    └── load_to_db.py
		
		├──  Streamlit visulization
		    └── Visuals.py
		
		└── README.md




