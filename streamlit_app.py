import streamlit as st
import pandas as pd
import pymysql
pymysql.install_as_MySQLdb()
from sqlalchemy import create_engine, text

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="OLA Analytics Platform",
    layout="wide",
    page_icon="🚖"
)

st.title("🚖 OLA Ride Analysis")

# -------------------------------------------------
# DATABASE CONNECTION
# -------------------------------------------------
@st.cache_resource
def get_engine():
    DB_USER = st.secrets["DB_USER"]
    DB_PASSWORD = st.secrets["DB_PASSWORD"]
    DB_HOST = st.secrets["DB_HOST"]
    DB_PORT = st.secrets["DB_PORT"]
    DB_NAME = st.secrets["DB_NAME"]

    connection_string = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
        f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

    engine = create_engine(
        connection_string,
        connect_args={"ssl": {"ssl_disabled": False}}
    )

    return engine


engine = get_engine()

# -------------------------------------------------
# SQL QUERIES DICTIONARY
# -------------------------------------------------
queries = {
    "1️⃣ Successful Bookings": """
        SELECT *
        FROM clean_ola_data
        WHERE Booking_Status = 'Success';
    """,

    "2️⃣ Avg Ride Distance per Vehicle": """
        SELECT Vehicle_Type, AVG(Ride_Distance) AS Avg_distance
        FROM clean_ola_data
        GROUP BY Vehicle_Type;
    """,

    "3️⃣ Cancelled by Customer Count": """
        SELECT COUNT(*) AS Cancelled_by_customer
        FROM clean_ola_data
        WHERE Booking_Status = 'Canceled by Customer';
    """,

    "4️⃣ Top 5 Customers by Rides": """
        SELECT Customer_ID, COUNT(*) AS Total_rides
        FROM clean_ola_data
        GROUP BY Customer_ID
        ORDER BY Total_rides DESC
        LIMIT 5;
    """,

    "5️⃣ Driver Cancellations (Personal Issues)": """
        SELECT COUNT(*) AS Driver_cancellations
        FROM clean_ola_data
        WHERE Booking_Status = 'Canceled by Driver'
        AND Canceled_Rides_by_Driver = 'Personal & Car related issue';
    """,

    "6️⃣ Max & Min Driver Rating (Prime Sedan)": """
        SELECT 
        MAX(Driver_Ratings) AS max_rating,
        MIN(Driver_Ratings) AS min_rating
        FROM clean_ola_data
        WHERE Vehicle_Type = 'Prime Sedan';
    """,

    "7️⃣ Rides Paid via UPI": """
        SELECT *
        FROM clean_ola_data
        WHERE Payment_Method = 'UPI';
    """,

    "8️⃣ Avg Customer Rating per Vehicle": """
        SELECT Vehicle_Type,
        AVG(Customer_Rating) AS avg_customer_rating
        FROM clean_ola_data
        GROUP BY Vehicle_Type;
    """,

    "9️⃣ Total Revenue (Successful Rides)": """
        SELECT SUM(Booking_Value) AS total_revenue
        FROM clean_ola_data
        WHERE Booking_Status = 'Success';
    """,

    "🔟 Incomplete Rides with Reason": """
        SELECT Booking_ID,
        Booking_Status,
        Incomplete_Rides_Reason
        FROM clean_ola_data
        WHERE Incomplete_Rides = 'Yes';
    """
}

# -------------------------------------------------
# CREATE TABS
# -------------------------------------------------
tab1, tab2 = st.tabs(["📊 Power BI Dashboard", "📈 SQL Query Analysis"])

# =================================================
# TAB 1 — POWER BI
# =================================================
with tab1:
    st.subheader("📊 Interactive Power BI Dashboard")
    powerbi_url = st.secrets["POWERBI_EMBED_URL"]

    st.components.v1.iframe(
        powerbi_url,
        width=1500,
        height=800,
        scrolling=True
    )

# =================================================
# TAB 2 — SQL ANALYSIS
# =================================================
with tab2:

    st.subheader("📈 SQL Business Analysis")

    selected_query = st.selectbox(
        "Select Business Question",
        list(queries.keys())
    )

    if selected_query:
        query = queries[selected_query]

        with st.spinner("Running Query..."):
            df = pd.read_sql(query, engine)

        st.success("Query Executed Successfully")

        # If single value result → show metric
        if df.shape[1] == 1 and df.shape[0] == 1:
            value = df.iloc[0, 0]
            st.metric(label="Result", value=value)
        else:
            st.dataframe(df, use_container_width=True)

            col1, col2 = st.columns(2)
            col1.metric("Rows Returned", df.shape[0])
            col2.metric("Columns", df.shape[1])

            csv = df.to_csv(index=False).encode("utf-8")

            st.download_button(
                label="Download Result as CSV",
                data=csv,
                file_name="query_result.csv",
                mime="text/csv"
            )