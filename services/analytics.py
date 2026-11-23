import pandas as pd
import numpy as np
from pathlib import Path


# ==========================================
# CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / "data" / "chicago_crimes_repaired.csv"


# ==========================================
# 1. LOAD AND PREPARE DATA
# ==========================================

def load_crime_data():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Crime dataset not found at: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH, low_memory=False)

    # Standardize column names
    df.columns = df.columns.str.strip().str.lower()

    # Validate required columns
    required_columns = [
        "date",
        "arrest",
        "iucr_code",
        "community_code",
        "year",
        "fbi_code",
        "location_desc"
    ]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {missing_columns}"
        )

    # Parse dates
    df["date_parsed"] = pd.to_datetime(
        df["date"],
        format="mixed",
        errors="coerce"
    )

    # Convert year to numeric
    df["year"] = pd.to_numeric(
        df["year"], errors="coerce"
    )

    # Use date-derived year when the year column is missing
    df["analysis_year"] = df["year"].fillna(
        df["date_parsed"].dt.year
    )

    # Derive month and weekday from date
    df["analysis_month"] = (
        df["date_parsed"].dt.month
    )

    df["analysis_weekday"] = (
        df["date_parsed"].dt.day_name()
    )

    # Convert arrest values safely
    arrest_values = (
        df["arrest"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    true_values = ["true", "1", "yes", "y"]
    false_values = ["false", "0", "no", "n"]

    df["arrest_valid"] = arrest_values.isin(
        true_values + false_values
    )

    df["is_arrest"] = arrest_values.isin(
        true_values
    )

    return df


# ==========================================
# 2. DASHBOARD KPI VALUES
# ==========================================

def get_dashboard_kpis():

    df = load_crime_data()

    total_records = len(df)

    valid_arrests = df["arrest_valid"].sum()

    total_arrests = int(
        df.loc[df["arrest_valid"], "is_arrest"].sum()
    )

    arrest_rate = (
        total_arrests / valid_arrests * 100
        if valid_arrests > 0 else 0
    )

    unique_iucr_codes = int(
        df["iucr_code"].nunique()
    )

    unique_communities = int(
        df["community_code"].nunique()
    )

    return {
        "total_records": int(total_records),
        "total_arrests": total_arrests,
        "arrest_rate": round(arrest_rate, 2),
        "unique_iucr_codes": unique_iucr_codes,
        "unique_communities": unique_communities
    }


# ==========================================
# 3. YEARLY CRIME COUNTS
# ==========================================

def get_yearly_crimes():

    df = load_crime_data()

    result = (
        df.dropna(subset=["analysis_year"])
        .groupby("analysis_year")
        .size()
        .reset_index(name="crime_count")
        .sort_values("analysis_year")
    )

    result["analysis_year"] = (
        result["analysis_year"].astype(int)
    )

    return result


# ==========================================
# 4. YEARLY ARREST COUNTS
# ==========================================

def get_yearly_arrests():

    df = load_crime_data()

    result = (
        df[df["arrest_valid"]]
        .groupby("analysis_year")["is_arrest"]
        .sum()
        .reset_index(name="arrest_count")
        .sort_values("analysis_year")
    )

    result["analysis_year"] = (
        result["analysis_year"].astype(int)
    )

    return result


# ==========================================
# 5. TOP IUCR CODES
# ==========================================

def get_top_crime_codes(limit=10):

    df = load_crime_data()

    result = (
        df["iucr_code"]
        .dropna()
        .value_counts()
        .head(limit)
        .rename_axis("iucr_code")
        .reset_index(name="crime_count")
    )

    valid_count = df["iucr_code"].notna().sum()

    result["percentage"] = (
        result["crime_count"] / valid_count * 100
    ).round(2)

    return result


# ==========================================
# 6. TOP COMMUNITY AREAS
# ==========================================

def get_top_communities(limit=10):

    df = load_crime_data()

    result = (
        df["community_code"]
        .dropna()
        .value_counts()
        .head(limit)
        .rename_axis("community_code")
        .reset_index(name="crime_count")
    )

    return result


# ==========================================
# 7. MONTHLY CRIME DISTRIBUTION
# ==========================================

def get_crimes_by_month():

    df = load_crime_data()

    result = (
        df.dropna(subset=["analysis_month"])
        .groupby("analysis_month")
        .size()
        .reset_index(name="crime_count")
        .sort_values("analysis_month")
    )

    return result


# ==========================================
# 8. WEEKDAY CRIME DISTRIBUTION
# ==========================================

def get_crimes_by_weekday():

    df = load_crime_data()

    weekday_order = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    result = (
        df["analysis_weekday"]
        .value_counts()
        .reindex(weekday_order, fill_value=0)
        .rename_axis("weekday")
        .reset_index(name="crime_count")
    )

    return result


# ==========================================
# 9. TOP CRIME LOCATIONS
# ==========================================

def get_top_locations(limit=10):

    df = load_crime_data()

    result = (
        df["location_desc"]
        .dropna()
        .value_counts()
        .head(limit)
        .rename_axis("location")
        .reset_index(name="crime_count")
    )

    return result


# ==========================================
# 10. FBI CODE DISTRIBUTION
# ==========================================

def get_fbi_distribution():

    df = load_crime_data()

    result = (
        df["fbi_code"]
        .dropna()
        .value_counts()
        .rename_axis("fbi_code")
        .reset_index(name="crime_count")
    )

    return result


# ==========================================
# 11. DATA QUALITY REPORT
# ==========================================

def get_data_quality():

    df = load_crime_data()

    missing_values = (
        df.isnull()
        .sum()
        .to_dict()
    )

    return {
        "total_records": int(len(df)),
        "total_columns": int(len(df.columns) - 6),
        "duplicate_records": int(
            df.duplicated().sum()
        ),
        "invalid_dates": int(
            df["date_parsed"].isna().sum()
        ),
        "missing_arrest_values": int(
            (~df["arrest_valid"]).sum()
        ),
        "missing_iucr_codes": int(
            df["iucr_code"].isna().sum()
        ),
        "missing_community_codes": int(
            df["community_code"].isna().sum()
        ),
        "missing_values": missing_values
    }


# ==========================================
# 12. AUTOMATIC ANALYTICAL INSIGHTS
# ==========================================

def get_analytical_insights():

    df = load_crime_data()

    insights = []

    # Yearly analysis
    yearly = get_yearly_crimes()

    if not yearly.empty:
        highest_year = yearly.loc[
            yearly["crime_count"].idxmax()
        ]

        insights.append({
            "title": "Highest Crime Year",
            "value": int(highest_year["analysis_year"]),
            "description": (
                f"{int(highest_year['crime_count']):,} "
                "records were recorded in this year."
            )
        })

    # Monthly analysis
    monthly = get_crimes_by_month()

    if not monthly.empty:
        highest_month = monthly.loc[
            monthly["crime_count"].idxmax()
        ]

        month_name = pd.Timestamp(
            month=int(highest_month["analysis_month"]),
            year=2020,
            day=1
        ).strftime("%B")

        insights.append({
            "title": "Highest Crime Month",
            "value": month_name,
            "description": (
                f"{int(highest_month['crime_count']):,} "
                "records were recorded in this month."
            )
        })

    # Arrest analysis
    kpis = get_dashboard_kpis()

    insights.append({
        "title": "Arrest Rate",
        "value": f"{kpis['arrest_rate']}%",
        "description": (
            f"{kpis['total_arrests']:,} arrests "
            "among records with a valid arrest status."
        )
    })

    # Community analysis
    communities = get_top_communities(limit=1)

    if not communities.empty:
        top_community = communities.iloc[0]

        insights.append({
            "title": "Highest Crime Community Code",
            "value": int(top_community["community_code"]),
            "description": (
                f"{int(top_community['crime_count']):,} "
                "records were associated with this community code."
            )
        })

    return insights


# ==========================================
# 13. COMPLETE DASHBOARD DATA
# ==========================================

def get_dashboard_data():

    return {
        "kpis": get_dashboard_kpis(),
        "yearly_crimes": get_yearly_crimes().to_dict(
            orient="records"
        ),
        "yearly_arrests": get_yearly_arrests().to_dict(
            orient="records"
        ),
        "top_crime_codes": get_top_crime_codes().to_dict(
            orient="records"
        ),
        "top_communities": get_top_communities().to_dict(
            orient="records"
        ),
        "monthly_crimes": get_crimes_by_month().to_dict(
            orient="records"
        ),
        "weekday_crimes": get_crimes_by_weekday().to_dict(
            orient="records"
        ),
        "top_locations": get_top_locations().to_dict(
            orient="records"
        ),
        "fbi_distribution": get_fbi_distribution().to_dict(
            orient="records"
        ),
        "data_quality": get_data_quality(),
        "insights": get_analytical_insights()
    }


# ==========================================
# 14. TEST ANALYTICS MODULE
# ==========================================

if __name__ == "__main__":

    print("\nCHICAGO CRIME ANALYTICS TEST")
    print("=" * 50)

    print("\nDASHBOARD KPIs")
    print(get_dashboard_kpis())

    print("\nYEARLY CRIMES")
    print(get_yearly_crimes())

    print("\nYEARLY ARRESTS")
    print(get_yearly_arrests())

    print("\nTOP IUCR CODES")
    print(get_top_crime_codes())

    print("\nTOP COMMUNITIES")
    print(get_top_communities())

    print("\nMONTHLY CRIMES")
    print(get_crimes_by_month())

    print("\nWEEKDAY CRIMES")
    print(get_crimes_by_weekday())

    print("\nTOP LOCATIONS")
    print(get_top_locations())

    print("\nFBI DISTRIBUTION")
    print(get_fbi_distribution())

    print("\nDATA QUALITY")
    print(get_data_quality())

    print("\nANALYTICAL INSIGHTS")
    for insight in get_analytical_insights():
        print(insight)

    print("\nANALYTICS MODULE TEST COMPLETED")