"""Offline regression checks; fixture counts are never published as user data."""
import hashlib
import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch
from urllib.request import Request

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from profile_data import (CalendarParser, Client, DataError, SameHostRedirect, collect,
                          count, curated_upstream, dates, impact_markdown, public_prs, replace_section,
                          streak, summarize, visible_commit_count)
from render_profile import dashboard, footer, header, impact, pending
from update_profile import write_changed


def history(start, values):
    return {(start + timedelta(days=i)).isoformat(): n for i, n in enumerate(values)}


def fixture_snapshot():
    today = date(2026, 1, 3)
    stats = summarize(history(date(2026, 1, 1), [1, 0, 2]), today)
    stats["visible_commits_365"] = 2
    return {"schema_version": 1, "login": "Miko997", "as_of": today.isoformat(), "stats": stats,
            "upstream": {"merged": []}}


def pr(repo="org/project", title="Small fix", number=1):
    return {"html_url": f"https://github.com/{repo}/pull/{number}", "number": number,
            "title": title, "user": {"login": "Miko997"}, "state": "closed", "draft": False,
            "pull_request": {"merged_at": "2026-01-01T12:00:00Z"},
            "body": "SECRET_INTERNAL_BODY", "internal_branch": "SECRET_BRANCH"}


class FakeClient:
    def __init__(self, response, token=""):
        self.response = response
        self.calls = []
        self.token = token

    def request(self, url, payload=None):
        self.calls.append((url, payload))
        return self.response(url, payload) if callable(self.response) else self.response


class CalendarTests(unittest.TestCase):
    def test_tooltips_and_zero(self):
        p = CalendarParser()
        p.feed('<td id="a" data-date="2026-01-01" data-level="1"></td>'
               '<td id="b" data-date="2026-01-02" data-level="0"></td>'
               '<tool-tip for="a"><b>1 contribution</b> on January 1.</tool-tip>'
               '<tool-tip for="b">No contributions on January 2.</tool-tip>')
        self.assertEqual(p.result(date(2026, 1, 1), date(2026, 1, 2)),
                         {"2026-01-01": 1, "2026-01-02": 0})

    def test_rect_data_count_and_aria(self):
        p = CalendarParser()
        p.feed('<rect data-date="2026-01-01" data-count="1,234" />'
               '<td data-date="2026-01-02" aria-label="2 contributions on January 2."></td>')
        self.assertEqual(list(p.result(date(2026, 1, 1), date(2026, 1, 2)).values()), [1234, 2])

    def test_intensity_never_guessed_as_count(self):
        p = CalendarParser()
        p.feed('<td data-date="2026-01-01" data-level="4"></td>')
        with self.assertRaises(DataError):
            p.result(date(2026, 1, 1), date(2026, 1, 1))

    def test_missing_date_fails(self):
        with self.assertRaises(DataError):
            CalendarParser().result(date(2026, 1, 1), date(2026, 1, 1))

    def test_duplicate_date_fails(self):
        with self.assertRaises(DataError):
            CalendarParser().feed('<td data-date="2026-01-01" data-count="2"></td>' * 2)

    def test_invalid_date_fails(self):
        with self.assertRaises(DataError):
            CalendarParser().feed('<td data-date="not-a-date"></td>')

    def test_reject_invalid_counts(self):
        for value in (-1, 2.5, True, "2", None):
            with self.subTest(value=value), self.assertRaises(DataError):
                count(value)


class MetricTests(unittest.TestCase):
    def test_today_and_yesterday_grace(self):
        data = history(date(2026, 1, 1), [1, 2, 3, 0, 0])
        self.assertEqual(streak(data, date(2026, 1, 3))["current"], 3)
        self.assertEqual(streak(data, date(2026, 1, 4))["current"], 3)
        self.assertEqual(streak(data, date(2026, 1, 5))["current"], 0)

    def test_streak_across_year_boundary(self):
        data = history(date(2025, 12, 30), [1, 1, 1, 1])
        s = streak(data, date(2026, 1, 2))
        self.assertEqual((s["current"], s["longest"]), (4, 4))
        self.assertEqual(s["longest_start"], "2025-12-30")

    def test_leap_year_exact_365_days(self):
        data = history(date(2024, 1, 1), [1]*366)
        s = summarize(data, date(2024, 12, 31))
        self.assertEqual((s["all_time"], s["last_365"], len(s["days"])), (366, 365, 365))
        self.assertIn(["2024-02-29", 1], s["days"])
        self.assertEqual(s["streak"]["longest"], 366)

    def test_future_dates_not_counted(self):
        data = history(date(2026, 1, 1), [1, 2, 9])
        self.assertEqual(summarize(data, date(2026, 1, 2))["all_time"], 3)

    def test_gap_not_silently_zero(self):
        with self.assertRaises(DataError):
            summarize({"2026-01-01": 1, "2026-01-03": 2}, date(2026, 1, 3))

    def test_empty_calendar_fails(self):
        with self.assertRaises(DataError):
            summarize({}, date(2026, 1, 3))

    def test_zero_activity_is_valid(self):
        s = summarize(history(date(2026, 1, 1), [0, 0]), date(2026, 1, 2))
        self.assertEqual(s["all_time"], 0)
        self.assertEqual(s["streak"]["current"], 0)
        self.assertIsNone(s["first_contribution"])

    def test_future_only_history_is_unavailable(self):
        with self.assertRaises(DataError):
            summarize({"2027-01-01": 1}, date(2026, 1, 1))

    def test_unordered_dates_and_delayed_reporting(self):
        raw = {"2026-01-03": 0, "2026-01-01": 2, "2026-01-02": 0}
        before = summarize(raw, date(2026, 1, 3))
        raw["2026-01-02"] = 5  # GitHub reports yesterday's count later.
        after = summarize(raw, date(2026, 1, 3))
        self.assertEqual(before["streak"]["current"], 0)
        self.assertEqual(after["streak"]["current"], 2)
        self.assertEqual(after["last_365"], 7)
        self.assertEqual(after["days"], sorted(after["days"]))


class PrivacyTests(unittest.TestCase):
    def test_only_public_prs_and_allowlisted_fields(self):
        client = FakeClient({"total_count": 1, "incomplete_results": False, "items": [pr()]})
        out = public_prs(client, "Miko997", "merged")
        self.assertIn("is%3Apublic", client.calls[0][0])
        self.assertNotIn("SECRET", json.dumps(out))
        self.assertEqual(set(out[0]), {"repo", "number", "title", "url", "state", "draft", "merged_at"})

    def test_missing_merge_evidence_and_drafts_rejected(self):
        for mode in ("open", "draft", "no-date", "bad-date", "number"):
            item = pr()
            if mode == "open":
                item["state"] = "open"
            elif mode == "draft":
                item["draft"] = True
            elif mode == "number":
                item["number"] = 50
            else:
                item["pull_request"]["merged_at"] = None if mode == "no-date" else "invalid"
            with self.subTest(mode=mode), self.assertRaises(DataError):
                public_prs(FakeClient({"total_count": 1, "items": [item]}), "Miko997")

    def test_open_search_is_not_supported(self):
        with self.assertRaises(DataError):
            public_prs(FakeClient({}), "Miko997", "open")

    def test_incomplete_search_does_not_publish(self):
        for total, incomplete in ((1001, False), (1, True)):
            with self.subTest(total=total), self.assertRaises(DataError):
                public_prs(FakeClient({"total_count": total, "incomplete_results": incomplete}), "Miko997", "merged")

    def test_own_repository_not_upstream(self):
        with self.assertRaises(DataError):
            public_prs(FakeClient({"total_count": 1, "items": [pr("Miko997/project")]}), "Miko997", "merged")

    def test_author_must_match(self):
        item = pr()
        item["user"]["login"] = "someone-else"
        with self.assertRaises(DataError):
            public_prs(FakeClient({"total_count": 1, "items": [item]}), "Miko997", "merged")

    def test_commit_query_requests_only_aggregate(self):
        client = FakeClient({"data": {"user": {"contributionsCollection": {"totalCommitContributions": 7}}}}, token="TEST_ONLY")
        self.assertEqual(visible_commit_count(client, "Miko997", date(2026, 1, 3)), 7)
        query = client.calls[0][1]["query"]
        self.assertIn("totalCommitContributions", query)
        self.assertNotIn("repositories", query)
        self.assertNotIn("ByRepository", query)

    def test_optional_query_failure_is_not_zero(self):
        self.assertIsNone(visible_commit_count(FakeClient({"errors": [{"message": "not accessible"}]}, token="TEST_ONLY"), "Miko997", date(2026, 1, 3)))

    def test_https_and_host_allowlist(self):
        for url in ("https://example.com/", "http://api.github.com/users/x", "https://api.github.com.evil.test/"):
            with self.subTest(url=url), self.assertRaises(DataError):
                Client("TEST_ONLY").request(url)

    def test_no_cross_host_or_downgrade_redirect(self):
        handler = SameHostRedirect()
        for url in ("https://other.test/path", "http://api.github.com/path"):
            with self.subTest(url=url), self.assertRaises(DataError):
                handler.redirect_request(Request("https://api.github.com/path"), None, 302, "", {}, url)

    def test_full_pipeline_uses_real_response_counts(self):
        def respond(url, payload):
            if "/users/Miko997" in url and "api.github.com" in url:
                return {"created_at": "2026-01-01T00:00:00Z"}
            if "/contributions?" in url:
                return ''.join(f'<td data-date="2026-01-0{i}" data-count="{n}"></td>' for i, n in enumerate([1, 0, 2], 1))
            if "/search/issues?" in url:
                return {"total_count": 0, "incomplete_results": False, "items": []}
            raise AssertionError("Unexpected API request")
        out = collect(FakeClient(respond), "Miko997", date(2026, 1, 3))
        self.assertEqual(out["stats"]["all_time"], 3)
        self.assertEqual(out["stats"]["streak"]["current"], 1)
        self.assertNotIn("private_repositories", json.dumps(out))
        self.assertNotIn("open", out["upstream"])


class RenderingTests(unittest.TestCase):
    def test_svg_is_safe_and_well_formed(self):
        s = fixture_snapshot()
        for content in (header(), dashboard(s), dashboard(s, False), impact(s), footer(), pending()):
            root = ET.fromstring(content)
            self.assertTrue(root.tag.endswith("svg"))
            for banned in ("<script", "foreignObject", "onload=", "<image", "https://"):
                self.assertNotIn(banned, content)
            self.assertIn("<title", content)
            self.assertIn("<desc", content)

    def test_static_has_no_keyframes(self):
        self.assertNotIn("@keyframes", dashboard(fixture_snapshot(), False))
        self.assertIn("prefers-reduced-motion", dashboard(fixture_snapshot()))

    def test_flame_morph_has_independent_static_preference_fallback(self):
        snapshot = fixture_snapshot()
        moving = ET.fromstring(dashboard(snapshot))
        ns = {"s": "http://www.w3.org/2000/svg"}
        animations = moving.findall(".//s:animate", ns)
        self.assertEqual(len(animations), 16)
        self.assertTrue(all(node.get("attributeName") == "d" for node in animations))
        self.assertTrue(all(node.get("values").split(";")[0] == node.get("values").split(";")[-1]
                            for node in animations))
        still = ET.fromstring(dashboard(snapshot, False))
        self.assertEqual(still.findall(".//s:animate", ns), [])
        for suffix in ("motion", "still"):
            self.assertIsNotNone(moving.find(f".//s:g[@class='plasma-{suffix}']", ns))
        snapshot["stats"]["streak"]["current"] = 0
        self.assertNotIn("<animate", dashboard(snapshot))

    def test_365_calendar_titles(self):
        content = dashboard(fixture_snapshot())
        self.assertEqual(content.count(" contribution</title>") + content.count(" contributions</title>"), 365)
        self.assertIn("3 contributions in 365 days", content)

    def test_impact_excludes_open_drafts_and_unverified_ecosystems(self):
        s = fixture_snapshot()
        item = {"repo": "newton-physics/newton", "number": 4189, "title": "Fix",
                "url": "https://github.com/newton-physics/newton/pull/4189", "state": "open",
                "draft": False, "merged_at": "2026-01-01T12:00:00Z"}
        for state, draft, merged_at in (("open", False, item["merged_at"]), ("merged", True, item["merged_at"]), ("merged", False, None)):
            s["upstream"]["merged"] = [dict(item, state=state, draft=draft, merged_at=merged_at)]
            self.assertEqual(curated_upstream(s), [])
            self.assertEqual(impact_markdown(s), "")
        s["upstream"]["merged"] = [dict(item, state="merged")] * 2
        content = impact_markdown(s)
        self.assertEqual(content.count("Newton Physics"), 1)
        self.assertIn(item["url"], content)
        self.assertNotIn("merged", content)
        self.assertNotIn("Open", content)

    def test_marker_replacement_preserves_other_content(self):
        text = "PREFIX\n<!-- IMPACT:START -->old<!-- IMPACT:END -->\nSUFFIX"
        new = replace_section(text, "IMPACT", "new")
        self.assertTrue(new.startswith("PREFIX"))
        self.assertTrue(new.endswith("SUFFIX"))
        with self.assertRaises(DataError):
            replace_section("missing markers", "IMPACT", "new")
        with self.assertRaises(DataError):
            replace_section(text+text, "IMPACT", "new")

    def test_unchanged_output_not_rewritten(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/"x.txt"
            write_changed(path, "same")
            before = path.stat().st_mtime_ns
            write_changed(path, "same")
            self.assertEqual(path.stat().st_mtime_ns, before)

    def test_original_hero_references_and_bytes(self):
        readme = (ROOT/"README.md").read_text()
        self.assertIn('src="https://raw.githubusercontent.com/Miko997/metriplane/main/docs/assets/metriplane-hero.jpg"', readme)
        self.assertIn('src="./assets/cursed-dawn-hero.jpg"', readme)
        path = ROOT/"assets/cursed-dawn-hero.jpg"
        self.assertTrue(path.exists(), "Protected Cursed Dawn artwork must remain present")
        raw = path.read_bytes()
        blob = hashlib.sha1(f"blob {len(raw)}\0".encode()+raw).hexdigest()
        self.assertEqual(blob, "8afda374869b2080925c8e70e05734c39bc28daf")
        self.assertNotIn("## Capability map", readme)
        self.assertNotIn("capability-panel.png", readme)

    def test_checked_in_generated_data_is_consistent(self):
        path = ROOT/"data/public-activity.json"
        if path.exists():
            s = json.loads(path.read_text())
            self.assertEqual(s["login"], "Miko997")
            self.assertEqual(len(s["stats"]["days"]), 365)
            self.assertEqual(sum(n for _, n in s["stats"]["days"]), s["stats"]["last_365"])
            for item in (ROOT/"assets/generated").glob("*.svg"):
                tree = ET.fromstring(item.read_text())
                if item.name.startswith("contribution-core"):
                    cells = [node for node in tree.iter() if "data-date" in node.attrib]
                    self.assertEqual(len(cells), 365, item.name)
                    self.assertEqual({node.attrib["data-date"]: int(node.attrib["data-count"])
                                      for node in cells}, dict(s["stats"]["days"]), item.name)


if __name__ == "__main__":
    unittest.main()
