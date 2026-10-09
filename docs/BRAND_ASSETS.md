# Button artwork sources

The buttons retain their original frames, labels, destinations and motion.
Their symbols now use the source artwork below, with its original proportions.
The complete source inventory, licenses, adaptations and checksums are in
[`brand-sources.json`](brand-sources.json). Original downloads are retained in
`assets/brands/originals/`; self-contained presentation SVGs are in
`assets/brands/icons/`.

| Button | Official source | Presentation |
| --- | --- | --- |
| Newton Physics | [Newton documentation artwork](https://github.com/newton-physics/newton/blob/c361452db95979eac77679bc49ef3c6b7c6dd9c4/docs/_static/newton-logo-dark.png) | Original PNG and alpha silhouette; lavender SVG paint filter. |
| MuJoCo | [MuJoCo banner](https://github.com/google-deepmind/mujoco/blob/0998957cf026b78f35e3a1eebd2cd3312d810b08/doc/images/banner.svg) | Complete original vector wordmark in lavender. |
| OpenUSD | [OpenUSD symbol](https://openusd.org/images/USDLogoUnsized.svg) | All four original paths in lavender. |
| ROS 2 | [Open Robotics artwork](https://github.com/openrobotics/artwork/blob/4024191d62211c4d4fa024e9974dd372d92aa23a/orgunits/ros.svg) | Official white nine-dot mark; ROS 2 is identified by the existing label. |
| RViz | [RViz project logo](https://github.com/ros2/rviz/blob/0d5c197fabebb0fe25ad4ca1076e28a7be967b5c/rviz_common/images/splash.png) | Original PNG, with a cool monochrome SVG paint filter. |
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
official brand variants. Newton and RViz retain the downloaded bitmap bytes
inside the SVG; no tracing or generative redraw is involved. The ROS Perception
vector can be reproduced with `scripts/art/extract_ros_brand_icons.py` from its
vendored editable source. `scripts/brand_icons.py` embeds each asset directly
inside its plaque, so GitHub needs no external icon service.

Run `python3 scripts/render_contacts.py` for contact buttons. The regular profile
refresh rebuilds the upstream plaques from the same local artwork. Hashed image
filenames ensure that GitHub's image cache receives the changed icons.
