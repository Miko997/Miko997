"""Verify anonymous GraphQL calendar totals without requesting repository objects."""
from __future__ import annotations

from datetime import date

from profile_data import DataError, count, dates, summarize

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){
  user(login:$login){contributionsCollection(from:$from,to:$to){
    restrictedContributionsCount
    contributionCalendar{
      totalContributions
      weeks{contributionDays{date contributionCount}}
    }
  }}
}"""


def aggregate_calendar(client, login: str, start: date, end: date):
    if not client.token:
        return None
    try:
        result = client.request("https://api.github.com/graphql", {
            "query": QUERY, "variables": {
                "login": login, "from": start.isoformat() + "T00:00:00Z",
                "to": end.isoformat() + "T23:59:59Z"}})
        if result.get("errors"):
            return None
        collection = result["data"]["user"]["contributionsCollection"]
        calendar = collection["contributionCalendar"]
        restricted = count(collection["restrictedContributionsCount"])
        total = count(calendar["totalContributions"])
        days = {}
        for week in calendar["weeks"]:
            for item in week["contributionDays"]:
                day = date.fromisoformat(item["date"])
                if start <= day <= end:
                    if day.isoformat() in days:
                        raise DataError("Duplicate aggregate calendar date")
                    days[day.isoformat()] = count(item["contributionCount"])
        expected = {day.isoformat() for day in dates(start, end)}
        if set(days) != expected or sum(days.values()) != total or restricted > total:
            raise DataError("Incomplete or inconsistent aggregate calendar")
        return days, restricted
    except (DataError, KeyError, TypeError, ValueError):
        return None


def verify_visibility(snapshot: dict, client, today: date) -> dict:
    """Use a complete coherent calendar, never add restricted counts a second time."""
    visibility = {"aggregate_calendar": "unavailable",
                  "anonymous_private_counts_reported": None,
                  "restricted_contributions_all_time": None,
                  "public_calendar_all_time": snapshot["stats"]["all_time"],
                  "aggregate_calendar_all_time": None}
    snapshot["visibility"] = visibility
    if not client.token:
        return snapshot
    all_days = {}
    restricted = 0
    created = date.fromisoformat(snapshot["account_created"])
    for year in range(created.year, today.year + 1):
        result = aggregate_calendar(client, snapshot["login"], date(year, 1, 1),
                                    min(date(year, 12, 31), today))
        if result is None:
            return snapshot
        year_days, year_restricted = result
        all_days.update(year_days)
        restricted += year_restricted
    stats = summarize(all_days, today)
    visibility.update({"aggregate_calendar": "verified",
                       "anonymous_private_counts_reported": restricted > 0,
                       "restricted_contributions_all_time": restricted,
                       "aggregate_calendar_all_time": stats["all_time"]})
    # Whole calendars are selected, not stitched from the maximum of each day.
    # A stale or reduced-scope GraphQL response must not erase public activity.
    public = snapshot["stats"]
    if stats["all_time"] < public["all_time"] or any(
            all_days.get(day, 0) < number for day, number in public["days"]):
        visibility["aggregate_calendar"] = "public-calendar-retained"
        return snapshot
    stats["visible_commits_365"] = public["visible_commits_365"]
    snapshot["stats"] = stats
    snapshot["source"] = "github-verified-aggregate-contribution-calendar"
    return snapshot
