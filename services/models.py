from services.database import db


class Community(db.Model):

    __tablename__ = "communities"

    # Primary Key
    community_code = db.Column(
        db.Integer,
        primary_key=True
    )

    # Community Information
    community_name = db.Column(
        db.String(100),
        nullable=False
    )

    population = db.Column(
        db.Integer,
        nullable=False
    )

    # Geographic Information
    area_sqmile = db.Column(
        db.Float,
        nullable=False
    )

    area_sqkm = db.Column(
        db.Float,
        nullable=False
    )

    # Population Density
    density_per_sqmi = db.Column(
        db.Float,
        nullable=False
    )

    density_per_sqkm = db.Column(
        db.Float,
        nullable=False
    )

    def __repr__(self):
        return (
            f"<Community {self.community_code}: "
            f"{self.community_name}>"
        )