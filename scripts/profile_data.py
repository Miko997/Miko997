"""Fetch published contribution counts and explicitly public upstream PRs only."""
from __future__ import annotations

import json
import re
import time
from datetime import date, datetime, timedelta
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener


class DataError(RuntimeError):
    """Incomplete or unexpected input; never replace a good snapshot with zeroes."""


def dates(start: date, end: date):
    for offset in range((end - start).days + 1):
        yield start + timedelta(days=offset)


def count(value) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise DataError("Invalid nonnegative count")
    return value


class CalendarParser(HTMLParser):
    """Handle GitHub's td/rect calendars and separate tool-tip elements."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.cells = {}
        self.tooltips = {}
        self.target = None
        self.text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {"td", "rect"} and attrs.get("data-date"):
            day = attrs["data-date"]
            try:
                date.fromisoformat(day)
            except ValueError as exc:
                raise DataError("Invalid calendar date") from exc
            if day in self.cells:
                raise DataError("Duplicate contribution calendar date")
            raw = attrs.get("data-count")
            self.cells[day] = (attrs.get("id"), raw, attrs.get("aria-label", ""))
        if tag == "tool-tip" and attrs.get("for"):
            self.target = attrs["for"]
            self.text = []

    def handle_data(self, data):
        if self.target is not None:
            self.text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.target is not None:
            self.tooltips[self.target] = " ".join(self.text)
            self.target = None

    def result(self, start: date, end: date) -> dict[str, int]:
        out = {}
        for day in dates(start, end):
            key = day.isoformat()
            if key not in self.cells:
                raise DataError("Contribution calendar is missing dates")
            ident, raw, label = self.cells[key]
            if raw is not None:
                if not re.fullmatch(r"\d[\d,]*", raw):
                    raise DataError("Invalid calendar count")
                value = int(raw.replace(",", ""))
            else:
                text = self.tooltips.get(ident, label)
                match = re.search(r"\b(No|[\d,]+) contributions?\b", text, re.I)
                if not match:
                    raise DataError("Contribution count missing; intensity is not a count")
                value = 0 if match[1].lower() == "no" else int(match[1].replace(",", ""))
            out[key] = count(value)
        return out


class SameHostRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if urlsplit(newurl).scheme != "https" or urlsplit(req.full_url).netloc != urlsplit(newurl).netloc:
            raise DataError("Cross-host redirects are not permitted")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


class Client:
    def __init__(self, token: str = ""):
        self.token = token
        self.opener = build_opener(SameHostRedirect())

    def request(self, url: str, payload: dict | None = None):
        parsed = urlsplit(url)
        if parsed.scheme != "https" or parsed.netloc not in {"github.com", "api.github.com"}:
            raise DataError("Unexpected data host")
        headers = {"User-Agent": "Miko997-Hextech-Profile", "Accept-Language": "en-US"}
        api = parsed.netloc == "api.github.com"
        headers["Accept"] = "application/vnd.github+json" if api else "text/html"
        if api and self.token:
            headers["Authorization"] = "Bearer " + self.token
        if payload is not None:
            headers["Content-Type"] = "application/json"
        req = Request(url, data=json.dumps(payload).encode() if payload else None, headers=headers)
        for attempt in range(3):
            try:
                with self.opener.open(req, timeout=40) as response:
                    raw = response.read(10_000_001)
                if len(raw) > 10_000_000:
                    raise DataError("Data response exceeds size limit")
                try:
                    text = raw.decode("utf-8")
                    result = json.loads(text) if api else text
                except (UnicodeError, json.JSONDecodeError):
                    raise DataError("Invalid GitHub response; previous snapshot retained") from None
                if api and not isinstance(result, dict):
                    raise DataError("Unexpected GitHub response structure; previous snapshot retained")
                return result
            except HTTPError as exc:
                if attempt == 2 or exc.code not in {403, 429, 500, 502, 503, 504}:
                    raise DataError(f"GitHub returned HTTP {exc.code}; previous snapshot retained") from None
            except (URLError, TimeoutError, OSError) as exc:
                if attempt == 2:
                    raise DataError("GitHub request failed; previous snapshot retained") from None
            time.sleep(2 ** attempt)
        raise DataError("GitHub request failed")


def fetch_calendar(client: Client, login: str, today: date) -> tuple[dict[str, int], str]:
    """Never authenticate the public calendar or request private repository records."""
    metadata = client.request(f"https://api.github.com/users/{login}")
    created = date.fromisoformat(metadata["created_at"][:10])
    if not 2007 <= created.year or created > today:
        raise DataError("Invalid account creation year")
    days = {}
    for year in range(created.year, today.year + 1):
        start = date(year, 1, 1)
        end = min(date(year, 12, 31), today)
        query = urlencode({"from": start.isoformat(), "to": end.isoformat()})
        html = client.request(f"https://github.com/users/{login}/contributions?{query}")
        parser = CalendarParser()
        parser.feed(html)
        days.update(parser.result(start, end))
    return days, created.isoformat()


def visible_commit_count(client: Client, login: str, today: date) -> int | None:
    """An optional, separately labelled aggregate. Never a guessed private split."""
    if not client.token:
        return None
    start = (today - timedelta(days=364)).isoformat() + "T00:00:00Z"
    end = today.isoformat() + "T23:59:59Z"
    query = """query($login:String!,$from:DateTime!,$to:DateTime!){
      user(login:$login){contributionsCollection(from:$from,to:$to){
        totalCommitContributions
      }}
    }"""
    try:
        result = client.request("https://api.github.com/graphql", {
            "query": query, "variables": {"login": login, "from": start, "to": end}})
        if result.get("errors"):
            return None
        return count(result["data"]["user"]["contributionsCollection"]["totalCommitContributions"])
    except (DataError, KeyError, TypeError):
        return None


def public_prs(client: Client, login: str, state: str = "merged") -> list[dict]:
    if state != "merged":
        raise DataError("Only merged upstream evidence is collected")
    query = f"is:pr is:public author:{login} -user:{login} is:merged draft:false"
    out = {}
    page = 1
    while True:
        params = urlencode({"q": query, "per_page": 100, "page": page, "sort": "updated", "order": "desc"})
        response = client.request("https://api.github.com/search/issues?" + params)
        total = count(response["total_count"])
        if response.get("incomplete_results") or total > 1000:
            raise DataError("Incomplete public PR search; refusing truncated impact counts")
        items = response["items"]
        for item in items:
            url = item.get("html_url", "")
            match = re.fullmatch(r"https://github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)", url)
            if not match or "pull_request" not in item:
                raise DataError("Unexpected public PR result")
            if item.get("user", {}).get("login", "").lower() != login.lower():
                raise DataError("PR author does not match the configured account")
            repo = match[1]
            if repo.split("/")[0].lower() == login.lower():
                raise DataError("Own repository included in upstream search")
            merged_at = item["pull_request"].get("merged_at")
            try:
                merged_date = datetime.fromisoformat(merged_at.replace("Z", "+00:00"))
            except (AttributeError, TypeError, ValueError):
                raise DataError("Merged PR evidence lacks a valid merge date") from None
            if item.get("state") != "closed" or item.get("draft") is not False or merged_date.tzinfo is None:
                raise DataError("Unmerged or draft PR returned in merged evidence")
            if item.get("number") != int(match[2]):
                raise DataError("PR number does not match its public URL")
            # Explicit allowlist: bodies, branches, patches, and internal fields are discarded.
            out[url] = {"repo": repo, "number": int(match[2]), "title": str(item["title"]),
                        "url": url, "state": "merged", "draft": False, "merged_at": merged_at}
        if page * 100 >= total:
            if len(out) != total:
                raise DataError("Public PR search changed during pagination; retry next run")
            break
        if not items:
            raise DataError("Unexpected empty PR page")
        page += 1
    return sorted(out.values(), key=lambda x: (x["repo"].lower(), x["number"]), reverse=True)


def streak(days: dict[str, int], today: date) -> dict:
    active = [date.fromisoformat(d) for d, n in sorted(days.items()) if n and date.fromisoformat(d) <= today]
    best = run = 0
    previous = None
    best_start = best_end = start = None
    for day in active:
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        if run == 1:
            start = day
        if run > best:
            best, best_start, best_end = run, start, day
        previous = day
    end = today if days.get(today.isoformat(), 0) else today - timedelta(days=1)
    cursor = end
    current = 0
    while days.get(cursor.isoformat(), 0):
        current += 1
        cursor -= timedelta(days=1)
    return {"current": current, "current_start": (cursor + timedelta(days=1)).isoformat() if current else None,
            "current_end": end.isoformat() if current else None, "longest": best,
            "longest_start": best_start.isoformat() if best_start else None,
            "longest_end": best_end.isoformat() if best_end else None}


def summarize(days: dict[str, int], today: date) -> dict:
    if not days:
        raise DataError("No calendar data")
    cleaned = {d: count(n) for d, n in days.items() if date.fromisoformat(d) <= today}
    if not cleaned:
        raise DataError("No calendar data at or before the measurement date")
    first = date.fromisoformat(min(cleaned))
    # Detect gaps rather than silently interpreting unavailable days as inactivity.
    if any(d.isoformat() not in cleaned for d in dates(first, today)):
        raise DataError("Calendar history contains a gap")
    window = []
    for d in dates(today - timedelta(days=364), today):
        n = 0 if d < first else cleaned[d.isoformat()]
        window.append([d.isoformat(), n])
    return {"all_time": sum(cleaned.values()), "last_365": sum(n for _, n in window),
            "active_days_365": sum(n > 0 for _, n in window), "days": window,
            "first_contribution": next((d for d, n in sorted(cleaned.items()) if n), None),
            "streak": streak(cleaned, today)}


def collect(client: Client, login: str, today: date) -> dict:
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}", login):
        raise DataError("Invalid GitHub login")
    days, created = fetch_calendar(client, login, today)
    stats = summarize(days, today)
    stats["visible_commits_365"] = visible_commit_count(client, login, today)
    merged = public_prs(client, login, "merged")
    return {"schema_version": 2, "login": login, "as_of": today.isoformat(),
            "account_created": created, "source": "github-public-contribution-calendar",
            "privacy": "Published daily aggregates only. No private repository details requested.",
            "stats": stats, "upstream": {"merged": merged}}


def markdown_text(value: str) -> str:
    value = " ".join(value.split())
    return re.sub(r"([\\`*_{}\[\]<>()|])", r"\\\1", value)


# Selected engineering examples. A configured ecosystem appears only while its
# linked contribution is present in the current, verified merged-public search.
ECOSYSTEMS = (
    ("Newton Physics", "newton-physics/newton", 4189, "MJCF orientation during import"),
    ("ROS 2", "ros2/rclcpp", 3294, "Wait-set ownership on failed removal"),
    ("Microsoft TypeSpec", "microsoft/typespec", 12042, "Valid deprecated OpenAPI parameter directives"),
    ("conda-forge", "conda-forge/staged-recipes", 34480, "Metriplane package recipe"),
    ("trimesh", "mikedh/trimesh", 2599, "Exact closure of discretized circles"),
)


def curated_upstream(snapshot: dict) -> list[dict]:
    evidence = {}
    for item in snapshot["upstream"]["merged"]:
        # Defense in depth for manually supplied snapshots and offline previews.
        expected_url = f"https://github.com/{item['repo']}/pull/{item['number']}"
        if (item.get("state") == "merged" and item.get("draft") is False
                and item.get("merged_at") and item.get("url") == expected_url):
            evidence[(item["repo"].lower(), item["number"])] = item
    selected = []
    for name, repo, number, description in ECOSYSTEMS:
        item = evidence.get((repo.lower(), number))
        if item:
            selected.append({"name": name, "repo": repo, "description": description,
                             "url": item["url"]})
    return selected


def impact_markdown(snapshot: dict) -> str:
    selected = curated_upstream(snapshot)
    if not selected:
        return ""  # Missing evidence never becomes a fabricated affiliation.
    return " · ".join(f"**[{markdown_text(item['name'])}]({item['url']})**" for item in selected)


def replace_section(text: str, name: str, replacement: str) -> str:
    start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
    if text.count(start) != 1 or text.count(end) != 1 or text.index(start) > text.index(end):
        raise DataError(f"Missing or duplicate {name} markers")
    before, rest = text.split(start, 1)
    _, after = rest.split(end, 1)
    return before + start + "\n" + replacement + "\n" + end + after
