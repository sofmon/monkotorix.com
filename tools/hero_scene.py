"""Generate the Monkotorix hero scene as an inline, CSS-themable SVG.

Every fill uses a class (styled from the page's CSS custom properties) so the same
markup renders as a morning cove (light) or the cove at night (dark).
"""
import math, sys

W, H = 1600, 900


def catmull(points, samples=24):
    """Sample a Catmull-Rom spline through points; returns list of (x, y)."""
    pts = [points[0]] + points + [points[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for s in range(samples):
            t = s / samples
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    out.append(points[-1])
    return out


def smooth_path(points, closed=False):
    """Catmull-Rom -> cubic bezier path data through the given points."""
    n = len(points)
    if closed:
        pts = [points[-1]] + points + [points[0], points[1]]
    else:
        pts = [points[0]] + points + [points[-1]]
    d = f"M{points[0][0]:.1f} {points[0][1]:.1f}"
    rng = range(1, n + 1) if closed else range(1, n)
    for i in rng:
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
    return d + (" Z" if closed else "")


def lengths(poly):
    acc = [0.0]
    for (x0, y0), (x1, y1) in zip(poly, poly[1:]):
        acc.append(acc[-1] + math.hypot(x1 - x0, y1 - y0))
    return acc


def at(poly, acc, f):
    target = f * acc[-1]
    for i in range(1, len(acc)):
        if acc[i] >= target:
            seg = acc[i] - acc[i - 1] or 1
            u = (target - acc[i - 1]) / seg
            (x0, y0), (x1, y1) = poly[i - 1], poly[i]
            return x0 + (x1 - x0) * u, y0 + (y1 - y0) * u, math.atan2(y1 - y0, x1 - x0)
    x, y = poly[-1]
    return x, y, 0


# Usage: hero_scene.py sky|land [bottom]. `bottom` (default 960) extends the foreground
# further down, for taller renders such as the Sofmon portfolio card.
B = int(sys.argv[2]) if len(sys.argv) > 2 else 960

# --- the winding path: bottom centre up to the cove shore -------------------
centre = [(830, 960), (600, 872), (985, 806), (690, 758), (905, 724), (790, 703)]
poly = catmull(centre, 40)
acc = lengths(poly)
# the drawn ribbon may start further down than the stops' path when the foreground is extended
draw = catmull([(900, B + 60)] + centre, 40) if B > 960 else poly
draw_acc = lengths(draw)
w0, w1, y_far, y_near = 120, 10, 703, 960  # ribbon width near and far (perspective by depth)


def width(y):
    return min(165.0, w1 + (w0 - w1) * max(0.0, (y - y_far) / (y_near - y_far)) ** 1.6)


left, right = [], []
for i, (x, y) in enumerate(draw):
    f = draw_acc[i] / draw_acc[-1]
    _, _, ang = at(draw, draw_acc, min(max(f, 0.0005), 0.9995))
    nx, ny = -math.sin(ang), math.cos(ang)
    hw = width(y) / 2
    left.append((x + nx * hw, y + ny * hw))
    right.append((x - nx * hw, y - ny * hw))
ribbon = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in left) + " L" + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(right)) + " Z"

# dotted centre line (dots shrink with distance)
dots = []
n_dots = 34
for k in range(n_dots):
    f = (k + 0.5) / n_dots
    x, y, _ = at(poly, acc, f)
    r = 1.2 + 5.2 * (1 - f) ** 1.5
    dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}"/>')

# six waypoints, one per development area, nearest = area 1
stops = []
fracs = [0.2, 0.37, 0.525, 0.665, 0.795, 0.905]
for i, f in enumerate(fracs):
    x, y, _ = at(poly, acc, f)
    r = 5 + 16 * (1 - f) ** 1.3
    stops.append(
        f'<g class="h-stop h-a{i + 1}" style="--i:{i}">'
        f'<circle class="h-stop-glow" cx="{x:.1f}" cy="{y - r * 0.15:.1f}" r="{r * 1.75:.1f}"/>'
        f'<ellipse class="h-stop-shadow" cx="{x:.1f}" cy="{y + r * 0.55:.1f}" rx="{r * 1.05:.1f}" ry="{r * 0.32:.1f}"/>'
        f'<circle class="h-stop-disc" cx="{x:.1f}" cy="{y - r * 0.15:.1f}" r="{r:.1f}" stroke-width="{max(1.2, r * 0.22):.1f}"/>'
        f'<circle class="h-stop-shine" cx="{x - r * 0.32:.1f}" cy="{y - r * 0.5:.1f}" r="{r * 0.24:.1f}"/>'
        f"</g>"
    )

# --- landscape --------------------------------------------------------------
# Nothing but sky and glow above y≈490: wide screens crop the top of the land art.
far_hills = smooth_path([(-40, 600), (90, 538), (250, 510), (420, 552), (560, 588), (700, 602), (960, 606), (1120, 580), (1260, 526), (1420, 492), (1560, 518), (1660, 560)])
far_hills += f" L1660 640 L-40 640 Z"

left_head = smooth_path([(-40, 520), (120, 528), (300, 560), (470, 606), (590, 664), (660, 726), (700, 800)]) + f" L700 {B} L-40 {B} Z"
right_head = smooth_path([(1660, 500), (1500, 514), (1330, 554), (1170, 600), (1040, 648), (960, 712), (930, 800)]) + f" L930 {B} L1660 {B} Z"

near = smooth_path([(-40, 770), (160, 742), (380, 736), (560, 718), (720, 700), (860, 696), (1010, 712), (1200, 738), (1400, 744), (1660, 724)]) + f" L1660 {B} L-40 {B} Z"
front_left = smooth_path([(-40, 830), (140, 808), (330, 822), (520, 868), (640, 940)]) + (f" L600 {B}" if B > 960 else "") + f" L-40 {B} Z"
front_right = smooth_path([(1660, 812), (1480, 800), (1290, 822), (1100, 872), (990, 940)]) + (f" L1040 {B}" if B > 960 else "") + f" L1660 {B} Z"

shore = smooth_path([(520, 716), (640, 700), (800, 693), (960, 698), (1070, 716), (960, 728), (800, 724), (640, 730)], closed=True)


def tree(x, y, s, cls="h-tree"):
    return (
        f'<g class="{cls}"><rect class="h-trunk" x="{x - 2.4 * s:.1f}" y="{y - 4 * s:.1f}" width="{4.8 * s:.1f}" height="{16 * s:.1f}" rx="{2 * s:.1f}"/>'
        f'<circle cx="{x:.1f}" cy="{y - 14 * s:.1f}" r="{13 * s:.1f}"/>'
        f'<circle cx="{x - 8 * s:.1f}" cy="{y - 7 * s:.1f}" r="{9 * s:.1f}"/>'
        f'<circle cx="{x + 8 * s:.1f}" cy="{y - 6 * s:.1f}" r="{9.5 * s:.1f}"/></g>'
    )


trees = "".join([
    tree(150, 540, 1.6), tree(205, 552, 1.15), tree(330, 578, 1.35), tree(56, 532, 1.0),
    tree(1370, 546, 1.5), tree(1450, 530, 1.1), tree(1520, 522, 1.35),
    tree(250, 812, 2.4, "h-tree h-tree-near"), tree(330, 826, 1.7, "h-tree h-tree-near"),
    tree(1380, 808, 2.2, "h-tree h-tree-near"),
])

# lighthouse on the right headland (a nod to the Stay Cove harbour and Monko Focus's Sunny beach)
lx, ly = 1205, 592
lighthouse = (
    f'<g class="h-lighthouse">'
    f'<circle class="h-beam" cx="{lx}" cy="{ly - 58}" r="40"/>'
    f'<path class="h-lh-body" d="M{lx - 13} {ly} L{lx - 8} {ly - 52} L{lx + 8} {ly - 52} L{lx + 13} {ly} Z"/>'
    f'<path class="h-lh-band" d="M{lx - 11.6} {ly - 16} L{lx - 10.4} {ly - 28} L{lx + 10.4} {ly - 28} L{lx + 11.6} {ly - 16} Z"/>'
    f'<path class="h-lh-band" d="M{lx - 9.4} {ly - 40} L{lx - 8.6} {ly - 48} L{lx + 8.6} {ly - 48} L{lx + 9.4} {ly - 40} Z"/>'
    f'<rect class="h-lh-lamp" x="{lx - 6}" y="{ly - 64}" width="12" height="12" rx="2"/>'
    f'<path class="h-lh-roof" d="M{lx - 9} {ly - 64} L{lx} {ly - 74} L{lx + 9} {ly - 64} Z"/>'
    f"</g>"
)


def cloud(x, y, s, cls="h-cloud"):
    return (
        f'<g class="{cls}"><ellipse cx="{x:.0f}" cy="{y:.0f}" rx="{70 * s:.0f}" ry="{18 * s:.0f}"/>'
        f'<circle cx="{x - 26 * s:.0f}" cy="{y - 12 * s:.0f}" r="{22 * s:.0f}"/>'
        f'<circle cx="{x + 8 * s:.0f}" cy="{y - 22 * s:.0f}" r="{28 * s:.0f}"/>'
        f'<circle cx="{x + 38 * s:.0f}" cy="{y - 8 * s:.0f}" r="{18 * s:.0f}"/></g>'
    )


clouds = cloud(240, 330, 1.25) + cloud(1340, 250, 1.0) + cloud(390, 470, 0.75, "h-cloud h-cloud-low") + cloud(1320, 440, 0.7, "h-cloud h-cloud-low")

# stars: deterministic scatter in the upper sky (only visible in dark mode)
stars = []
seed = 7
for k in range(70):
    seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    x = seed % W
    seed = (seed * 1103515245 + 12345) & 0x7FFFFFFF
    y = 105 + seed % 345  # below the top bar, where dots would sit on the nav labels
    r = 0.9 + (k % 4) * 0.45
    if 380 < x < 1220 and y > 90:
        continue  # keep the headline column clear: stray dots read like punctuation
    stars.append(f'<circle cx="{x}" cy="{y}" r="{r:.2f}"/>')
sparkle = lambda x, y, s: f'<path d="M{x} {y - 10 * s} L{x + 2.6 * s} {y - 2.6 * s} L{x + 10 * s} {y} L{x + 2.6 * s} {y + 2.6 * s} L{x} {y + 10 * s} L{x - 2.6 * s} {y + 2.6 * s} L{x - 10 * s} {y} L{x - 2.6 * s} {y - 2.6 * s} Z"/>'
sparkles = sparkle(1290, 400, 1.3) + sparkle(330, 225, 1.0) + sparkle(1480, 330, 0.8)

birds = (
    '<path d="M968 522 q10 -9 20 0 q10 -9 20 0"/>'
    '<path d="M1016 500 q7 -6 14 0 q7 -6 14 0"/>'
    '<path d="M700 508 q8 -7 16 0 q8 -7 16 0"/>'
)

sx, sy = 880, 566  # sun / moon, rising behind the cove
VY, VH = 440, (460 if B == 960 else B - 480)  # the landscape viewBox: y 440..900 by default

sky = f'''<svg class="hero-sky" viewBox="0 0 {W} {H}" preserveAspectRatio="xMidYMid slice" aria-hidden="true" focusable="false">
  <g class="h-stars">{"".join(stars)}</g>
  <g class="h-sparkles">{sparkles}</g>
  {clouds}
</svg>'''

land = f'''<svg class="hero-land" viewBox="0 {VY} {W} {VH}" preserveAspectRatio="xMidYMax slice" aria-hidden="true" focusable="false">
  <defs>
    <radialGradient id="h-glow" cx=".5" cy=".5" r=".5">
      <stop class="h-glow-0" offset="0"/><stop class="h-glow-1" offset=".72"/>
    </radialGradient>
    <linearGradient id="h-sea" x1="0" y1="0" x2="0" y2="1">
      <stop class="h-sea-0" offset="0"/><stop class="h-sea-1" offset="1"/>
    </linearGradient>
    <radialGradient id="h-beam-g" cx=".5" cy=".5" r=".5">
      <stop class="h-beam-0" offset="0"/><stop class="h-beam-1" offset="1"/>
    </radialGradient>
    <linearGradient id="h-path" x1="0" y1="0" x2="0" y2="1">
      <stop class="h-path-0" offset="0"/><stop class="h-path-1" offset="1"/>
    </linearGradient>
  </defs>
  <ellipse cx="{sx}" cy="{sy - 10}" rx="520" ry="{sy - 10 - VY}" fill="url(#h-glow)"/>
  <circle class="h-sun" cx="{sx}" cy="{sy}" r="74"/>
  <g class="h-birds">{birds}</g>
  <path class="h-far" d="{far_hills}"/>
  <rect y="548" width="{W}" height="{H - 548}" fill="url(#h-sea)"/>
  <g class="h-glint">
    <rect x="{sx - 90}" y="586" width="180" height="5" rx="2.5"/>
    <rect x="{sx - 60}" y="604" width="120" height="4" rx="2"/>
    <rect x="{sx - 110}" y="622" width="150" height="4" rx="2"/>
    <rect x="{sx - 30}" y="640" width="90" height="3" rx="1.5"/>
    <rect x="{sx - 70}" y="660" width="60" height="3" rx="1.5"/>
  </g>
  <path class="h-head h-head-l" d="{left_head}"/>
  <path class="h-head h-head-r" d="{right_head}"/>
  {lighthouse}
  <path class="h-sand" d="{shore}"/>
  <path class="h-near" d="{near}"/>
  <path class="h-front" d="{front_left}"/>
  <path class="h-front" d="{front_right}"/>
  {trees}
  <path class="h-path" d="{ribbon}" fill="url(#h-path)"/>
  <g class="h-dots">{"".join(dots)}</g>
  {"".join(stops)}
</svg>'''

which = sys.argv[1] if len(sys.argv) > 1 else "land"
sys.stdout.write(sky if which == "sky" else land)
