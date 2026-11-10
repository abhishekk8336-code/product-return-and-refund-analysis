import streamlit as st
import pandas as pd
import plotly.express as px

from utils.calculations import (
    calculate_overview,
    category_analysis,
    return_reason_analysis,
    monthly_analysis,
    top_returned_products,
    regional_analysis
)

# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="Product Return & Refund Analytics",
    page_icon="📊",
    layout="wide"
)

# ---------------- CUSTOM CSS ----------------

st.markdown("""
<style>
    .main {
        background-color: #f5f7fb;
    }

    .block-container {
        padding-top: 2rem;
    }

    div[data-testid="stMetric"] {
        background-color: white;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 2px 5px rgba(0,0,0,0.04);
    }

    h1, h2, h3 {
        color: #172554;
    }
</style>
""", unsafe_allow_html=True)


# ---------------- LOAD DATA ----------------

@st.cache_data
def load_data():
    df = pd.read_csv(
        "data/ecommerce_returns_cleaned.csv",
        parse_dates=["Order_Date", "Return_Date"]
    )
    return df


# ---------------- HEADER ----------------

st.title("📊 Product Return & Refund Analytics")

st.markdown(
    "### E-commerce Business Intelligence Dashboard"
)

st.caption(
    "Analyze product returns, refund patterns and customer behavior."
)

st.divider()


# ---------------- SIDEBAR ----------------

st.sidebar.title("📈 Analytics Panel")

page = st.sidebar.radio(
    "Navigation",
    [
        "Overview",
        "Product Analysis",
        "Return Analysis",
        "Time Analysis",
        "Regional Analysis"
    ]
)

st.sidebar.divider()

st.sidebar.subheader("Dataset")


# ---------------- DATA UPLOAD ----------------

uploaded_file = st.sidebar.file_uploader(
    "Upload CSV Dataset",
    type=["csv"]
)

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)

        required_columns = [
            "Order_ID", "Order_Date", "Product_Name",
            "Category", "Quantity", "Unit_Price",
            "Region", "Return_Status", "Return_Reason",
            "Refund_Amount", "Refund_Status"
        ]

        missing_columns = [
            col for col in required_columns if col not in df.columns
        ]

        if missing_columns:
            st.error(f"Missing columns: {missing_columns}")
            st.stop()

        df["Order_Date"] = pd.to_datetime(
            df["Order_Date"], errors="coerce"
        )

        df["Return_Date"] = pd.to_datetime(
            df["Return_Date"], errors="coerce"
        )

        df = df.dropna(subset=["Order_ID", "Order_Date"])

        df = df.drop_duplicates(subset=["Order_ID"])

        df["Refund_Amount"] = pd.to_numeric(
            df["Refund_Amount"], errors="coerce"
        ).fillna(0)

        st.sidebar.success("Dataset uploaded successfully!")

    except Exception as e:
        st.error(f"Unable to load dataset: {e}")
        st.stop()

else:
    df = load_data()


# ---------------- FILTERS ----------------

st.sidebar.divider()
st.sidebar.subheader("Filters")

df = df.copy()

if df.empty:
    st.warning("No valid records found in the dataset.")
    st.stop()

min_date = df["Order_Date"].min().date()
max_date = df["Order_Date"].max().date()

date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

categories = sorted(df["Category"].dropna().unique())

selected_categories = st.sidebar.multiselect(
    "Select Categories",
    categories,
    default=categories
)

regions = sorted(df["Region"].dropna().unique())

selected_regions = st.sidebar.multiselect(
    "Select Regions",
    regions,
    default=regions
)

# Apply filters
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:

    start_date, end_date = date_range

    df = df[
        (df["Order_Date"].dt.date >= start_date) &
        (df["Order_Date"].dt.date <= end_date)
    ]

df = df[
    (df["Category"].isin(selected_categories)) &
    (df["Region"].isin(selected_regions))
]

if df.empty:
    st.warning("No records match the selected filters.")
    st.stop()


# ---------------- OVERVIEW ----------------

if page == "Overview":

    st.subheader("Business Performance Overview")

    overview = calculate_overview(df)

    # KPI cards
    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Orders",
        f"{overview['Total Orders']:,}"
    )

    col2.metric(
        "Returned Orders",
        f"{overview['Returned Orders']:,}"
    )

    col3.metric(
        "Return Rate",
        f"{overview['Return Rate (%)']}%"
    )

    col4.metric(
        "Total Refund",
        f"₹{overview['Total Refund Amount']:,.0f}"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:

        category_df = category_analysis(df)

        fig = px.bar(
            category_df,
            x="Category",
            y="Return_Rate",
            color="Return_Rate",
            title="Return Rate by Category",
            labels={
                "Return_Rate": "Return Rate (%)"
            },
            text_auto=".2f"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        reason_df = return_reason_analysis(df)

        fig = px.pie(
            reason_df,
            names="Return_Reason",
            values="Count",
            title="Return Reasons Distribution",
            hole=0.4
        )

        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Monthly Return Trends")

    monthly_df = monthly_analysis(df)

    fig = px.line(
        monthly_df,
        x="Month",
        y="Return_Rate",
        markers=True,
        title="Monthly Return Rate",
        labels={
            "Return_Rate": "Return Rate (%)",
            "Month": "Month"
        }
    )

    st.plotly_chart(fig, use_container_width=True)


# ---------------- PRODUCT ANALYSIS ----------------

elif page == "Product Analysis":

    st.subheader("Product Performance Analysis")

    product_df = top_returned_products(df)

    fig = px.bar(
        product_df,
        x="Returned_Orders",
        y="Product_Name",
        orientation="h",
        color="Refund_Amount",
        title="Top 10 Returned Products",
        text="Returned_Orders"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category-wise Analysis")

    category_df = category_analysis(df)

    st.dataframe(
        category_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------- RETURN ANALYSIS ----------------

elif page == "Return Analysis":

    st.subheader("Return Reason Analysis")

    reason_df = return_reason_analysis(df)

    col1, col2 = st.columns(2)

    with col1:

        fig = px.pie(
            reason_df,
            names="Return_Reason",
            values="Count",
            hole=0.4,
            title="Return Reasons"
        )

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig = px.bar(
            reason_df,
            x="Return_Reason",
            y="Count",
            title="Number of Returns by Reason",
            color="Count"
        )

        fig.update_layout(xaxis_tickangle=-35)

        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        reason_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------- TIME ANALYSIS ----------------

elif page == "Time Analysis":

    st.subheader("Monthly Performance Analysis")

    monthly_df = monthly_analysis(df)

    fig = px.line(
        monthly_df,
        x="Month",
        y=["Total_Orders", "Returned_Orders"],
        markers=True,
        title="Orders vs Returned Orders"
    )

    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(
        monthly_df,
        x="Month",
        y="Refund_Amount",
        title="Monthly Refund Amount",
        color="Refund_Amount"
    )

    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        monthly_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------- REGIONAL ANALYSIS ----------------

elif page == "Regional Analysis":

    st.subheader("Region-wise Return Analysis")

    region_df = regional_analysis(df)

    col1, col2 = st.columns(2)

    with col1:

        fig = px.bar(
            region_df,
            x="Region",
            y="Return_Rate",
            title="Return Rate by Region",
            color="Return_Rate"
        )

        fig.update_layout(xaxis_tickangle=-35)

        st.plotly_chart(fig, use_container_width=True)

    with col2:

        fig = px.bar(
            region_df,
            x="Region",
            y="Refund_Amount",
            title="Refund Amount by Region",
            color="Refund_Amount"
        )

        fig.update_layout(xaxis_tickangle=-35)

        st.plotly_chart(fig, use_container_width=True)

    st.dataframe(
        region_df,
        use_container_width=True,
        hide_index=True
    )


# ---------------- DOWNLOAD DATA ----------------

st.sidebar.divider()

st.sidebar.download_button(
    label="📥 Download Filtered Dataset",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name="filtered_returns_data.csv",
    mime="text/csv"
)

st.sidebar.caption(
    "Product Return & Refund Analysis | B.Tech Data Analytics Project"
)