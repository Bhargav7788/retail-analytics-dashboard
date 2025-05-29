import streamlit as st
import sqlite3
import pandas as pd
from prophet import Prophet
from prophet.plot import plot_plotly
import plotly.graph_objs as go
import requests
from streamlit_lottie import st_lottie

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Retail Analytics Dashboard", layout="wide")

# ✅ Load verified Lottie animation
def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

lottie_chart = load_lottieurl("https://assets10.lottiefiles.com/packages/lf20_w51pcehl.json")

# ✅ Display header with or without animation
if lottie_chart:
    col1, col2 = st.columns([1, 3])
    with col1:
        st_lottie(lottie_chart, height=200, speed=1, loop=True, quality="high")
    with col2:
        st.title("📊 Retail Analytics Dashboard")
        st.markdown("Get real-time insights into your sales, profit, and trends — all in one place.")
else:
    st.title("📊 Retail Analytics Dashboard")
    st.markdown("Get real-time insights into your sales, profit, and trends — all in one place.")

# ------------------ DB CONNECTION ------------------
conn = sqlite3.connect("retail_analytics.db")

# ------------------ TOP PRODUCTS ------------------
st.subheader("🏆 Top 10 Best-Selling Products")
query1 = """
SELECT [Product Name], ROUND(SUM(Sales), 2) AS Total_Sales
FROM orders
GROUP BY [Product Name]
ORDER BY Total_Sales DESC
LIMIT 10;
"""
df1 = pd.read_sql_query(query1, conn)
st.bar_chart(df1.set_index("Product Name"))

# ------------------ PROFIT BY REGION ------------------
st.subheader("📍 Total Profit by Region")
query2 = """
SELECT Region, ROUND(SUM(Profit), 2) AS Total_Profit
FROM orders
GROUP BY Region
ORDER BY Total_Profit DESC;
"""
df2 = pd.read_sql_query(query2, conn)
st.bar_chart(df2.set_index("Region"))

# ------------------ MONTHLY REVENUE ------------------
st.subheader("📈 Monthly Revenue Trend")
query3 = """
SELECT 
    strftime('%Y-%m', substr([Order Date], 7, 4) || '-' ||
                      substr([Order Date], 1, 2) || '-' ||
                      substr([Order Date], 4, 2)) AS Month,
    ROUND(SUM(Sales), 2) AS Total_Sales
FROM orders
WHERE Month IS NOT NULL
GROUP BY Month
ORDER BY Month;
"""
df3 = pd.read_sql_query(query3, conn)
st.line_chart(df3.set_index("Month"))

# ------------------ TOP CUSTOMERS ------------------
st.subheader("👤 Top 5 Customers by Total Spend")
query4 = """
SELECT [Customer Name], ROUND(SUM(Sales), 2) AS Total_Spend
FROM orders
GROUP BY [Customer Name]
ORDER BY Total_Spend DESC
LIMIT 5;
"""
df4 = pd.read_sql_query(query4, conn)
st.dataframe(df4)

# ------------------ CATEGORY STATS ------------------
st.subheader("📦 Sales & Profit by Product Category")
query5 = """
SELECT Category, ROUND(SUM(Sales), 2) AS Total_Sales, ROUND(SUM(Profit), 2) AS Total_Profit
FROM orders
GROUP BY Category
ORDER BY Total_Sales DESC;
"""
df5 = pd.read_sql_query(query5, conn)
st.dataframe(df5)

# ------------------ FORECASTING ------------------
st.subheader("🔮 Monthly Sales Forecast")
query_forecast = """
SELECT 
    strftime('%Y-%m', substr([Order Date], 7, 4) || '-' ||
                      substr([Order Date], 1, 2) || '-' ||
                      substr([Order Date], 4, 2)) AS Month,
    SUM(Sales) AS Total_Sales
FROM orders
GROUP BY Month
ORDER BY Month;
"""
df_monthly = pd.read_sql_query(query_forecast, conn)

df_prophet = df_monthly.rename(columns={"Month": "ds", "Total_Sales": "y"})
df_prophet["ds"] = pd.to_datetime(df_prophet["ds"], errors="coerce")
df_prophet = df_prophet.dropna(subset=["ds", "y"])

model = Prophet()
model.fit(df_prophet)
future = model.make_future_dataframe(periods=6, freq="M")
forecast = model.predict(future)

fig = plot_plotly(model, forecast)
st.plotly_chart(fig)

with st.expander("📋 View Forecast Data"):
    st.write(forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(6))

# ------------------ TEXT TO SQL ------------------
st.subheader("💬 Smart SQL Assistant (Offline Mode)")
query_map = {
    "sales by category": """
        SELECT Category, ROUND(SUM(Sales), 2) AS Total_Sales
        FROM orders
        GROUP BY Category
        ORDER BY Total_Sales DESC;
    """,
    "profit by region": """
        SELECT Region, ROUND(SUM(Profit), 2) AS Total_Profit
        FROM orders
        GROUP BY Region
        ORDER BY Total_Profit DESC;
    """,
    "top customers": """
        SELECT [Customer Name], ROUND(SUM(Sales), 2) AS Total_Spend
        FROM orders
        GROUP BY [Customer Name]
        ORDER BY Total_Spend DESC
        LIMIT 5;
    """,
    "monthly revenue": """
        SELECT strftime('%Y-%m', substr([Order Date], 7, 4) || '-' ||
                                  substr([Order Date], 1, 2) || '-' ||
                                  substr([Order Date], 4, 2)) AS Month,
        ROUND(SUM(Sales), 2) AS Total_Sales
        FROM orders
        GROUP BY Month
        ORDER BY Month;
    """
}
user_question = st.text_input("Ask me something (e.g., sales by category, top customers, profit by region):")
if user_question:
    matched_query = None
    for key in query_map:
        if key in user_question.lower():
            matched_query = query_map[key]
            break
    if matched_query:
        try:
            result = pd.read_sql_query(matched_query, conn)
            st.success("✅ Query executed successfully!")
            st.dataframe(result)
        except Exception as e:
            st.error(f"⚠️ Error executing query: {e}")
    else:
        st.warning("🤔 Try: sales by category, top customers, or profit by region.")

# ------------------ FILTER SECTION ------------------
st.subheader("🎛️ Interactive Drilldown: Analyze by Year, Region, and Category")

df_full = pd.read_sql_query("SELECT * FROM orders", conn)
df_full["Order Date"] = pd.to_datetime(df_full["Order Date"], errors="coerce")
df_full = df_full.dropna(subset=["Order Date"])
df_full["Year"] = df_full["Order Date"].dt.year
years = sorted(df_full["Year"].dropna().unique())
regions = sorted(df_full["Region"].dropna().unique())
categories = sorted(df_full["Category"].dropna().unique())

col1, col2, col3 = st.columns(3)
year_selected = col1.selectbox("Select Year", years, index=len(years)-1)
region_selected = col2.selectbox("Select Region", ["All"] + regions)
category_selected = col3.selectbox("Select Category", ["All"] + categories)

filtered_df = df_full[df_full["Year"] == year_selected]
if region_selected != "All":
    filtered_df = filtered_df[filtered_df["Region"] == region_selected]
if category_selected != "All":
    filtered_df = filtered_df[filtered_df["Category"] == category_selected]

st.markdown(f"📦 Showing data for **{year_selected}**, **{region_selected if region_selected != 'All' else 'All Regions'}**, **{category_selected if category_selected != 'All' else 'All Categories'}**")
st.write(f"Total Orders: {len(filtered_df)}")

col4, col5 = st.columns(2)
col4.metric("💰 Total Sales", f"${filtered_df['Sales'].sum():,.2f}")
col5.metric("📈 Total Profit", f"${filtered_df['Profit'].sum():,.2f}")
st.bar_chart(filtered_df.groupby("Sub-Category")["Sales"].sum().sort_values(ascending=False))

# ------------------ CLOSE DB ------------------
conn.close()
