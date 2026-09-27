import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from board import collect, load_jobs, render

ROOT = Path(__file__).resolve().parents[1]


class BoardTests(unittest.TestCase):
    def test_sample_counts(self) -> None:
        rows, sources, summary = collect(load_jobs(ROOT / "fixtures" / "jobs.json"))
        self.assertEqual(summary["jobs"], 2)
        self.assertEqual(summary["open"], 1)
        self.assertEqual(summary["sent"], 1)
        self.assertEqual(len(sources), 3)
        self.assertEqual(rows[0]["status"], "לא הוגש")
        self.assertEqual(rows[1]["kind"], "טופס באתר")

    def test_duplicate_url_is_one_source(self) -> None:
        jobs = [
            {"company": "א", "title": "ת", "source_url": "https://example.com/same", "status": "not_submitted"},
            {"company": "ב", "title": "ת", "source_url": "https://example.com/same", "status": "closed"},
        ]
        _, sources, summary = collect(jobs)
        self.assertEqual(len(sources), 1)
        self.assertEqual(summary["open"], 1)
        self.assertEqual(summary["closed"], 1)

    def test_html_is_escaped(self) -> None:
        page = render([{"company": "<b>", "title": "ת", "status": "not_submitted", "application_type": "email"}])
        self.assertIn("&lt;b&gt;", page)
        self.assertNotIn("<b>", page.split("<style>", 1)[-1])


if __name__ == "__main__":
    unittest.main()
