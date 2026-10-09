# Signature artwork

The header is an original procedural robot workcell. Its warm machined-bronze edges, sapphire switch and violet optical channels carry the palette; the robot physically operates the switch. The suspended LED housings, bronze end caps and violet/blue diffusers are also original Blender geometry. Their subtle light spill is composited, while the robot and contact shadows remain physically rendered. No stock meshes, textures, Arcane imagery or externally generated bitmap imagery are used.

The motion is contained entirely in animated WebP images and synchronized with the name treatment. GitHub needs no JavaScript, embedded video, external font loading or multiple independently timed layers.

## Timeline

| Time | Action |
| --- | --- |
| 0–5.0s | Quiet pose; name remains white and the suspended LED diffusers stay dark. |
| 5.0–6.65s | Shoulder and elbow articulate; the vertical gripper approaches and contacts the cap. |
| 6.65–6.85s | The cap physically depresses by 0.074 model units. Optical channels activate at 6.8s. |
| 6.8–16.8s | The name receives a blue/violet fill and fine energy ribbon; both LED fixtures illuminate from the same activation value. |
| 7.05–8.8s | The cap releases, the tool clears it, and the arm returns to its resting pose. |
| 16.8–17.8s | The name, device and suspended lighting fade smoothly to their quiet state. |
| 17.8–20.0s | Quiet hold. The last composition is identical to the first. |

A momentary switch triggers the ten-second name effect. The arm therefore withdraws after the press instead of remaining unnaturally frozen on the cap throughout the effect. Active letter strokes remain solid and legible; no flashing, disappearing text or decorative particle shower is used.

## Published files

- `assets/signature-header-animated.webp` — 1400 × 525 desktop motion sequence; 1,151,620 bytes.
- `assets/signature-header-mobile-animated.webp` — 650 × 719 mobile motion sequence; 1,028,622 bytes.
- `assets/signature-header.webp` — quiet desktop image, also the reduced-motion fallback.
- `assets/signature-header-mobile.webp` — quiet mobile image, also the reduced-motion fallback.
- `assets/source/switch-scene-quiet.webp` and `switch-scene-active.webp` — compact rendered still sources with actual Cycles shadow-catcher transparency.
- `assets/source/lab-light-off.webp` and `lab-light-on.webp` — original Cycles renders of the suspended fixture in both states.
- `assets/source/fonts/InterVariable.ttf` and `Inter-LICENSE.txt` — Inter 4.1 and its SIL Open Font License.

The README selects static files for `prefers-reduced-motion: reduce`, with mobile sources before desktop sources. Animated WebP itself cannot evaluate a reduced-motion media query. The static files use exactly the same composition, geometry and type positioning as the animation's first frame.

## Editable sources and reproduction

Requires Blender 5.0.1 (Cycles), Python 3, Pillow and NumPy. Rendering was verified with an NVIDIA RTX 5070 Ti through OptiX; the scene setup supports CPU fallback. These art tools are not dependencies of the scheduled GitHub activity refresh.

```sh
blender -b --python-exit-code 1 --python scripts/art/render_header_motion.py -- --size 1000 --samples 96 --save-scene
python3 scripts/art/compose_header_motion.py
python3 scripts/art/link_header_assets.py
```

The checked-in fixture layers are used directly. To rebuild them after editing their geometry:

```sh
blender -b --python-exit-code 1 --python scripts/art/render_lab_lights.py
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

`compose_header_motion.py` typesets the name and descriptor, synchronizes the activation effect, and exports both responsive sequences. Rendered movement uses 20fps. Slow motion confined to letterforms uses 12.5fps. Long holds are authored once, then remuxed into 40ms transparent continuation frames. These lossless 1 × 1 no-op frames preserve the existing canvas without duplicating the rendered artwork. This fixes a measured early-advance issue in the local WebKit browser; all original 50/80ms movement and lettering frames remain unchanged. The physically rendered pose cache is reused for compositing refinements.

`remux_webp_holds.py` implements the final container-only timing adjustment according to the [official WebP ANMF specification](https://developers.google.com/speed/webp/docs/riff_container). Every remuxed frame was verified pixel-identical to the original timeline. Local WebKit checks then matched the intended 5.000s, 6.650s, 6.850s and 8.100s poses, including the full quiet opening.

The authoritative editable animation source is the Python geometry and timing. `--save-scene` additionally saves a Blender inspection scene at the quiet pose; it is not a separate baked animation project. Robot pose frames and their timing manifest remain under `work/header-v2/`; the current compositing storyboard and comparisons are under `work/header-v3/` rather than bloating published assets. If geometry, materials or lighting change, clear that script's `pose-*.png` cache before rerendering; existing poses are deliberately reused for resumable rendering.

## Development and review evidence

The first version compared three real Cycles concepts: an optical core inside a gantry, a robot simulation workcell, and a crystalline electromechanical instrument. The workcell was selected for its direct engineering relevance. Independent review found the laboratory too trophy-like and the optical instrument too suggestive of unexplained fantasy machinery.

The first four refinements replaced simple cylinders with detailed housings and recessed fasteners; corrected the approach visualization; removed the studio-image boundary through a transparent shadow catcher; and increased mobile descriptor readability. The accepted v1 static images remain preserved in the local review evidence and Git history.

The second version adds the user's requested physical activation story. The initial preview exposed a power symbol that read as a C/G at the camera angle; it was reoriented toward the viewer before final rendering. Quiet optical channels were darkened so that the press produces an unambiguous lighting change. A six-moment desktop/mobile storyboard exposes rest, approach, pressed contact, release, energized hold and quiet reset.

The third version increases the name from 77 to 85px in the desktop master and from 65 to 72px in the mobile master (about 10%). Two suspended laboratory LED fixtures occupy the previously empty ceiling space. Mobile places their suspension rail below the descriptor; neither lamp overlaps the text. One shared activation function drives the fixtures, optical device and name, so no separate animated image can drift out of sync. There is no strobe or separate brightness modulation. The accepted v2 assets and source files are preserved in `work/header-v3/baseline/`.

The encoded assets can be checked without Blender:

```sh
python3 scripts/art/validate_header_motion.py --manifest work/header-v2/motion-manifest.json
```

The delivered files total 2.08 MiB, each decode to 367 frames over exactly 20,000ms, and preserve a 5,000ms opening hold. The measured active-name interior contrast stays above 7.4:1 at the fifth percentile. The fixture diffusers remain pixel-identical to their quiet state before the press and brighten by approximately 178 RGB levels while active; the small encoded reset difference stays below 3/255. Lossy WebP encoding introduces mean first/last pixel differences of 0.69/255 (desktop) and 0.85/255 (mobile); the unencoded first and last images are identical.

The validator decodes the complete animation and checks the 20-second duration, five-second opening hold, quiet ending, loop-image continuity, active-name contrast and combined image budget. It additionally checks that the fixture diffusers stay dark before the press, brighten during the energized state, and return to their original quiet state. With the optional render manifest it also checks fixed link lengths and exact cap/tool contact across all contact frames.

The scene is a stylized engineering illustration. Its path, device dimensions and optical behavior are authored for the composition and are not presented as measured robot telemetry or a validated industrial simulation.

## Typography and reference provenance

Inter uses optical size 32 for the name, optical size 14 for the descriptor, weight 610 for the name and 400 for the descriptor. The canvas is `#090b12`; quiet name text is `#f1f3ff`; the descriptor is `#aab6ce`. The energized name moves between luminous lavender and sapphire blue while retaining its silhouette and readable luminance.

- [Inter 4.1 source and license](https://github.com/rsms/inter/tree/v4.1) — bundled unmodified from the official project.
- [Blender 5.0.1 official release](https://download.blender.org/release/Blender5.0/) — portable archive verified against its official SHA-256 file before local use.
- [NVIDIA robotics platform](https://www.nvidia.com/en-us/industries/robotics/) — research reference for readable industrial simulation scenes; no artwork or models copied.

All visible text is typeset into the WebP for consistent GitHub proxy rendering. The README supplies equivalent alternative text. The static and animated images contain no contribution numbers, secrets or external resource dependencies.

## Immutable README image links

After composition, run `python3 scripts/art/link_header_assets.py`. It creates content-addressed copies of the four final images and updates the README. The mapping is recorded in `assets/header-manifest.json`. Canonical files remain the editable build outputs. This avoids GitHub image-cache behavior that can ignore query-string version tokens.
