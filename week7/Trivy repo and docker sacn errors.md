# Build and Push ECS Application — Job Log

| Field | Value |
|---|---|
| Repository | `ste777V6/DevopsBootcamp2026` |
| Pull request | #40 |
| Workflow run | #4 — *Created new pipelinme for repo and docker image check* |
| Job | Build and Push ECS Application |
| Status | ❌ Failed |
| Duration | 43s |

## Step durations

Steps before the build log: 2s, 2s, 15s, 7s, 0s, 1s, 9s
Steps after the build log: 0s, 3s, 0s, 0s, 0s, 0s, 0s, 1s, 0s, 0s, 0s

## Docker build log

### Base image extraction

```text
#6 extracting sha256:3764a9a7d1e8a98213ab2201a41dbf3da9c60240ea35a5ea96ab994555070a70
#6 extracting sha256:3764a9a7d1e8a98213ab2201a41dbf3da9c60240ea35a5ea96ab994555070a70 0.1s done
#6 extracting sha256:b0dc7f87bef15c2536cb182d6c48b52f90a0522884ec9eb222f833fa97ffebf0
#6 extracting sha256:b0dc7f87bef15c2536cb182d6c48b52f90a0522884ec9eb222f833fa97ffebf0 0.5s done
#6 extracting sha256:06ad939ed42b51caafb25b14810875d14e0ee0c441d3e2e5e46475fb8c150bca
#6 extracting sha256:06ad939ed42b51caafb25b14810875d14e0ee0c441d3e2e5e46475fb8c150bca done
#6 DONE 3.1s
```

### [2/5] WORKDIR /app

```text
#7 [2/5] WORKDIR /app
#7 DONE 0.0s
```

### [3/5] COPY requirements.txt /app

```text
#8 [3/5] COPY requirements.txt /app
#8 DONE 0.0s
```

### [4/5] RUN pip install -r requirements.txt

```text
#9 [4/5] RUN pip install -r requirements.txt
#9 1.535 Collecting flask>=3.0 (from -r requirements.txt (line 1))
#9 1.573   Downloading flask-3.1.3-py3-none-any.whl.metadata (3.2 kB)
#9 1.598 Collecting gunicorn (from -r requirements.txt (line 2))
#9 1.605   Downloading gunicorn-26.2.0-py3-none-any.whl.metadata (5.5 kB)
#9 1.624 Collecting Flask-SQLAlchemy (from -r requirements.txt (line 3))
#9 1.632   Downloading flask_sqlalchemy-3.1.1-py3-none-any.whl.metadata (3.4 kB)
#9 1.652 Collecting python-dotenv (from -r requirements.txt (line 4))
#9 1.659   Downloading python_dotenv-1.2.3-py3-none-any.whl.metadata (29 kB)
#9 1.727 Collecting psycopg2-binary (from -r requirements.txt (line 5))
#9 1.735   Downloading psycopg2_binary-2.9.13-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl.metadata (4.9 kB)
#9 1.749 Collecting blinker>=1.9.0 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.759   Downloading blinker-1.9.0-py3-none-any.whl.metadata (1.6 kB)
#9 1.779 Collecting click>=8.1.3 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.787   Downloading click-8.5.0-py3-none-any.whl.metadata (2.6 kB)
#9 1.802 Collecting itsdangerous>=2.2.0 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.808   Downloading itsdangerous-2.2.0-py3-none-any.whl.metadata (1.9 kB)
#9 1.826 Collecting jinja2>=3.1.2 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.834   Downloading jinja2-3.1.6-py3-none-any.whl.metadata (2.9 kB)
#9 1.877 Collecting markupsafe>=2.1.1 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.885   Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (2.7 kB)
#9 1.908 Collecting werkzeug>=3.1.0 (from flask>=3.0->-r requirements.txt (line 1))
#9 1.916   Downloading werkzeug-3.1.9-py3-none-any.whl.metadata (4.1 kB)
#9 2.176 Collecting sqlalchemy>=2.0.16 (from Flask-SQLAlchemy->-r requirements.txt (line 3))
#9 2.186   Downloading sqlalchemy-2.1.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl.metadata (9.7 kB)
#9 2.218 Collecting typing-extensions>=4.6.0 (from sqlalchemy>=2.0.16->Flask-SQLAlchemy->-r requirements.txt (line 3))
#9 2.226   Downloading typing_extensions-4.16.0-py3-none-any.whl.metadata (3.3 kB)
#9 2.239 Downloading flask-3.1.3-py3-none-any.whl (103 kB)
#9 2.257 Downloading gunicorn-26.2.0-py3-none-any.whl (228 kB)
#9 2.272 Downloading flask_sqlalchemy-3.1.1-py3-none-any.whl (25 kB)
#9 2.281 Downloading python_dotenv-1.2.3-py3-none-any.whl (22 kB)
#9 2.291 Downloading psycopg2_binary-2.9.13-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.whl (4.3 MB)
#9 2.331    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.3/4.3 MB 107.0 MB/s eta 0:00:00
#9 2.339 Downloading blinker-1.9.0-py3-none-any.whl (8.5 kB)
#9 2.348 Downloading click-8.5.0-py3-none-any.whl (125 kB)
#9 2.358 Downloading itsdangerous-2.2.0-py3-none-any.whl (16 kB)
#9 2.367 Downloading jinja2-3.1.6-py3-none-any.whl (134 kB)
#9 2.377 Downloading markupsafe-3.0.3-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (22 kB)
#9 2.388 Downloading sqlalchemy-2.1.1-cp312-cp312-manylinux2014_x86_64.manylinux_2_17_x86_64.manylinux_2_28_x86_64.whl (4.7 MB)
#9 2.410    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 4.7/4.7 MB 241.7 MB/s eta 0:00:00
#9 2.418 Downloading werkzeug-3.1.9-py3-none-any.whl (228 kB)
#9 2.428 Downloading typing_extensions-4.16.0-py3-none-any.whl (45 kB)
#9 2.470 Installing collected packages: typing-extensions, python-dotenv, psycopg2-binary, markupsafe, itsdangerous, gunicorn, click, blinker, werkzeug, sqlalchemy, jinja2, flask, Flask-SQLAlchemy
#9 4.216 Successfully installed Flask-SQLAlchemy-3.1.1 blinker-1.9.0 click-8.5.0 flask-3.1.3 gunicorn-26.2.0 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.3 psycopg2-binary-2.9.13 python-dotenv-1.2.3 sqlalchemy-2.1.1 typing-extensions-4.16.0 werkzeug-3.1.9
#9 4.217 WARNING: Running pip as the 'root' user can result in broken permissions and conflicting behaviour with the system package manager, possibly rendering your system unusable. It is recommended to use a virtual environment instead: https://pip.pypa.io/warnings/venv. Use the --root-user-action option if you know what you are doing and want to suppress this warning.
#9 4.292
#9 4.292 [notice] A new release of pip is available: 25.0.1 -> 26.2.1
#9 4.292 [notice] To update, run: pip install --upgrade pip
#9 DONE 4.4s
```

#### Installed packages

| Package | Version |
|---|---|
| flask | 3.1.3 |
| gunicorn | 26.2.0 |
| Flask-SQLAlchemy | 3.1.1 |
| python-dotenv | 1.2.3 |
| psycopg2-binary | 2.9.13 |
| blinker | 1.9.0 |
| click | 8.5.0 |
| itsdangerous | 2.2.0 |
| jinja2 | 3.1.6 |
| markupsafe | 3.0.3 |
| werkzeug | 3.1.9 |
| sqlalchemy | 2.1.1 |
| typing-extensions | 4.16.0 |

### [5/5] COPY . /app

```text
#10 [5/5] COPY . /app
#10 DONE 0.0s
```

### Exporting image

```text
#11 exporting to image
#11 exporting layers
#11 exporting layers 0.6s done
#11 writing image sha256:183d69fbb220490e67be424b6a65630ab45a7054ff2d22d1962f4b5eaf09d880 done
#11 naming to docker.io/library/bootcamp2026-student-portal-ecr:fe9fdb7764b12a718ca32ab057aea5df7e88a94e done
#11 DONE 0.6s
```

- **Image ID:** `sha256:183d69fbb220490e67be424b6a65630ab45a7054ff2d22d1962f4b5eaf09d880`
- **Tag:** `docker.io/library/bootcamp2026-student-portal-ecr:fe9fdb7764b12a718ca32ab057aea5df7e88a94e`

## Notes

- The Docker build completed successfully (all 5 stages DONE). The job failure occurred in a later step whose output is not included in this log.
- Warning: pip runs as `root` inside the image — consider a non-root user or virtual environment.