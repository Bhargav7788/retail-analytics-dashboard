import sqlite3
import pandas as pd

# Connect to the SQLite database
conn = sqlite3.connect("retail_analytics.db")

# QUERY 1: Top 10 Best-Selling Products
print("\n✅ Top 10 Best-Selling Products by Total Sales:\n")
query1 = """
SELECT 
    [Product Name], 
    ROUND(SUM(Sales), 2) AS Total_Sales
FROM orders
GROUP BY [Product Name]
ORDER BY Total_Sales DESC
LIMIT 10;
"""
df1 = pd.read_sql_query(query1, conn)
print(df1.to_string(index=False))

# QUERY 2: Profit by Region
print("\n📍 Total Profit by Region:\n")
query2 = """
SELECT 
    Region,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM orders
GROUP BY Region
ORDER BY Total_Profit DESC;
"""
df2 = pd.read_sql_query(query2, conn)
print(df2.to_string(index=False))

# QUERY 3: Monthly Revenue Trend (fixed parsing MM/DD/YYYY to proper date)
print("\n📈 Monthly Revenue Trend:\n")
query3 = """
SELECT 
    strftime('%Y-%m', substr([Order Date], 7, 4) || '-' || substr([Order Date], 1, 2) || '-' || substr([Order Date], 4, 2)) AS Month,
    ROUND(SUM(Sales), 2) AS Total_Sales
FROM orders
GROUP BY Month
ORDER BY Month;
"""
df3 = pd.read_sql_query(query3, conn)
print(df3.to_string(index=False))

df3 = pd.read_sql_query(query3, conn)
print(df3.to_string(index=False))

# QUERY 4: Top 5 Customers by Total Spend
print("\n👤 Top 5 Customers by Total Spend:\n")
query4 = """
SELECT 
    [Customer Name],
    ROUND(SUM(Sales), 2) AS Total_Spend
FROM orders
GROUP BY [Customer Name]
ORDER BY Total_Spend DESC
LIMIT 5;
"""
df4 = pd.read_sql_query(query4, conn)
print(df4.to_string(index=False))

# QUERY 5: Sales & Profit by Category
print("\n📦 Sales & Profit by Product Category:\n")
query5 = """
SELECT 
    Category,
    ROUND(SUM(Sales), 2) AS Total_Sales,
    ROUND(SUM(Profit), 2) AS Total_Profit
FROM orders
GROUP BY Category
ORDER BY Total_Sales DESC;
"""
df5 = pd.read_sql_query(query5, conn)
print(df5.to_string(index=False))

# Close the connection
conn.close()
