from flask import Flask, render_template_string, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os
import time

app = Flask(__name__)

# Build DB URI from docker-compose environment variables
DB_USER = os.getenv("DB_USER", "myuser")
DB_PASSWORD = os.getenv("DB_PASSWORD", "mypassword")
DB_HOST = os.getenv("DB_HOST", "db")  # IMPORTANT: service name, not localhost
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "mydb")

app.config["SQLALCHEMY_DATABASE_URI"] = (
    f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# --------------------
# Model
# --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)


# --------------------
# HTML Template
# --------------------
TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Simple App</title>
</head>
<body style="font-family: Arial; max-width: 600px; margin: 50px auto;">
    <h1>User Registration</h1>

    <form method="POST">
        <input type="text" name="name" placeholder="Name" required><br>
        <input type="email" name="email" placeholder="Email" required><br>
        <button type="submit">Submit</button>
    </form>

    <h2>Users ({{ users|length }})</h2>
    <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
        <tr><th>ID</th><th>Name</th><th>Email</th></tr>
        {% for user in users %}
        <tr>
            <td>{{ user.id }}</td>
            <td>{{ user.name }}</td>
            <td>{{ user.email }}</td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
"""


# --------------------
# Routes
# --------------------
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user = User(
            name=request.form["name"],
            email=request.form["email"]
        )
        db.session.add(user)
        db.session.commit()
        return redirect("/")

    users = User.query.all()
    return render_template_string(TEMPLATE, users=users)


# --------------------
# DB wait logic (IMPORTANT for Docker)
# --------------------
def wait_for_db():
    retries = 10
    for i in range(retries):
        try:
            db.create_all()
            print("✓ Database connected & tables created")
            return
        except Exception as e:
            print(f"⏳ Waiting for DB... ({i+1}/{retries}) -> {e}")
            time.sleep(2)

    raise Exception("❌ Database not available")


# --------------------
# App start
# --------------------
if __name__ == "__main__":
    with app.app_context():
        wait_for_db()

    app.run(host="0.0.0.0", port=5000)