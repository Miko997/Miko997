# Hextech profile system

This is a data pipeline, not a GIF with fixed numbers. GitHub Actions fetches the
account's current published contribution counts, computes the metrics, renders
self-contained SVGs, and updates the README's upstream contribution section.
The flame, circuit lights and orbital strokes animate in the browser. Numbers
are real text regenerated from the data; animation never invents activity.

## Updates

`.github/workflows/profile.yml` runs at minutes 17 and 47 each hour (UTC), on
relevant pushes to this profile repository, and through **Run workflow**. GitHub
can delay scheduled jobs. The workflow stores no new commit when its outputs are
unchanged. Updates use the GitHub Actions bot identity, not Miko's identity.

The public snapshot is `data/public-activity.json`. It contains the measurement
date, aggregate counts, 365 daily totals, and explicitly public upstream PR
metadata. Generated image URLs include a content fingerprint to reduce stale
image-cache reuse after the underlying data changes.

A push in another repository does **not** automatically trigger a workflow here.
It is picked up on the next scheduled refresh, after GitHub has counted it.
GitHub documents that a qualifying commit can take up to 24 hours to appear in
the contribution graph. Truly event-triggered cross-repository refresh is also
supported via `repository_dispatch` with event type `profile-refresh` and an empty
client payload. Nothing is installed in other repositories by this change.
A caller needs permission to dispatch to this profile repository; its ordinary
repository-scoped `GITHUB_TOKEN` cannot write to another repository. Do not send
private repository names, branch names, commit messages, or IDs in the payload.

GitHub may disable schedules in a public repository after 60 days without
repository activity. The workflow status is linked from the profile. Use **Run
workflow** or re-enable the workflow if necessary. Branch protection requiring
PRs can block the bot's push; the workflow fails rather than bypassing protection.

## What the numbers mean

| Metric | Definition |
| --- | --- |
| Contributions / 365d | Sum of exactly 365 GitHub calendar dates ending on the measurement date. This can differ slightly from GitHub's native “last year” display range. |
| All-time contributions | Sum of published daily counts from the account's creation year through the measurement date. All years are refetched, not extrapolated. |
| Active days / 365 | Dates in that window with at least one contribution. The segmented signal is chronological, one segment per day. |
| Current streak | Consecutive contribution dates ending today, or yesterday if today has no activity yet. It resets when both today and yesterday are inactive. |
| Longest streak | Longest consecutive run in the fetched all-time calendar, including runs across year boundaries. |
| Visible commit contributions / 365d | Separately queried `totalCommitContributions` aggregate visible to the workflow's GitHub token. Unavailable means the optional query failed, not zero. It is not presented as an all-private commit total. |
| Merged upstream PRs | Authored public PRs returned by `is:merged`, excluding repositories owned by Miko997. Not commits, reviews, organization membership, or a quality score. |
| Open upstream work | Authored public PRs returned by `is:open`. Open and draft work is never called merged. |

**Contributions are not synonymous with commits.** GitHub also counts qualifying
PRs, issues, reviews and other contribution types. The flame is therefore
labelled a *contribution streak*. The anonymous private calendar does not expose
the per-type breakdown needed to promise an exact private-only commit streak.
Dates are GitHub's reported calendar dates; the end date is taken in UTC. The
pipeline does not attempt to rebucket commit timestamps into Helsinki time.

## Private work: counts, not contents

The calendar is fetched **without authentication** from GitHub's public profile
calendar. It includes private contributions only when GitHub publishes their
anonymous counts. Enable **Your profile → Contribution settings → Private
contributions** to include those counts while keeping repositories private.
Without that setting, the pipeline cannot infer or manufacture hidden activity.

No personal access token with access to private repositories is needed. The
workflow's built-in `GITHUB_TOKEN` is scoped to this public profile repository.
GraphQL requests only aggregate integers and daily calendar counts, never
repository objects. A second, complete calendar is validated against the public
calendar before it is used. The `restrictedContributionsCount` value is recorded
only as visibility evidence; it is **never added** to the calendar total, because
those counts may already be included. `visibility` in the public snapshot records
which source was used and whether anonymous private counts were returned. A zero
restricted count does not prove that the account has no private work. Public upstream PR searches always include `is:public`; only repository
name, public URL, title, number, state and draft flag are retained. PR bodies,
patches and branch metadata are discarded. No private repository is enumerated,
cloned, downloaded, or written into logs or public artifacts.

Never add a hand-entered “700 private commits” correction: that would become
stale, risk double counting, and confuse contributions with commits.

## Rendering and accessibility

The palette is near-black, violet and electric blue. SVGs contain no scripts,
external fonts, remote image dependencies, or `foreignObject`. The graph shows
exactly 365 dates. Inactive cells never light up as active. Subtle light pulses
do not change the stored counts. Text remains readable without animation.
Reduced-motion preferences disable animation, and the README provides a static
calendar alternative. Each SVG has a title and description.

GitHub README images are not an interactive application: hover support varies,
and JavaScript is not used. GitHub's native green contribution calendar below
the README cannot be restyled, replaced or hidden for other visitors through a
profile README. This custom console lives inside the README.

## Protected artwork

The Metriplane hero retains this exact reference:

`https://raw.githubusercontent.com/Miko997/metriplane/main/docs/assets/metriplane-hero.jpg`

The Cursed Dawn hero retains `assets/cursed-dawn-hero.jpg`, unchanged. The original
blob SHA is `8afda374869b2080925c8e70e05734c39bc28daf`. Tests check the reference and,
when the file is present, the exact Git blob hash. Neither image is recolored,
redrawn, cropped, replaced, or processed by the update script.

## Maintenance

Requires Python 3.10+ and its standard library; no pip packages or third-party
stats service is required at runtime.

```sh
python3 -m unittest discover -s tests -v
python3 scripts/update_profile.py
```

Local unauthenticated refresh is supported subject to GitHub's public API rate
limits; the optional visible-commit metric needs the workflow token. Do not
commit tokens. The GitHub-hosted runner provides its own token automatically.

Edit the layout in `scripts/render_profile.py`; fetching and calculations are in
`scripts/profile_data.py` and `scripts/calendar_visibility.py`. Keep the README's
`IMPACT` markers intact. Generated assets should not be edited manually.
Source/test changes trigger regeneration.
A failed or incomplete collection does not publish fake zeroes or overwrite the
last successful snapshot. Public PR search pagination is checked; more than
1,000 results fails explicitly and requires date-partitioned retrieval rather
than silently truncating statistics. Standard tests never access the network.

## GitHub documentation

- [Contribution visibility](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/manage-visibility-settings-for-private-contributions-and-achievements)
- [Profile contribution rules](https://docs.github.com/en/account-and-profile/reference/profile-contributions-reference)
- [Missing or delayed contributions](https://docs.github.com/en/account-and-profile/how-tos/contribution-settings/troubleshooting-missing-contributions)
- [Workflow events and schedules](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)
- [GraphQL contribution aggregates](https://docs.github.com/en/graphql/reference/users)
