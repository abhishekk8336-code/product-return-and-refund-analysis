import pandas as pd


def calculate_overview(df):

    total_orders = df["Order_ID"].nunique()

    returned_orders = df[
        df["Return_Status"] == "Returned"
    ]["Order_ID"].nunique()

    not_returned = total_orders - returned_orders

    return_rate = (
        returned_orders / total_orders * 100
        if total_orders > 0 else 0
    )

    total_refund = df["Refund_Amount"].sum()

    refunded_orders = df[
        df["Refund_Amount"] > 0
    ]["Order_ID"].nunique()

    average_refund = (
        total_refund / refunded_orders
        if refunded_orders > 0 else 0
    )

    return {
        "Total Orders": total_orders,
        "Returned Orders": returned_orders,
        "Not Returned": not_returned,
        "Return Rate (%)": round(return_rate, 2),
        "Total Refund Amount": round(total_refund, 2),
        "Average Refund Amount": round(average_refund, 2)
    }


def category_analysis(df):

    result = df.groupby("Category").agg(
        Total_Orders=("Order_ID", "nunique"),
        Returned_Orders=(
            "Return_Status",
            lambda x: (x == "Returned").sum()
        ),
        Refund_Amount=("Refund_Amount", "sum")
    ).reset_index()

    result["Return_Rate"] = (
        result["Returned_Orders"] /
        result["Total_Orders"] * 100
    ).round(2)

    return result.sort_values(
        "Return_Rate", ascending=False
    )


def return_reason_analysis(df):

    returned = df[
        df["Return_Status"] == "Returned"
    ]

    result = returned["Return_Reason"].value_counts().reset_index()

    result.columns = ["Return_Reason", "Count"]

    return result


def monthly_analysis(df):

    monthly = df.copy()

    monthly["Month"] = (
        monthly["Order_Date"].dt.to_period("M").astype(str)
    )

    result = monthly.groupby("Month").agg(
        Total_Orders=("Order_ID", "nunique"),
        Returned_Orders=(
            "Return_Status",
            lambda x: (x == "Returned").sum()
        ),
        Refund_Amount=("Refund_Amount", "sum")
    ).reset_index()

    result["Return_Rate"] = (
        result["Returned_Orders"] /
        result["Total_Orders"] * 100
    ).round(2)

    return result


def top_returned_products(df):

    returned = df[
        df["Return_Status"] == "Returned"
    ]

    result = returned.groupby("Product_Name").agg(
        Returned_Orders=("Order_ID", "nunique"),
        Refund_Amount=("Refund_Amount", "sum")
    ).reset_index()

    return result.sort_values(
        "Returned_Orders", ascending=False
    ).head(10)


def regional_analysis(df):

    result = df.groupby("Region").agg(
        Total_Orders=("Order_ID", "nunique"),
        Returned_Orders=(
            "Return_Status",
            lambda x: (x == "Returned").sum()
        ),
        Refund_Amount=("Refund_Amount", "sum")
    ).reset_index()

    result["Return_Rate"] = (
        result["Returned_Orders"] /
        result["Total_Orders"] * 100
    ).round(2)

    return result.sort_values(
        "Return_Rate", ascending=False
    )


if __name__ == "__main__":

    df = pd.read_csv(
        "data/ecommerce_returns_cleaned.csv",
        parse_dates=["Order_Date", "Return_Date"]
    )

    print("\n========== OVERALL ANALYSIS ==========")

    overview = calculate_overview(df)

    for key, value in overview.items():
        print(f"{key}: {value}")

    print("\n========== CATEGORY ANALYSIS ==========")
    print(category_analysis(df).to_string(index=False))

    print("\n========== RETURN REASONS ==========")
    print(return_reason_analysis(df).to_string(index=False))

    print("\n========== MONTHLY ANALYSIS ==========")
    print(monthly_analysis(df).to_string(index=False))

    print("\n========== TOP 10 RETURNED PRODUCTS ==========")
    print(top_returned_products(df).to_string(index=False))

    print("\n========== REGIONAL ANALYSIS ==========")
    print(regional_analysis(df).to_string(index=False))

    print("\nEDA COMPLETED SUCCESSFULLY!")