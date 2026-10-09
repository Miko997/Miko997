# Profile redesign — independent review

Review date: 2026-10-09. Local validation must not be confused with a published GitHub rendering. Nothing may be pushed, opened as a pull request, or published before Miko approves the completed visual result.

## Original profile baseline and scope

The baseline is the clean checkout captured before edits in `work/review/baseline` outside the repository. Screenshots include the actual public profile and browser renders of repository assets in a GitHub-style shell. The shell is an approximation of GitHub typography, content width and spacing; it does not reproduce GitHub sanitization, caching or every profile breakpoint.

Observed initial problems: the ring header is flat and diagrammatic; navigational and explanatory text delays the actual work; an oversized activity panel repeats data definitions in tiny labels; an 11-row merged-PR table plus an expanded open-work list makes the profile read as an administrative report; badges and footer decoration repeat links and compete with protected project images. At 375px viewport the desktop-sized activity SVG is scaled below comfortable reading size.

## Browser/image constraints

- GitHub explicitly supports `<picture>` in Markdown and recommends repository-relative image links. Source: [GitHub formatting documentation](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
- Theme selection via `<picture>` and `prefers-color-scheme` is a documented GitHub feature. Source: [GitHub changelog](https://github.blog/changelog/2022-05-19-specify-theme-context-for-images-in-markdown-beta/).
- The current public `html-pipeline` sanitizer allowlist contains `picture`, `source`, `srcset` and `media`. This is supporting implementation evidence, not a guarantee of every GitHub production configuration. Source: [sanitization filter](https://github.com/gjtorikian/html-pipeline/blob/main/lib/html_pipeline/sanitization_filter.rb).
- SVG image mode allows declarative CSS/SVG animation while disabling scripting, interaction and external-resource loading. Data URLs and same-document references remain permitted. Therefore fonts and raster components must be embedded or avoid external dependencies. Sources: [W3C processing modes](https://www.w3.org/TR/SVG/conform.html), [MDN SVG as an image](https://developer.mozilla.org/en-US/docs/Web/SVG/Guides/SVG_as_an_image).
- Reduced-motion CSS is user-preference dependent. An explicit static `<picture>` source plus internal CSS protection provides a useful double layer, but the actual selected source and stable rendered frames must be tested. Source: [MDN reduced motion](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@media/prefers-reduced-motion).
- GitHub proxies images with Camo; stale content can persist. GitHub documents cache checks/purging. Content-dependent query tokens are a practical cache-busting strategy, not an immediate freshness guarantee. Source: [GitHub anonymized URLs](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-anonymized-urls).

### Empirical browser checks

Chrome 155.0.8059.39, Linux, local HTTP `<img>` context:

- A representative CSS `d: path(...)` morph changed 2,813 pixels across 700ms, confirming animation within an image rather than only inline SVG.
- Playwright `reduced_motion="reduce"` emulation applies to the parent document and a directly loaded SVG, but did not propagate to embedded SVG media queries. This is a test-harness distinction, not evidence that operating-system reduced motion is ignored.
- Launching Chrome with browser-level `--force-prefers-reduced-motion` stopped the embedded animation: zero changed pixels. Selecting an explicit static source through `<picture>` also produced zero changed pixels under Playwright's media emulation.
- Final production checks are recorded below; the generic probe was used only to establish the image-context test method.

## Visual reference rationale

[Blender Studio lighting/rendering comparisons](https://studio.blender.org/training/blender-fundamentals-45-lts/blender_4-5_lts_lighting-rendering-theory-cycles/) demonstrate the importance of grounded illumination, reflected light and physical surface response. [NVIDIA Newton](https://developer.nvidia.com/newton-physics) provides a field-specific reference for simulated mechanisms and spatial information. These are technique/subject references, not copied artwork. The signature object should read as an inspectable mechanism or spatial model, not as an unexplained fantasy ornament.

## First iteration — concept review

Three real Cycles-rendered prototypes were inspected side-by-side. **A, Hexcore laboratory** has credible specular materials but its central orb reads as a decorative energy trophy. **B, Simulation field** makes the connection to robotics immediately visible: an articulated mechanism, physical workpiece, sampled path and spatial representation. **C, Electromechanical optics** has strong diagonal depth but an ambiguous purpose that weakens professional specificity. B is the strongest direction on subject relevance, legibility and quiet space for the name.

Initial concept criticism: all three share the same type-left/object-right composition, so the first board explores motifs more than full visual directions. Broader composition changes were requested for A and C. In B, smooth joints and an unconnected trajectory read as a toy model rather than inspected engineering; mechanical seams, wrist detail and a connected toolpath were requested. A visible rectangular floor cut needs a clean fade.

## First iteration — four substantive refinement cycles

Concept exploration is separate. Each cycle was rendered before further changes; root captures are retained in the task's `work/review/cycle-1` through `cycle-4` directories. Additional independent frame captures are in `activity-v1`, `activity-v2`, `composition-v1` and `composition-v3`.

1. **Integrated composition.** Replaced the old header/card/navigation/badge hierarchy with one signature image, two clear activity metrics, a real calendar and concise project links. Added a separate compact calendar with two chronological half-year panels. Criticism: clipped flame tip, small mobile labels, barely visible energy movement and a toy-like robot with an unexplained orbit.
2. **Mechanism and motion.** Added real joint flanges, fasteners, housing seams and a wrist/gripper; replaced the orbit with a workpiece-to-tool path. Rebuilt icon-shaped fire into 16 independently shaped advecting ribbons and connected active calendar cells with a masked travelling pulse. Eight frames over a full 12-second travel cycle demonstrate progress from early active dates to October. Criticism: the plasma's pointed base read as a feather/crystal; mobile legend remained tiny; a floor boundary weakened the hero.
3. **Depth, hierarchy and readable data.** Replaced the floor rectangle with a Cycles shadow catcher, strengthened the blue-white ignition volume, enlarged compact labels, removed the repeated professional-summary paragraph and replaced the evidence table with five linked ecosystems. The header and activity now read as an adjacent pair. Criticism: lower plasma still too pointed; 1,024px laptop layout exposed small desktop calendar labels.
4. **Shape and production refinement.** Rounded the plasma's ignition/base, replaced dense polygon sampling with smooth cubic paths to reduce asset weight, enlarged desktop calendar labels and legend, and verified static/reduced-motion behavior at browser level. Header mobile typesetting is 14px at a 309px rendered width. Independent data review caught and fixed a stale-GraphQL fallback that could otherwise lower a previously enriched snapshot.

### Independent final checks

The local shell uses GitHub's REST Markdown-rendered HTML, with public repository context. The server returned HTTP 200 and preserved both `<picture>` elements and all `source` media attributes, including combined width and reduced-motion preferences. This verifies the Markdown transform; it does not simulate GitHub Camo or prove a newly published profile rendering. See [GitHub Markdown API](https://docs.github.com/en/rest/markdown/markdown).

Screenshots cover 1,440px desktop, 1,280px laptop, an additional 1,024px laptop, 375px mobile, light/dark themes, reduced-motion selection and explicit static variants. The selected sources were checked from the browser's `currentSrc`, not inferred from filenames. All image loads succeeded and document width stayed within each viewport.

Pixel comparison tests run on the actual SVGs embedded as `<img>` images. Animated desktop/mobile changed across frames; inactive day interiors and both numeric regions stayed unchanged. Both static variants and both animated variants under browser-level reduced motion produced identical frames. Synthetic streaks 0, 1, 10, 100 and 365 were rendered separately to check extinguishing and numeric fit; these are explicitly test fixtures, never profile data.

### Cross-browser follow-up

The initial implementation used CSS `d` morphing. [MDN marks that property as limited availability](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/Properties/d), so the production flame was changed to SVG SMIL path morphs. Reduced motion selects a separately drawn still group and hides the animated group; CSS does not claim to pause SMIL. The `<picture>` static source remains the primary fallback, and static files contain no animation elements.

- **Chrome 155:** all eight production checks pass. Animated images changed 18,124 and 16,223 pixels across the sampled interval; inactive cell interiors and numeric regions changed zero pixels. Browser-level reduced-motion and explicit static images changed zero pixels.
- **Firefox 157:** all eight production animation/static/reduced-motion checks pass, including visible flame movement.
- **Playwright WebKit 26.6:** the embedded SVG reports reduced motion even while parent-page emulation reports no preference. A red/blue media-query control isolated this mismatch, consistent with [WebKit's SVG preference-propagation issue](https://bugs.webkit.org/show_bug.cgi?id=283894). The unchanged production file therefore correctly displayed its still group. A clearly separate local probe with only the reduced-motion CSS removed changed 17,266 pixels and visibly morphed the flame, confirming SMIL/`use` support in the image renderer. This is an engine capability check, **not** a claim that physical Safari/iOS has been tested.

Final local captures and a 12-second motion preview are retained in the task's `work/review/final`; pixel results are in `work/review/final-verification-smil`. The Chrome pixel checks can be reproduced from the repository with `scripts/verify_rendering.py` using an isolated environment containing Playwright and Pillow. There is no browser dependency in scheduled data refreshes.

### First-iteration critical assessment

| Category | Directional score | Evidence and remaining criticism |
| --- | ---: | --- |
| Visual identity | 8.5 | Original, restrained robot workcell and violet-blue light; still a compact stylized maquette rather than a cinematic environment. |
| Composition | 8.5 | Name, mechanism and activity have a clear order; each preserved project image has its own visual language, so the complete page is less uniform than the signature/activity pair. |
| Typography | 8.5 | Intentional Inter header, clear stable numerals, dedicated mobile composition; activity text uses local system fallback fonts. |
| Motion design | 8 | Actual contour advection and chronological energy travel; plasma remains visibly procedural, and sparse historical months necessarily have little motion. |
| Engineering relevance | 9 | Joint/wrist geometry, toolpath and spatial overlay connect directly to robotics and simulation. |
| Information clarity | 9 | Two primary metrics, one date range, exact daily cells, concise verified ecosystems. |
| GitHub compatibility | 8 | Official server Markdown transform and image-context tests pass; final hosted profile/Camo verification is pending approval. |
| Technical robustness | 9 | Real published calendar data, merged-only evidence, zero-state rendering and retained-output failure handling; live Actions run awaits publication. |
| Performance | 8.5 | Compact WebP header and bounded vector assets; animated blur/morph costs were observed visually but not profiled on low-end mobile hardware. |
| Professional credibility | 8.5 | Selected engineering ecosystems and shipped work are prominent; the artistic flame is intentionally more expressive than typical research profiles. |

These scores do **not** establish a 9/10 average. They are critical design judgments, not measured quality guarantees or a reason to ignore unresolved correctness defects. The rendered result is substantially more coherent and readable than the baseline, while the remaining stylistic limitations are judgments about this implementation, not proof that a better result is impossible within GitHub.

### Separate reviewer findings

- **Creative direction:** B is more specific to this engineer than A or C; strong negative space and minimal color avoid a generic neon dashboard. The staged object remains intentionally stylized.
- **Motion:** The calendar follows actual active dates and leaves inactive cells unchanged. The plasma has real contour change rather than a scaled icon. Chrome and Firefox production checks pass; the WebKit engine probe is qualified above and does not replace a physical Safari/iOS check.
- **Engineering/data:** The independently found degraded-calendar fallback was fixed and regression-tested. A fresh successful retrieval still reported 1,574 contributions and a 6-day current streak on 2026-10-09.
- **Privacy/security:** The GraphQL query requests aggregate date/count fields, no private repository objects. Public PR metadata is explicitly allowlisted. No secret-bearing output is required for the artwork or local previews.
- **Portfolio/copy:** Open/draft PRs, administrative counts, decorative footer and repetitive prose are removed. The inherited research DOI returned HTTP 403 to an automated check, so availability could not be verified; this does not prove the DOI is broken.

## Second iteration — current Hextech result

This is the current review candidate. The first-iteration counts, captures and scores above are historical. The accepted v1 deliverables were preserved in the task's `work/review/v2-baseline` before editing. A fresh public-data refresh for v2 reported **1,576 contributions across the same 365 dates and a 6-day current streak**; the earlier 1,574 total is retained only as a record of v1.

### Visual changes and independent criticism

- **Mechanical interaction:** the robot now has a physical switch, restrained brass seams, a faceted base and blue-violet lighting. Fixed link lengths and aligned finger/cap contact make the press readable. An initially ambiguous power glyph was corrected before the final encoding. The name remains complete and readable throughout its color treatment.
- **Connected activity hierarchy:** one subdued frame groups the plasma with the current-streak numeral. The contribution total remains the primary left-hand metric. A narrow moving rail occupies the existing divider position, without adding a tall decorative section. Review caught the compact date crossing the frame's lower-left chamfer; the compact date and rail were moved down while preserving the calendar geometry.
- **Compact evidence links:** five static 148×68 plaques use original geometric motifs, muted brass seams and 14px titles. They form one desktop row and a readable 2+2+1 arrangement at 309px content width. Their links still target verified merged pull requests. The plaques add theme without another moving layer.
- **Restrained composition:** the finished desktop and mobile views remain orderly in both GitHub themes. The art deliberately keeps its dark background in light mode. The small workcell still reads as a stylized maquette; the flame remains visibly procedural. These are current aesthetic limitations, not technical impossibility claims.

### Timing and delivery behavior

The encoded hero loop is exactly 20 seconds: quiet white name through 5 seconds, physical approach and contact around 6.65 seconds, name activation around 6.8 seconds, arm return by 8.8 seconds, active name through 16.8 seconds, and a fade to the quiet state by 17.8 seconds. The remaining interval provides a calm reset. The desktop and mobile compositions have separate animated WebPs and separate quiet static WebPs. The final animated files are 1,089,362 bytes at 1400×525 and 994,876 bytes at 650×719. Each has 366 encoded frames; transparent no-op hold segments preserve the quiet artwork without increasing the rendered motion cadence.

The beginning and end use the same rendered composition. Lossy encoding introduces mean decoded endpoint differences of 0.445 and 0.608 RGB levels out of 255, so the result is described as **visually seamless**, not pixel-identical. All strokes remain visible during the name effect; the header validator measured the active letter-stroke fifth-percentile contrast above 7.4:1.

### Current validation evidence

The final GitHub REST Markdown transform and local browser shell are retained in `work/review/v2-final` outside the repository. All nine viewport/theme/preference configurations loaded every image and stayed within the viewport. Actual `currentSrc` values confirm mobile artwork below 600px and both static header and static activity for reduced motion. The explicit static preview also selects both quiet assets. The hosted GitHub/Camo check remains pending approval to publish.

The activity pixel verifier now locates numeric regions by semantic SVG IDs and derives the divider position from its path geometry. Ten checks cover animation, static and browser-level reduced motion, including two synthetic zero-streak cases: an extinguished flame stays unchanged while the separate rail moves. Inactive day interiors and both displayed numbers stay unchanged. After the final compact spacing correction, all five affected Chrome cases and all four affected Firefox cases passed again. Synthetic streaks 0, 1, 10, 100 and 365 were also inspected for fit.

The animated header was independently decoded into timing contact sheets in `work/review/v2-header-timing`. Chrome and Firefox each passed four desktop/mobile normal/reduced-motion checks: the quiet interval stays unchanged, the active interval changes, and static selections stay unchanged. The local WebKit engine was checked separately from physical Safari/iOS. Its initial encoding played the first loop early despite resource loads completing within milliseconds. A controlled side-by-side probe isolated this from navigation or screenshot timing. Splitting only the long quiet holds into 40ms transparent no-op frames fixed the observed behavior without changing any decoded image at the corresponding encoded time; the extra container overhead is 8,142 bytes per asset. Final desktop/mobile WebKit candidates stayed pixel-identical through 4.4 seconds, showed the active state at 8.1 seconds, and returned to quiet after the loop. Nearest-frame matching aligned measured 5.000, 6.650, 6.850 and 8.100-second captures with those exact encoded timestamps. Evidence is in `work/review/v2-webkit-final-candidate`. This is validation of the local WebKit engine, **not** a physical Safari/iOS test. Chrome and Firefox were verified before the container-only hold split; the final split preserves every decoded pixel at the same nominal time.

### Current critical assessment

| Category | Directional score | Current evidence or limitation |
| --- | ---: | --- |
| Visual identity | 9 | Coherent brass, dark metal and violet-blue interaction; original mechanism and plaques. |
| Composition | 9 | Shared streak frame and compact evidence tiles strengthen grouping without multiplying moving panels. |
| Typography | 8.5 | White/colored name stays readable; dedicated mobile typesetting; small calendar labels still require close reading. |
| Motion design | 8.5 | Physical cause-and-effect, slow name treatment and stable real metrics; plasma remains procedural. |
| Engineering relevance | 9 | Articulated mechanism, consistent link geometry and physical switch travel. |
| Information clarity | 9 | Exact dates and counts survive every static/reduced variant; verified evidence remains one click away. |
| GitHub compatibility | 8 | Official Markdown transform and local image tests pass; hosted proxy behavior and physical Safari remain unverified. |
| Technical robustness | 9 | Refreshed real data, retained outputs on failure, zero-state behavior and targeted regressions. |
| Performance | 8 | Roughly 1MB animated hero per selected viewport; no low-end device decoding/battery profile. |
| Professional credibility | 8.5 | Focused engineering evidence and restrained theme; the expressive plasma remains an aesthetic choice. |

This remains a critical local review candidate, not an unqualified 9/10-average claim. No blocking layout or data defect remains in the inspected final compositions. Browser-specific timing evidence and publication limitations must accompany any compatibility claim.

## Release limitation

The final hosted GitHub profile, including image proxy/cache behavior, can only be checked after the approved changes become accessible to GitHub. The user explicitly requires approval before a push. Local image-context tests are necessary evidence but cannot close the GitHub production-compatibility check.
