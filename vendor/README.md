# Frontend dependencies

The site serves Docsify 4.13.1 and Prism 1.30.0 from this directory. Both packages
use the MIT license; the original license notices are included beside their files.

`manifest.json` records the exact versioned download URL and SHA-256 for every
asset and license. The only upstream change is removing the Google Fonts import
from `vue.css`; its original SHA-256 is also recorded. The theme's existing system
font fallbacks are used. Docsify emoji aliases are disabled to avoid fetching
emoji images from GitHub; Unicode emoji in lesson text still render normally.

To update a dependency, download its files and license from the new exact version,
update the manifest hashes, and update the references in `index.html` and the
explicit publication list in `scripts/build_public_site.py`. Run the consolidated
checks and the browser check before publishing.
