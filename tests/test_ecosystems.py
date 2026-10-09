"""Plaques share the showcase's verified contribution gate and remain simple images."""
import copy
import base64
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from profile_data import ECOSYSTEMS, LANDED_COMMITS, SHOWCASE_ORDER, curated_upstream, impact_markdown, summarize
from render_ecosystems import HEIGHT, WIDTH, ecosystem_assets, plaque
from update_profile import prepare_outputs


def snapshot():
    stats = summarize({"2026-10-01": 1, "2026-10-02": 0, "2026-10-03": 2}, date(2026, 10, 3))
    stats["visible_commits_365"] = None
    return {"schema_version": 3, "login": "Miko997", "as_of": "2026-10-03",
            "account_created": "2026-10-01", "source": "github-public-contribution-calendar",
            "stats": stats, "upstream": {"merged": [
        {"repo": repo, "number": number, "title": description,
         "url": f"https://github.com/{repo}/pull/{number}", "state": "merged",
         "draft": False, "merged_at": "2026-10-01T12:00:00Z"}
        for name, repo, number, description in ECOSYSTEMS], "landed_commits": [
        {"repo": repo, "sha": sha, "url": f"https://github.com/{repo}/commit/{sha}",
         "author": "Miko997", "default_branch": "main", "default_branch_verified": True}
        for name, repo, sha, description in LANDED_COMMITS]}}


class EcosystemTests(unittest.TestCase):
    def test_every_image_is_linked_to_its_verified_evidence(self):
        s = snapshot()
        assets = ecosystem_assets(s)
        markup = impact_markdown(s)
        self.assertEqual(len(assets), 6)
        links = re.findall(r'<a href="([^"]+)"><img src="\./([^"]+)"', markup)
        self.assertEqual(len(links), 6)
        self.assertEqual({path for _, path in links}, set(assets))
        self.assertEqual({url for url, _ in links}, {item["url"] for items in s["upstream"].values() for item in items})
        self.assertEqual(tuple(item["name"] for item in curated_upstream(s)), SHOWCASE_ORDER)

    def test_missing_open_and_draft_evidence_cannot_generate_tiles(self):
        for mode in ("empty", "open", "draft", "unverified"):
            s = snapshot()
            s["upstream"]["landed_commits"] = []
            for item in s["upstream"]["merged"]:
                if mode == "open":
                    item["state"] = "open"
                elif mode == "draft":
                    item["draft"] = True
                elif mode == "unverified":
                    item["merged_at"] = None
            if mode == "empty":
                s["upstream"]["merged"] = []
            with self.subTest(mode=mode):
                self.assertEqual(ecosystem_assets(s), {})
                self.assertEqual(impact_markdown(s), "")

    def test_one_missing_evidence_removes_only_its_tile(self):
        s = snapshot()
        s["upstream"]["merged"].pop(0)
        assets = ecosystem_assets(s)
        self.assertEqual(len(assets), 5)
        self.assertNotIn("assets/generated/ecosystem-newton.svg", assets)
        self.assertNotIn("Newton Physics", impact_markdown(s))

    def test_plaques_are_static_self_contained_accessible_svg(self):
        assets = ecosystem_assets(snapshot())
        for path, content in assets.items():
            with self.subTest(path=path):
                root = ET.fromstring(content)
                self.assertEqual((int(root.attrib["width"]), int(root.attrib["height"])), (WIDTH, HEIGHT))
                self.assertTrue(root.find("{http://www.w3.org/2000/svg}title").text)
                self.assertTrue(root.find("{http://www.w3.org/2000/svg}desc").text)
                for banned in ("<script", "<animate", "@keyframes", "foreignObject", "onload="):
                    self.assertNotIn(banned, content)
                # Pixar and RViz use raster source artwork. Their PNGs are
                # vendored inline; no network references may enter an SVG image.
                for node in root.iter():
                    for attr, value in node.attrib.items():
                        if attr.rsplit("}", 1)[-1] == "href":
                            self.assertEqual(node.tag, "{http://www.w3.org/2000/svg}image")
                            self.assertTrue(value.startswith("data:image/png;base64,"))
                            pixels = base64.b64decode(value.split(",", 1)[1], validate=True)
                            self.assertTrue(pixels.startswith(b"\x89PNG\r\n\x1a\n"))
                self.assertLess(len(content.encode()), 128 * 1024)

    def test_display_tiles_allow_two_columns_in_real_mobile_readme(self):
        self.assertLessEqual(2 * 126 + 5, 293)
        self.assertLessEqual(6 * 126 + 5 * 5, 782)
        markup = impact_markdown(snapshot())
        self.assertNotIn("<table", markup)
        self.assertNotIn("&nbsp;", markup)
        self.assertEqual(markup.count('width="126"'), 6)
        self.assertEqual(markup.count('height="58"'), 6)

    def test_duplicate_evidence_does_not_duplicate_images_or_links(self):
        s = snapshot()
        baseline = ecosystem_assets(s), impact_markdown(s)
        s["upstream"]["merged"] += copy.deepcopy(s["upstream"]["merged"])
        s["upstream"]["landed_commits"] += copy.deepcopy(s["upstream"]["landed_commits"])
        self.assertEqual((ecosystem_assets(s), impact_markdown(s)), baseline)

    def test_landed_commits_need_verified_branch_and_authorship(self):
        for field, value in (("default_branch_verified", False), ("author", "someone-else"),
                             ("default_branch", ""), ("url", "https://example.com/")):
            s = snapshot()
            for item in s["upstream"]["landed_commits"]:
                item[field] = value
            with self.subTest(field=field):
                names = {item["name"] for item in curated_upstream(s)}
                self.assertNotIn("MuJoCo", names)
                self.assertNotIn("OpenUSD", names)
                self.assertEqual(len(names), 4)


class EcosystemIntegrationTests(unittest.TestCase):
    readme = ('<!-- IMPACT:START -->old<!-- IMPACT:END -->\n'
              '<img src="./assets/generated/contribution-core.svg" alt="old counts" />')

    def test_refresh_links_resolve_to_generated_plaques_with_cache_hashes(self):
        s = snapshot()
        outputs = prepare_outputs(s, self.readme)
        images = re.findall(r'<img src="\./(assets/generated/ecosystem-[a-z0-9-]+--([0-9a-f]{12})\.svg)"',
                            outputs["README.md"])
        self.assertEqual(len(images), 6)
        self.assertEqual({re.sub(r"--[0-9a-f]{12}", "", name) for name, _ in images}, set(ecosystem_assets(s)))
        for name, _ in images:
            self.assertIn(name, outputs)
            ET.fromstring(outputs[name])
        # Activity and plaques belong to one refreshed presentation snapshot.
        all_hashes = re.findall(r"--([0-9a-f]{12})\.svg", outputs["README.md"])
        self.assertEqual(len(all_hashes), 7)
        self.assertEqual(len(set(all_hashes)), 1)

    def test_plaque_design_change_invalidates_readme_cache(self):
        s = snapshot()
        before = prepare_outputs(s, self.readme)
        with patch("render_ecosystems.plaque", side_effect=lambda item: plaque(item).replace("#9b8054", "#9b8055")):
            after = prepare_outputs(s, before["README.md"])
        self.assertNotEqual(before["assets/generated/ecosystem-newton.svg"],
                            after["assets/generated/ecosystem-newton.svg"])
        self.assertNotEqual(re.findall(r"--([0-9a-f]{12})\.svg", before["README.md"]),
                            re.findall(r"--([0-9a-f]{12})\.svg", after["README.md"]))
        self.assertEqual(before["data/public-activity.json"], after["data/public-activity.json"])

    def test_missing_evidence_removes_previous_link_and_produces_no_tile(self):
        s = snapshot()
        before = prepare_outputs(s, self.readme)
        s["upstream"]["merged"].pop(0)
        after = prepare_outputs(s, before["README.md"])
        self.assertNotIn("assets/generated/ecosystem-newton.svg", after)
        self.assertNotIn("ecosystem-newton", after["README.md"])
        self.assertNotIn("https://github.com/newton-physics/newton/pull/4205", after["README.md"])
        self.assertEqual(len([name for name in after if name.startswith("assets/generated/ecosystem-") and "--" not in name]), 5)


if __name__ == "__main__":
    unittest.main()
