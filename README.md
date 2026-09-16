# Enhance Listing — clickable prototype

Single-file HTML prototype of the 24.online "Enhance Listing" pipeline (Bosch kettle demo).
No backend, no build tooling beyond one Python script. Everything (images, CSS, JS) is inlined into one HTML file.

## What's in here

```
pipeline-prototype.html   ← built artifact. This is what gets deployed. Never edit by hand.
source/
  build4.py               ← the build script. Run this to regenerate the HTML.
  template4.html          ← main page: steps 1–6 skeleton, all shared CSS/JS (PX.* API), mobile rules
  gallery-slides-variations_19.html   ← step 5 block (USP brief + gallery generation), untouched original
  aplus-briefing_39.html              ← step 6 block (A+ sections brief), untouched original
  gpatch.py               ← string patches applied to the gallery block
  build2.py               ← loader: splits the two blocks into css/body/js, prefixes their ids (g_ / a_)
  *.jpg *.png             ← images that get base64-inlined (product photos, slides, A+ posters)
```

## Build

```
cd source
python3 build4.py        # needs Python 3 + Pillow (pip install pillow)
# → writes source/pipeline-prototype.html (≈5 MB)
```

Copy the result to wherever `pipeline-prototype.html` is served from. The file is self-contained: no external
requests except Google Fonts and Tabler Icons CDN.

## How the build works

`build4.py` does not use a framework. It is a sequence of literal string replacements:

1. `build2.py` reads the two block files, splits each into `css / body / js`, renames every `id` with a prefix
   (`g_` for gallery, `a_` for A+) so the two blocks can live on one page.
2. `gpatch.py` and the inline patches in `build4.py` rewrite specific snippets of the blocks'
   JS/CSS (e.g. add counters, locks, mobile rules). Every patch is guarded by an `assert` — if the
   original snippet changed, the build fails loudly instead of silently skipping.
3. Images are read with Pillow, resized, base64-encoded and injected via placeholders
   (`__MAIN__`, `__APIMG__`, `__APD__` …).
4. The blocks' css/body/js are inserted into `template4.html` at `/*GCSS*/`, `<!--GBODY-->`, `/*GJS*/`,
   `/*ACSS*/`, `<!--ABODY-->`, `/*AJS*/`.

Practical consequence: **if you change a snippet that a patch targets, the assert in `build4.py` or `gpatch.py`
will fail** — update the patch's search string alongside.

## Where things live

| Want to change… | Edit |
|---|---|
| Step order, headers, copy of steps 1–4, editor modal, upsell modal, top bar | `template4.html` |
| Mobile layout (≤ 640 px) | `template4.html`, block `@media (max-width:640px)` near the end of the CSS; plus `gcss+=` / `acss+=` blocks in `build4.py` |
| Gallery / USP brief behaviour | `gpatch.py` (structural) or `build4.py` `gjs=gjs.replace(...)` lines |
| A+ sections behaviour | `build4.py` `ajs=ajs.replace(...)` lines |
| Which images are used | `build4.py`, the `b64(Image.open(...))` lines |
| Narrator lines ("Now your brand style." etc.) | `template4.html`, `say('sN', [...])` calls in `run*` functions |

## Runtime model (what the JS does)

- Steps are `<section class="stp" id="s2…s7">`. Helpers in `template4.html`: `busy(n)`, `done(n)`, `finish(n, took, summaryHtml)`,
  `setCollapsed(el, bool)`, `alignTop(el)` (scrolls a section under the fixed top bar), `say(afterId, chunks)` (typewriter narrator).
- Transitions between steps always go: narrator text → collapse previous step → align next step under the top bar.
- `window.GAL` / `window.APL` are the small APIs the two blocks expose to the page (get/set/add/left/regen).
- **Monetisation rules** (all mock, state lives in memory):
  - Header pill = listings balance, hard-coded to 0, links to `https://24.online/topup`.
  - "Approve" on a brief locks the button and freezes the brief (`GAL.approved`, `window.APL_APPROVED`).
  - After approval each slide/module has 3 regenerations and 3 comments (`s.left`, `s.cmUsed`, `it.left`);
    main image has 3 variations (`V.makes`). Exhausted → `PX.upsell(kind)` → one modal, contextual copy,
    "Buy 10 listings" → `/topup`.
  - Add USP / Add Section / "New brief…" after approval → same upsell.
- Bottom bar buttons: **Finish** runs the whole pipeline at 30× speed (`fastMode()` monkey-patches `Date.now`,
  `performance.now`, timers). **Reset** = reload.

## Mobile (≤ 640 px) specifics

Fixed top bar and bottom bar; prompt inputs open as modals (`#vpmodal`); swipe-left to delete on cards/rows
(short swipe reveals Delete, long swipe deletes with Undo); coverflow swipes; all hover-only controls are visible by default.
Desktop behaviour is unchanged by these rules — they are all inside media queries or `matchMedia` checks.

## Known limitations

- Prototype only: no persistence, no network. Voice input uses the browser's Web Speech API (Chrome/Safari).
- `pipeline-prototype.html` is ~5 MB because of inlined images.
