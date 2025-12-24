# from flask import Flask, render_template, request
# from db import get_connection
#
# app = Flask(__name__)
#
# @app.route("/")
# def index():
#     return render_template("index.html")
#
# # -------------------------------
# # POLLING UNIT RESULTS
# # -------------------------------
# @app.route("/polling-unit")
# def polling_unit():
#     conn = get_connection()
#     cursor = conn.cursor(dictionary=True)
#
#     # Get polling units
#     cursor.execute(
#         "SELECT uniqueid, polling_unit_name FROM polling_unit"
#     )
#     polling_units = cursor.fetchall()
#
#     results = None
#     pu_id = request.args.get("pu_id")
#
#     if pu_id:
#         cursor.execute("""
#             SELECT party_abbreviation, party_score
#             FROM announced_pu_results
#             WHERE polling_unit_id = %s
#         """, (pu_id,))
#         results = cursor.fetchall()
#
#     conn.close()
#     return render_template(
#         "polling_unit.html",
#         polling_units=polling_units,
#         results=results
#     )
#
from flask import Flask, render_template, request
from database import get_connection


app = Flask(__name__)

# -------------------------------------------------
# HOME PAGE
# -------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


# -------------------------------------------------
# QUESTION 1:
# Display results for a selected polling unit
# -------------------------------------------------
@app.route("/polling-unit")
def polling_unit():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch all polling units
    cursor.execute("""
        SELECT uniqueid, polling_unit_name
        FROM polling_unit
    """)
    polling_units = cursor.fetchall()

    results = None
    pu_id = request.args.get("pu_id")

    if pu_id:
        cursor.execute("""
            SELECT party_abbreviation, party_score
            FROM announced_pu_results
            WHERE polling_unit_uniqueid = %s
        """, (pu_id,))
        results = cursor.fetchall()

    conn.close()

    return render_template(
        "polling_unit.html",
        polling_units=polling_units,
        results=results
    )


# -------------------------------------------------
# QUESTION 2:
# Display summed results for an LGA
# (DO NOT use announced_lga_results)
# -------------------------------------------------
@app.route("/lga-results")
def lga_results():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT lga_id, lga_name
        FROM lga
    """)
    lgas = cursor.fetchall()

    results = None
    lga_id = request.args.get("lga_id")

    if lga_id:
        cursor.execute("""
            SELECT apr.party_abbreviation,
                   SUM(apr.party_score) AS total_score
            FROM announced_pu_results apr
            JOIN polling_unit pu
              ON apr.polling_unit_id = pu.uniqueid
            WHERE pu.lga_id = %s
            GROUP BY apr.party_abbreviation
        """, (lga_id,))
        results = cursor.fetchall()

    conn.close()

    return render_template(
        "index.html",
        lgas=lgas,
        results=results
    )


# -------------------------------------------------
# QUESTION 3:
# Add new polling unit and its results
# -------------------------------------------------
@app.route("/add-results", methods=["GET", "POST"])
def add_results():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        polling_unit_name = request.form["polling_unit_name"]
        lga_id = request.form["lga_id"]

        # Insert new polling unit
        cursor.execute("""
            INSERT INTO polling_unit (polling_unit_name, lga_id)
            VALUES (%s, %s)
        """, (polling_unit_name, lga_id))

        polling_unit_id = cursor.lastrowid

        parties = ["APC", "PDP", "LP"]

        for party in parties:
            score = request.form[party]
            cursor.execute("""
                INSERT INTO announced_pu_results
                (polling_unit_id, party_abbreviation, party_score)
                VALUES (%s, %s, %s)
            """, (polling_unit_id, party, score))

        conn.commit()

    cursor.execute("""
        SELECT lga_id, lga_name
        FROM lga
    """)
    lgas = cursor.fetchall()

    conn.close()

    return render_template("add_results.html", lgas=lgas)


# -------------------------------------------------
# RUN APPLICATION
# -------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
