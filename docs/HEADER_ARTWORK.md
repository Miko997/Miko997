# Signature artwork

The header is an original procedural robot workcell. Its warm machined-bronze edges, sapphire switch and violet optical channels carry the palette; the robot physically operates the switch. Thirty-three little glass bulbs on desktop, and twenty-seven on mobile, hang from three asymmetrically sagging cables across the wall behind the name and descriptor. Their curved glass envelopes, ribbed brass sockets, graphite collars and internal hairpin elements are original Blender geometry. Local violet, sapphire and lavender light pools are composited onto a faint graphite wall, while the robot and contact shadows remain physically rendered. No stock meshes, textures, Arcane or Stranger Things imagery or externally generated bitmap imagery are used.

The motion is contained entirely in animated WebP images and synchronized with the name treatment. GitHub needs no JavaScript, embedded video, external font loading or multiple independently timed layers.

## Timeline

| Time | Action |
| --- | --- |
| 0–0.04s | The original quiet canvas initializes the animation; the name is white and the unlit glass bulbs and cables remain visible. |
| 0.04–1.65s | Shoulder and elbow articulate immediately; measurable robot motion appears by 0.10s. The vertical gripper approaches and contacts the cap. |
| 1.65–1.85s | The cap physically depresses by 0.074 model units. Optical channels activate at 1.8s. |
| 1.8–11.8s | The name receives a blue/violet fill and fine energy ribbon; individual glass bulbs blink off and reignite with irregular local timing from the same activation clock. |
| 2.05–3.8s | The cap releases, the tool clears it, and the arm returns to its resting pose. |
| 11.8–12.8s | The name, device and bulb wall fade smoothly to their quiet state. |
| 12.8–15.0s | Quiet settling hold. At 12.84s the image is pixel-identical to the first frame, making the loop continuous. |

A momentary switch triggers the ten-second name effect. Each bulb has independent deterministic on intervals of 0.50–1.18s and fully off dwells of 0.35–0.90s. Short 0.08–0.12s attacks and 0.10–0.16s releases make the blinking distinct without switching the entire wall together. Several bulbs therefore change while others remain lit or dark. The name effect remains continuously legible and does not blink. The arm therefore withdraws after the press instead of remaining unnaturally frozen on the cap throughout the effect. Active letter strokes remain solid and legible; no flashing, disappearing text or decorative particle shower is used.

## Published files

- `assets/signature-header-animated.webp` — 1400 × 525 desktop motion sequence; 1,779,476 bytes, 243 encoded frames.
- `assets/signature-header-mobile-animated.webp` — 650 × 719 mobile motion sequence; 1,489,314 bytes, 242 encoded frames.
- `assets/signature-header.webp` — quiet desktop image, also the reduced-motion fallback.
- `assets/signature-header-mobile.webp` — quiet mobile image, also the reduced-motion fallback.
- `assets/source/switch-scene-quiet.webp` and `switch-scene-active.webp` — compact rendered still sources with actual Cycles shadow-catcher transparency.
- `assets/source/bulb-{sapphire,violet,lavender}-{off,on}.webp` — six original transparent Cycles renders of the small glass bulb in three colors and both states.
- `assets/source/fonts/InterVariable.ttf` and `Inter-LICENSE.txt` — Inter 4.1 and its SIL Open Font License.

The README selects static files for `prefers-reduced-motion: reduce`, with mobile sources before desktop sources. Animated WebP itself cannot evaluate a reduced-motion media query. The static files use exactly the same composition, geometry and type positioning as the animation's first frame.

## Editable sources and reproduction

Requires Blender 5.0.1 (Cycles), Python 3, Pillow and NumPy. Rendering was verified with an NVIDIA RTX 5070 Ti through OptiX; the scene setup supports CPU fallback. These art tools are not dependencies of the scheduled GitHub activity refresh.

```sh
blender -b --python-exit-code 1 --python scripts/art/render_header_motion.py -- --size 1000 --samples 96 --save-scene
python3 scripts/art/compose_header_motion.py
python3 scripts/art/link_header_assets.py
```

The checked-in bulb sprites are used directly. To rebuild them after editing their geometry:

```sh
blender -b --python-exit-code 1 --python scripts/art/render_bulb_wall.py
python3 scripts/art/compose_header.py --package-lights
```

For quick art review with nine physically rendered poses:

```sh
blender -b --python-exit-code 1 --python scripts/art/render_header_motion.py -- --preview --size 900 --samples 72
python3 scripts/art/compose_header_motion.py --preview
```

To regenerate only quiet typesetting from the checked-in source:

```sh
python3 scripts/art/compose_header.py
```

`render_header_motion.py` builds the precision housing, joints, switch, lighting and physical motion. The two arm links use analytic planar inverse kinematics with fixed lengths of 1.29 and 1.19 model units. A vertical tool constraint keeps the pads aligned with the cap. During contact, cap displacement and fingertip height are derived from the same value; the robot never scales, slides as a whole, or changes link length to imitate movement.

`compose_header_motion.py` typesets the name and descriptor, synchronizes the name and individual bulb effects, and exports both responsive sequences. Rendered movement uses 20fps. Slow motion confined to letterforms uses 12.5fps. Long holds are authored once, then remuxed into 40ms transparent continuation frames. These lossless 1 × 1 no-op frames preserve the existing canvas without duplicating the rendered artwork. This fixes a measured early-advance issue in the local WebKit browser; all original 50/80ms movement and lettering frames remain unchanged. The physically rendered pose cache is reused for compositing refinements.

`remux_webp_holds.py` implements the final container-only timing adjustment according to the [official WebP ANMF specification](https://developers.google.com/speed/webp/docs/riff_container). Every remuxed frame was verified pixel-identical to the original timeline. The loop-closure step also replaces the image payload at the authored 17.840s quiet boundary with the identical full-canvas opaque first frame. This avoids independent lossy approximations at the loop seam without re-encoding: the v4 verification established that all 312 earlier decoded frames and every duration stayed unchanged, while all 54 ending frames became pixel-identical to the first; the same container operation is retained for v5. The container helper checks full-canvas size, replacement mode and opacity before this operation.

Historical v2–v5 local WebKit checks for the hold adjustment matched the then-intended 5.000s, 6.650s, 6.850s and 8.100s poses, including the former quiet opening. The current immediate-start edit was checked through native WebP decoding; browser replay was not available in this environment.

The immediate-start refinement removes exactly five seconds through `trim_quiet_opening()` in the same container helper. It retains the original fully opaque first image for 40ms so that subsequent delta frames have the correct canvas, shortens the first retained tiny-motion frame from 100ms to 60ms, and copies all remaining compressed image payloads unchanged. The initial pose, reduced-motion files, full ten-second energy span, bulb blink sequence and final 2.16-second exact quiet hold are preserved. Every decoded retained frame is pixel-identical to the corresponding former frame; only its presentation time changes.

The Blender pose cache, manifest and internal bulb/name functions deliberately retain their established 20-second authoring clock, avoiding unnecessary rendering or cache invalidation. Published time is authoring time minus 5s, with the original quiet image used for the 40ms initialization. `compose_header_motion.py` applies the trim automatically after encoding and loop closure, emits a 15-second timing manifest, and labels preview evidence in published time. The validator adds the same five-second offset when reconstructing the backdrop or reading cached poses.

To apply the timing-only change to an existing original 20-second asset without rendering:

```sh
python3 scripts/art/remux_webp_holds.py original-20s.webp immediate-15s.webp --trim-opening-ms 5000
```

The helper rejects a prefix containing visible changes, a missing exact trim boundary, or an unsuitable initialization frame. It should be applied once to the original baseline, not repeatedly to an already-trimmed export.

The authoritative editable animation source is the Python geometry and timing. `--save-scene` additionally saves a Blender inspection scene at the quiet pose; it is not a separate baked animation project. Robot pose frames and their timing manifest remain under `work/header-v2/`; the current compositing storyboard and comparisons are under `work/header-immediate/` rather than bloating published assets. If geometry, materials or lighting change, clear that script's `pose-*.png` cache before rerendering; existing poses are deliberately reused for resumable rendering.

## Development and review evidence

The first version compared three real Cycles concepts: an optical core inside a gantry, a robot simulation workcell, and a crystalline electromechanical instrument. The workcell was selected for its direct engineering relevance. Independent review found the laboratory too trophy-like and the optical instrument too suggestive of unexplained fantasy machinery.

The first four refinements replaced simple cylinders with detailed housings and recessed fasteners; corrected the approach visualization; removed the studio-image boundary through a transparent shadow catcher; and increased mobile descriptor readability. The accepted v1 static images remain preserved in the local review evidence and Git history.

The second version adds the user's requested physical activation story. The initial preview exposed a power symbol that read as a C/G at the camera angle; it was reoriented toward the viewer before final rendering. Quiet optical channels were darkened so that the press produces an unambiguous lighting change. A six-moment desktop/mobile storyboard exposes rest, approach, pressed contact, release, energized hold and quiet reset.

The third version increased the name from 77 to 85px in the desktop master and from 65 to 72px in the mobile master (about 10%). Its two overhead LED bars did not match the user's intended light-wall reference. They were replaced in the fourth version with 27 individual glass bulbs on three sagging cables across the name side of the image. The rejected v3 assets and source are preserved in `work/header-v4/baseline/`.

The fourth version uses a separate text foreground. The robot and wall are composed first, then a feathered shadow follows each individual text glyph, then the name and descriptor are drawn. This leaves the wall visible between words and avoids a rectangular dark nameplate. The first storyboard exposed bright bulb tangencies behind the mobile descriptor; enlarging the glyph-shaped protection raised actual-background readability without moving the cords away from the name.

At that fourth refinement, the larger name, quiet white state, physical press and original twenty-second timing remained unchanged. The desktop wall occupies the left name field; the mobile wall occupies the entire upper name/descriptor area. Twenty-seven small bodies have visible sockets, transparent-glass shading and irregular mild tilts. Their three colors are sapphire, violet and lavender. The lettering never flashes, and no alphabet-wall reproduction is used.

The fifth version extends the desktop cables from x=795 to x=975, adding two bulbs to each strand while retaining the original approximate horizontal spacing. This gives eleven bulbs per strand (33 total) and keeps the rightmost lower lamp clear of the robot base. The mobile layout remains nine bulbs per strand (27 total), because its wall already fills the available width. The faint wall surface expands with the desktop cables and still fades continuously into the canvas.

The former shallow brightness wave is replaced by full off/on blinking. Every socket has a reproducible seeded schedule, so several changing lit/dark bulbs remain visible at once. When the switch interval ends at 11.8s (16.8s in the preserved authoring clock), each local state is held while the shared one-second envelope fades the remaining lit lamps. No new reignitions occur during that fade. The v4 header and source baseline are preserved under `work/header-v5/baseline/`. Before final encoding, a 7.1-second desktop/mobile GIF excerpt and six-frame contact sheets verify that the repeated dark states are visually distinct. Independent review decoded all 71 preview frames and measured 4–6 clear off/on cycles in every unobscured sampled bulb (29 on desktop, 20 on mobile), with 82–153/255 brightness swings and differing schedules between bulbs.
The encoded assets can be checked without Blender:

```sh
python3 scripts/art/validate_header_motion.py --manifest work/header-v2/motion-manifest.json
# Optional local verification of every retained frame against the former timeline:
python3 scripts/art/validate_header_motion.py --baseline work/header-immediate/baseline
```

The validator decodes the complete animation and checks the 15-second duration, at most 40ms of initialization, measurable robot motion by 100ms, quiet ending, exact loop-image equality and combined image budget. A meaningful motion change requires at least 100 native robot-region pixels to differ from the first frame by more than 24/255 in one color channel; the desktop and mobile images change 541 and 399 pixels respectively at 100ms. It reconstructs the actual lit wall beneath the text at six decoded frame-start times and checks the worst name and descriptor contrast against those local backgrounds; a fixed near-black denominator or mismatched sample time would overstate contrast at a blink boundary.

Selected unobstructed bulbs are measured throughout the encoded active interval. Each must fall close to its quiet glass brightness and return to its illuminated state repeatedly: at least three off dwells and three on dwells of 160ms or longer, plus three relights. The measurement uses the decoded bulb pixels, not only the authored schedule. Protected text neighborhoods and neighboring light pools are excluded. It additionally checks the responsive bulb counts, exact quiet opening/reset, and matching static fallback. With the optional robot render manifest it checks fixed link lengths and exact cap/tool contact across all contact frames.

Current decoded validation results and the before/after baseline are recorded under `work/header-immediate/`; previous bulb-wall development evidence remains under `work/header-v5/`.
The scene is a stylized engineering illustration. Its path, device dimensions and optical behavior are authored for the composition and are not presented as measured robot telemetry or a validated industrial simulation.

## Typography and reference provenance

Inter uses optical size 32 for the name, optical size 14 for the descriptor, weight 610 for the name and 400 for the descriptor. The canvas is `#090b12`; quiet name text is `#f1f3ff`; the descriptor is `#aab6ce`. The energized name moves between luminous lavender and sapphire blue while retaining its silhouette and readable luminance.

- [Inter 4.1 source and license](https://github.com/rsms/inter/tree/v4.1) — bundled unmodified from the official project.
- [Blender 5.0.1 official release](https://download.blender.org/release/Blender5.0/) — portable archive verified against its official SHA-256 file before local use.
- [NVIDIA robotics platform](https://www.nvidia.com/en-us/industries/robotics/) — research reference for readable industrial simulation scenes; no artwork or models copied.

The user-supplied light-wall reference informed only the structural idea of many separate hanging bulbs on several sagging cords behind text. Its wallpaper, alphabet, multicolor arrangement and scene are not copied. The original graphite/brass wall geometry and blue/violet palette belong to this composition.

All visible text is typeset into the WebP for consistent GitHub proxy rendering. The README supplies equivalent alternative text. The static and animated images contain no contribution numbers, secrets or external resource dependencies.

## Immutable README image links

After composition, run `python3 scripts/art/link_header_assets.py`. It creates content-addressed copies of the four final images and updates the README. The mapping is recorded in `assets/header-manifest.json`. Canonical files remain the editable build outputs. This avoids GitHub image-cache behavior that can ignore query-string version tokens.
