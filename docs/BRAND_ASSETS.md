# Button artwork sources

The buttons retain their original frames, labels, destinations and motion.
Their symbols now use the source artwork below, with its original proportions.
The complete source inventory, licenses, adaptations and checksums are in
[`brand-sources.json`](brand-sources.json). Original downloads are retained in
`assets/brands/originals/`; self-contained presentation SVGs are in
`assets/brands/icons/`.

The first three associations were explicitly selected by the profile owner:
NVIDIA for Newton Physics, Google for MuJoCo, and Pixar for OpenUSD. The project
labels and links continue to identify the actual upstream contribution; the
chosen marks do not assert exclusive project ownership or employment.

| Button | Official source | Presentation |
| --- | --- | --- |
| Newton Physics | [NVIDIA website mark](https://www.nvidia.com/en-us/) | Original NVIDIA eye path in lavender, transparent. |
| MuJoCo | [Google identity artwork](https://developers.google.com/identity/branding-guidelines) | All four original Google G paths in lavender, without button framing. |
| OpenUSD | [Pixar website wordmark](https://www.pixar.com/) | Original transparent PNG, with a pale SVG paint filter preserving alpha. |
| ROS 2 | [Open Robotics artwork](https://github.com/openrobotics/artwork/blob/4024191d62211c4d4fa024e9974dd372d92aa23a/orgunits/ros.svg) | Official white nine-dot mark; ROS 2 is identified by the existing label. |
| RViz | [Original isolated RViz artwork](https://github.com/ros-visualization/rviz/blob/c4964de840d97b1377456a2054662551816b0a54/image_src/rviz_isolated.xcf) | Exact RGBA pixels from its isolated lettering layer; transparent, with no ground, rectangle or shadow layer. |
| ROS Perception | [Original organization artwork](https://github.com/openrobotics/artwork/blob/4024191d62211c4d4fa024e9974dd372d92aa23a/orgunits/ros_logos.graffle) | All 234 rectangles from the named perception layer, in official white. |
| LinkedIn | [LinkedIn brand resources](https://brand.linkedin.com/in-logo) | Official inbug vector geometry, white variant. |
| ORCID | [ORCID brand library](https://info.orcid.org/brand-guidelines/) | Supplied reversed-white iD vector. |
| YouTube | [YouTube's own site](https://about.youtube/) | Original monochrome icon path in white. |
| Steam | [Steam's own site](https://store.steampowered.com/) | Original circular symbol paths, inverse-white treatment. |
| Email | [Google Material Icons](https://github.com/google/material-design-icons/blob/49d4db35df873165d6bd6ba09b063c7dafbac2f4/src/communication/mail_outline/materialicons/24px.svg) | Original mail_outline geometry in the existing pale-blue icon color. |
| Research archive | [Zenodo artwork](https://about.zenodo.org/) | Supplied white Zenodo symbol, matching the linked archive. |

Open Robotics' organization artwork is attributed under CC BY-NC 4.0; the
included license and original source document accompany its two marks. RViz
dedicates its package graphics to the public domain. Google Material Icons and
MuJoCo include Apache 2.0 license copies; Newton documentation includes CC BY 4.0
attribution. Other brand conditions and source-specific terms are recorded in
the inventory. The trademarks belong to their respective owners. These links
identify projects and profile destinations and do not claim endorsement.

The palette adaptations are presentation choices for this profile, not new
official brand variants. Pixar retains its downloaded bitmap bytes inside the
SVG. RViz is losslessly decoded from the original native XCF lettering layer,
omitting the separate shadow layer. Its source layers can be exported with
`scripts/art/export_rviz_xcf.py`. No tracing, matting or generated pixels are
used in the published icons. Earlier splash-image and project-mark sources are
retained for provenance. The ROS Perception
vector can be reproduced with `scripts/art/extract_ros_brand_icons.py` from its
vendored editable source. `scripts/brand_icons.py` embeds each asset directly
inside its plaque, so GitHub needs no external icon service.

Run `python3 scripts/render_contacts.py` for contact buttons. The regular profile
refresh rebuilds the upstream plaques from the same local artwork. Hashed image
filenames ensure that GitHub's image cache receives the changed icons.
