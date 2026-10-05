#!/usr/bin/env python3
"""Triage Trivy findings by severity, EPSS and CISA KEV, and write an HTML report.

Works with any Trivy JSON report (`trivy image|fs|config|repo --format json`)
and handles all three kinds of finding Trivy produces:

  * vulnerabilities    enriched with FIRST EPSS scores and the CISA KEV catalog
  * misconfigurations  (IaC, Dockerfiles, Kubernetes) triaged on severity
  * secrets            triaged as P1: a committed credential must be rotated

Priority rules (the EPSS threshold is configurable):
  P1  Act now   vulnerability in CISA KEV, or a secret found
  P2  High      vulnerability with EPSS probability >= --epss-high (default 0.10)
  P3  Medium    CRITICAL or HIGH vulnerability or misconfiguration
  P4  Low       everything else

Outputs: a self-contained HTML report (--html), a Markdown summary (--summary,
e.g. "$GITHUB_STEP_SUMMARY") and the enriched findings as JSON (--json).

Standard library only, so it runs on any runner with Python 3.9+ and adds
nothing to the pipeline's supply chain.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import sys
import urllib.parse
import urllib.request
from collections import Counter
from pathlib import Path

KEV_URLS = (
    "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json",
    "https://raw.githubusercontent.com/cisagov/kev-data/develop/known_exploited_vulnerabilities.json",
)
EPSS_URL = "https://api.first.org/data/v1/epss"
EPSS_BATCH = 100
HTTP_TIMEOUT = 30
USER_AGENT = "trivy-triage/1.1 (+github-actions)"

SEVERITY_RANK = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "UNKNOWN": 0}
PRIORITIES = {
    "P1": ("Act now", "In CISA KEV (exploited in the wild), or a secret found in code"),
    "P2": ("High", "EPSS at or above the threshold: exploitation likely soon"),
    "P3": ("Medium", "CRITICAL or HIGH, no exploitation signal"),
    "P4": ("Low", "Everything else"),
}
KIND_LABEL = {"vuln": "Vulnerability", "misconfig": "Misconfiguration", "secret": "Secret"}


# --------------------------------------------------------------------------- #
# Data sources
# --------------------------------------------------------------------------- #
def http_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:  # noqa: S310 (fixed https URLs)
        return json.load(resp)


def load_kev(kev_file: str | None, offline: bool) -> tuple[dict, str]:
    """Return ({cve: entry}, provenance text)."""
    if kev_file:
        data = json.loads(Path(kev_file).read_text(encoding="utf-8"))
        source = f"file {kev_file}"
    elif offline:
        return {}, "CISA KEV not loaded (offline)"
    else:
        data, source, errors = None, "", []
        for url in KEV_URLS:
            try:
                data, source = http_get_json(url), url
                break
            except (OSError, json.JSONDecodeError) as exc:
                errors.append(f"{url}: {exc}")
        if data is None:
            warn("KEV catalog unavailable, P1 not assessed for vulnerabilities: " + " | ".join(errors))
            return {}, "CISA KEV unavailable: P1 not assessed for vulnerabilities"
    entries = {v["cveID"]: v for v in data.get("vulnerabilities", []) if v.get("cveID")}
    version = data.get("catalogVersion", "?")
    return entries, f"CISA KEV catalog {version} ({len(entries)} entries) from {source}"


def load_epss(cves: list[str], epss_file: str | None, offline: bool) -> tuple[dict, str]:
    """Return ({cve: {"epss", "percentile", "date"}}, provenance text)."""
    rows: list[dict] = []
    if epss_file:
        rows = json.loads(Path(epss_file).read_text(encoding="utf-8")).get("data", [])
        source = f"file {epss_file}"
    elif not cves:
        return {}, "FIRST EPSS not queried (no CVEs in this scan)"
    elif offline:
        return {}, "FIRST EPSS not loaded (offline)"
    else:
        source = EPSS_URL
        for i in range(0, len(cves), EPSS_BATCH):
            chunk = cves[i : i + EPSS_BATCH]
            query = urllib.parse.urlencode({"cve": ",".join(chunk), "limit": EPSS_BATCH})
            try:
                rows.extend(http_get_json(f"{EPSS_URL}?{query}").get("data", []))
            except (OSError, json.JSONDecodeError) as exc:
                warn(f"EPSS lookup failed for {len(chunk)} CVEs: {exc}")
                source = f"{EPSS_URL} (partial)"
    scores = {}
    for r in rows:
        try:
            scores[r["cve"]] = {"epss": float(r["epss"]), "percentile": float(r["percentile"]), "date": r.get("date", "")}
        except (KeyError, TypeError, ValueError):
            continue
    dates = sorted({s["date"] for s in scores.values() if s["date"]})
    as_of = f", scores dated {dates[-1]}" if dates else ""
    return scores, f"FIRST EPSS ({len(scores)} CVEs scored{as_of}) from {source}"


# --------------------------------------------------------------------------- #
# Trivy parsing and triage
# --------------------------------------------------------------------------- #
def cvss_score(vuln: dict) -> float | None:
    """Best available CVSS base score: NVD first, then any vendor."""
    cvss = vuln.get("CVSS") or {}
    for source in ["nvd"] + [k for k in cvss if k != "nvd"]:
        entry = cvss.get(source) or {}
        for key in ("V40Score", "V3Score", "V2Score"):
            if isinstance(entry.get(key), (int, float)):
                return float(entry[key])
    return None


def location(target: str, start, end=None) -> str:
    if not start:
        return target
    return f"{target}:{start}" + (f"-{end}" if end and end != start else "")


def base(kind: str, fid: str, severity: str, title: str, url: str, target: str) -> dict:
    return {
        "kind": kind,
        "id": fid,
        "is_cve": fid.upper().startswith("CVE-"),
        "severity": (severity or "UNKNOWN").upper(),
        "title": title,
        "url": url or "",
        "target": target,
        # filled per kind below or by triage()
        "cvss": None, "package": "", "installed": "", "fixed": "",
        "where": target, "resource": "", "resolution": "", "category": "",
    }


def parse_trivy(report: dict) -> list[dict]:
    findings = []
    for result in report.get("Results") or []:
        target = result.get("Target", "")

        for v in result.get("Vulnerabilities") or []:
            f = base("vuln", v.get("VulnerabilityID", ""), v.get("Severity"),
                     v.get("Title") or (v.get("Description") or "")[:140], v.get("PrimaryURL"), target)
            f.update(cvss=cvss_score(v), package=v.get("PkgName", ""),
                     installed=v.get("InstalledVersion", ""), fixed=v.get("FixedVersion", ""))
            findings.append(f)

        for m in result.get("Misconfigurations") or []:
            if (m.get("Status") or "FAIL") != "FAIL":
                continue
            cause = m.get("CauseMetadata") or {}
            f = base("misconfig", m.get("ID") or m.get("AVDID", ""), m.get("Severity"),
                     m.get("Title") or m.get("Message", ""), m.get("PrimaryURL"), target)
            f.update(where=location(target, cause.get("StartLine"), cause.get("EndLine")),
                     resource=cause.get("Resource", ""), resolution=m.get("Resolution", ""))
            findings.append(f)

        for s in result.get("Secrets") or []:
            # Never copy s["Match"]: even redacted, it does not belong in a report artifact.
            f = base("secret", s.get("RuleID", ""), s.get("Severity"), s.get("Title", ""), "", target)
            f.update(where=location(target, s.get("StartLine"), s.get("EndLine")), category=s.get("Category", ""))
            findings.append(f)
    return findings


def triage(findings: list[dict], kev: dict, epss: dict, epss_high: float) -> list[dict]:
    for f in findings:
        k = kev.get(f["id"]) if f["kind"] == "vuln" else None
        e = epss.get(f["id"]) if f["kind"] == "vuln" else None
        f["kev"] = bool(k)
        f["kev_added"] = k.get("dateAdded", "") if k else ""
        f["kev_due"] = k.get("dueDate", "") if k else ""
        f["kev_ransomware"] = (k.get("knownRansomwareCampaignUse", "") == "Known") if k else False
        f["epss"] = e["epss"] if e else None
        f["epss_pct"] = e["percentile"] if e else None
        high = SEVERITY_RANK.get(f["severity"], 0) >= SEVERITY_RANK["HIGH"]
        if f["kind"] == "secret" or f["kev"]:
            f["priority"] = "P1"
        elif f["epss"] is not None and f["epss"] >= epss_high:
            f["priority"] = "P2"
        elif high:
            f["priority"] = "P3"
        else:
            f["priority"] = "P4"
    findings.sort(
        key=lambda f: (f["priority"], -(f["epss"] or 0.0), -SEVERITY_RANK.get(f["severity"], 0),
                       -(f["cvss"] or 0.0), f["id"])
    )
    return findings


# --------------------------------------------------------------------------- #
# Output
# --------------------------------------------------------------------------- #
def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def safe_link(url: str, text: str) -> str:
    if url.startswith("https://"):
        return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(text)}</a>'
    return esc(text)


def pill(f: dict) -> str:
    return f'<span class="pill {f["priority"].lower()}">{f["priority"]}</span>'


def sev(f: dict) -> str:
    return f'<span class="sev {f["severity"].lower()}">{esc(f["severity"])}</span>'


def fmt_epss(f: dict) -> str:
    if f["epss"] is None:
        return '<span class="muted">not scored</span>' if f["is_cve"] else '<span class="muted">n/a</span>'
    return f'{f["epss"] * 100:.2f}%<span class="sub">top {max(0.0, (1 - f["epss_pct"]) * 100):.1f}%</span>'


def vuln_rows(items: list[dict]) -> str:
    rows = []
    for f in items:
        kev_cell = '<span class="muted">no</span>'
        if f["kev"]:
            kev_cell = f'<span class="kev">KEV</span><span class="sub">added {esc(f["kev_added"])}</span>'
            if f["kev_ransomware"]:
                kev_cell += '<span class="sub ransom">ransomware use</span>'
        fixed = esc(f["fixed"]) if f["fixed"] else '<span class="warn">no fix yet</span>'
        cvss = f'{f["cvss"]:.1f}' if f["cvss"] is not None else '<span class="muted">n/a</span>'
        rows.append(
            f"<tr><td>{pill(f)}</td><td class=\"mono\">{safe_link(f['url'], f['id'])}</td><td>{sev(f)}</td>"
            f"<td class=\"num-cell\">{cvss}</td><td class=\"num-cell\">{fmt_epss(f)}</td><td>{kev_cell}</td>"
            f"<td class=\"mono\">{esc(f['package'])}</td><td class=\"mono\">{esc(f['installed'])}</td>"
            f"<td class=\"mono\">{fixed}</td>"
            f"<td>{esc(f['title'])}<span class=\"sub mono\">{esc(f['target'])}</span></td></tr>"
        )
    head = ("<th>Priority</th><th>ID</th><th>Severity</th><th>CVSS</th><th>EPSS</th><th>KEV</th>"
            "<th>Package</th><th>Installed</th><th>Fixed in</th><th>Title · target</th>")
    return head, "".join(rows)


def misconfig_rows(items: list[dict]) -> str:
    rows = [
        f"<tr><td>{pill(f)}</td><td class=\"mono\">{safe_link(f['url'], f['id'])}</td><td>{sev(f)}</td>"
        f"<td class=\"mono\">{esc(f['where'])}<span class=\"sub\">{esc(f['resource'])}</span></td>"
        f"<td>{esc(f['title'])}<span class=\"sub\">{esc(f['resolution'])}</span></td></tr>"
        for f in items
    ]
    return ("<th>Priority</th><th>Check</th><th>Severity</th><th>Where · resource</th><th>Issue · how to fix</th>",
            "".join(rows))


def secret_rows(items: list[dict]) -> str:
    rows = [
        f"<tr><td>{pill(f)}</td><td class=\"mono\">{esc(f['id'])}</td><td>{sev(f)}</td>"
        f"<td>{esc(f['category'])}</td><td class=\"mono\">{esc(f['where'])}</td>"
        f"<td>{esc(f['title'])}<span class=\"sub\">Rotate the credential, then remove it from git history.</span></td></tr>"
        for f in items
    ]
    return ("<th>Priority</th><th>Rule</th><th>Severity</th><th>Category</th><th>Where</th><th>What to do</th>",
            "".join(rows))


def section(title: str, items: list[dict], builder, min_width: int) -> str:
    if not items:
        return ""
    head, body = builder(items)
    return (f'<section><h2>{esc(title)} <span class="count">{len(items)}</span></h2>'
            f'<div class="panel"><table style="min-width:{min_width}px"><thead><tr>{head}</tr></thead>'
            f"<tbody>{body}</tbody></table></div></section>")


def render_html(findings: list[dict], meta: dict) -> str:
    counts = Counter(f["priority"] for f in findings)
    kinds = Counter(f["kind"] for f in findings)
    by_kind = {k: [f for f in findings if f["kind"] == k] for k in KIND_LABEL}

    cards = "".join(
        f'<div class="card {p.lower()}"><div class="num">{counts.get(p, 0)}</div>'
        f'<div class="lbl">{p} · {esc(name)}</div><div class="rule">{esc(rule)}</div></div>'
        for p, (name, rule) in PRIORITIES.items()
    )
    kind_line = " · ".join(f"{kinds[k]} {KIND_LABEL[k].lower()}{'s' if kinds[k] != 1 else ''}"
                           for k in KIND_LABEL if kinds.get(k)) or "no findings"
    sections = (
        section("Vulnerabilities", by_kind["vuln"], vuln_rows, 1100)
        + section("Misconfigurations", by_kind["misconfig"], misconfig_rows, 860)
        + section("Secrets", by_kind["secret"], secret_rows, 860)
    ) or '<section class="panel empty">No findings in this scan.</section>'
    notes = "".join(f"<li>{esc(n)}</li>" for n in meta["notes"])

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Security triage · {esc(meta["title"])}</title>
<style>
:root{{--bg:#f6f7f9;--panel:#fff;--ink:#17202b;--muted:#5d6876;--line:#dde2e8;
--p1:#b42318;--p1bg:#fdecea;--p2:#b54708;--p2bg:#fef3e2;--p3:#175cd3;--p3bg:#e9f1fe;--p4:#5d6876;--p4bg:#eef1f4}}
@media (prefers-color-scheme:dark){{:root{{--bg:#0f141b;--panel:#161d26;--ink:#e6eaf0;--muted:#97a3b3;--line:#2a3441;
--p1:#ff8a80;--p1bg:#3a1a19;--p2:#ffb86b;--p2bg:#35260f;--p3:#8ab8ff;--p3bg:#172840;--p4:#a9b3c1;--p4bg:#232b36}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--ink);font:14px/1.5 -apple-system,"Segoe UI",Roboto,sans-serif;padding:32px 20px}}
main{{max-width:1280px;margin:0 auto;display:flex;flex-direction:column;gap:24px}}
h1{{margin:0;font-size:24px}} h2{{margin:0 0 8px;font-size:16px}}
.count{{color:var(--muted);font-weight:400}}
.meta{{color:var(--muted);font-size:13px}}
.mono{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12.5px}}
.cards{{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:12px}}
@media (max-width:760px){{.cards{{grid-template-columns:repeat(2,minmax(0,1fr))}}}}
.card{{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px 16px;border-top:4px solid var(--p4)}}
.card.p1{{border-top-color:var(--p1)}} .card.p2{{border-top-color:var(--p2)}} .card.p3{{border-top-color:var(--p3)}}
.card .num{{font-size:30px;font-weight:700;font-variant-numeric:tabular-nums}}
.card .lbl{{font-weight:600}} .card .rule{{color:var(--muted);font-size:12.5px}}
.panel{{background:var(--panel);border:1px solid var(--line);border-radius:10px;overflow-x:auto}}
table{{border-collapse:collapse;width:100%}}
th,td{{text-align:left;padding:9px 12px;border-bottom:1px solid var(--line);vertical-align:top}}
th{{font-size:11.5px;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);background:var(--panel)}}
tr:last-child td{{border-bottom:0}}
.num-cell{{font-variant-numeric:tabular-nums;white-space:nowrap}}
.sub{{display:block;color:var(--muted);font-size:11.5px}}
.pill{{display:inline-block;font-weight:700;font-size:12px;padding:2px 8px;border-radius:4px}}
.pill.p1{{color:var(--p1);background:var(--p1bg)}} .pill.p2{{color:var(--p2);background:var(--p2bg)}}
.pill.p3{{color:var(--p3);background:var(--p3bg)}} .pill.p4{{color:var(--p4);background:var(--p4bg)}}
.sev{{font-size:12px;font-weight:600}} .sev.critical{{color:var(--p1)}} .sev.high{{color:var(--p2)}}
.kev{{font-weight:700;color:var(--p1)}} .ransom{{color:var(--p1)}} .warn{{color:var(--p2)}} .muted{{color:var(--muted)}}
.empty{{text-align:center;color:var(--muted);padding:32px}}
a{{color:var(--p3)}} ul{{margin:0;padding-left:20px;color:var(--muted);font-size:13px}}
</style>
</head>
<body>
<main>
<header>
<h1>Security triage · {esc(meta["title"])}</h1>
<div class="meta">{len(findings)} findings · {esc(kind_line)} · generated {esc(meta["generated"])}</div>
</header>
<section class="cards">{cards}</section>
{sections}
<section>
<h2>Sources and rules</h2>
<ul>{notes}</ul>
</section>
</main>
</body>
</html>
"""


def md(value) -> str:
    return str(value or "").replace("|", "\\|").replace("\n", " ")


def render_summary(findings: list[dict], meta: dict) -> str:
    counts = Counter(f["priority"] for f in findings)
    lines = [f"## Security triage · {md(meta['title'])}", "", "| Priority | Meaning | Findings |", "|---|---|---|"]
    for p, (name, rule) in PRIORITIES.items():
        lines.append(f"| **{p}** {name} | {rule} | {counts.get(p, 0)} |")
    top = [f for f in findings if f["priority"] in ("P1", "P2")][:15]
    if top:
        lines += ["", "### Fix first", "", "| ID | Type | Severity | EPSS | KEV | Where | Fix |", "|---|---|---|---|---|---|---|"]
        for f in top:
            epss = f"{f['epss'] * 100:.2f}%" if f["epss"] is not None else "n/a"
            kev = f"yes (added {f['kev_added']})" if f["kev"] else ("no" if f["kind"] == "vuln" else "n/a")
            where = f"`{md(f['package'])} {md(f['installed'])}`" if f["kind"] == "vuln" else f"`{md(f['where'])}`"
            if f["kind"] == "vuln":
                fix = md(f["fixed"]) or "no fix yet"
            elif f["kind"] == "secret":
                fix = "rotate the credential"
            else:
                fix = md(f["resolution"])
            lines.append(f"| {md(f['id'])} | {KIND_LABEL[f['kind']]} | {f['severity']} | {epss} | {kev} | {where} | {fix} |")
    lines += ["", f"Full report: download the `{md(meta['artifact'])}` artifact from this run.", ""]
    lines += [f"<sub>{md(n)}</sub><br>" for n in meta["notes"]]
    return "\n".join(lines) + "\n"


def warn(msg: str) -> None:
    print(f"::warning title=trivy-triage::{msg}", file=sys.stderr)


# --------------------------------------------------------------------------- #
def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", required=True, help="Trivy JSON report")
    ap.add_argument("--html", default="trivy-triage.html", help="HTML report to write")
    ap.add_argument("--summary", help="Markdown summary to append to (e.g. $GITHUB_STEP_SUMMARY)")
    ap.add_argument("--json", dest="json_out", help="Write enriched findings as JSON")
    ap.add_argument("--title", default="Trivy scan", help="Report title, e.g. the image or folder name")
    ap.add_argument("--artifact", default="trivy-triage-report", help="Artifact name shown in the summary")
    ap.add_argument("--epss-high", type=float, default=0.10, help="EPSS probability for P2 (default 0.10)")
    ap.add_argument("--fail-on", choices=["P1", "P2", "P3", "none"], default="none",
                    help="Exit 1 if any finding is at this priority or higher (default: none)")
    ap.add_argument("--kev-file", help="Use a local KEV JSON instead of downloading it")
    ap.add_argument("--epss-file", help="Use a local EPSS API response instead of querying it")
    ap.add_argument("--offline", action="store_true", help="Skip all network lookups")
    args = ap.parse_args()

    report = json.loads(Path(args.input).read_text(encoding="utf-8"))
    findings = parse_trivy(report)
    cves = sorted({f["id"] for f in findings if f["kind"] == "vuln" and f["is_cve"]})

    if any(f["kind"] == "vuln" for f in findings):
        kev, kev_note = load_kev(args.kev_file, args.offline)
        epss, epss_note = load_epss(cves, args.epss_file, args.offline)
    else:
        kev, kev_note = {}, "CISA KEV not needed (no vulnerabilities in this scan)"
        epss, epss_note = {}, "FIRST EPSS not needed (no vulnerabilities in this scan)"
    findings = triage(findings, kev, epss, args.epss_high)

    meta = {
        "title": args.title,
        "artifact": args.artifact,
        "generated": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "notes": [
            kev_note,
            epss_note,
            f"P1 = vulnerability in KEV, or any secret · P2 = EPSS ≥ {args.epss_high:.0%} · "
            "P3 = CRITICAL/HIGH · P4 = rest. EPSS and KEV cover CVE IDs only; GHSA IDs, "
            "misconfigurations and other findings are triaged on severity.",
            f"Scanned: {report.get('ArtifactName', 'unknown')} ({report.get('ArtifactType', 'unknown type')})",
        ],
    }

    for out in (args.html, args.json_out):
        if out:
            Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.html).write_text(render_html(findings, meta), encoding="utf-8")
    if args.summary:
        with open(args.summary, "a", encoding="utf-8") as fh:
            fh.write(render_summary(findings, meta))
    if args.json_out:
        Path(args.json_out).write_text(json.dumps(findings, indent=2), encoding="utf-8")

    counts = Counter(f["priority"] for f in findings)
    print(f"trivy-triage: {len(findings)} findings · " + " · ".join(f"{p} {counts.get(p, 0)}" for p in PRIORITIES))
    print(f"trivy-triage: report written to {args.html}")

    if args.fail_on != "none":
        blocking = [f for f in findings if f["priority"] <= args.fail_on]
        if blocking:
            print(f"::error title=trivy-triage::{len(blocking)} finding(s) at {args.fail_on} or higher")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
