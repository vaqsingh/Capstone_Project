from flask import Flask, render_template, request, redirect, url_for, flash
from sqlalchemy.exc import IntegrityError

from services.database import db, init_db
from services.models import Community


# ==========================================
# APPLICATION CONFIGURATION
# ==========================================

app = Flask(__name__)
app.secret_key = "chicago-crime-development-key"

# Initialize database
init_db(app)

# Create database tables
with app.app_context():
    db.create_all()


# ==========================================
# HOME ROUTE
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# DASHBOARD ROUTE
# ==========================================

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


# ==========================================
# READ COMMUNITIES
# ==========================================

@app.route("/communities")
def communities():
    community_records = Community.query.order_by(
        Community.community_code.asc()
    ).all()

    return render_template(
        "communities.html",
        communities=community_records
    )


# ==========================================
# CREATE COMMUNITY
# ==========================================

@app.route("/communities/create", methods=["POST"])
def create_community():

    try:
        community = Community(
            community_code=int(request.form["community_code"]),
            community_name=request.form["community_name"].strip(),
            population=int(request.form["population"]),
            area_sqmile=float(request.form["area_sqmile"]),
            area_sqkm=float(request.form["area_sqkm"]),
            density_per_sqmi=float(request.form["density_per_sqmi"]),
            density_per_sqkm=float(request.form["density_per_sqkm"])
        )

        if not community.community_name:
            raise ValueError("Community name is required.")

        if community.community_code <= 0:
            raise ValueError("Community code must be positive.")

        if community.population < 0:
            raise ValueError("Population cannot be negative.")

        if (
            community.area_sqmile <= 0
            or community.area_sqkm <= 0
            or community.density_per_sqmi < 0
            or community.density_per_sqkm < 0
        ):
            raise ValueError("Invalid area or density values.")

        db.session.add(community)
        db.session.commit()

        flash("Community added successfully!", "success")

    except ValueError as error:
        db.session.rollback()
        flash(str(error), "error")

    except IntegrityError:
        db.session.rollback()
        flash("Community code already exists!", "error")

    return redirect(url_for("communities"))


# ==========================================
# UPDATE COMMUNITY
# ==========================================

@app.route(
    "/communities/<int:community_code>/edit",
    methods=["GET", "POST"]
)
def update_community(community_code):

    community = Community.query.get_or_404(community_code)

    if request.method == "POST":

        try:
            community.community_name = request.form["community_name"].strip()
            community.population = int(request.form["population"])
            community.area_sqmile = float(request.form["area_sqmile"])
            community.area_sqkm = float(request.form["area_sqkm"])
            community.density_per_sqmi = float(request.form["density_per_sqmi"])
            community.density_per_sqkm = float(request.form["density_per_sqkm"])

            if not community.community_name:
                raise ValueError("Community name is required.")

            if community.population < 0:
                raise ValueError("Population cannot be negative.")

            if (
                community.area_sqmile <= 0
                or community.area_sqkm <= 0
                or community.density_per_sqmi < 0
                or community.density_per_sqkm < 0
            ):
                raise ValueError("Invalid area or density values.")

            db.session.commit()

            flash("Community updated successfully!", "success")
            return redirect(url_for("communities"))

        except ValueError as error:
            db.session.rollback()
            flash(str(error), "error")

    return render_template(
        "edit_community.html",
        community=community
    )


# ==========================================
# DELETE COMMUNITY
# ==========================================

@app.route(
    "/communities/<int:community_code>/delete",
    methods=["POST"]
)
def delete_community(community_code):

    community = Community.query.get_or_404(community_code)

    try:
        db.session.delete(community)
        db.session.commit()

        flash("Community deleted successfully!", "success")

    except Exception as error:
        db.session.rollback()
        flash(f"Unable to delete community: {error}", "error")

    return redirect(url_for("communities"))


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)