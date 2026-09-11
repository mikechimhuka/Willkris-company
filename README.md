# Wilkris Company design review

This is a design-only modernization of http://www.wilkris.com/main.htm.
The original live website has not been modified. The hosted Sites preview is private.

## Files

- `dist/`: complete, directly editable static website, including local fonts, original photographs, software screenshots, and demonstrations.
- `source-original/`: original pages downloaded from Wilkris, with an extracted content inventory for comparison.
- `scripts/build.py`: creates the redesigned HTML from the original content; shared templates and layout are here.
- `dist/assets/site.css`: shared visual styling and responsive layouts.
- `dist/assets/site.js`: mobile navigation and on-demand demonstration playback.
- `scripts/validate.py`: checks original wording, routes, local references, and document semantics.

Serve `dist/` with any static web server. To regenerate HTML, install `requirements.txt` in a Python virtual environment and run `python scripts/build.py`, followed by `python scripts/validate.py`. No JavaScript build or package installation is required to serve the site.

## Content and compatibility

All 24 original linked HTML addresses are preserved, including seven product detail pages, four FAQ categories, four fluid-filling guides, and four demonstration pages. The root homepage and the earlier design's main route aliases are also provided.

Original wording and specifications are intentionally retained, including historical dates, typographical errors, dated product statements, and differing technical ranges on different pages. These have not been independently updated or reconciled because the requested scope is design only.

All referenced original media were recovered. Product photographs are low-resolution source images and have not been replaced with generated illustrations. Original BMP software screenshots are available through the image links.

Four original SWF demonstrations are preserved and load on demand using the self-hosted Ruffle 0.6.0 player. The original files remain downloadable. Flash instruction text is retained under “Original playback instructions.” The underlying legacy demonstrations retain their original small controls, text, and accessibility limitations; the surrounding website uses accessible HTML. Startup/rendering was verified for all four demonstrations, but exhaustive testing of every legacy simulation state was not performed.

## Review performed

- Original text compared with rendered HTML; local page, image, and download references checked.
- Desktop homepage/catalog visually reviewed; mobile specification table visually reviewed.
- All 20 non-demo original pages checked at 390px width for horizontal overflow and loaded-image failures.
- Mobile menu open/close, Escape focus return, and FAQ keyboard toggling checked.
- Four original demonstrations rendered in the browser.
- No contact form or new server-side feature was added. Email and phone links use the original contact details.

Font sources: Google Fonts DM Sans and Manrope. Ruffle source: https://github.com/ruffle-rs/ruffle; bundled licenses are retained in `dist/assets/ruffle/`.
