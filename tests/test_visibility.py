"""Anonymous private aggregates must be validated, never guessed or double-counted."""
import copy
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from calendar_visibility import QUERY, aggregate_calendar, verify_visibility
from profile_data import summarize


class Client:
    token = "TEST_ONLY"

    def __init__(self, numbers=(1, 2, 3), restricted=0):
        days = [{"date": f"2026-01-0{i}", "contributionCount": n}
                for i, n in enumerate(numbers, 1)]
        self.collection = {"restrictedContributionsCount": restricted,
                           "contributionCalendar": {"totalContributions": sum(numbers),
                                                    "weeks": [{"contributionDays": days}]}}

    def request(self, url, payload):
        assert url == "https://api.github.com/graphql"
        assert payload["variables"]["login"] == "Miko997"
        return {"data": {"user": {"contributionsCollection": self.collection}}}


def snapshot():
    stats = summarize({"2026-01-01": 1, "2026-01-02": 0, "2026-01-03": 2}, date(2026, 1, 3))
    stats["visible_commits_365"] = 2
    return {"login": "Miko997", "account_created": "2026-01-01",
            "source": "github-public-contribution-calendar", "stats": stats}


class VisibilityTests(unittest.TestCase):
    def test_complete_calendar_used_without_double_counting(self):
        result = verify_visibility(snapshot(), Client(restricted=3), date(2026, 1, 3))
        self.assertEqual(result["stats"]["all_time"], 6)  # Not 6 + 3.
        self.assertEqual(result["stats"]["streak"]["current"], 3)
        self.assertEqual(result["stats"]["visible_commits_365"], 2)
        self.assertTrue(result["visibility"]["anonymous_private_counts_reported"])

    def test_lower_scope_does_not_erase_public_counts(self):
        result = verify_visibility(snapshot(), Client((1, 0, 0)), date(2026, 1, 3))
        self.assertEqual(result["stats"]["all_time"], 3)
        self.assertEqual(result["visibility"]["aggregate_calendar"], "public-calendar-retained")

    def test_calendar_not_stitched_from_daily_maxima(self):
        result = verify_visibility(snapshot(), Client((0, 10, 2)), date(2026, 1, 3))
        self.assertEqual(result["stats"]["all_time"], 3)
        self.assertEqual(result["stats"]["active_days_365"], 2)

    def test_unknown_visibility_not_labelled_zero(self):
        client = Client()
        client.token = ""
        result = verify_visibility(snapshot(), client, date(2026, 1, 3))
        self.assertIsNone(result["visibility"]["restricted_contributions_all_time"])
        self.assertEqual(result["visibility"]["aggregate_calendar"], "unavailable")

    def test_missing_duplicate_inconsistent_and_invalid_fail_closed(self):
        for mode in ("missing", "duplicate", "sum", "negative", "restricted"):
            client = Client()
            calendar = client.collection["contributionCalendar"]
            days = calendar["weeks"][0]["contributionDays"]
            if mode == "missing":
                days.pop()
            elif mode == "duplicate":
                days.append(copy.deepcopy(days[0]))
            elif mode == "sum":
                calendar["totalContributions"] += 1
            elif mode == "negative":
                days[0]["contributionCount"] = -1
            else:
                client.collection["restrictedContributionsCount"] = 100
            with self.subTest(mode=mode):
                self.assertIsNone(aggregate_calendar(client, "Miko997", date(2026, 1, 1), date(2026, 1, 3)))

    def test_query_contains_no_repository_or_commit_objects(self):
        self.assertIn("restrictedContributionsCount", QUERY)
        self.assertIn("contributionCount", QUERY)
        for prohibited in ("repository", "repositories", "commitContributionsByRepository", "nodes", "edges", "email", "name"):
            self.assertNotIn(prohibited, QUERY)


if __name__ == "__main__":
    unittest.main()
