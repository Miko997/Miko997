# Signature artwork

The header is an original procedural robot workcell. Its warm machined-bronze edges, sapphire switch and violet optical channels carry the palette; the robot physically operates the switch. Twenty-seven little glass bulbs hang from three asymmetrically sagging cables across the wall behind the name and descriptor. Their curved glass envelopes, ribbed brass sockets, graphite collars and internal hairpin elements are original Blender geometry. Local violet, sapphire and lavender light pools are composited onto a faint graphite wall, while the robot and contact shadows remain physically rendered. No stock meshes, textures, Arcane or Stranger Things imagery or externally generated bitmap imagery are used.

The motion is contained entirely in animated WebP images and synchronized with the name treatment. GitHub needs no JavaScript, embedded video, external font loading or multiple independently timed layers.

## Timeline

| Time | Action |
| --- | --- |
| 0–5.0s | Quiet pose; name remains white and all 27 glass bulbs stay dark but their sockets and three cables remain visible. |
| 5.0–6.65s | Shoulder and elbow articulate; the vertical gripper approaches and contacts the cap. |
| 6.65–6.85s | The cap physically depresses by 0.074 model units. Optical channels activate at 6.8s. |
| 6.8–16.8s | The name receives a blue/violet fill and fine energy ribbon; a local wave travels through the 27 bulbs from the same activation clock. |
| 7.05–8.8s | The cap releases, the tool clears it, and the arm returns to its resting pose. |
| 16.8–17.8s | The name, device and bulb wall fade smoothly to their quiet state. |
| 17.8–20.0s | Quiet hold. The last composition is identical to the first. |

A momentary switch triggers the ten-second name effect. The bulb wave has a steady illuminated base with one broad, slowly travelling brightness maximum; the lamp bodies never blink on and off. The arm therefore withdraws after the press instead of remaining unnaturally frozen on the cap throughout the effect. Active letter strokes remain solid and legible; no flashing, disappearing text or decorative particle shower is used.

## Published files

- `assets/signature-header-animated.webp` — 1400 × 525 desktop motion sequence; 1,432,904 bytes.
- `assets/signature-header-mobile-animated.webp` — 650 × 719 mobile motion sequence; 1,280,078 bytes.
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

`compose_header_motion.py` typesets the name and descriptor, synchronizes the name and 27 local bulb effects, and exports both responsive sequences. Rendered movement uses 20fps. Slow motion confined to letterforms uses 12.5fps. Long holds are authored once, then remuxed into 40ms transparent continuation frames. These lossless 1 × 1 no-op frames preserve the existing canvas without duplicating the rendered artwork. This fixes a measured early-advance issue in the local WebKit browser; all original 50/80ms movement and lettering frames remain unchanged. The physically rendered pose cache is reused for compositing refinements.

`remux_webp_holds.py` implements the final container-only timing adjustment according to the [official WebP ANMF specification](https://developers.google.com/speed/webp/docs/riff_container). Every remuxed frame was verified pixel-identical to the original timeline. The v4 output also replaces the image payload at the authored 17.840s quiet boundary with the identical full-canvas opaque first frame. This avoids independent lossy approximations at the loop seam without re-encoding: all 312 earlier decoded frames and every duration were verified unchanged; the final 54 frames are now pixel-identical to the first. The container helper checks full-canvas size, replacement mode and opacity before this operation.

Local WebKit checks for the hold adjustment matched the intended 5.000s, 6.650s, 6.850s and 8.100s poses, including the full quiet opening.

The authoritative editable animation source is the Python geometry and timing. `--save-scene` additionally saves a Blender inspection scene at the quiet pose; it is not a separate baked animation project. Robot pose frames and their timing manifest remain under `work/header-v2/`; the current compositing storyboard and comparisons are under `work/header-v4/` rather than bloating published assets. If geometry, materials or lighting change, clear that script's `pose-*.png` cache before rerendering; existing poses are deliberately reused for resumable rendering.

## Development and review evidence

The first version compared three real Cycles concepts: an optical core inside a gantry, a robot simulation workcell, and a crystalline electromechanical instrument. The workcell was selected for its direct engineering relevance. Independent review found the laboratory too trophy-like and the optical instrument too suggestive of unexplained fantasy machinery.

The first four refinements replaced simple cylinders with detailed housings and recessed fasteners; corrected the approach visualization; removed the studio-image boundary through a transparent shadow catcher; and increased mobile descriptor readability. The accepted v1 static images remain preserved in the local review evidence and Git history.

The second version adds the user's requested physical activation story. The initial preview exposed a power symbol that read as a C/G at the camera angle; it was reoriented toward the viewer before final rendering. Quiet optical channels were darkened so that the press produces an unambiguous lighting change. A six-moment desktop/mobile storyboard exposes rest, approach, pressed contact, release, energized hold and quiet reset.

The third version increased the name from 77 to 85px in the desktop master and from 65 to 72px in the mobile master (about 10%). Its two overhead LED bars did not match the user's intended light-wall reference. They were replaced in the fourth version with 27 individual glass bulbs on three sagging cables across the name side of the image. The rejected v3 assets and source are preserved in `work/header-v4/baseline/`.

The fourth version uses a separate text foreground. The robot and wall are composed first, then a feathered shadow follows each individual text glyph, then the name and descriptor are drawn. This leaves the wall visible between words and avoids a rectangular dark nameplate. The first storyboard exposed bright bulb tangencies behind the mobile descriptor; enlarging the glyph-shaped protection raised actual-background readability without moving the cords away from the name.

The larger name, quiet white state, physical press and twenty-second timing remain unchanged. The desktop wall occupies the left name field; the mobile wall occupies the entire upper name/descriptor area. Twenty-seven small bodies have visible sockets, transparent-glass shading and irregular mild tilts. Their three colors are sapphire, violet and lavender. No rapid flicker, flashing or alphabet-wall reproduction is used.
The encoded assets can be checked without Blender:

```sh
python3 scripts/art/validate_header_motion.py --manifest work/header-v2/motion-manifest.json
```

The validator decodes the complete animation and checks the 20-second duration, five-second opening hold, quiet ending, loop-image continuity and combined image budget. It reconstructs the actual lit wall beneath the text and checks name and descriptor contrast against that local background; a fixed near-black denominator would overstate contrast behind a bulb. It also checks that 27 bulb bodies on three cables stay quiet before the press, brighten during the energized state, and return to quiet. Protected glyph neighborhoods are excluded from the lamp timing measurement. With the optional render manifest it checks fixed link lengths and exact cap/tool contact across all contact frames.

Pre-encode storyboard measurements after the glyph protection refinement give minimum active-name contrast of 6.23:1 desktop and 6.02:1 mobile against the actual wall. Descriptor minima are 8.40:1 and 7.93:1 respectively. The final encoded files total 2.59 MiB, each with 366 frames over exactly 20,000ms. Decoded active-name contrast at the fifth percentile is 7.27:1 desktop and 7.23:1 mobile; the descriptor measures 9.09:1 and 8.90:1 against the actual wall. Both opening holds are 5,000ms; both final quiet holds are 2,160ms. Pre-press bulb changes, final bulb reset errors and first/last decoded loop errors are all exactly zero. Reduced-motion static images match the first-frame composition, with mean RGB differences below 0.85/255 from their independent WebP quality settings. The complete validation results and final file manifest are recorded in the local `work/header-v4/` evidence.
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
