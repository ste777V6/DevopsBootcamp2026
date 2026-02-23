# Database setup for Week3 Day2 app

This file shows quick commands to create the Postgres database and environment variables used by the app.

1) Create DB and user using `psql` (run as postgres/superuser):

```bash
psql -U postgres -c "CREATE USER devops_user WITH PASSWORD 'changeme';"
psql -U postgres -c "CREATE DATABASE devopsbootcamp OWNER devops_user;"
psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE devopsbootcamp TO devops_user;"
# Optionally create the table now (the Flask app also runs `CREATE TABLE IF NOT EXISTS` at startup):
psql -U devops_user -d devopsbootcamp -c "CREATE TABLE IF NOT EXISTS students (id SERIAL PRIMARY KEY, name TEXT NOT NULL, country TEXT NOT NULL, created_at TIMESTAMP DEFAULT now());"
```

2) Example environment variables (see `.env.example`):

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=devopsbootcamp
DB_USER=devops_user
DB_PASSWORD=changeme
FLASK_SECRET=change_this_to_a_random_value
```

On PowerShell set for current session:

```powershell
$env:DB_HOST = 'localhost'
$env:DB_PORT = '5432'
$env:DB_NAME = 'devopsbootcamp'
$env:DB_USER = 'devops_user'
$env:DB_PASSWORD = 'changeme'
$env:FLASK_SECRET = 'change_this'
```

3) Install dependencies and run the app:

```powershell
# install deps
pip install -r "week3/day2/app/requirements.txt"

# run app
python "week3/day2/app/app.py"
```

4) Troubleshooting:
- If the app cannot connect, check the DB credentials and that Postgres is listening on the host/port.
- To manually inspect the table:

```bash
psql -U devops_user -d devopsbootcamp -c "SELECT * FROM students LIMIT 10;"
```
