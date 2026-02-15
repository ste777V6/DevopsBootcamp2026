# Run Flask with Gunicorn (port 800) and expose via Nginx (ports 80/443)
Summary
- Use systemd to run Gunicorn bound to 127.0.0.1:8000 and let the system `nginx` service reverse-proxy on ports 80/443.

Prerequisites (one-time on server)
- Python 3 and virtualenv installed.
- System packages: `nginx`, `python3-venv` (or similar), and systemd (Linux).

One-time app setup

```bash
cd /full/path/to/DevopsBootcamp2026/week2/flask_dummy_app
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
deactivate

Recommended systemd unit (create `/etc/systemd/system/flask_dummy_app.service`):

```ini
[Unit]  
Description=Flask Dummy App (gunicorn)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/full/path/to/DevopsBootcamp2026/week2/flask_dummy_app
Environment="PATH=/full/path/to/DevopsBootcamp2026/week2/flask_dummy_app/.venv/bin"
ExecStart=/full/path/to/DevopsBootcamp2026/week2/flask_dummy_app/.venv/bin/gunicorn -w 4 -b 127.0.0.1:8000 app:app
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Install and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now flask_dummy_app.service
sudo systemctl status flask_dummy_app.service
```

Nginx (example) — proxy to 127.0.0.1:8000

HTTP server block (80 -> redirect to HTTPS):

```nginx
server {
	listen 80;
	server_name your.domain.tld;
	return 301 https://$host$request_uri;
}

```

HTTPS server block (proxy to Gunicorn)

```nginx
server {
	listen 443 ssl http2;
	server_name your.domain.tld;

	ssl_certificate /etc/letsencrypt/live/your.domain.tld/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/your.domain.tld/privkey.pem;

	location / {
	proxy_pass http://127.0.0.1:8000;
	proxy_set_header Host $host;
	proxy_set_header X-Real-IP $remote_addr;
	proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
	proxy_set_header X-Forwarded-Proto $scheme;
	proxy_http_version 1.1;
	proxy_set_header Upgrade $http_upgrade;
	proxy_set_header Connection "upgrade";
	}
}

```

Notes
- Do not start `nginx` from the app script; use the system `nginx` service (`sudo systemctl enable --now nginx`).
- Do not run `pip install` on each service start; install dependencies during deployment.
- Consider using a unix socket (`/run/flask_dummy_app.sock`) instead of TCP for slightly better performance. If using a socket, update `ExecStart` and `proxy_pass` accordingly.

Troubleshooting

```bash
sudo journalctl -u flask_dummy_app.service -f
sudo systemctl restart flask_dummy_app.service
sudo systemctl status nginx
sudo journalctl -u nginx -f
```

Replace `/full/path/to/...` and `your.domain.tld` with your server paths and domain.
