import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

plt.style.use("ggplot")
PRIMARY = "#0984E3"    # biru utama
SECONDARY = "#74B9FF"  # biru soft
ACCENT = "#A29BFE"     # ungu soft
SUCCESS = "#00B894"    # hijau
DANGER = "#D63031"     # merah

st.set_page_config(
    page_title="E-Commerce RFM Dashboard",
    page_icon="🛒",
    layout="wide"
)


df = pd.read_csv("ecommerce_data.csv")
rfm_df = pd.read_csv("rfm_data.csv")

df["order_purchase_timestamp"] = pd.to_datetime(df["order_purchase_timestamp"])
df["order_delivered_customer_date"] = pd.to_datetime(df["order_delivered_customer_date"])

rfm_df["segment"] = rfm_df["segment"].astype(str).str.strip()


df = df.merge(
    rfm_df[["customer_unique_id", "segment"]],
    on="customer_unique_id",
    how="left"
)

df["segment"] = df["segment"].fillna("Unknown")


# SIDEBAR
with st.sidebar:
    st.title("📊 Filter Dashboard")
    st.caption("By Avelina")

    min_date = df["order_purchase_timestamp"].min()
    max_date = df["order_purchase_timestamp"].max()

    start_date = st.date_input("Start Date", min_date)
    end_date = st.date_input("End Date", max_date)

df_filtered = df[
    (df["order_purchase_timestamp"] >= pd.to_datetime(start_date)) &
    (df["order_purchase_timestamp"] <= pd.to_datetime(end_date))
].copy()


df_ship = df_filtered.dropna(
    subset=["order_delivered_customer_date", "order_purchase_timestamp"]
).copy()

df_ship["shipping_duration"] = (
    df_ship["order_delivered_customer_date"] -
    df_ship["order_purchase_timestamp"]
).dt.days


# HEADER
st.title("🛒 E-Commerce Analytics Dashboard")
st.caption("By Avelina Garcia Wong")

st.markdown("---")

# KPI
st.subheader("📊 Key Metrics")
col1, col2, col3 = st.columns(3)

col1.metric("💰 Revenue", f"{df_filtered['price'].sum():,.0f}")
col2.metric("🧾 Orders", df_filtered["order_id"].nunique())
col3.metric("👥 Customers", df_filtered["customer_id"].nunique())

st.markdown("---")


# TOP PRODUCT
st.header("1️⃣ Top Product by Top Customers")

top_customers = df_filtered[
    df_filtered["segment"].str.contains("Top", case=False, na=False)
]["customer_id"]

df_top = df_filtered[df_filtered["customer_id"].isin(top_customers)]

if df_top.empty:
    df_top = df_filtered

top_products = (
    df_top.groupby("category")["order_id"]
    .count()
    .sort_values(ascending=False)
    .head(10)
)

col1, col2 = st.columns([3,1])

with col1:
    fig, ax = plt.subplots()
    top_products.sort_values().plot(
        kind="barh",
        ax=ax,
        color=PRIMARY
    )
    ax.set_xlabel("Jumlah Order")
    ax.set_title("Top Product (Top Customers)")
    st.pyplot(fig)

with col2:
    st.subheader("📌 Insight")
    st.metric("Top Category", top_products.index[0])

st.markdown("---")

# REVENUE CATEGORY & SEGMENT

st.header("2️⃣ Revenue by Category & Segment")

# Chart 1
category_revenue = df_filtered.groupby('category')['total_price'] \
    .sum().sort_values(ascending=False).head(10)

fig1, ax1 = plt.subplots(figsize=(10,5))
category_revenue.plot(
    kind='bar',
    ax=ax1,
    color=PRIMARY
)
ax1.set_title('Top Product Categories by Revenue')
ax1.set_ylabel("Revenue")
st.pyplot(fig1)

# Chart 2
segment_category = df_filtered.groupby(
    ['category', 'segment']
)['total_price'].sum().reset_index()

pivot = segment_category.pivot(
    index='category',
    columns='segment',
    values='total_price'
).fillna(0)

pivot = pivot.loc[
    pivot.sum(axis=1).sort_values(ascending=False).index
].head(10)

fig2, ax2 = plt.subplots(figsize=(12,6))
pivot.plot(
    kind='bar',
    ax=ax2,
    color=[PRIMARY, SECONDARY, ACCENT]
)
ax2.set_title('Revenue by Category & Segment')
ax2.set_ylabel("Revenue")
st.pyplot(fig2)

col1, col2 = st.columns(2)

col1.metric("Top Category", category_revenue.idxmax())
col2.metric("Highest Revenue", f"{category_revenue.max():,.0f}")

st.markdown("---")


# SHIPPING PERFORMANCE
st.header("3️⃣ Shipping Performance")
shipping_state = df_ship.groupby("customer_state")["shipping_duration"].mean().sort_values()
col1, col2 = st.columns(2)

with col1:
    st.subheader("🚀 Fastest Delivery")

    st.metric("State", shipping_state.idxmin())
    st.metric("Avg Days", f"{shipping_state.min():.2f}")

    fig, ax = plt.subplots()
    shipping_state.head(10).plot(
        kind="bar",
        ax=ax,
        color=SUCCESS
    )
    st.pyplot(fig)

with col2:
    st.subheader("🐢 Slowest Delivery")

    st.metric("State", shipping_state.idxmax())
    st.metric("Avg Days", f"{shipping_state.max():.2f}")

    fig, ax = plt.subplots()
    shipping_state.tail(10).plot(
        kind="bar",
        ax=ax,
        color=DANGER
    )
    st.pyplot(fig)

st.markdown("---")


# FOOTER
st.caption("📊 Built with Streamlit | © Avelina Garcia Wong 2026")