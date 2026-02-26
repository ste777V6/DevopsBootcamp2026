from flask import Flask, render_template_string, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# load .env located next to this file (overrides environment when present)
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '.env'))

app = Flask(__name__)
app.static_folder = 'static'
app.secret_key = os.environ.get('FLASK_SECRET', 'devopsbootcampdev')


# Database helpers - configure via environment variables
DB_CONFIG = {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': int(os.environ.get('DB_PORT', 5432)),
        'dbname': os.environ.get('DB_NAME', 'devopsbootcamp'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', ''),
}


def get_conn():
        return psycopg2.connect(**DB_CONFIG)


def init_db():
    try:
        conn = get_conn()
        cur = conn.cursor()
        # Attempt to create table; concurrent creates can race and cause
        # duplicate-object errors (sequence/type already exists). Treat
        # those specific errors as non-fatal so multiple workers can start.
        try:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS students (
                    id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL,
                    country TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT now()
                )
                """
            )
            conn.commit()
        except Exception as e:
            # If another process created parts of the table concurrently,
            # Postgres can raise UniqueViolation for sequences/types.
            # Ignore those and proceed; re-raise other errors.
            try:
                import psycopg2
                if isinstance(e, psycopg2.errors.UniqueViolation) or 'already exists' in str(e):
                    print(f"init_db: concurrent create detected, continuing: {e}")
                    conn.rollback()
                else:
                    raise
            except ImportError:
                # If psycopg2.errors isn't available for some reason, fall
                # back to checking message text.
                if 'already exists' in str(e):
                    print(f"init_db: concurrent create detected, continuing: {e}")
                    conn.rollback()
                else:
                    raise
        finally:
            cur.close()
            conn.close()
    except Exception as e:
        # Fail fast: if we cannot create the required table (and it's not
        # a harmless 'already exists' situation), raise so the process
        # doesn't start without DB ready.
        print(f"init_db: could not create table: {e}")
        raise


# Ensure DB table exists before application startup (WSGI imports the module)
try:
    init_db()
except Exception as e:
    print(f"Fatal: database initialization failed: {e}")
    # Re-raise to prevent the app from starting in an invalid state
    raise


BASE_TEMPLATE = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width,initial-scale=1">
        <title>Week3 Day2</title>
        <style>
            body { font-family: Arial, Helvetica, sans-serif; margin:0; background:#f6f8fb; color:#0b1220 }
            header { background:#0f172a; color:#fff; padding:12px 20px }
            nav { max-width:900px; margin:0 auto; display:flex; gap:12px }
            nav a { color:#94a3b8; text-decoration:none; padding:8px 12px }
            nav a:hover { color:#fff }
            main { max-width:900px; margin:28px auto; padding:0 20px }
            .card { background:#fff; border-radius:8px; padding:18px; box-shadow:0 6px 18px rgba(2,6,23,0.08) }
            table { width:100%; border-collapse:collapse; margin-bottom:16px }
            th, td { text-align:left; padding:8px; border-bottom:1px solid #eef2f7 }
            form { display:flex; gap:8px; flex-wrap:wrap; align-items:center }
            input[type=text] { padding:8px 10px; border:1px solid #dbe7f0; border-radius:6px; flex:1 }
            button { padding:9px 14px; background:#0f172a; color:#fff; border:none; border-radius:6px }
            .flash { padding:10px; border-radius:6px; margin-bottom:12px }
            .flash.success { background:#ecfdf5; color:#065f46 }
            .flash.error { background:#ffebee; color:#7f1d1d }
        </style>
    </head>
    <body>
        <header>
            <nav>
                <a href="/">Home</a>
                <a href="/students">Students</a>
            </nav>
        </header>
        <main>
            {% with messages = get_flashed_messages(with_categories=true) %}
                {% if messages %}
                    {% for cat, msg in messages %}
                        <div class="flash {{ 'success' if cat == 'success' else 'error' }}">{{ msg }}</div>
                    {% endfor %}
                {% endif %}
            {% endwith %}
            {{ body|safe }}
        </main>
    </body>
</html>
"""


STUDENTS_BODY = """
<div class="card">
    <h3>Students</h3>
    {% if students and students|length > 0 %}
        <table>
            <thead>
                <tr><th>ID</th><th>Name</th><th>Country</th><th>Added</th></tr>
            </thead>
            <tbody>
                {% for s in students %}
                    <tr>
                        <td>{{ s.id }}</td>
                        <td>{{ s.name }}</td>
                        <td>{{ s.country }}</td>
                        <td>{{ s.created_at }}</td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <p>No students yet.</p>
    {% endif %}

    <h4>Add student</h4>
    <form method="post" action="/students">
        <input type="text" name="name" placeholder="Student name" required>
        <input type="text" name="country" placeholder="Country" required>
        <button type="submit">Submit</button>
    </form>
</div>
"""


@app.route('/')
def index():
        body = '<div class="card"><h2>Welcome</h2><p>Use the navigation to manage students.</p></div>'
        return render_template_string(BASE_TEMPLATE, body=body)


@app.route('/students', methods=['GET', 'POST'])
def students():
        if request.method == 'POST':
                name = (request.form.get('name') or '').strip()
                country = (request.form.get('country') or '').strip()
                if not name or not country:
                        flash('Name and country are required.', 'error')
                        return redirect(url_for('students'))
                try:
                        conn = get_conn()
                        cur = conn.cursor()
                        cur.execute('INSERT INTO students (name, country) VALUES (%s, %s)', (name, country))
                        conn.commit()
                        cur.close()
                        conn.close()
                        flash('Student saved.', 'success')
                except Exception as e:
                        flash(f'Database error: {e}', 'error')
                return redirect(url_for('students'))

        # GET: fetch students
        students_data = []
        try:
                conn = get_conn()
                cur = conn.cursor(cursor_factory=RealDictCursor)
                cur.execute('SELECT id, name, country, created_at FROM students ORDER BY id DESC')
                students_data = cur.fetchall()
                cur.close()
                conn.close()
        except Exception as e:
                # show error as flash but still render page
                flash(f'Could not read students from DB: {e}', 'error')

        body = render_template_string(STUDENTS_BODY, students=students_data)
        return render_template_string(BASE_TEMPLATE, body=body)


if __name__ == '__main__':
        init_db()
        app.run(debug=True, host='0.0.0.0', port=5000)
