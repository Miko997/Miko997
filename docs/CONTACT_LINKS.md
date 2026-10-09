# Contact plaques

Edit `data/contact-links.json`, then run `python3 scripts/render_contacts.py` to rebuild the linked images and the `CONTACTS` block in the README. Assets use content-addressed filenames so GitHub's image cache cannot hide a design change.

The graphite and brass plaques keep their labels and icons still. A narrow violet/blue light follows a quiet 20-second cycle. Each plaque is an independent image: GitHub README images cannot receive a switch event from the header, share a guaranteed animation clock, or implement a custom click effect. Clicking a plaque opens its ordinary hyperlink. The header's lights, name and robot share one animation and are precisely synchronized.

Icons are embedded from `assets/brands/icons/` by `scripts/brand_icons.py`.
Official source artwork and any color adaptations are recorded in
`BRAND_ASSETS.md`. The generic email symbol comes from Google's Material Icons;
the Research archive button uses Zenodo's symbol, matching its destination.

A `picture` source selects a fully static SVG when reduced motion is requested. Each animated SVG also contains a reduced-motion rule as a second safeguard. Neither variant contains JavaScript, external assets or fonts. The public destinations and their evidence are recorded in `profile-link-sources.json`; the front page presents only the links.

Google Scholar is intentionally absent until an exact profile URL is supplied or independently verified.
