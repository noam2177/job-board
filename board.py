"""Turn a local jobs file into one HTML page. This does not send mail."""

from __future__ import annotations

import html
import json
from pathlib import Path

_STATUS = {
    "not_submitted": "לא הוגש",
    "email_sent": "מייל נשלח",
    "submitted": "טופס הוגש",
    "closed": "נסגר",
}
_KIND = {"email": "מייל", "web_form": "טופס באתר"}


def load_jobs(path: Path) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    jobs = data.get("jobs") if isinstance(data, dict) else None
    return [job for job in jobs if isinstance(job, dict)] if isinstance(jobs, list) else []


def collect(jobs: list[dict]) -> tuple[list[dict], list[dict], dict]:
    rows: list[dict] = []
    sources: list[dict] = []
    seen: set[str] = set()
    for job in jobs:
        company = str(job.get("company") or "")
        title = str(job.get("title") or "")
        status = _STATUS.get(str(job.get("status") or "not_submitted"), "לא הוגש")
        rows.append(
            {
                "company": company,
                "title": title,
                "location": str(job.get("location") or ""),
                "kind": _KIND.get(str(job.get("application_type") or ""), "לא ידוע"),
                "status": status,
                "source": str(job.get("source_url") or ""),
                "notes": str(job.get("notes") or ""),
            }
        )
        for label, url in (
            ("דף המשרה", str(job.get("source_url") or "")),
            ("לוח", str(job.get("source_index_url") or "")),
        ):
            if not url or url in seen:
                continue
            seen.add(url)
            sources.append({"label": label, "url": url, "company": company, "title": title})
    summary = {
        "jobs": len(rows),
        "sources": len(sources),
        "sent": sum(1 for row in rows if row["status"] == "מייל נשלח"),
        "open": sum(1 for row in rows if row["status"] == "לא הוגש"),
    }
    return rows, sources, summary


def render(jobs: list[dict]) -> str:
    rows, sources, summary = collect(jobs)

    def cell(value: object) -> str:
        return html.escape(str(value or ""), quote=True)

    job_html = []
    for row in rows:
        link = f'<a href="{cell(row["source"])}">{cell(row["source"])}</a>' if row["source"] else ""
        job_html.append(
            "<tr>"
            f"<td>{cell(row['company'])}</td>"
            f"<td>{cell(row['title'])}</td>"
            f"<td>{cell(row['location'])}</td>"
            f"<td>{cell(row['kind'])}</td>"
            f"<td>{cell(row['status'])}</td>"
            f"<td>{link}</td>"
            f"<td>{cell(row['notes'])}</td>"
            "</tr>"
        )
    source_html = [
        "<tr>"
        f"<td>{cell(row['label'])}</td>"
        f"<td>{cell(row['company'])}</td>"
        f"<td>{cell(row['title'])}</td>"
        f'<td><a href="{cell(row["url"])}">{cell(row["url"])}</a></td>'
        "</tr>"
        for row in sources
    ]
    return f"""<!DOCTYPE html>
<html lang="he" dir="rtl">
<head>
<meta charset="utf-8">
<title>מעקב משרות</title>
<style>
body {{ font-family: Segoe UI, Arial, sans-serif; margin: 24px; background: #f6f4ef; color: #1c1915; }}
table {{ border-collapse: collapse; width: 100%; background: white; margin: 12px 0 28px; }}
th, td {{ border: 1px solid #e4ddd0; padding: 8px; text-align: right; vertical-align: top; }}
th {{ background: #efe7d6; }}
a {{ word-break: break-all; }}
</style>
</head>
<body>
<h1>מעקב משרות</h1>
<p>{summary['jobs']} משרות · {summary['sources']} מקורות · {summary['sent']} נשלחו · {summary['open']} עדיין לא הוגשו.</p>
<h2>משרות</h2>
<table>
<thead><tr><th>חברה</th><th>תפקיד</th><th>מיקום</th><th>סוג</th><th>סטטוס</th><th>מקור</th><th>הערה</th></tr></thead>
<tbody>{''.join(job_html)}</tbody>
</table>
<h2>מקורות</h2>
<table>
<thead><tr><th>סוג</th><th>חברה</th><th>תפקיד</th><th>כתובת</th></tr></thead>
<tbody>{''.join(source_html)}</tbody>
</table>
</body>
</html>
"""


def write_board(source: Path, dest: Path) -> Path:
    dest.write_text(render(load_jobs(source)), encoding="utf-8")
    return dest


def main() -> None:
    root = Path(__file__).resolve().parent
    dest = write_board(root / "fixtures" / "jobs.json", root / "board.html")
    print(dest)


if __name__ == "__main__":
    main()
