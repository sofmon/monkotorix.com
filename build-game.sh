#!/bin/bash
# Rebuild one beta game into site/games/<slug>/.
#
#   ./build-game.sh neurocrew        # Monko Focus     <- ../neurocrew       (or $NEUROCREW_DIR)
#   ./build-game.sh lezen-met-olli   # Lezen met Olli  <- ../lezenmetollie   (or $LEZENMETOLLI_DIR)
#   ./build-game.sh all              # both
#
# Run this whenever a game changes and you want the website copy updated.
# Both games build with a RELATIVE base (vite.config.ts: base: './'), so they work
# under /games/<slug>/ as-is and need no path patching. The game checkout is copied
# to a temp dir and built there, so the game repos (their node_modules and dist/)
# are left untouched. The only things changed in the built game's index.html are the
# site's Content-Security-Policy, title, canonical URL, description and social-preview
# metadata, plus the name and description in the PWA manifest when the game has one.
#
# The game repos have no package-lock.json, so the first build records one in
# tools/locks/<slug>.package-lock.json and later builds install exactly those
# versions with `npm ci`. Delete a lockfile there to pick up newer dependencies, or when
# `npm ci` stops with "not in sync" because a game's package.json changed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
SITE="$ROOT/site"
ORIGIN="https://monkotorix.com"

# The site's own policy, adapted for the games (Monko Focus ships the same one in _headers).
CSP="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; manifest-src 'self'; media-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'"

# A subshell function, so the EXIT trap cleans the temp dir up on success and on failure.
build() (
  slug="$1" src="$2" page_title="$3" og_title="$4" og_desc="$5" og_image="$6"
  tmp="$(mktemp -d)"
  trap 'rm -rf "$tmp"' EXIT

  echo "Building $slug from $src"
  rsync -a --exclude node_modules --exclude dist --exclude .git --exclude 'tests/output' "$src/" "$tmp/src/"
  (
    cd "$tmp/src"
    lock="$ROOT/tools/locks/$slug.package-lock.json"
    if [ -f package-lock.json ]; then
      npm ci --no-audit --no-fund --loglevel=error
    elif [ -f "$lock" ]; then
      cp "$lock" package-lock.json
      npm ci --no-audit --no-fund --loglevel=error
    else
      echo "note: no lockfile for $slug yet; recording one in tools/locks/" >&2
      npm install --no-audit --no-fund --loglevel=error
      mkdir -p "$ROOT/tools/locks"
      cp package-lock.json "$lock"
    fi
    # The flags land on the `vite build` at the end of the package's build script.
    npm run build -- --outDir "$tmp/out" --emptyOutDir
  )

  # Hosting files for other platforms (Netlify, IIS, Azure, Apache) only apply at a
  # site root; under /games/<slug>/ they would just be served as public files.
  rm -f "$tmp/out/_headers" "$tmp/out/web.config" "$tmp/out/staticwebapp.config.json" "$tmp/out/.htaccess"

  python3 - "$tmp/out" "$page_title" "$ORIGIN/games/$slug/" "$og_title" "$og_desc" "$ORIGIN/assets/$og_image" "$CSP" <<'PY'
import html, json, os, re, sys
out, page_title, url, title, desc, image, csp = sys.argv[1:]
path = os.path.join(out, "index.html")
page = open(path, encoding="utf-8").read()
esc = lambda s: html.escape(s, quote=True)
# Injected right after <title>, which comes before the game's own script and stylesheet.
extra = f'''
    <meta http-equiv="Content-Security-Policy" content="{csp}" />
    <meta name="referrer" content="strict-origin-when-cross-origin" />
    <link rel="canonical" href="{url}" />
    <meta property="og:type" content="website" />
    <meta property="og:site_name" content="Monkotorix" />
    <meta property="og:title" content="{esc(title)}" />
    <meta property="og:description" content="{esc(desc)}" />
    <meta property="og:url" content="{url}" />
    <meta property="og:image" content="{image}" />
    <meta property="og:image:width" content="1200" />
    <meta property="og:image:height" content="630" />
    <meta name="twitter:card" content="summary_large_image" />'''
# The site sets the page title too, so search results and tabs use the site's wording.
page, n = re.subn(r"<title>[^<]*</title>", lambda m: f"<title>{esc(page_title)}</title>" + extra, page, count=1)
assert n == 1, "<title> not found in built index.html"
# The site's own wording describes what children do in the game, so it replaces the
# game's description too (search results show this one).
page, n = re.subn(r'<meta name="description" content="[^"]*"', f'<meta name="description" content="{esc(desc)}"', page, count=1)
assert n == 1, "meta description not found in built index.html"
open(path, "w", encoding="utf-8").write(page)

# The install prompt shows the manifest's name and description: keep them in line with the site.
manifest = os.path.join(out, "manifest.webmanifest")
if os.path.exists(manifest):
    m = json.load(open(manifest, encoding="utf-8"))
    m["name"] = page_title
    m["description"] = desc.split(" No accounts")[0]
    json.dump(m, open(manifest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
PY

  mkdir -p "$SITE/games"
  rm -rf "$SITE/games/$slug"
  mv "$tmp/out" "$SITE/games/$slug"
  echo "Updated $SITE/games/$slug"
)

build_neurocrew() {
  build neurocrew \
    "${NEUROCREW_DIR:-$ROOT/../neurocrew}" \
    "Monko Focus – Movement & puzzle games" \
    "Monko Focus (beta) — play in your browser" \
    "Playful movement and puzzle games for children aged 4 to 8, in English and Dutch. No accounts, no ads, no tracking. A Monkotorix beta." \
    "og-neurocrew.jpg"
}

build_lezen_met_olli() {
  build lezen-met-olli \
    "${LEZENMETOLLI_DIR:-$ROOT/../lezenmetollie}" \
    "Lezen met Olli" \
    "Lezen met Olli (bèta) — speel in je browser" \
    "Een vrolijk Nederlands spel met letters, klanken en woorden, met Olli de uil. Geen account, geen reclame, geen tracking. Een Monkotorix bèta." \
    "og-lezen-met-olli.jpg"
}

case "${1:-all}" in
  neurocrew) build_neurocrew ;;
  lezen-met-olli) build_lezen_met_olli ;;
  all) build_neurocrew; build_lezen_met_olli ;;
  *) echo "usage: $0 [neurocrew|lezen-met-olli|all]" >&2; exit 2 ;;
esac
