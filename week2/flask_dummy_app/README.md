# Flask Static App

Minimal static site served by a tiny Flask app.

Quick start (PowerShell on Windows):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

If you prefer a POSIX shell (bash, WSL):

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Run with Gunicorn (production, POSIX / WSL):

```bash
# install dependencies first
pip install -r requirements.txt
# run Gunicorn with 2 worker processes
gunicorn -w 2 -b 0.0.0.0:8000 "app:app"
```

On Windows use WSL or a production-ready server; Gunicorn is not supported natively on Windows.

Deploy on AWS EC2:

- **Security group:** open the port you plan to use (e.g. `80` or `8000`) to your IPs or 0.0.0.0/0 as appropriate.
- **Run:** bind Gunicorn to `0.0.0.0` so EC2 accepts external connections. Example (port 8000):

```bash
pip install -r requirements.txt
gunicorn -w 2 -b 0.0.0.0:8000 "app:app" &
```

- For production on port 80 use a reverse proxy (NGINX) or run with appropriate privileges; consider a `systemd` service for reliability.
