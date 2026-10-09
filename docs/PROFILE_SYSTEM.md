# Profile system

The signature header is an original rendered 3D animation with a matching still. The activity images are
self-contained SVGs generated from GitHub's published daily counts. Art rendering
and activity refresh are separate: a new contribution never requires rendering
or modifying the header, Metriplane image, or Cursed Dawn image.

## Data and definitions

`data/public-activity.json` is the dated public snapshot. Schema 3 contains daily
aggregate counts, calculated statistics, source/visibility evidence, authored
merged public PRs, and separately verified authored commits accepted upstream.
It contains no open or draft PR records. Accepted commits are never counted as
additional authored merged PRs or added to GitHub's daily contribution totals.

| Value | Definition |
| --- | --- |
| Contributions | Sum of exactly 365 GitHub calendar dates, including the measurement date. This can differ from GitHub's native “last year” range. |
| Current streak | Consecutive active dates ending today, or yesterday while today has no recorded activity. It becomes zero when both today and yesterday are inactive. |
| Longest streak | Longest consecutive run across the entire fetched history, including year boundaries. Retained in data, omitted from the visual. |
| All-time contributions | Sum from the account's creation year through the measurement date. Retained in data, omitted from the visual. |
| Visible commit contributions | Optional `totalCommitContributions` aggregate available to the existing workflow token. Unavailable is `null`, never an inferred zero. Not displayed. |

Contributions include qualifying activity beyond commits. Dates are those reported
by GitHub, with the measurement date taken in UTC. They are not rebucketed into the
visitor's timezone. The collector refetches complete calendar history, so delayed
activity and corrections can update both totals and streaks. Missing or duplicate
dates, invalid counts and incomplete searches fail the refresh instead of creating
fictional zeroes. Future dates are excluded; leap dates follow the real calendar.

The optional activity-type chart is intentionally omitted. The public anonymous
private calendar does not provide a reliable complete private-type breakdown;
public category aggregates cannot honestly become percentages of all activity.

## Privacy and source selection

The public profile calendar is fetched **without authentication**. GitHub publishes
anonymous private activity there only according to the account's visibility
settings. To enable it: **Your profile → Contribution settings → Private
contributions**. This repository does not change that setting.

The workflow uses its existing built-in `GITHUB_TOKEN`, scoped to this public
profile repository. No additional credential or private-repository scope is needed.
The optional GraphQL verification requests only aggregate integers and daily
calendar counts, never repositories, commits, messages, branches or issue records.
It checks that every date is present exactly once and that daily counts sum to the
reported total. A complete aggregate calendar may replace the public calendar;
the two calendars are never stitched together using daily maxima.

`restrictedContributionsCount` is visibility evidence, **never an addition** to
the contribution total. Unknown visibility remains `null`. Zero restricted counts
do not prove the account has no private work. A lower aggregate result does not
erase the public calendar. If aggregate verification becomes unavailable or returns
a reduced calendar and previously verified counts would be lost, the refresh
retains the previous output.
No manual correction is added for hidden work.

Public PR searches include `is:public is:merged draft:false`, the configured author,
and exclusion of their own repositories. Results must be closed, non-draft and
have a valid `merged_at` timestamp. The collector retains only repository, number,
public title and URL, state, draft flag and merge date. Bodies, patches and branches
are discarded. Open work is neither requested nor showcased.

Some projects integrate patches without marking their original PR as merged.
The explicit `LANDED_COMMITS` selection verifies those accepted contributions
separately: the repository must be public, the exact upstream commit must identify
Miko997 as its author, and a comparison must prove it is an ancestor of the current
public default branch. Only repository, SHA, public URL, author and branch-verification
fields are retained; source code, commit messages and comparison patches are discarded.
Every refresh repeats this verification. An API failure or failed proof retains
the previous presentation instead of publishing an unverified contribution.

The `ECOSYSTEMS` and `LANDED_COMMITS` configuration in `scripts/profile_data.py`
selects six relevant projects. Each plaque links directly to a verified merged PR
or accepted authored commit. OpenUSD's source PR remains correctly described as
closed without merge; its bot-integrated upstream commit supplies the evidence.
MuJoCo's accepted authored test commit arrived through another person's merged PR.
The complete public audit and selection reasons are in `docs/upstream-audit.json`.
These links do not
imply employment, project membership or maintainer status. Ownership
or maintainership of the user's own project must be described separately.

`scripts/render_ecosystems.py` turns that same verified selection into compact
static plaques under `assets/generated/ecosystem-*.svg`. Their geometric motifs
are original editorial artwork, not official project logos. Every plaque links
to its selected upstream evidence. Missing, open, draft or unverified evidence produces
neither a plaque output nor a README link. Their native canvas is 148 × 68;
the README displays them at 126 × 58 so all six fit inside a 782-pixel
desktop content area, while two fit inside GitHub's actual 293-pixel
mobile content area at a 375-pixel viewport.

## Refresh and failure behavior

`.github/workflows/profile.yml` runs at minutes 17 and 47 each hour (UTC), on
relevant changes in this repository, through **Run workflow**, and optionally
through `repository_dispatch` with event type `profile-refresh`. Schedules can be
delayed by GitHub. A push in another repository does not automatically trigger a
refresh here; it appears after GitHub counts it and a refresh succeeds. Qualifying
contributions can take up to 24 hours to appear.

No dispatcher is installed elsewhere. An authorized external caller would need
permission to dispatch to this profile repository; do not include private names,
branches, messages or identifiers in the payload. The ordinary token of another
repository cannot write here. Public repositories can have inactive schedules
disabled; inspect the Actions page and re-enable or manually run as needed.

All collection, validation and rendering finish before files are replaced. API,
parse, validation or rendering failure preserves the previous outputs. Each file
is replaced atomically. Identical contents are not rewritten, and the workflow
makes no commit when the generated files are unchanged. GitHub branch protection
can block publication; the workflow fails rather than bypassing it.

The image fingerprint hashes all four rendered activity variants and the verified
ecosystem plaques. README images use filenames containing that fingerprint.
GitHub's branch-image redirect can drop query parameters, and its raw CDN can
return a cached image despite a new query string; changing the actual filename
avoids that stale-image collision. Canonical filenames remain available for tools.
The generated asset manifest retains three generations of fingerprinted files
so recently cached README pages can still load their images. Older owned aliases
are removed only after a successful refresh.

Plaques and their evidence links are regenerated on the same refresh. Alternative
activity text uses the same total, date range and streak as the image. The workflow
writes README, the JSON snapshot, generated activity/ecosystem SVGs and their
manifest; header and project artwork are outside its output list. All rendering
finishes before any refresh output is written, so a rendering error preserves the
previous presentation.

## Rendering and accessibility

- `assets/signature-header-animated.webp` and `assets/signature-header-mobile-animated.webp`: a synchronized robot press and name-lighting loop.
- `assets/signature-header.webp` and `assets/signature-header-mobile.webp`: matching
  still artwork; selected first for reduced motion. Editable procedural source
  and rendering instructions are under `scripts/art/` and `docs/HEADER_ARTWORK.md`.
- `assets/generated/contribution-core.svg`: desktop animation.
- `assets/generated/contribution-core-mobile.svg`: mobile layout with two calendar
  panels, keeping all 365 dates and their chronological positions.
- The matching `-static.svg` files: identical counts and date cells without motion.

The near-black, blue and violet system uses a restrained sans-serif hierarchy.
The SVGs use local font fallbacks; no network fonts, JavaScript, external images,
`foreignObject` or third-party stats service is required. Each has a title,
description and a date/count tooltip for every cell. Reduced-motion preferences
select the static image in the README. In the animated SVG, a media query
hides the SMIL flame group, shows separate still contours, and disables the
calendar and particle CSS animation. A static link also allows direct viewing.

Cell fill intensity is derived from each actual count. Animation accents only
active dates; it never changes cell counts or makes a zero date active. A restrained instrument frame explicitly groups the plasma and current-streak
number. The plasma flame and its text remain separate. At zero streak the live flame is extinguished.
The number remains ordinary generated text for any valid streak length.
A thin animated plasma seam separates metrics from the calendar; it is purely
decorative, stays outside the dated cells, and has its own static contours.
The header animation is pre-rendered into WebP, with the physical press and
name effect in one file so they remain synchronized. Reduced-motion picture
sources choose the still header; embedded WebP motion does not rely on CSS.
The README cannot set GitHub's prose font; the artwork controls its own typography.

GitHub renders README images in an image context. The flame uses declarative
SVG SMIL path morphing; it does not depend on the CSS `d` property, which Safari
does not support. Complete base contours remain when animation is unsupported. The profile uses no script-dependent behavior. Local previews do not
prove identical GitHub proxy behavior: validate the actual branch-rendered README
after approval to push. GitHub's native calendar below the README cannot be hidden
or restyled by this repository.

## Protected artwork

Metriplane retains this exact reference:

`https://raw.githubusercontent.com/Miko997/metriplane/main/docs/assets/metriplane-hero.jpg`

Cursed Dawn retains `assets/cursed-dawn-hero.jpg`. Its original Git blob hash is
`8afda374869b2080925c8e70e05734c39bc28daf`; the test checks those exact bytes.
The refresh script does not process either image.

## Maintenance

Runtime activity refresh requires only Python 3.10+ and its standard library:

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_profile.py
```

Unauthenticated local refresh is supported within GitHub's public API rate limit.
Optional GraphQL values remain unavailable without the workflow token. Never
commit a token. Standard tests are offline and cover dates, streaks, privacy,
merged evidence, static/mobile rendering, cache updates, output retention,
unchanged refreshes and protected artwork.

Edit data logic in `scripts/profile_data.py` / `scripts/calendar_visibility.py`,
activity artwork in `scripts/render_profile.py`, and refresh orchestration in
`scripts/update_profile.py`. Preserve the README's `IMPACT` markers. Do not manually
edit generated activity SVGs. A search over 1,000 merged PRs fails explicitly;
partition the query by date before that threshold is reached.

## Optional browser regression checks

The offline unit suite needs no additional packages. For local pixel checks,
install Playwright and Pillow in an isolated environment, then run:

```sh
python3 scripts/verify_rendering.py --browser /usr/bin/google-chrome
```

This compares animated, static and browser-level reduced-motion frames at desktop
and mobile source sizes. It fails if numbers move, inactive cell interiors change,
or static images animate. It also captures clearly labelled synthetic streak
values 0, 1, 10, 100 and 365. All captures remain under ignored `work/review/`.
It does not contact GitHub, modify production images or replace live data.

## GitHub references

- [Private contribution visibility](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements)
- [Contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
- [Missing or delayed contributions](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions)
- [Workflow events and schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GraphQL contribution aggregates](https://docs.github.com/en/graphql/reference/users)
