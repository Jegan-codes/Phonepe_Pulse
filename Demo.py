#%%writefile app.py
import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Function to connect to SQLite database
def get_data(query, params=None):
    conn = sqlite3.connect("weather_database.sqlite")
    if params:
        df = pd.read_sql_query(query, conn, params=params)
    else:
        df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# Streamlit App Title
st.set_page_config(page_title="Weather Data Analysis", layout="wide")

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Project Introduction", "Weather Data Visualization", "SQL Queries", "Creator Info"])

# -------------------------------- PAGE 1: Introduction --------------------------------
if page == "Project Introduction":
    st.title("🌦️ Weather Data Analysis")
    st.subheader("📊 A Streamlit App for Exploring Weather Trends")
    st.write("""
    This project analyzes weather data from different cities using an SQLite database.
    It provides visualizations for temperature, humidity, and other weather parameters.

    **Features:**
    - View and filter weather data by city, date, or month.
    - Generate dynamic visualizations.
    - Run predefined SQL queries to explore insights.

    **Database Used:** `weather_database.sqlite`
    """)

# -------------------------------- PAGE 2: Weather Data Visualization --------------------------------
elif page == "Weather Data Visualization":
    st.title("📊 Weather Data Visualizer")

    # Fetch city list
    cities = get_data("SELECT DISTINCT City FROM weather_data")["City"].tolist()

    # Filters
    selected_city = st.selectbox("Select City", cities)
    date_option = st.radio("Filter By:", ["Specific Day", "Entire Month"])

    if date_option == "Specific Day":
        selected_date = st.date_input("Choose a Date")
        query = "SELECT * FROM weather_data WHERE City = ? AND Date = ?"
        df = get_data(query, params=(selected_city, selected_date.strftime("%Y-%m-%d")))
    else:
        selected_month = st.selectbox("Select Month", range(1, 13))
        query = "SELECT * FROM weather_data WHERE City = ? AND strftime('%m', Date) = ?"
        df = get_data(query, params=(selected_city, f"{selected_month:02d}"))

    if not df.empty:
        st.write("### Weather Data", df)

        # Visualization
        st.write("### Temperature Trends")
        plt.figure(figsize=(10, 5))
        sns.lineplot(data=df, x="Date", y="Temperature_C", marker="o", label="Temperature (°C)")
        plt.xticks(rotation=45)
        st.pyplot(plt)
    else:
        st.warning("No data available for the selected filters.")

# -------------------------------- PAGE 3: SQL Queries --------------------------------
elif page == "SQL Queries":
    st.title("📋 SQL Query Results")

    queries = {
        "1. Average Temperature per City": "SELECT City, AVG(Temperature_C) AS Avg_Temperature FROM weather_data GROUP BY City",
        "2. Highest Humidity per City": "SELECT City, MAX(Humidity_Percentage) AS Max_Humidity FROM weather_data GROUP BY City",
        "3. Lowest Temperature Recorded": "SELECT City, MIN(Temperature_C) AS Min_Temperature, Date FROM weather_data",
        "4. Wind Speed Trends": "SELECT City, AVG(Wind_Speed_kmh) AS Avg_Wind_Speed FROM weather_data GROUP BY City",
        "5. Most Common Weather Condition": "SELECT Weather_Condition, COUNT(*) AS Frequency FROM weather_data GROUP BY Weather_Condition ORDER BY Frequency DESC LIMIT 1"
    }

    selected_query = st.selectbox("Choose a Query", list(queries.keys()))
    query_result = get_data(queries[selected_query])

    st.write("### Query Result:")
    st.dataframe(query_result)

# -------------------------------- PAGE 4: Creator Info --------------------------------
elif page == "Creator Info":
    st.title("👩‍💻 Creator of this Project")
    st.write("""
    **Developed by:** Vinodhini
    **Skills:** Python, SQL, Data Analysis,Streamlit, Pandas
    """)
    st.image("https://via.placeholder.com/150", caption="Your Profile Picture", width=150)
