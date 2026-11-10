import pandas as pd
import os


def clean_data(df):

    print("\n========== DATA CLEANING ==========")

    # 1. Original dataset information
    original_rows = len(df)

    print("Original records:", original_rows)

    # 2. Check missing values
    print("\nMissing values before cleaning:")
    print(df.isnull().sum())

    # 3. Remove duplicate records
    duplicates = df.duplicated().sum()

    df = df.drop_duplicates().copy()

    print("\nDuplicates removed:", duplicates)

    # 4. Convert date columns
    df["Order_Date"] = pd.to_datetime(
        df["Order_Date"], errors="coerce"
    )

    df["Return_Date"] = pd.to_datetime(
        df["Return_Date"], errors="coerce"
    )

    # 5. Convert numerical columns
    df["Quantity"] = pd.to_numeric(
        df["Quantity"], errors="coerce"
    )

    df["Unit_Price"] = pd.to_numeric(
        df["Unit_Price"], errors="coerce"
    )

    df["Refund_Amount"] = pd.to_numeric(
        df["Refund_Amount"], errors="coerce"
    )

    # 6. Remove invalid essential records
    df = df.dropna(
        subset=["Order_ID", "Order_Date", "Quantity", "Unit_Price"]
    ).copy()

    df = df[
        (df["Quantity"] > 0) &
        (df["Unit_Price"] >= 0)
    ].copy()

    # 7. Handle missing categorical values
    df["Region"] = df["Region"].fillna("Unknown")

    df["Payment_Method"] = df["Payment_Method"].fillna("Unknown")

    # 8. Handle return reasons
    returned = df["Return_Status"] == "Returned"

    df.loc[returned, "Return_Reason"] = (
        df.loc[returned, "Return_Reason"].fillna("Not Specified")
    )

    df.loc[~returned, "Return_Reason"] = "Not Applicable"

    # 9. Handle missing refund amounts
    df["Refund_Amount"] = df["Refund_Amount"].fillna(0)

    # 10. Save cleaned dataset
    os.makedirs("data", exist_ok=True)

    df.to_csv("data/ecommerce_returns_cleaned.csv", index=False)

    # 11. Final summary
    print("\nMissing values after cleaning:")
    print(df.isnull().sum())

    print("\n========== CLEANING SUMMARY ==========")
    print("Original records:", original_rows)
    print("Duplicates removed:", duplicates)
    print("Final records:", len(df))
    print("Records removed:", original_rows - len(df))

    print("\nCleaned dataset saved successfully!")

    return df


if __name__ == "__main__":

    raw_data = pd.read_csv("data/ecommerce_returns_raw.csv")

    cleaned_data = clean_data(raw_data)

    print("\nFirst five cleaned records:")
    print(cleaned_data.head())