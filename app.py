import streamlit as st
import snowflake.connector
import pandas as pd

# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="Enterprise Sales Dashboard",
    layout="wide"
)



st.title("📊 Internal Hackathon : Enterprise Sales Analytics Dashboard")

# --------------------------------------------------
# Create Snowflake Connection (Streamlit Cloud)
# --------------------------------------------------
@st.cache_resource
def get_connection():
    return snowflake.connector.connect(
        user=st.secrets["snowflake"]["user"],
        password=st.secrets["snowflake"]["password"],
        account=st.secrets["snowflake"]["account"],
        warehouse=st.secrets["snowflake"]["warehouse"],
        database=st.secrets["snowflake"]["database"],
        schema=st.secrets["snowflake"]["schema"],
        role=st.secrets["snowflake"]["role"]
    )

conn = get_connection()

def load_df(sql):
    return pd.read_sql(sql, conn)

# --------------------------------------------------
# Executive Summary
# --------------------------------------------------
st.header("📌 Executive Summary")

exec_df = load_df("""
    SELECT * FROM VW_EXEC_SUMMARY
""")

c1, c2, c3, c4, c5 = st.columns(5)

c1.metric("Total Orders", int(exec_df["TOTAL_ORDERS"][0]))
c2.metric("Total Revenue", f"{exec_df['TOTAL_REVENUE'][0]:,.2f}")
c3.metric("Avg Order Value", f"{exec_df['AVG_ORDER_VALUE'][0]:,.2f}")
c4.metric("Total Customers", int(exec_df["TOTAL_CUSTOMERS"][0]))
c5.metric("Total Products", int(exec_df["TOTAL_PRODUCTS"][0]))

st.divider()

# --------------------------------------------------
# Revenue by Region
# --------------------------------------------------
st.header("🌍 Revenue by Region")

region_df = load_df("""
    SELECT * FROM VW_REVENUE_BY_REGION
""")

st.bar_chart(
    region_df.set_index("REGION")["TOTAL_REVENUE"]
)

st.dataframe(region_df, use_container_width=True)

st.divider()

# --------------------------------------------------
# Revenue by Category
# --------------------------------------------------
st.header("📦 Revenue by Category")

cat_df = load_df("""
    SELECT * FROM VW_REVENUE_BY_CATEGORY
""")

st.bar_chart(
    cat_df.set_index("CATEGORY")["TOTAL_REVENUE"]
)

st.dataframe(cat_df, use_container_width=True)

st.divider()

# --------------------------------------------------
# Top 5 Customers
# --------------------------------------------------
st.header("🏆 Top 5 Customers")

cust_df = load_df("""
    SELECT
        NAME,
        TOTAL_REVENUE
    FROM VW_TOP_CUSTOMERS
    ORDER BY TOTAL_REVENUE DESC
    LIMIT 5
""")

st.dataframe(cust_df, use_container_width=True)

st.bar_chart(
    cust_df.set_index("NAME")["TOTAL_REVENUE"]
)

st.divider()

# --------------------------------------------------
# Monthly Revenue Trend
# --------------------------------------------------
st.header("📈 Monthly Revenue Trend")

trend_df = load_df("""
    SELECT * FROM VW_MONTHLY_TREND
""")

trend_df["YEAR_MONTH"] = (
    trend_df["YEAR"].astype(str) + "-" +
    trend_df["MONTH"].astype(str).str.zfill(2)
)

trend_df = trend_df.sort_values("YEAR_MONTH")

st.line_chart(
    trend_df.set_index("YEAR_MONTH")["TOTAL_REVENUE"]
)

st.dataframe(trend_df, use_container_width=True)

st.divider()

# --------------------------------------------------
# Monthly Revenue Growth %
# --------------------------------------------------
st.header("📊 Monthly Revenue Growth (%)")

growth_df = load_df("""
    SELECT * FROM VW_MONTHLY_REVENUE_GROWTH
""")

growth_df = growth_df.dropna(subset=["GROWTH_PERCENT"])

growth_df["YEAR_MONTH"] = (
    growth_df["YEAR"].astype(str) + "-" +
    growth_df["MONTH"].astype(str).str.zfill(2)
)

growth_df = growth_df.sort_values("YEAR_MONTH")

st.line_chart(
    growth_df.set_index("YEAR_MONTH")["GROWTH_PERCENT"]
)

st.dataframe(growth_df, use_container_width=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.caption("Source: Snowflake ENTERPRISE_DB | GOLD Layer | Streamlit Cloud")
