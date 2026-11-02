# monkotorix.com

The website for **Monkotorix**, small games for children, made by parents for their own
neurodivergent children and shared with other families. A Sofmon B.V. project, live at
https://monkotorix.com.

## Wording

Monkotorix is a small collection of games and playful activities, not a therapy, medical, diagnostic or
educational service. Copy describes **what the child does in a game** ("trace the trail",
"remember the sequence"), never what the game supposedly changes in the child ("improves
coordination", "trains working memory"). Avoid words like therapy, treatment, intervention,
clinical, develops, improves, boosts or teaches. The single site-level disclaimer lives in the
footer of `index.html` and `privacy/index.html`; don't repeat it elsewhere.

The one place that says *why* the games exist is the "Our goal" section. There, name the everyday
things the parents' own children found hard in plain words taken from the games ("waiting for the
green light", "switching when the rule changes"), never clinical terms ("impulse control",
"executive function"). The hope that practice helps is the parents' own belief ("we believe skills
like these grow with practice"), never a promised result.

Keep the voice modest: this is parents sharing what they made for their own children, not a
company or a platform. Write in British English ("colour", "favourite", "practise" as a verb) and
say "children", not "kids". Don't call the games free: the web versions may stay free, but
mobile versions may cost a small fee. The page has four sections — Our story, Our goal, The games and Why we
share it — and new copy should fit into those rather than add more.

It follows the same layout as `staycove.studio`: one self-contained page, the games
served from the same site under `/games/<game>/`, and zero third-party requests.

## Layout

| Path | What it is |
|---|---|
| `site/` | **The deployable web root.** Point your static host at this folder. |
| `site/index.html` | The one-page site. Self-contained (inline CSS), no build step. |
| `site/assets/site.js` | The only script: the light/dark theme switch (follows the system until a visitor picks a theme). |
| `site/assets/` | Self-hosted fonts (Fraunces, Inter), icons, game screenshots and social-preview images. |
| `site/games/neurocrew/` | **NeuroCrew** (beta), built from `../neurocrew`. |
| `site/games/lezen-met-olli/` | **Lezen met Olli** (beta), built from `../lezenmetollie`. |
| `site/privacy/` | Privacy notice for the website and both games. |
| `site/404.html`, `robots.txt`, `sitemap.xml`, `.nojekyll` | Hosting files. |
| `build-game.sh` | Rebuilds one or both games into `site/games/`. |
| `tools/locks/` | The exact dependency versions each game was built with (the game repos have no lockfile of their own). |
| `tools/hero_scene.py` | Draws the hero illustration (a cove at sunrise with a winding path of six coloured stops). |
| `tools/inject_hero.py` | Writes the hero illustration into `site/index.html` between its `hero-sky` / `hero-land` markers. |
| `brand/` | Brand assets that are not part of the site: the 512 px emblem and the 1536×1024 card image for the Sofmon portfolio. |

## Design

The site sits between its two siblings:

- **Light theme — "the cove by morning":** the Sofmon cove palette (cream, ink, sun, sea) and
  Sofmon's pill buttons and theme toggle.
- **Dark theme — "the cove at night":** Stay Cove Studio's ink and gold, its letter-spaced rule
  headings and game panels with a phone-framed screenshot.

All colours are CSS custom properties at the top of the `<style>` block in `index.html`; the six
accent colours (`--a1` … `--a6`) paint the stops on the hero path and the circles of the "Our goal"
diagram. Headings use Fraunces (soft) and body text uses Inter.

Calm by default: no autoplaying media, no looping animation (the hero path fades in once and stays
still), and `prefers-reduced-motion` turns off even that.

## Updating the games

```bash
./build-game.sh             # both games
./build-game.sh neurocrew
./build-game.sh lezen-met-olli
```

The script copies the sibling game checkout (or `$NEUROCREW_DIR` / `$LEZENMETOLLI_DIR`) to a temp
dir, installs and builds it there, removes hosting files that only apply at a site root, adds the
site's Content-Security-Policy, canonical URL and social-preview tags to the game's `index.html`,
and swaps the result into `site/games/<game>/`. The game repos themselves are not touched.

Dependencies are installed with `npm ci` from `tools/locks/<game>.package-lock.json`, so rebuilds
are reproducible. To pick up newer dependency versions, delete that lockfile and rebuild; a new one
is recorded. If a game’s `package.json` changes, `npm ci` stops with “not in sync”: delete
`tools/locks/<game>.package-lock.json` and rebuild to record a new one.

Both games build with a relative base (`base: './'`), so they work under `/games/<game>/` without
path patching. They share this origin's `localStorage` without clashing: NeuroCrew uses
`coordination-games:settings`, Lezen met Olli uses `lezen-met-olli`, and the site uses
`monkotorix-theme`. **Keep the game URLs stable** — progress is stored per address, so moving a
game resets children's progress.

## Updating the hero illustration

Edit `tools/hero_scene.py`, then:

```bash
python3 tools/inject_hero.py
```

The scene is two inline SVGs (`hero-sky` for clouds and stars, `hero-land` for the landscape)
whose colours come from the page's CSS variables, so the same drawing renders in both themes.

## Content security

`index.html` and `privacy/index.html` carry a Content-Security-Policy `<meta>` tag that only
allows the site's own files (`default-src 'self'`). Inline `<style>` and `style=""` attributes are
allowed; inline `<script>` is **not** — put any new script in `site/assets/`.

## Sofmon portfolio card

`brand/sofmon-card-monkotorix.jpg` (1536×1024) is framed for the 200 px-tall `.gallery-card-image`
on sofmon.com: the path and all six stops stay visible at phone, two-column and tablet widths.
Copy it to `docs/monkotorix.jpg` in the www.sofmon.com repo and add a card next to Stay Cove
Studio and FarCast:

```html
<div class="gallery-card">
  <div class="gallery-card-image" style="background: url('monkotorix.jpg') center / cover, linear-gradient(135deg, var(--sf-cove-ink-700), var(--sf-cove-sea-500));"></div>
  <div class="gallery-card-body">
    <h3>Monkotorix</h3>
    <p>Small games made by parents for their own neurodivergent children.</p>
    <div class="tag-list">
      <span class="tag">Children’s games</span>
      <span class="tag">Neurodiversity</span>
      <a href="https://monkotorix.com" class="tag tag-link" target="_blank" rel="noopener noreferrer"
        aria-label="monkotorix.com (opens in a new tab)">monkotorix.com<svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M7 17 17 7" /><path d="M8 7h9v9" /></svg></a>
    </div>
  </div>
</div>
```

With three cards, Sofmon's two-column `.gallery-grid` leaves the third on its own row; consider
`grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));` there.

## Deploying

Like Stay Cove Studio, the site deploys to **GitHub Pages**: every push to `main` runs
[.github/workflows/pages.yml](.github/workflows/pages.yml), which publishes the `site/` folder.
The custom domain `monkotorix.com` is set in the repo's **Settings → Pages** (HTTPS enforced);
DNS at the registrar points the apex at GitHub Pages' A addresses
(`185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`) and `www` at
`sofmon.github.io` with a CNAME, so `www.monkotorix.com` redirects to `monkotorix.com`.

The site expects to be served from the **domain root** (paths are `/assets/...`, `/games/...`).

The privacy notice (`site/privacy/index.html`) names GitHub Pages as the host. If the site moves
to another host, update that paragraph.

## Local preview

```bash
python3 -m http.server 4174 --directory site
```

Then open http://localhost:4174.
