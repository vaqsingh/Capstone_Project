import pandas as pd

from main import app
from services.database import db
from services.models import Community


CSV_PATH = "data/chicago_city_community.csv"


def import_communities():

    # Load CSV using Pandas
    df = pd.read_csv(CSV_PATH)

    print("Dataset loaded successfully!")
    print("Shape:", df.shape)
    print("\nColumns:")
    print(df.columns.tolist())

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert numeric columns
    numeric_columns = [
        "community_code",
        "population",
        "area_sqmile",
        "area_sqkm",
        "density_per_sqmi",
        "density_per_sqkm"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column].astype(str).str.replace(",", "", regex=False),
            errors="coerce"
        )

    # Validate missing or invalid values
    if df[numeric_columns].isnull().any().any():
        raise ValueError("Invalid or missing numeric values found.")

    if df["community_name"].isnull().any():
        raise ValueError("Community names cannot be empty.")

    if df["community_code"].duplicated().any():
        raise ValueError("Duplicate community codes found.")

    with app.app_context():

        # Avoid accidental duplicate imports
        if Community.query.count() > 0:
            print("Database already contains records.")
            print("Import cancelled to prevent duplication.")
            return

        communities = []

        for _, row in df.iterrows():

            community = Community(
                community_code=int(row["community_code"]),
                community_name=str(row["community_name"]).strip(),
                population=int(row["population"]),
                area_sqmile=float(row["area_sqmile"]),
                area_sqkm=float(row["area_sqkm"]),
                density_per_sqmi=float(row["density_per_sqmi"]),
                density_per_sqkm=float(row["density_per_sqkm"])
            )

            communities.append(community)

        db.session.add_all(communities)
        db.session.commit()

        print("\nImport successful!")
        print("Records inserted:", len(communities))


if __name__ == "__main__":
    import_communities()