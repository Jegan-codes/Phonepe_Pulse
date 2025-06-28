import psycopg2 
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# make a connection to the db
connection = psycopg2.connect(
                        host = "localhost",
                        port = "5432",
                        user = "postgres",
                        database = "phonepe_pulse_db",
                        password = "jegan"
                        )

cursor = connection.cursor()

# Streamlit App Title -- Introduction
page = st.sidebar.selectbox("Choose a page", ["Introduction", "Data Analysis"])

if page == "Introduction":

    st.markdown("# 📊 PhonePe Pulse Data Analysis")

    st.markdown("""
        <h2>Welcome to the PhonePe Pulse Data Analysis Dashboard</h2>

        <h3>This project is designed to explore and analyze data extracted from the PhonePe Pulse GitHub repository, 
        which contains rich information on digital transactions happening across India. The primary objective is to convert this raw, extensive data 
        into meaningful insights that can help understand user behavior, transaction patterns, and regional financial activity.</h3>

        <h3>Using interactive visualizations, we aim to:</h3>
        <ul>
            <li>  Track the growth and adoption of digital payments in various states and districts </li>
            <li> Study user engagement trends and application usage metrics </li>
            <li> Explore insurance-related data and financial service usage </li>
            <li> Provide region-wise transaction comparisons with filters for year and quarter </li>
        <ul>

        <h3>📌 Navigate to the <strong>Data Analysis</strong> page using the left sidebar to dive into these insights.</h3>

        <h4>Built with ❤️ using Streamlit, PostgreSQL, Plotly, Matplotlib and Python</h4>
        """, unsafe_allow_html=True)

# Data Analysis - Business Case Study
elif page == "Data Analysis":

    st.markdown("<h3>For the further inspection, we can click the following buttons </h3>",  unsafe_allow_html=True)
    data = st.selectbox("Click anyone below :", ["User Engagement and Growth Strategy", "Insurance Engagement Analysis", 
                                                 "Transaction Analysis Across States and Districts", "User Registration Analysis", 
                                                 "Insurance Transactions Analysis"])

    if data == "User Engagement and Growth Strategy" :
        # Fetch unique years
        cursor.execute("SELECT DISTINCT year FROM map_transaction ORDER BY year;")
        years = [row[0] for row in cursor.fetchall()]

        # Fetch unique quarters
        cursor.execute("SELECT DISTINCT quater FROM map_transaction ORDER BY quater;")
        quarters = [row[0] for row in cursor.fetchall()]

        # Streamlit dropdowns
        selected_year = st.selectbox("Select Year:", years)
        selected_quarter = st.selectbox("Select Quarter:", quarters)

        #================Query part-----------------

        query = """ SELECT SUM (transaction_amount), SUM (transaction_count) FROM map_transaction WHERE year = %s AND quater =%s;"""

        cursor.execute(query,(selected_year,selected_quarter))
        result = cursor.fetchone()

        total_amount = result[0] if result[0] is not None else 0
        total_count = result[1] if result[1] is not None else 0

        st.markdown(f"<h3>Total Transaction Amount: ₹{total_amount:,.2f}</h3>", unsafe_allow_html=True)
        st.markdown(f"<h3>Total Transaction Count: {total_count:,}</h3>", unsafe_allow_html=True)

    # --- Get State-wise Transaction Amount ---
        cursor.execute("""
        SELECT state, SUM(transaction_amount) as total_amount
        FROM map_transaction
        WHERE year = %s AND quater = %s
        GROUP BY state
        ORDER BY state;
        """, (selected_year, selected_quarter))

        data_rows = cursor.fetchall()
        df_map = pd.DataFrame(data_rows, columns=['state', 'transaction_amount'])

        state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island','andhra-pradesh' : 'Andhra Pradesh','arunachal-pradesh' : 'Arunachal Pradesh',
        'assam': 'Assam', 'bihar' : 'Bihar', 'chandigarh' : 'Chandigarh', 'chhattisgarh' : 'Chhattisgarh', 
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli', 'delhi': 'Delhi', 'goa' : 'Goa', 'gujarat' : 'Gujarat',
        'haryana' : 'Haryana', 'himachal-pradesh' : 'Himachal Pradesh', 'jammu-&-kashmir' : 'Jammu & Kashmir', 'jharkhand' : 'Jharkhand',
        'karnataka' : 'Karnataka', 'kerala' : 'Kerala', 'ladakh' : 'Ladakh', 'lakshadweep' : 'Lakshadweep', 'madhya-pradesh' : 'Madhya Pradesh',
        'maharashtra' : 'Maharashtra', 'manipur' : 'Manipur', 'meghalaya' : 'Meghalaya', 'mizoram' : 'Mizoram', 'nagaland' : 'Nagaland',
        'odisha': 'Odisha', 'puducherry': 'Puducherry', 'punjab' : 'Punjab', 'rajasthan' : 'Rajasthan', 'sikkim' : 'Sikkim', 
        'tamil-nadu' : 'Tamil Nadu', 'telangana' : 'Telangana', 'tripura' : 'Tripura', 'uttar-pradesh' : 'Uttar Pradesh',
        'uttarakhand' : 'Uttarakhand', 'west-bengal' : 'West Bengal'
        }

        df_map['state'] = df_map['state'].replace(state_name_map)
        # India GeoJSON for state boundaries
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

        # Choropleth Map
        fig = px.choropleth(
            df_map,
            geojson=geojson_url,
            featureidkey='properties.ST_NM',
            locations='state',
            color='transaction_amount',
            color_continuous_scale='Purples',
            title=f"State-wise Transaction Amount - {selected_year} Q{selected_quarter}"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Bar Chart - State-wise Transaction Amount
        st.subheader("📊 Bar Chart: State-wise Transaction Amount")
        bar_fig = px.bar(
            df_map.sort_values(by='transaction_amount', ascending=False),
            x='state',
            y='transaction_amount',
            text='transaction_amount',
            color='transaction_amount',
            color_continuous_scale='Purples',
            title=f"State-wise Transaction Amount (₹) - {selected_year} Q{selected_quarter}"
        )

        bar_fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        bar_fig.update_layout(xaxis_title="State", yaxis_title="Transaction Amount (₹)", xaxis_tickangle=-45)

        st.plotly_chart(bar_fig, use_container_width=True)


                #------------- Trend Analysis -------------

        st.subheader("📦 Box Plot: Transaction Amount Distribution by State")

        fig_box = px.box(
            df_map,
            x="state",
            y="transaction_amount",
            points="all",  # Show all points including outliers
            color="state",
            title=f"Distribution of Transaction Amounts by State - {selected_year} Q{selected_quarter}"
        )

        fig_box.update_layout(xaxis_tickangle=-45, showlegend=False)
        st.plotly_chart(fig_box, use_container_width=True)

        st.subheader("🧭 Treemap: State → District by Transaction Amount")

        # Fetch state and district-level data
        cursor.execute("""
            SELECT state, transaction_area, SUM(transaction_amount) as transaction_amount
            FROM map_transaction
            WHERE year = %s AND quater = %s
            GROUP BY state, transaction_area;
        """, (selected_year, selected_quarter))

        district_data = cursor.fetchall()
        df_districts = pd.DataFrame(district_data, columns=['state', 'transaction_area', 'transaction_amount'])

        # Replace state names
        df_districts['state'] = df_districts['state'].replace(state_name_map)

        # Treemap
        fig_tree = px.treemap(
            df_districts,
            path=['state', 'transaction_area'],
            values='transaction_amount',
            title=f"Treemap: State → District by Transaction Amount - {selected_year} Q{selected_quarter}",
            color='transaction_amount',
            color_continuous_scale='Purples'
        )

        st.plotly_chart(fig_tree, use_container_width=True)



    #============= Insurance Engagement Analysis ===============

    elif data == "Insurance Engagement Analysis" :
        # fetch unique years
        cursor.execute("SELECT DISTINCT year FROM map_users ORDER BY year;")
        year = [row[0] for row in cursor.fetchall()]

        # fetch unique quarters
        cursor.execute("SELECT DISTINCT quater FROM map_users ORDER BY quater;")
        quarter = [row[0] for row in cursor.fetchall()]

        # streamlit applications
        col1,col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Select the Year:", year)
        with col2 :
            selected_quarter = st.selectbox("Select the Quarter:", quarter)

        #------------ Query Part --------------

        query = """SELECT SUM (registered_users), SUM (app_opens) FROM map_users WHERE year = %s AND quater = %s;"""
        cursor.execute(query,(selected_year,selected_quarter))
        result = cursor.fetchone()

        total_users = result[0] if result[0] is not None else 0 
        total_apps = result[1] if result[1] is not None else 0

        st.markdown(f"### Total Registered Users : {total_users}",unsafe_allow_html = True)
        st.markdown(f"### Total App Opens : {total_apps}", unsafe_allow_html=True)
        

        # =========== Display in the Indian Map

        cursor.execute("""
        SELECT state, SUM(registered_users) as total_users
        FROM map_users
        WHERE year = %s AND quater = %s
        GROUP BY state
        ORDER BY state;
        """, (selected_year, selected_quarter))

        data_rows = cursor.fetchall()
        df_map = pd.DataFrame(data_rows, columns=['state', 'registered_users'])

        state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island','andhra-pradesh' : 'Andhra Pradesh','arunachal-pradesh' : 'Arunachal Pradesh',
        'assam': 'Assam', 'bihar' : 'Bihar', 'chandigarh' : 'Chandigarh', 'chhattisgarh' : 'Chhattisgarh', 
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli', 'delhi': 'Delhi', 'goa' : 'Goa', 'gujarat' : 'Gujarat',
        'haryana' : 'Haryana', 'himachal-pradesh' : 'Himachal Pradesh', 'jammu-&-kashmir' : 'Jammu & Kashmir', 'jharkhand' : 'Jharkhand',
        'karnataka' : 'Karnataka', 'kerala' : 'Kerala', 'ladakh' : 'Ladakh', 'lakshadweep' : 'Lakshadweep', 'madhya-pradesh' : 'Madhya Pradesh',
        'maharashtra' : 'Maharashtra', 'manipur' : 'Manipur', 'meghalaya' : 'Meghalaya', 'mizoram' : 'Mizoram', 'nagaland' : 'Nagaland',
        'odisha': 'Odisha', 'puducherry': 'Puducherry', 'punjab' : 'Punjab', 'rajasthan' : 'Rajasthan', 'sikkim' : 'Sikkim', 
        'tamil-nadu' : 'Tamil Nadu', 'telangana' : 'Telangana', 'tripura' : 'Tripura', 'uttar-pradesh' : 'Uttar Pradesh',
        'uttarakhand' : 'Uttarakhand', 'west-bengal' : 'West Bengal'
        }

        df_map['state'] = df_map['state'].replace(state_name_map)


        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
        fig = px.choropleth(
            df_map,
            geojson = geojson_url,
            featureidkey='properties.ST_NM',
            locations='state',
            color='registered_users',
            color_continuous_scale='Brown'
        )

        fig.update_geos(fitbounds="locations", visible=False)

        st.plotly_chart(fig, use_container_width=True)

        # ----------   Top 10 states with Registered Users -- 
        query_pie = """
            SELECT state, SUM(registered_users) AS total_users
            FROM map_users
            GROUP BY state
            ORDER BY total_users DESC
            LIMIT 10;
        """
        cursor.execute(query_pie)
        rows = cursor.fetchall()

        # Convert to DataFrame
        df_users = pd.DataFrame(rows, columns=["State", "Registered Users"])

        # Donut chart 
        fig = px.pie(
            df_users,
            names="State",
            values="Registered Users",
            title="Top 10 States by Registered Users",
            hole=0.4,  # Makes it a donut
            color_discrete_sequence=px.colors.sequential.RdBu
        )

        # Display in Streamlit
        st.plotly_chart(fig)

# ======= Apps opens as Null States =========
        query_apps = """
            SELECT state, SUM(registered_users) AS registered_users, SUM(app_opens) AS app_opens
            FROM map_users
            GROUP BY state ORDER BY state ASC LIMIT 15;
        """
        cursor.execute(query_apps)
        rows = cursor.fetchall()

        # Load into DataFrame
        df_apps = pd.DataFrame(rows, columns=["state", "registered_users", "app_opens"])

        # Add status column for coloring
        df_apps["status"] = df_apps["app_opens"].apply(lambda x: "Inactive" if x == 0 else "Active")

        # Create scatter plot
        fig = px.scatter(
            df_apps,
            x="registered_users",
            y="app_opens",
            color="status",
            hover_name="state",
            title="User Registration vs App Opens - least 15 ",
            labels={
                "registered_users": "Registered Users",
                "app_opens": "App Opens"
            },
            color_discrete_map={"Active": "green", "Inactive": "red"}
        )
        st.plotly_chart(fig)

        #======= Top and Bottom states ==
        
        query_top = """
            SELECT state, SUM(registered_users) AS total_users
            FROM map_users
            GROUP BY state
            ORDER BY total_users DESC
            LIMIT 10;
        """
        cursor.execute(query_top)
        rows_top = cursor.fetchall()
        df_top = pd.DataFrame(rows_top, columns=["State", "Registered Users"])

        # Query: Bottom 10 states by insurance registered users
        query_bottom = """
            SELECT state, SUM(registered_users) AS total_users
            FROM map_users
            GROUP BY state
            ORDER BY total_users ASC
            LIMIT 10;
        """
        cursor.execute(query_bottom)
        rows_bottom = cursor.fetchall()
        df_bottom = pd.DataFrame(rows_bottom, columns=["State", "Registered Users"])

        # Top 10 bar chart
        st.subheader("🔝 Top 10 States by Insurance Registered Users")
        fig_top = px.bar(
            df_top,
            x="Registered Users",
            y="State",
            orientation="h",
            color="Registered Users",
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_top)

        # Bottom 10 bar chart
        st.subheader("🧩 Bottom 10 States by Insurance Registered Users")
        fig_bottom = px.bar(
            df_bottom,
            x="Registered Users",
            y="State",
            orientation="h",
            color="Registered Users",
            color_continuous_scale="Oranges"
        )
        st.plotly_chart(fig_bottom)

    

# ==================  Transaction Analysis Across States and Districts =========

    elif data == "Transaction Analysis Across States and Districts" :
        # fetch unique years
        cursor.execute("SELECT DISTINCT year FROM top_transaction ORDER BY year;")
        year = [row[0] for row in cursor.fetchall()]

        # fetch unique quarters
        cursor.execute("SELECT DISTINCT quater FROM top_transaction ORDER BY quater;")
        quarter = [row[0] for row in cursor.fetchall()]

        # streamlit applications
        col1,col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Select the Year:", year)
        with col2 :
            selected_quarter = st.selectbox("Select the Quarter:", quarter)

        #------------ Query Part --------------

        query = """SELECT SUM (transaction_amount), SUM (transaction_count) FROM top_transaction WHERE year = %s AND quater = %s;"""
        cursor.execute(query,(selected_year,selected_quarter))
        result = cursor.fetchone()

        total_amount = result[0] if result[0] is not None else 0 
        total_count = result[1] if result[1] is not None else 0

        st.markdown(f"### Total Transaction Amount : {total_amount}",unsafe_allow_html = True)
        st.markdown(f"### Total Transaction Count : {total_count}", unsafe_allow_html=True)
        
        # --- Get State-wise Transaction Amount ---
        cursor.execute("""
        SELECT state, SUM(transaction_amount) as total_amount,
        SUM(transaction_count) as total_count
        FROM top_transaction
        WHERE year = %s AND quater = %s
        GROUP BY state
        ORDER BY state;
        """, (selected_year, selected_quarter))

        data_rows = cursor.fetchall()
        df_map = pd.DataFrame(data_rows, columns=['state', 'transaction_amount','transaction_count'])
        df_map['transaction_amount'] = pd.to_numeric(df_map['transaction_amount'], errors='coerce')

        state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island','andhra-pradesh' : 'Andhra Pradesh','arunachal-pradesh' : 'Arunachal Pradesh',
        'assam': 'Assam', 'bihar' : 'Bihar', 'chandigarh' : 'Chandigarh', 'chhattisgarh' : 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli', 'delhi': 'Delhi', 'goa' : 'Goa', 'gujarat' : 'Gujarat',
        'haryana' : 'Haryana', 'himachal-pradesh' : 'Himachal Pradesh', 'jammu-&-kashmir' : 'Jammu & Kashmir', 'jharkhand' : 'Jharkhand',
        'karnataka' : 'Karnataka', 'kerala' : 'Kerala', 'ladakh' : 'Ladakh', 'lakshadweep' : 'Lakshadweep', 'madhya-pradesh' : 'Madhya Pradesh',
        'maharashtra' : 'Maharashtra', 'manipur' : 'Manipur', 'meghalaya' : 'Meghalaya', 'mizoram' : 'Mizoram', 'nagaland' : 'Nagaland',
        'odisha': 'Odisha', 'puducherry': 'Puducherry', 'punjab' : 'Punjab', 'rajasthan' : 'Rajasthan', 'sikkim' : 'Sikkim',
        'tamil-nadu' : 'Tamil Nadu', 'telangana' : 'Telangana', 'tripura' : 'Tripura', 'uttar-pradesh' : 'Uttar Pradesh',
        'uttarakhand' : 'Uttarakhand', 'west-bengal' : 'West Bengal'
        }

        df_map['state'] = df_map['state'].replace(state_name_map)
        # India GeoJSON for state boundaries
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

        # Choropleth Map
        fig = px.choropleth(
            df_map,
            geojson=geojson_url,
            featureidkey='properties.ST_NM',
            locations='state',
            color='transaction_amount',
            hover_name='state',  
            hover_data={
                'transaction_amount': True,
                'transaction_count': True
            },
            color_continuous_scale='Reds',
            title=f"State-wise Transaction Amount - {selected_year} Q{selected_quarter}"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # Bar Chart - State-wise Transaction Amount
        st.subheader("📊 Bar Chart: States to be marketed to increase the Transaction Amount")

        query_states = """ SELECT state, SUM(transaction_count) as total_count FROM top_transaction GROUP BY state
                           ORDER BY total_count ASC LIMIT 12;"""
        
        cursor.execute(query_states)
        rows = cursor.fetchall()

        # Convert to DataFrame
        df_count = pd.DataFrame(rows, columns=["state", "transaction_count"])
        bar_fig = px.bar(
            df_count.sort_values(by='transaction_count', ascending=False),
            x='state',
            y='transaction_count',
            text='transaction_count',
            color='transaction_count',
            color_continuous_scale='Purples',
            title=f"State-wise Transaction count (₹) - {selected_year} Q{selected_quarter}"
        )

        bar_fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
        bar_fig.update_layout(xaxis_title="State", yaxis_title="Transaction Count (Units)", xaxis_tickangle=-45)

        st.plotly_chart(bar_fig, use_container_width=True)


                # Get top 5 and bottom 5 states by transaction amount

        query_rel = """
            SELECT state, SUM(transaction_amount) AS transaction_amount
            FROM top_transaction
            GROUP BY state;
        """
        cursor.execute(query_rel)
        rows = cursor.fetchall()

        # --- Create DataFrame ---
        df_txn = pd.DataFrame(rows, columns=["state", "transaction_amount"])
        df_txn["transaction_amount"] = pd.to_numeric(df_txn["transaction_amount"], errors="coerce")

        df_sorted = df_txn.sort_values(by="transaction_amount", ascending=False)
        top_5 = df_sorted.head(5)
        bottom_5 = df_sorted.tail(5)

        #  Scatter plot for Top 5
        st.subheader("📈 Top 5 States by Transaction Amount")
        fig_top = px.scatter(
            top_5,
            x="state",
            y="transaction_amount",
            size="transaction_amount",
            color="transaction_amount",
            hover_name="state",
            color_continuous_scale="Blues",
            title="Top 5 States - Transaction Amount"
        )
        st.plotly_chart(fig_top, use_container_width=True)

        # Step 3: Scatter plot for Bottom 5
        st.subheader("📉 Bottom 5 States by Transaction Amount")
        fig_bottom = px.scatter(
            bottom_5,
            x="state",
            y="transaction_amount",
            size="transaction_amount",
            color="transaction_amount",
            hover_name="state",
            color_continuous_scale="Reds",
            title="Bottom 5 States - Transaction Amount"
        )
        st.plotly_chart(fig_bottom, use_container_width=True)


        #===========  User Registration Analysis ==================

    elif data == "User Registration Analysis" :
        # fetch unique years
        cursor.execute("SELECT DISTINCT year FROM top_user ORDER BY year;")
        year = [row[0] for row in cursor.fetchall()]

        # fetch unique quarters
        cursor.execute("SELECT DISTINCT quater FROM top_user ORDER BY quater;")
        quarter = [row[0] for row in cursor.fetchall()]

        # streamlit applications
        col1,col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Select the Year:", year)
        with col2 :
            selected_quarter = st.selectbox("Select the Quarter:", quarter)

        #------------ Query Part --------------

        query_user = """SELECT SUM (registered_users) FROM top_user WHERE year = %s AND quater = %s;"""
        cursor.execute(query_user,(selected_year,selected_quarter))
        result = cursor.fetchone()

        total_user = result[0] if result[0] is not None else 0 
        
        st.markdown(f"### Total Registered Users : {total_user}",unsafe_allow_html = True)
        
        # --- Get State-wise Registered Users ---
        cursor.execute("""
        SELECT state, SUM(registered_users) as total_users
        FROM top_user
        WHERE year = %s AND quater = %s
        GROUP BY state
        ORDER BY state;
        """, (selected_year, selected_quarter))

        data_rows = cursor.fetchall()
        df_map = pd.DataFrame(data_rows, columns=['state', 'registered_users'])
        df_map['registered_users'] = pd.to_numeric(df_map['registered_users'], errors='coerce')

        state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island','andhra-pradesh' : 'Andhra Pradesh','arunachal-pradesh' : 'Arunachal Pradesh',
        'assam': 'Assam', 'bihar' : 'Bihar', 'chandigarh' : 'Chandigarh', 'chhattisgarh' : 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli', 'delhi': 'Delhi', 'goa' : 'Goa', 'gujarat' : 'Gujarat',
        'haryana' : 'Haryana', 'himachal-pradesh' : 'Himachal Pradesh', 'jammu-&-kashmir' : 'Jammu & Kashmir', 'jharkhand' : 'Jharkhand',
        'karnataka' : 'Karnataka', 'kerala' : 'Kerala', 'ladakh' : 'Ladakh', 'lakshadweep' : 'Lakshadweep', 'madhya-pradesh' : 'Madhya Pradesh',
        'maharashtra' : 'Maharashtra', 'manipur' : 'Manipur', 'meghalaya' : 'Meghalaya', 'mizoram' : 'Mizoram', 'nagaland' : 'Nagaland',
        'odisha': 'Odisha', 'puducherry': 'Puducherry', 'punjab' : 'Punjab', 'rajasthan' : 'Rajasthan', 'sikkim' : 'Sikkim',
        'tamil-nadu' : 'Tamil Nadu', 'telangana' : 'Telangana', 'tripura' : 'Tripura', 'uttar-pradesh' : 'Uttar Pradesh',
        'uttarakhand' : 'Uttarakhand', 'west-bengal' : 'West Bengal'
        }

        df_map['state'] = df_map['state'].replace(state_name_map)
        # India GeoJSON for state boundaries
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

        # Choropleth Map
        fig = px.choropleth(
            df_map,
            geojson=geojson_url,
            featureidkey='properties.ST_NM',
            locations='state',
            color='registered_users',
            color_continuous_scale = 'Greens',
            title=f"State-wise Registerted Users - {selected_year} Q{selected_quarter}"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)

        # --------------- most users registered during a specific year-quarter combination ----------

        query_com = f"""
            SELECT state, SUM(registered_users) AS registered_users
            FROM top_user
            WHERE year = {selected_year} AND quater = {selected_quarter}
            GROUP BY state
            ORDER BY registered_users DESC;
        """
        cursor.execute(query_com)
        rows = cursor.fetchall()

        df = pd.DataFrame(rows, columns=["state", "registered_users"])

        # Horizontal bar chart
        fig = px.bar(
            df,
            x="registered_users",
            y="state",
            orientation="h",
            color="registered_users",
            title=f"Registered Users by State - {selected_year} Q{selected_quarter}"
        )

        fig.update_layout(yaxis=dict(autorange="reversed"))  # highest on top
        st.plotly_chart(fig, use_container_width=True)


        # ===================  All data in single plot line chart ===============

        # Query all year, quarter and registered_users
        query_all = """
            SELECT year, quater, SUM(registered_users) as total_users
            FROM top_user
            GROUP BY year, quater
            ORDER BY year, quater;
        """
        cursor.execute(query_all)
        rows = cursor.fetchall()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=["year", "quater", "total_users"])

        # Create a combined column for year-quarter
        df["year_quarter"] = df["year"].astype(str) + " Q" + df["quater"].astype(str)

        # Sort by year and quarter again for proper line continuity
        df = df.sort_values(by=["year", "quater"])

        # Plot the line chart
        fig = px.line(
            df,
            x="year_quarter",
            y="total_users",
            markers=True,
            title="📈 Registered Users Trend Over All Year-Quarter",
            labels={"year_quarter": "Year - Quarter", "total_users": "Registered Users"},
        )

        # Show in Streamlit
        st.plotly_chart(fig, use_container_width=True)



    # --------------------------   Insurance Transactions Analysis  ------------------
    elif data == "Insurance Transactions Analysis" :
        # fetch unique years
        cursor.execute("SELECT DISTINCT year FROM top_insurance ORDER BY year;")
        year = [row[0] for row in cursor.fetchall()]

        # fetch unique quarters
        cursor.execute("SELECT DISTINCT quater FROM top_insurance ORDER BY quater;")
        quarter = [row[0] for row in cursor.fetchall()]

        # streamlit applications
        col1,col2 = st.columns(2)
        with col1:
            selected_year = st.selectbox("Select the Year:", year)
        with col2 :
            selected_quarter = st.selectbox("Select the Quarter:", quarter)

        #------------ Query Part --------------

        query_ins = """SELECT SUM (transaction_amount), SUM (transaction_count) FROM top_insurance WHERE year = %s AND quater = %s;"""
        cursor.execute(query_ins,(selected_year,selected_quarter))
        result = cursor.fetchone()

        total_amount = result[0] if result[0] is not None else 0 
        total_count = result[1] if result[1] is not None else 0
        
        st.markdown(f"### Total Transaction Amount : {total_amount}",unsafe_allow_html = True)
        st.markdown(f"### Total Transaction Count : {total_count}", unsafe_allow_html=True)
        
        # --- Get State-wise Transaction_amount and transaction_count ---

        cursor.execute("""
        SELECT state, SUM(transaction_amount) as total_amount,
        SUM(transaction_count) as total_count
        FROM top_insurance
        WHERE year = %s AND quater = %s
        GROUP BY state
        ORDER BY state;
        """, (selected_year, selected_quarter))

        data_rows = cursor.fetchall()
        df_map = pd.DataFrame(data_rows, columns=['state', 'transaction_amount', 'transaction_count'])
        df_map['transaction_amount'] = pd.to_numeric(df_map['transaction_amount'], errors='coerce')
        df_map['transaction_count'] = pd.to_numeric(df_map['transaction_count'], errors='coerce')

        state_name_map = {
        'andaman-&-nicobar-islands': 'Andaman & Nicobar Island','andhra-pradesh' : 'Andhra Pradesh','arunachal-pradesh' : 'Arunachal Pradesh',
        'assam': 'Assam', 'bihar' : 'Bihar', 'chandigarh' : 'Chandigarh', 'chhattisgarh' : 'Chhattisgarh',
        'dadra-&-nagar-haveli-&-daman-&-diu': 'Dadra and Nagar Haveli', 'delhi': 'Delhi', 'goa' : 'Goa', 'gujarat' : 'Gujarat',
        'haryana' : 'Haryana', 'himachal-pradesh' : 'Himachal Pradesh', 'jammu-&-kashmir' : 'Jammu & Kashmir', 'jharkhand' : 'Jharkhand',
        'karnataka' : 'Karnataka', 'kerala' : 'Kerala', 'ladakh' : 'Ladakh', 'lakshadweep' : 'Lakshadweep', 'madhya-pradesh' : 'Madhya Pradesh',
        'maharashtra' : 'Maharashtra', 'manipur' : 'Manipur', 'meghalaya' : 'Meghalaya', 'mizoram' : 'Mizoram', 'nagaland' : 'Nagaland',
        'odisha': 'Odisha', 'puducherry': 'Puducherry', 'punjab' : 'Punjab', 'rajasthan' : 'Rajasthan', 'sikkim' : 'Sikkim',
        'tamil-nadu' : 'Tamil Nadu', 'telangana' : 'Telangana', 'tripura' : 'Tripura', 'uttar-pradesh' : 'Uttar Pradesh',
        'uttarakhand' : 'Uttarakhand', 'west-bengal' : 'West Bengal'
        }

        df_map['state'] = df_map['state'].replace(state_name_map)
        # India GeoJSON for state boundaries
        geojson_url = "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"

        # Choropleth Map
        fig = px.choropleth(
            df_map,
            geojson=geojson_url,
            featureidkey='properties.ST_NM',
            locations='state',
            color='transaction_amount',
            hover_name='state',  
            hover_data={
                'transaction_amount': True,
                'transaction_count': True
            },
            color_continuous_scale = 'Reds',
            title=f"State-wise Transaction Amount - {selected_year} Q{selected_quarter}"
        )

        fig.update_geos(fitbounds="locations", visible=False)
        st.plotly_chart(fig, use_container_width=True)


        #--------  High Vs Low Trx States

        # --- Sample query ---
        query_trx = """
            SELECT state, SUM(transaction_amount) AS total_amount,
            SUM(transaction_count) AS total_count
            FROM top_insurance
            GROUP BY state
            ORDER BY total_count DESC;
        """
        cursor.execute(query_trx)
        rows = cursor.fetchall()

        # --- Convert to DataFrame ---
        df = pd.DataFrame(rows, columns=["State", "Total Transaction Amount", "Total Transaction Count"])

        df_sorted = df.sort_values(by="Total Transaction Count", ascending=False)

        # --- Top 5 states ---
        top_10 = df_sorted.head(5).reset_index(drop=True)

        # --- Bottom 5 states ---
        bottom_10 = df_sorted.tail(5).reset_index(drop=True)


        side1,side2 = st.columns(2)
        with side1 :
            # --- Display in Streamlit ---
            st.subheader("📋 Top 10 States by Total Transaction Count")
            st.table(top_10)
        with side2:
            st.subheader("📉 Bottom 10 States by Total Transaction Counts")
            st.table(bottom_10)


    # ----------------- Years wise sales =============

        # --- SQL Query: Year-wise total sales ---
        query_last = """
            SELECT year, SUM(transaction_amount) AS total_amount
            FROM top_insurance
            GROUP BY year
            ORDER BY year;
        """
        cursor.execute(query_last)
        rows = cursor.fetchall()

        # --- Convert to DataFrame ---
        df = pd.DataFrame(rows, columns=["Year", "Total_Amount"])

        # --- Pie Chart ---
        fig = px.pie(
            df,
            names="Year",
            values="Total_Amount",
            title="🧾 Year-wise Sales Distribution",
        )

        # Display in Streamlit
        st.plotly_chart(fig, use_container_width=True)



