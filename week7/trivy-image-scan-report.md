# Trivy Image Scan Report

| Field | Value |
|---|---|
| Image | `344707019777.dkr.ecr.us-east-1.amazonaws.com/bootcamp2026-student-portal-ecr:3e81c671d37167e339b41e6fd294759202bc7501` |
| OS | Debian 13.7 (87 packages) |
| Scan date | 2026-09-30 10:14 UTC |
| Scanners | vuln, secret |
| Vulnerability DB | `mirror.gcr.io/aquasec/trivy-db:2` (118.55 MiB, freshly downloaded) |

## Scan log

```text
2026-09-30T10:14:36Z  INFO  [vulndb] Need to update DB
2026-09-30T10:14:36Z  INFO  [vulndb] Downloading vulnerability DB...
2026-09-30T10:14:36Z  INFO  [vulndb] Downloading artifact...  repo="mirror.gcr.io/aquasec/trivy-db:2"
2026-09-30T10:14:41Z  INFO  [vulndb] Artifact successfully downloaded  repo="mirror.gcr.io/aquasec/trivy-db:2"
2026-09-30T10:14:41Z  INFO  [vuln] Vulnerability scanning is enabled
2026-09-30T10:14:41Z  INFO  [secret] Secret scanning is enabled
2026-09-30T10:14:41Z  INFO  [secret] If your scanning is slow, please try '--scanners vuln' to disable secret scanning
2026-09-30T10:14:41Z  INFO  [secret] Please see https://trivy.dev/docs/v0.74/guide/scanner/secret#recommendation for faster secret detection
2026-09-30T10:14:46Z  INFO  [python] Licenses acquired from one or more METADATA files may be subject to additional terms. Use `--debug` flag to see all affected packages.
2026-09-30T10:14:46Z  INFO  Detected OS  family="debian" version="13.7"
2026-09-30T10:14:46Z  INFO  [debian] Detecting vulnerabilities...  os_version="13" pkg_num=87
2026-09-30T10:14:46Z  INFO  Number of language-specific files  num=1
2026-09-30T10:14:46Z  INFO  [python-pkg] Detecting vulnerabilities...
2026-09-30T10:14:46Z  WARN  Using severities from other vendors for some vulnerabilities. Read https://trivy.dev/docs/v0.74/guide/scanner/vulnerability#severity-selection for details.
```

## Report summary

| Target | Type | Vulnerabilities | Secrets |
|---|---|---|---|
| `bootcamp2026-student-portal-ecr:3e81c671…` (debian 13.7) | debian | **6** | - |
| `blinker-1.9.0` | python-pkg | 0 | - |
| `click-8.5.0` | python-pkg | 0 | - |
| `flask-3.1.3` | python-pkg | 0 | - |
| `flask_sqlalchemy-3.1.1` | python-pkg | 0 | - |
| `gunicorn-26.2.0` | python-pkg | 0 | - |
| `itsdangerous-2.2.0` | python-pkg | 0 | - |
| `jinja2-3.1.6` | python-pkg | 0 | - |
| `markupsafe-3.0.3` | python-pkg | 0 | - |
| `pip-25.0.1` | python-pkg | 0 | - |
| `psycopg2_binary-2.9.13` | python-pkg | 0 | - |
| `python_dotenv-1.2.3` | python-pkg | 0 | - |
| `sqlalchemy-2.1.1` | python-pkg | 0 | - |
| `typing_extensions-4.16.0` | python-pkg | 0 | - |
| `werkzeug-3.1.9` | python-pkg | 0 | - |

Python packages are located under `usr/local/lib/python3.12/site-packages/`.

**Legend:** `-` = not scanned, `0` = clean (no security findings detected)

## Vulnerabilities — debian 13.7

**Total: 6 (HIGH: 6, CRITICAL: 0)**

| Library | Vulnerability | Severity | Status | Installed Version | Fixed Version | Title |
|---|---|---|---|---|---|---|
| libssl3t64 | [CVE-2026-75804](https://avd.aquasec.com/nvd/cve-2026-75804) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Denial of Service via unenforced QUIC connection flow control |
| libssl3t64 | [CVE-2026-84782](https://avd.aquasec.com/nvd/cve-2026-84782) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Information disclosure via DTLS handshake retransmission |
| openssl | [CVE-2026-75804](https://avd.aquasec.com/nvd/cve-2026-75804) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Denial of Service via unenforced QUIC connection flow control |
| openssl | [CVE-2026-84782](https://avd.aquasec.com/nvd/cve-2026-84782) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Information disclosure via DTLS handshake retransmission |
| openssl-provider-legacy | [CVE-2026-75804](https://avd.aquasec.com/nvd/cve-2026-75804) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Denial of Service via unenforced QUIC connection flow control |
| openssl-provider-legacy | [CVE-2026-84782](https://avd.aquasec.com/nvd/cve-2026-84782) | HIGH | fixed | 3.5.7-1~deb13u2 | 3.5.7-1~deb13u3 | OpenSSL: Information disclosure via DTLS handshake retransmission |

## Notes

- All 6 findings are the same 2 OpenSSL CVEs across 3 packages, and all are fixed in `3.5.7-1~deb13u3`.
- No vulnerabilities were found in any Python package.
- No secrets were detected.
