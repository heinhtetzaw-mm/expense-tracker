import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash

app = Flask(__name__)
app.secret_key = "dev"

DATABASE = "expenses.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    """)

    conn.commit()
    conn.close()


@app.get("/")
def home():
    conn = get_db_connection()

    selected_category = request.args.get("category", "")
    month_filter = request.args.get("month_filter", "all")

    selected_year = request.args.get("year")
    selected_month = request.args.get("month")

    now = datetime.now()

    if not selected_year:
        selected_year = now.year
    else:
        selected_year = int(selected_year)

    if not selected_month:
        selected_month = now.month
    else:
        selected_month = int(selected_month)

    month_prefix = f"{selected_year}-{selected_month:02d}"

    if month_filter == "all":
        if selected_category:
            expenses = conn.execute(
                "SELECT * FROM expenses WHERE category = ? ORDER BY id DESC",
                (selected_category,),
            ).fetchall()
        else:
            expenses = conn.execute(
                "SELECT * FROM expenses ORDER BY id DESC"
            ).fetchall()
    else:
        if selected_category:
            expenses = conn.execute(
                "SELECT * FROM expenses WHERE category = ? AND date LIKE ? ORDER BY id DESC",
                (selected_category, month_filter + "%"),
            ).fetchall()
        else:
            expenses = conn.execute(
                "SELECT * FROM expenses WHERE date LIKE ? ORDER BY id DESC",
                (month_filter + "%",),
            ).fetchall()

    total_all = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses"
    ).fetchone()["total"]

    total_month = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS total FROM expenses WHERE date LIKE ?",
        (month_prefix + "%",)
    ).fetchone()["total"]

    prev_year = selected_year
    prev_month = selected_month - 1
    if prev_month == 0:
        prev_month = 12
        prev_year -= 1

    next_year = selected_year
    next_month = selected_month + 1
    if next_month == 13:
        next_month = 1
        next_year += 1

    conn.close()

    return render_template(
        "index.html",
        expenses=expenses,
        selected_category=selected_category,
        total_all=total_all,
        total_month=total_month,
        selected_year=selected_year,
        selected_month=selected_month,
        prev_year=prev_year,
        prev_month=prev_month,
        next_year=next_year,
        next_month=next_month,
        month_filter=month_filter
    )


@app.post("/add")
def add_expense():
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]
    note = request.form["note"]

    conn = get_db_connection()
    conn.execute(
        "INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)",
        (amount, category, date, note),
    )
    conn.commit()
    conn.close()

    flash("Expense added ✅")

    return redirect("/")


@app.post("/delete/<int:expense_id>")
def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

    flash("Expense deleted 🗑️")

    return redirect("/")


@app.get("/edit/<int:expense_id>")
def edit_page(expense_id):
    conn = get_db_connection()
    expense = conn.execute(
        "SELECT * FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    conn.close()

    return render_template("edit.html", expense=expense)


@app.post("/edit/<int:expense_id>")
def edit_expense(expense_id):
    amount = request.form["amount"]
    category = request.form["category"]
    date = request.form["date"]
    note = request.form["note"]

    conn = get_db_connection()
    conn.execute(
        """
        UPDATE expenses
        SET amount = ?, category = ?, date = ?, note = ?
        WHERE id = ?
        """,
        (amount, category, date, note, expense_id),
    )
    conn.commit()
    conn.close()

    flash("Expense updated ✏️")

    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
