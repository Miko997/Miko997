# Signature artwork

An original procedural robot workcell with a physical fixture, optical workpiece outline and sampled approach path. It is illustrative artwork, not a claimed simulation result or an image of a commercial robot. All geometry, lights and materials are authored in `scripts/art/render_header_scene.py`; no stock meshes, textures, Arcane imagery or generated bitmap imagery are used.

The final composition uses physically rendered titanium, dark anodized housings, recessed fasteners, a service cable and an articulated two-finger gripper. Violet and blue appear in reflected light, thin encoder edges and the optical workpiece. The header stays static so that the activity visual carries the page's motion hierarchy.

## Files

- `assets/signature-header.webp` — 1600 × 600 desktop composition.
- `assets/signature-header-mobile.webp` — 750 × 830 mobile composition; selected with a `<picture>` source at 600px.
- `assets/source/simulation-scene.webp` — 1400 × 1400 editable-composition source, with actual Cycles shadow-catcher transparency.
- `scripts/art/render_header_scene.py` — builds the full editable Blender scene. Supports `laboratory`, `simulation` and `electromechanical` concepts and optional `.blend` saving.
- `scripts/art/compose_header.py` — typesets both compositions from the source with no network access.
- `assets/source/fonts/InterVariable.ttf` and `Inter-LICENSE.txt` — Inter 4.1 and its SIL Open Font License.

## Reproduce

Requires Blender 5.0.1 (Cycles), Python 3, Pillow and NumPy. The production render used an NVIDIA RTX 5070 Ti with OptiX; the script falls back to CPU when OptiX is unavailable. No runtime or Blender dependency is added to the scheduled GitHub data refresh.

From the repository root:

```sh
blender -b --python scripts/art/render_header_scene.py -- --concept simulation --output work/header/simulation.png --size 1400 --samples 160 --save-scene work/header/simulation.blend
python3 scripts/art/compose_header.py --scene work/header/simulation.png --save-source
```

To rebuild the typesetting alone from the checked-in scene:

```sh
python3 scripts/art/compose_header.py
```

The scene is original editable geometry; the Python generator is the authoritative art source. A `.blend` file is optional and generated on request with `--save-scene`. Large working renders and alternate concepts are kept out of published assets.

## Visual decisions and iterations

Three initial Cycles concepts were compared as real rendered images: a gantry-contained optical core, a robot simulation workcell, and a crystalline electromechanical instrument. The workcell was selected because its connection to robotics and reproducible engineering was immediate. Independent review found the laboratory concept too trophy-like and the optical instrument too suggestive of unexplained fantasy machinery.

1. The selected workcell was composed alongside restrained Inter text. Initial feedback identified uniform cylindrical arms, bright decorative samples and an image boundary.
2. Cast housings, inset panels, recessed bearings, real fastener geometry, wrist flange and gripper contact pads replaced the toy-like forms. A service cable follows the joints.
3. A workpiece-to-tool approach curve replaced the disconnected dotted orbit. Point-cloud samples were reduced. A transparent Cycles shadow catcher removed the studio rectangle while preserving the contact shadow.
4. Desktop and mobile typesetting were composed separately; mobile descriptor type was increased to remain approximately 14px at a 309px content width. The device, text and contrast were inspected at actual profile sizes before optimized WebP export.

Source render and comparison images are retained in the local `work/header/` review directory. The evidence includes the initial concept board, a second board exploring different compositional hierarchies, and the four intermediate compositions.

## Typography and references

Inter uses optical size 32 for the name, optical size 14 for body copy, weight 610 for the name and 400 for the descriptor. The final canvas is `#090b12`, type is `#f1f3ff`, descriptor is `#aab6ce`. The responsive layout retains name and descriptor as accessible alternative text in the README.

- [Inter 4.1 source and license](https://github.com/rsms/inter/tree/v4.1) — bundled unmodified from the official project.
- [Blender 5.0.1 official release](https://download.blender.org/release/Blender5.0/) — portable Linux archive verified against its SHA-256 file before local use.
- [NVIDIA robotics platform](https://www.nvidia.com/en-us/industries/robotics/) — research reference for readable industrial simulation scenes; no artwork or models copied.

No external fonts or images are loaded by either final header image. All visible text is typeset into the WebP. This preserves the chosen font through GitHub image proxying. The README supplies equivalent alt text, and the profile copy remains normal selectable text below it.
