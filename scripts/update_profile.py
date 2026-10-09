#!/usr/bin/env python3
"""Refresh published GitHub activity; artistic assets are built separately."""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from profile_data import Client, DataError, collect, impact_markdown, replace_section
from calendar_visibility import verify_visibility
from render_profile import dashboard
from render_ecosystems import ecosystem_assets

ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = "assets/generated/asset-manifest.json"
ASSET_STEM = r"(?:contribution-core(?:-mobile)?(?:-static)?|ecosystem-[a-z0-9]+(?:-[a-z0-9]+)*)"
ALIAS_NAME = re.compile(ASSET_STEM + r"--[0-9a-f]{12}\.svg")


def write_changed(path: Path, text: str):
    if path.exists() and path.read_text(encoding="utf-8") == text:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        tmp.write(text)
        name = tmp.name
    os.replace(name, path)


def manifest_generations(manifest: dict | None) -> list[dict]:
    if manifest is None:
        return []
    try:
        generations = manifest["generations"]
        if manifest["schema_version"] != 1 or not isinstance(generations, list):
            raise ValueError
        fingerprints = set()
        for generation in generations:
            fingerprint, files = generation["fingerprint"], generation["files"]
            if (not re.fullmatch(r"[0-9a-f]{12}", fingerprint) or fingerprint in fingerprints
                    or not isinstance(files, list) or len(set(files)) != len(files)
                    or any(not ALIAS_NAME.fullmatch(name) or
                           not name.endswith(f"--{fingerprint}.svg") for name in files)):
                raise ValueError
            fingerprints.add(fingerprint)
        return generations
    except (KeyError, TypeError, ValueError):
        raise DataError("Invalid generated asset manifest; previous outputs retained") from None


def prepare_outputs(snapshot: dict, readme: str, previous_manifest: dict | None = None) -> dict[str, str]:
    """Render every output before changing any file; no network or side effects."""
    outputs = {}
    for compact in (False, True):
        for animated in (True, False):
            suffix = ("-mobile" if compact else "") + ("" if animated else "-static")
            outputs[f"assets/generated/contribution-core{suffix}.svg"] = dashboard(
                snapshot, animated=animated, compact=compact)
    outputs.update(ecosystem_assets(snapshot))
    # Immutable filenames work even when GitHub's image CDN discards query strings.
    # Canonical filenames remain available to local tooling and static inspections.
    fingerprint = hashlib.sha256("\n".join(outputs.values()).encode()).hexdigest()[:12]
    aliases = {name[:-4] + f"--{fingerprint}.svg": content for name, content in outputs.items()}
    generations = [{"fingerprint": fingerprint, "files": [Path(name).name for name in aliases]}]
    generations += [g for g in manifest_generations(previous_manifest) if g["fingerprint"] != fingerprint][:2]
    manifest = {"schema_version": 1, "generations": generations}
    outputs.update(aliases)
    readme = replace_section(readme, "IMPACT", impact_markdown(snapshot))
    readme = re.sub(r"(assets/generated/" + ASSET_STEM + r")(?:--[0-9a-f]{12})?\.svg(?:\?v=[0-9a-f]+)?",
                    lambda m: m[1] + f"--{fingerprint}.svg", readme)
    stats = snapshot["stats"]
    alt = (f"{stats['last_365']:,} GitHub contributions from {stats['days'][0][0]} to "
           f"{snapshot['as_of']}; current contribution streak {stats['streak']['current']} days")
    def update_alt(match):
        tag = match[0]
        if not re.search(r'\bsrc="[^"]*assets/generated/contribution-core', tag):
            return tag
        if re.search(r'\balt="[^"]*"', tag):
            return re.sub(r'\balt="[^"]*"', f'alt="{alt}"', tag)
        return tag.replace("<img", f'<img alt="{alt}"', 1)
    readme = re.sub(r"<img\b[^>]*>", update_alt, readme, flags=re.S)
    outputs["data/public-activity.json"] = json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n"
    outputs["README.md"] = readme
    outputs[MANIFEST_PATH] = json.dumps(manifest, indent=2) + "\n"
    return outputs


def prune_expired_aliases(root: Path, previous_manifest: dict | None, manifest: dict):
    """Remove only expired aliases named in our previous validated manifest."""
    retained = {name for g in manifest_generations(manifest) for name in g["files"]}
    previous = {name for g in manifest_generations(previous_manifest) for name in g["files"]}
    for name in sorted(previous - retained):
        (root / "assets/generated" / name).unlink(missing_ok=True)


def validate_refresh(previous: dict | None, snapshot: dict):
    """Do not degrade an enriched calendar because an optional API is unavailable."""
    if not previous or previous.get("source") != "github-verified-aggregate-contribution-calendar":
        return
    if snapshot.get("source") == "github-verified-aggregate-contribution-calendar":
        return
    old_days = dict(previous["stats"]["days"])
    if (snapshot["stats"]["all_time"] < previous["stats"]["all_time"] or
            any(n < old_days.get(day, 0) for day, n in snapshot["stats"]["days"])):
        raise DataError("Aggregate calendar unavailable or reduced; previous snapshot retained")


def refresh(root: Path = ROOT, client=None, today=None):
    today = today or datetime.now(timezone.utc).date()
    client = client if client is not None else Client(os.environ.get("GITHUB_TOKEN", ""))
    snapshot = verify_visibility(collect(client, "Miko997", today), client, today)
    previous_path = root / "data/public-activity.json"
    previous = json.loads(previous_path.read_text()) if previous_path.exists() else None
    validate_refresh(previous, snapshot)
    readme = root.joinpath("README.md").read_text(encoding="utf-8")
    manifest_path = root / MANIFEST_PATH
    previous_manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else None
    outputs = prepare_outputs(snapshot, readme, previous_manifest)
    for name, content in outputs.items():
        write_changed(root / name, content)
    # Cached README HTML can still use the two preceding generations. Never
    # remove their files, nor prune anything after a failed collection or write.
    prune_expired_aliases(root, previous_manifest, json.loads(outputs[MANIFEST_PATH]))
    return snapshot


def main():
    snapshot = refresh()
    stats = snapshot["stats"]
    print(f"Verified {snapshot['login']}: {stats['last_365']} contributions / 365d; "
          f"current streak {stats['streak']['current']} days.")
    print(f"Aggregate calendar: {snapshot['visibility']['aggregate_calendar']}.")
    print("Only published daily aggregates and merged public PR evidence were retained.")


if __name__ == "__main__":
    try:
        main()
    except DataError as exc:
        print(f"Profile refresh failed: {exc}", file=sys.stderr)
        sys.exit(1)
    except (KeyError, TypeError, ValueError):
        # Never echo raw upstream content or a GraphQL error into a public CI log.
        print("Profile refresh failed: unexpected response structure; previous snapshot retained", file=sys.stderr)
        sys.exit(1)
