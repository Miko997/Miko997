"""Failure retention, deterministic refresh, and complete image/data agreement."""
import copy
import json
import re
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from unittest.mock import Mock, patch
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from profile_data import Client, DataError, summarize
from update_profile import prepare_outputs, refresh, validate_refresh


def snapshot():
    stats = summarize({"2026-01-01": 1, "2026-01-02": 0, "2026-01-03": 2}, date(2026, 1, 3))
    stats["visible_commits_365"] = None
    return {"schema_version": 2, "login": "Miko997", "as_of": "2026-01-03",
            "account_created": "2026-01-01", "source": "github-public-contribution-calendar",
            "stats": stats, "upstream": {"merged": []},
            "visibility": {"aggregate_calendar": "unavailable"}}


def readme():
    return ('<!-- IMPACT:START -->old<!-- IMPACT:END -->\n<picture>\n'
            '<source srcset="./assets/generated/contribution-core-mobile-static.svg?v=abc" />\n'
            '<source srcset="./assets/generated/contribution-core-mobile.svg?v=abc" />\n'
            '<source srcset="./assets/generated/contribution-core-static.svg?v=abc" />\n'
            '<img src="./assets/generated/contribution-core.svg?v=abc" alt="stale" />\n'
            '</picture>\n<img src="./assets/signature-header.webp" alt="Miko" />')


class RefreshTests(unittest.TestCase):
    def test_fetch_failure_preserves_every_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(readme())
            (root / "data").mkdir()
            (root / "data/public-activity.json").write_text(json.dumps(snapshot()))
            before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
            with patch("update_profile.collect", side_effect=DataError("rate limit")):
                with self.assertRaises(DataError):
                    refresh(root, Client(), date(2026, 1, 3))
            self.assertEqual(before, {p: p.read_bytes() for p in root.rglob("*") if p.is_file()})

    def test_render_failure_also_preserves_every_file(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(readme())
            before = (root / "README.md").read_bytes()
            with patch("update_profile.collect", return_value=snapshot()), patch(
                    "update_profile.dashboard", side_effect=ValueError("render failed")):
                with self.assertRaises(ValueError):
                    refresh(root, Client(), date(2026, 1, 3))
            self.assertEqual((root / "README.md").read_bytes(), before)
            self.assertFalse((root / "data/public-activity.json").exists())

    def test_unchanged_refresh_preserves_all_mtimes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "README.md").write_text(readme())
            with patch("update_profile.collect", side_effect=lambda *a: snapshot()):
                refresh(root, Client(), date(2026, 1, 3))
                before = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
                refresh(root, Client(), date(2026, 1, 3))
                self.assertEqual(before, {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()})

    def test_all_four_variants_match_dates_counts_and_metrics(self):
        s = snapshot()
        out = prepare_outputs(s, readme())
        images = {name: content for name, content in out.items() if name.endswith(".svg")}
        self.assertEqual(len(images), 4)
        for name, content in images.items():
            tree = ET.fromstring(content)
            cells = [n for n in tree.iter() if "data-date" in n.attrib]
            expected = {d: str(n) for d, n in s["stats"]["days"]}
            self.assertEqual({n.attrib["data-date"]: n.attrib["data-count"] for n in cells}, expected, name)
            self.assertEqual(len(cells), 365, name)
            self.assertIn("3 contributions in 365 days", content)
            if "static" in name:
                self.assertNotIn("@keyframes", content)
                self.assertNotIn("<animate", content)

    def test_cache_covers_mobile_and_static_and_alt_is_current(self):
        out = prepare_outputs(snapshot(), readme())
        tags = re.findall(r'contribution-core[^"\s]+', out["README.md"])
        self.assertEqual(len(tags), 4)
        self.assertEqual(len({s.split("?v=")[1] for s in tags}), 1)
        self.assertIn('alt="3 GitHub contributions from 2025-01-04 to 2026-01-03; current contribution streak 1 days"', out["README.md"])
        self.assertIn('alt="Miko"', out["README.md"])
        self.assertFalse(any("header" in name or "footer" in name for name in out))

    def test_design_change_invalidates_image_cache(self):
        before = prepare_outputs(snapshot(), readme())["README.md"]
        with patch("update_profile.dashboard", return_value="<svg>new art</svg>"):
            after = prepare_outputs(snapshot(), readme())["README.md"]
        self.assertNotEqual(re.findall(r"v=([0-9a-f]+)", before), re.findall(r"v=([0-9a-f]+)", after))

    def test_optional_api_outage_cannot_erase_previously_verified_counts(self):
        old = snapshot()
        old["source"] = "github-verified-aggregate-contribution-calendar"
        old["stats"]["days"][-1][1] = 20
        with self.assertRaises(DataError):
            validate_refresh(old, snapshot())
        # A complete newly verified source may contain a legitimate correction.
        new = snapshot()
        new["visibility"]["aggregate_calendar"] = "verified"
        new["source"] = "github-verified-aggregate-contribution-calendar"
        validate_refresh(old, new)

    def test_stale_graphql_cannot_erase_previous_enriched_calendar(self):
        old = snapshot()
        old["source"] = "github-verified-aggregate-contribution-calendar"
        old["stats"]["all_time"] = 1574
        old["stats"]["days"][-1][1] = 20
        new = snapshot()
        new["stats"]["all_time"] = 965
        new["visibility"] = {"aggregate_calendar": "public-calendar-retained",
                             "aggregate_calendar_all_time": 900}
        with self.assertRaises(DataError):
            validate_refresh(old, new)

    def test_zero_and_three_digit_streaks_are_data_dependent(self):
        for number in (0, 1, 10, 100):
            s = snapshot()
            s["stats"]["streak"]["current"] = number
            images = prepare_outputs(s, readme())
            for path, svg in images.items():
                if path.endswith(".svg"):
                    self.assertIn(f'>{number}</text>', svg)
                    if number == 0:
                        self.assertIn("No current streak", svg)


class RequestTests(unittest.TestCase):
    def test_rate_limit_retries_then_fails_without_response_body(self):
        client = Client("TEST_ONLY")
        client.opener = Mock()
        client.opener.open.side_effect = HTTPError("https://api.github.com/graphql", 429,
                                                   "SECRET_RESPONSE", {}, None)
        with patch("profile_data.time.sleep"):
            with self.assertRaisesRegex(DataError, "HTTP 429") as error:
                client.request("https://api.github.com/graphql", {"query": "x"})
        self.assertEqual(client.opener.open.call_count, 3)
        self.assertNotIn("SECRET", str(error.exception))

    def test_html_calendar_never_sends_api_token(self):
        client = Client("TEST_ONLY")
        response = Mock()
        response.read.return_value = b"calendar"
        client.opener = Mock()
        client.opener.open.return_value.__enter__ = Mock(return_value=response)
        client.opener.open.return_value.__exit__ = Mock(return_value=None)
        client.request("https://github.com/users/Miko997/contributions")
        request = client.opener.open.call_args.args[0]
        self.assertNotIn("Authorization", request.headers)

    def test_malformed_json_fails_without_echoing_body(self):
        client = Client()
        response = Mock()
        response.read.return_value = b"SECRET_BROKEN_BODY"
        client.opener = Mock()
        client.opener.open.return_value.__enter__ = Mock(return_value=response)
        client.opener.open.return_value.__exit__ = Mock(return_value=None)
        with self.assertRaises(DataError) as error:
            client.request("https://api.github.com/users/Miko997")
        self.assertNotIn("SECRET", str(error.exception))


if __name__ == "__main__":
    unittest.main()
