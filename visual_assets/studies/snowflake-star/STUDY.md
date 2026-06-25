# Snowflake-star study — a symbolic secondary mark from the leaf's "shadow"

Exploration, 2026-06-19. **Status: discussion drafts, nothing adopted.** Output of
the prompt "use the *shadow* of `leaf-botanical-cells` as the basis for a star with
snowflake characteristics, with a symbolic point count."

This is **not** a proposal to replace the leaf or the seal. The botanical sugar-maple
leaf is the identity and the seal is the tiny mark (DESIGN-CRITERIA.md, Addendum 2);
both are settled. This study asks a narrower question: *is there a second, civic
geometric mark hiding inside the leaf we already drew* — one that could serve as an
alternate seal, a section/area glyph, a loading/footer device, or social/merch art,
the way `mark-northstar` already does.

---

## 1. The "shadow" — where this comes from

`leaf-botanical-cells.svg` is built two ways at once:

- **the fill** = six colour wedges meeting at the visual centre `C = (50, 44)`;
- **the shadow** = six off-white **rays** that radiate from `C` and thread out
  through the lobes (`stroke #F7F4EE`, the lines that divide the wedges).

Those rays are the bones of the leaf. The `cells-lines` study (`studies/cells-lines/`)
already isolated them — strip the colour and the maple silhouette and you are left with
a **radial ray-burst from a single centre**. That burst is one short step from two
civic geometries Canada already owns:

1. a **star** — rays from a centre, the navigational/observatory idea ("CanObs" =
   *observatory*; the footer already carries `mark-northstar`); and
2. a **snowflake** — rays from a centre that *branch* (dendrites), the most Canadian
   crystal there is, and the "every one unique" metaphor for a country of distinct
   members.

So the move is: **take the leaf's ray-burst → generalize the ray count → let each ray
branch like frost.** The star is the leaf's skeleton; the snowflake is that skeleton
told it's winter.

---

## 2. Why a star/snowflake fits CanObs (and where it must stay subordinate)

**Fits:**

- *Observatory.* The name is about watching, orienting, returning to a fixed point.
  A star — specifically a polestar — is the on-brand metaphor, and we already use one.
- *Canada-recognition without the maple cliché.* A snowflake reads "Canada / North /
  winter" instantly and sits **far from Government-of-Canada visual territory** (no
  FIP, no flag-leaf RCAF-roundel problem — criterion 9). It is arguably *more*
  ownable than another leaf.
- *Federation symbolism.* A radial mark has a natural, honest place to encode the
  members of the federation: one arm each. The leaf can't do this; a star can.
- *System fit.* It is line-drawn from a centre — the exact construction language of
  the seal's line-leaf and the outline family. It composes with what exists.

**Must stay subordinate:**

- The leaf is the identifier. A star cannot become *the* mark — at 16–24px a
  many-armed star degrades to a generic sunburst (see §6), the same failure that
  demoted the botanical leaf and produced the seal. Any star here is a **secondary
  motif** (like the north star), not a logo replacement.
- One nation, one primary mark. Two competing identifiers dilute (the lesson that
  retired the classic leaf). This must read as *family*, not as a rival.

---

## 3. The symbolic point count — and the honest tension

The brief's reason to exist is the **count**. Options on the table:

| Points | Reading | Notes |
|---|---|---|
| **10** | the ten **provinces** | Clean, but silently drops the three territories and ~120k northerners — politically awkward for a national-data site. |
| **11** | **Canada + 10 provinces**, *or* provinces + "the territories" as one idea | Two good narratives. The strongest: a **polestar nucleus = Canada** with **10 province arms** around it (see `star11-canada-seal`). |
| **13** | **10 provinces + 3 territories** | The complete, defensible federation count. The "ideal but difficult" — see below. |

**The deliberate tension (worth stating to the owner up front):** a *real* snowflake is
**six-fold** (hexagonal ice). 10, 11, 13 are **not** multiples of six, so a literal
snowflake cannot carry these counts. We have three honest responses, and the study
shows all three:

1. **Own the break.** Use an N-pointed *star with frost detailing* and let the meaning
   justify the non-crystalline symmetry. (The dendrite seals do this.) Most truthful to
   the count; least truthful to crystallography.
2. **Compass/observatory star**, where N points are expected and carry no ice claim
   (a compass rose can have any number of points). Cleanest small-size behaviour.
3. **Stay six-fold and encode the count elsewhere** — e.g. a true hexagonal snowflake
   whose *tips* or *branch nodes* are counted, or 13 cells in the centre. (Not drawn
   here; flagged as a path if the owner wants crystallographic honesty over arm-count
   legibility.)

**13 is "difficult" for three concrete reasons:** (a) it fights six-fold ice hardest;
(b) thirteen arms in a ~40px-radius disc start to merge into a sunburst; and (c) "13"
has unlucky connotations in some audiences — a national mark probably shouldn't make a
viewer count to thirteen and pause. **11 (polestar + provinces) is the most defensible
single recommendation**; 13 is the most *complete*; 10 is the most legible but the least
inclusive.

---

## 4. Design elements & motifs

- **Construction:** every arm radiates from centre `C`; arms are evenly spaced
  `360/N`, **top arm first** (12 o'clock anchor, like the seal's leaf and the
  compass). Mirrors the cells leaf's centre-out geometry exactly.
- **Snowflake dendrite:** each arm = a central spine + **paired side-spurs at 60°**
  (the hexagonal ice angle — so even a non-six-fold star keeps real frost grammar in
  its *branches*) + a small terminal fork. Round line caps, off-white stroke.
- **Two registers, mirroring the existing system:**
  - **Seal register** — off-white lines on a Deep Maroon disc (`#7A263A`), identical
    construction to `monogram.svg`. The disc gives the solid mass tiny sizes need.
  - **Display register** — Deep Navy lines on Warm Off-White, like the outline family;
    for ≥~96px art only.
- **Palette:** strictly the locked 8-colour set. Off-white `#F7F4EE`, maroon
  `#7A263A`, navy `#17324D`; the Wheat ring `#D9B36C` on the compass variant; the
  cells-hybrid distributes the six area colours across the arms (direct leaf lineage).
- **The polestar nucleus** (`star11-canada-seal`) literally re-uses the
  `mark-northstar` four-point star at the centre — Canada as the fixed point the
  provinces orbit. This is the cleanest bridge to what's already on the site.
- **Distinguishing special members** (the 13 = 10+3 case): in `star13-dendrite-seal`
  the **three northern arms** (top of the disc) are drawn **shorter and simpler**
  (no second spur pair) — territories read as a subtle *crown* of younger/smaller
  members rather than as twelve identical points plus one. Open question whether this
  reads as intentional or as lopsided (see §7).

---

## 5. The variants (see `board.svg.png`)

| File | Count · reading | Register | Role it would audition for |
|---|---|---|---|
| `star13-dendrite-seal.svg` | 13 = provinces + **3 short** territory arms | maroon seal | the "complete federation" seal |
| `star11-canada-seal.svg` | 11 = **polestar Canada** + 10 provinces | maroon seal | **lead candidate** — ties to north star |
| `star10-dendrite-seal.svg` | 10 = provinces | maroon seal | cleanest snowflake, least inclusive |
| `star13-compass-seal.svg` | 13, compass points | maroon seal | small-size survivor (filled, not line) |
| `star11-compass.svg` | 11, compass + Wheat ring | navy on light | observatory/compass reading |
| `star13-dendrite-navy.svg` | 13 uniform (equal members) | navy line on light | display art, banners, About page |
| `star13-cells.svg` | 13 rays in the six area colours | colour on light | explicit leaf-lineage / data-variety |

`board.svg` renders each at 120px on light **and** on navy, plus 40px and 24px, so the
scale behaviour is visible at a glance. Regenerate with `python3 _gen.py && python3
_board.py && qlmanage -t -s 1100 -o . board.svg`.

---

## 6. Scale behaviour (the decisive constraint)

On the board, the **line dendrites collapse to a fuzzy disc by ~24px** — exactly the
botanical-leaf failure that produced the seal. This means:

- A line snowflake-star can be a **display/secondary motif** (footer, section glyph,
  hero, social art) but **cannot be the favicon/navbar mark**.
- The **compass/filled variants** (`*-compass*`) hold their shape down to ~20px because
  they are solid mass, not stroke — these are the only candidates if a *tiny* star is
  ever wanted. They trade snowflake delicacy for a harder, sun/compass read.

This is the same display-vs-tiny split the brand already lives by; nothing here escapes
it. A snowflake-star earns its place as a **second motif beside the north star**, not as
a new logo.

---

## 7. Open questions for discussion

1. **Which count carries it?** Recommendation: **11 = polestar + provinces**
   (`star11-canada-seal`) — inclusive-enough, on-brand (observatory polestar), avoids
   the "13" pause. 13 if completeness must win over legibility.
2. **Snowflake honesty vs arm-count:** accept the non-six-fold break (own it), or keep
   true hexagonal ice and count the *nodes* instead?
3. **Does the 3-short-arm "territory crown" read as intentional** or just lopsided? If
   the latter, fall back to a uniform 13 (the navy variant) and carry the 10+3 meaning
   in the caption only.
4. **What job is this for?** Alternate seal? A per-section glyph? Footer companion to
   the north star? Merch/social only? The job decides the register and the size floor.
5. **Relationship to `mark-northstar`:** is this a *replacement* for the footer star (a
   richer, more meaningful version) or an *addition*? Two stars may be one too many.
6. **Does it dilute the leaf?** Honest check against the "two competing marks" lesson —
   acceptable only if it stays clearly secondary and clearly *family*.

If any direction has legs, the next step is a focused round on that single count + the
true-pixel board the seal got (`studies/tiny-mark/`), before anything touches the kit.

---

## 8. Iteration 2 — compass-star family (owner direction 2026-06-19)

**Verdict on iteration 1:** the **dendrite/snowflake construction is dropped** — too
simple and cluttered, and it read as a **sun**, not a snowflake. Kept: the two compass
forms (`star13-compass-seal`, `star11-compass`) and the **cells-colour hybrid** idea.

**The fix that worked: alternating point lengths.** Giving the points alternating
**long / short** radii (short ≈ 35–50% of long) + a tighter centre breaks the
even-spike sunburst and snaps the read to a **compass rose / observatory star**. Adding
faint radial **facet lines** centre→tip (literally the leaf's "shadow" rays) reinforces
the compass reading. Builder: `_gen2.py`; boards `board2.svg.png` (first pass) and
`board2b.svg.png` (sharper alternation that de-suns the 13s).

**What reads best now:**

| File | Why |
|---|---|
| `c13-sharp-cells.svg` | the **cells-colour compass rose** — reads like a painted navigational rose, carries the leaf palette/lineage; best large/colour piece |
| `c11-alt-obs.svg` · `c11-sharp-seal.svg` | cleanest **11-point** compass — fewest points, sharpest star read, holds smallest |
| `c13-sharp-obs.svg` · `c13-sharp-seal.svg` | the **13** now reads as a compass star, not a sun (vs the soft iteration-2a versions) |
| `c13-territories-sharp.svg` | 10 long province points + **3 short territory points** at the top — now reads as an intentional northern crown, not lopsided |

**Recipe that works:** `long ≈ 46–47`, `short ≈ 17–19` (sharp) or `24–26` (soft),
inner valley radius `rin ≈ 10–12`. Lower `rin` + bigger long/short gap = sharper, more
compass, less sun. More points (13 > 11 > 10) = busier, so 13 needs the sharpest
alternation; **10–11 are the most legible** and the strongest if count-completeness can
yield to clarity.

**Open for next round:** pick ONE count to carry it (11 still the safest, 13 the most
complete and now viable when sharp); decide colour vs seal as the lead; then a true-pixel
small-size board before anything is proposed for the kit.

---

## 9. Iteration 3 — the leaf actually *becoming* the star (owner direction 2026-06-19)

Owner picked `c13-sharp-obs`, `c13-sharp-cells`, `c11-alt-obs` as the best — but raised
the real question: **none of those use the shadow/skeleton lines as actual structure;
can one logo (the existing leaf-cells) fade naturally into the star, so the connection
is *felt*?**

**The structural fact that makes this possible:** `leaf-botanical-cells` is not a leaf
*with* a star inside it — it **is** a six-ray radial burst from centre `C=(50,44)`
**clipped to a leaf silhouette**. Six colour wedges, six off-white dividing rays (the
"shadow"). **Drop the clip and the leaf is already a six-point cells star.** So the leaf
can dissolve into the star with no sleight of hand — same rays, same six colours, same
centre. The star's facet lines *are* the leaf's skeleton.

Two morph filmstrips demonstrate it (`_gen3.py`):

- **`morph-cells.svg`** — leaf → rays break out → **un-clipped to the colour wheel** →
  pulled into a regular **6-point cells star** → resampled to 13. The six colours carry
  through the entire sequence; this is the version where the connection is most *felt*.
- **`morph-obs.svg`** (on navy) — leaf → **the skeleton rays alone** → 6-ray line star →
  resampled to 13. Here the leaf's off-white skeleton literally becomes the star's
  facet lines.

**The discovery — `skel-star6-cells.svg`:** the regular **6-point cells star** is the
leaf released and tidied. It is the strongest mark in the whole study: an exact,
demonstrable derivation from the existing logo, it keeps the six brand colours, and it
holds them down to ~24px. `skel-star6-navy.svg` is its minimal sibling (off-white 6-ray
star on a maroon/navy disc — same construction as the seal).

**The count tension, sharpened.** The leaf's true ray count is **6**, and six already
*means something* on this site: the **six thematic areas** (and their six locked
colours). So:

- **6-point** = perfect leaf derivation **+ the six-areas symbolism the brand already
  owns**. No resampling, no broken six-fold. The honest answer to "felt connection."
- **10 / 11 / 13** = the federation symbolism, but each is a **resample away from the
  leaf's real six** — the connection is narrated, not structural.

That is the genuine fork for discussion: **a star that is structurally the leaf and
means "the six areas" (6-point), vs a star that means "the federation" but is a
looser relative of the leaf (10/11/13).** The morphs let us show either: the 6-point as
the true terminus, or the 6→13 resample as an explicit, visible step.

**Keepers from this round** (`board3.svg.png`): `skel-star6-cells`, `skel-star6-navy`,
`morph-star13-cells-facets`, `morph-star13-obs-facets`. **Recommendation:** lead with
the **6-point cells star** (structure + six-areas meaning), and keep the **13 observatory
+ facets** as the federation-count variant if that symbolism is wanted. Next steps if a
direction lands: turn the morph into an actual animation (SMIL/CSS) so the fade plays on
the landing/About page, and run a true-pixel small-size board.

---

## 10. Iteration 4 — the 12-point star locked to the six rays (owner direction 2026-06-19)

Owner's construction: **the six leaf rays as the exact angular positions of six
SHORT points, with a LONGER point bisecting each gap → a 12-point star.** Built in
`_gen4.py`. Because the leaf is an irregular hexagon (its six rays sit at ≈30°, 78°,
138°, 221°, 282°, 331° — gaps of 48–83°, *not* even 60°), the resulting 12-point star
is **subtly irregular**: it carries the leaf's true geometry rather than a mechanical
clock-face. `star12-proof.svg` overlays the star on the faded leaf with the six rays
drawn dashed and the six short tips dotted — they land exactly on the rays.

**This is the cleanest structural answer yet.** The short points *are* the leaf's
skeleton (no resampling, no narration); the long points are the new star growing
between them. And **12 carries its own honest meanings** — a 12-point compass rose, the
twelve hours/months (an *observatory*/time resonance) — without having to claim a
federation count it doesn't fit. Counts to keep in the conversation:
6 (areas) · 12 (this) · 13 (federation, resampled).

**Variants & verdict** (`board4.svg.png`, `_zoom*` comparisons):

| File | Read |
|---|---|
| `star12-obs-sharp.svg` · `star12-obs.svg` | navy fill + Wheat ring — clean compass/observatory; **lead** |
| `star12-seal.svg` · `star12-seal-sharp.svg` | off-white on maroon disc — the seal register |
| `star12-cells-v3.svg` (navy long points) | **best colour version** — navy gives structure, the six leaf colours read as the short points |
| `star12-cells.svg` (wheat long) | warm, but the gold long points overpower the coloured leaf-ray points |
| `star12-cells-v2.svg` (off-white long) | **fails** — off-white long points vanish into the off-white disc; only the six colour points show (would need a navy/maroon ground) |

**Recommendation after iteration 4:** the **12-point observatory** (`star12-obs-sharp`)
and its **seal** sibling are the strongest single mark — they use the leaf's rays as
real structure, read unmistakably as a compass/observatory star, sit in the existing
seal/disc register, and dodge the federation-count and broken-six-fold problems. Carry
**`star12-cells-v3`** as the expressive colour lockup and **`star12-proof`** as the
"here's why it's the leaf" explainer. The 6-point (§9) remains the alternative if the
six-areas meaning is preferred over a fuller compass.

> **Directory cleaned 2026-06-19.** Iterations 1–4 moved to `_archive/` (see its
> README). Active root = `_gen5.py`, the `star12-*` colour/outline set, `board5.svg`,
> and `star12-proof.svg/.png`.

---

## 11. Iteration 5 — colour approaches + outline family (owner direction 2026-06-19)

Owner: the **12-point cells is the best**; open question is **how to handle the
colour**. Also: build an **outline version** (like the leaf's outline family), and
**remove the central hub** in all of them — the little pivot dot made it read as a
literal compass; we want the star / snowflake / compass influences *balanced*, not the
compass dominant. Done (`_gen5.py`, `board5.svg`). Hub removed everywhere — the points
now converge to a clean centre.

**Structural note that sets the colour logic:** the six LONG points bisect the gaps
between rays — i.e. they point through the **centres of the leaf's six colour wedges**.
So the leaf-faithful map is **long points = the six area colours; short points (on the
ray boundaries) = the off-white skeleton.** That is literally the leaf's own colour
system, released into a star.

**Four approaches (`board5.svg.png`):**

- **A · leaf-faithful** — long = the six area colours, short = off-white, with thin
  off-white **skeleton separators** (so every colour reads even where a wedge colour
  matches the ground). `star12-leaf-navy` / `-seal` / `-light`.
- **B · two-tone** — larger vs smaller, one colour each. `star12-duo-*`.
- **C · mono / solid** — one colour. `star12-solid-*`.
- **D · outline** — stroke silhouette like the leaf outline; plus a per-point coloured
  **outline-cells**. `star12-outline-navy` / `-maroon` / `-cells`.

**Owner reactions (2026-06-19):**

- **`star12-leaf-navy` — favourite.** The white inner six points read as the snowflake
  motif; the navy-on-navy long point is the one challenge, and the off-white skeleton
  outline is the right fix (kept).
- **`star12-leaf-light` — liked, but rebalanced.** Navy was repeating (one long point
  *and* all the short points) → unbalanced. **Fixed:** short points are now off-white
  outlined slate (the snowflake points, readable on light), so **navy appears only once**
  (its single long point).
- **Two-tone:** `duo-maroon-navy` feels **aggressive**; **`duo-navy-gold` is softer** →
  the preferred two-tone.
- **Outline + solid:** liked as-is.

**Working lead:** `star12-leaf-navy` as the expressive/colour mark (snowflake-forward),
with `star12-leaf-seal` for the maroon register, `duo-navy-gold` as the simpler two-tone,
the `outline-*` set for the display/line register, and `solid-*` for one-colour use.
`star12-proof.svg/.png` is the explainer.

**Intended use — an About page.** Owner idea: a new **About → "Our marks"** page that
explains the leaf and how this star grows out of it, with `star12-proof` as the hook.
Logged as the planned home for this work. *Not wired into the live site yet* — the mark
isn't adopted, and the navbar still carries no mark, so a public "our logo" page would
be premature. Ready to draft the page (and/or animate the leaf→star morph for it) on the
owner's go.

---

## 12. Iteration 6 — the FULL outline of the twelve spikes (owner direction 2026-06-25)

The iter-5 outline family only traced the **outer edge** (`outline-navy/-maroon` = one
zig-zag silhouette; `outline-cells` = twelve *open* chevrons). The missing register: each
of the twelve spikes drawn as its **own complete outlined cell**, so the internal
structure — the leaf's skeleton — reads as line art (the same step that turns the leaf's
filled cells into the leaf outline). Built in `_gen6.py` (same TIPS/geometry as `_gen5`),
two centre treatments, `board6.svg.png`:

| set | centre | verdict |
|---|---|---|
| **`star12-fulloutline-{navy,maroon,seal}`** + **`-cells`** / **`-cells-navy`** | spikes converge to the centre | **the deliverable** — matches the iter-5 "no hub, points converge to a clean centre" direction |
| `star12-ringoutline-{navy,cells,cells-navy}` | open inner 12-gon (hub ring) | **not recommended** — reintroduces a central ring, the very hub removed in iter-5 |

**Reads best:** `star12-fulloutline-navy` (clean line snowflake-star) and
`star12-fulloutline-seal` (white-on-maroon — survives smallest because the disc carries
the mass). Same size floor as all the line work: legible as a display/secondary mark,
collapses by ~20px (use a disc/solid register if a tiny version is ever needed).

### Iteration 7 — refined after owner review (2026-06-25)

Owner flagged three problems with the iter-6 full outline. All fixed in `_gen7.py`
(`board7.svg.png`):

1. **Too thick** → stroke **2.2 → 1.5** (board shows 1.2 / 1.5 / 1.8; weight is one
   constant — owner's final pick: 1.2 is the most delicate snowflake, 1.5 holds better at
   medium sizes).
2. **Inconsistent colours where inner/outer lines connect** → iter-6 stroked each spike as
   a *closed* kite, so the shared valley→centre spokes were drawn **twice in two colours**
   (arbitrary last-wins). Now drawn in two clean passes: the inner **skeleton once in a
   single neutral** (faint grey), then the 12 point **chevrons each in one colour** — every
   line has exactly one defined colour.
3. **A spike vanishing into a same-colour ground** (navy point on navy) → the colour
   (`cells`) version moved off navy onto **off-white**: neutral = slate, gold → **deep
   ochre** so the warm point holds a thin stroke on light. `star12-fulloutline-cells-navy`
   retired to `_archive/`.

**Canonical refined set:** `star12-fulloutline-{navy, maroon, seal, cells}`.

### Iteration 8 — cells outline: inner vs outer colour priority (owner 2026-06-25)

iter-7 faded the inner skeleton grey; the owner read the faded inner lines (overlapping
toward the centre) as **awkward/unintentional**. Fixed by giving the inner spokes a
**definite** colour by priority instead of a fade (`_gen8.py`, `board8.svg.png`). Long and
short points strictly alternate, so each valley spoke borders exactly one of each:

- **`star12-fulloutline-cells-outer`** — the spoke takes its LONG point's area colour → the
  six area colours read as full **wedges to the centre** (bold, colour-forward, compass-rose).
- **`star12-fulloutline-cells-inner`** — the spoke takes its SHORT point's colour (slate) → a
  clean **slate snowflake** inside, colour only on the outer tips (calm, colour as accent).

Both read intentionally (no fade). Lean: **outer** for the expressive colour mark (the six
area colours genuinely carry it / strongest leaf lineage), **inner** if the calmer snowflake
is preferred. Owner's pick → becomes the canonical `star12-fulloutline-cells`; the faded
iter-7 `-cells` is superseded.

### Iteration 9 — the mono full outline in every brand colour (owner 2026-06-25)

"All the choices on hand": the single-colour full outline in each locked palette colour
(`_gen9.py`, `board9.svg.png`), in the brand's usual two registers:

- **Light register** (transparent — lines only, drop on any light page): `navy`, `maroon`,
  `lake`, `boreal`, `slate`, **`ochre`** (deep ochre = the light-safe gold; Prairie Gold is
  too low-contrast as a thin stroke on off-white), `linkblue`.
- **On a disc** (the light inks vanish on off-white): `offwhite-on-navy`, `wheat-on-navy`,
  `gold-on-navy` (Prairie Gold pops on navy), and the maroon **`seal`** (off-white on maroon).

Files: `star12-fulloutline-{navy,maroon,lake,boreal,slate,ochre,linkblue}` +
`-{offwhite,wheat,gold}-on-navy` + `-seal`. Border Grey omitted (a UI/border utility colour,
not a mark colour). Weight 1.5 throughout (still the owner's open knob).

### Iteration 10 — inner-priority cells: choosing the neutral (owner 2026-06-25)

Two findings closed the colour ("cells") version:

- **Outer-priority DROPPED** — the six colour spokes meeting at the dead centre overlap messily.
- **Inner-priority kept**, but its **slate** neutral collided with the slate AREA point (one of
  the six). Tested three near-white neutrals on off-white *and* pure-white grounds (`_gen10.py`,
  `board10.svg.png`): **white #FFFFFF** = crisp white snowflake on a warm ground (distinct from all
  six, clean centre) but vanishes on pure white; **off-white #F7F4EE** = the page ground, invisible
  on off-white; **border-grey #D9DEE5** ("faded white") = faintly visible on both, subtle everywhere.

**RESOLVED — canonical `star12-fulloutline-cells.svg` = inner-priority + white inner on a baked-in
off-white disc** (the disc guarantees the warm ground, so the white reads on any page incl. the
white site body; `star12-fulloutline-cells.svg.png` is the proof). Slate now appears only once (its
area point). **`star12-fulloutline-cells-inner-bordergrey`** kept as the disc-free alternative (works
on any light bg, just subtle). Rejected/superseded → `_archive/`: `-cells-outer`, the iter-8 slate
`-cells-inner`, `-cells-inner-offwhite`, `-cells-inner-white` (the canonical supersedes it w/ the disc).

---

## 13. Final assessment & recommended use

**What it is.** A *secondary*, civic geometric mark that is **structurally the leaf**:
a 12-point star whose six short points sit on the leaf-cells' six skeleton rays and whose
six long points bisect the gaps (through the wedge centres). The derivation is exact, not
narrated (`star12-proof`). Twelve carries honest meanings — a **compass rose / observatory
star**, the **twelve hours/months** (a watching-and-returning, *observatory* resonance) —
without claiming a federation count it doesn't fit (10/11/13 all fight the leaf's true
six-fold and the snowflake's six-fold; see §3, §10).

**Why it earns a place.** On-brand (observatory metaphor; reads "Canada/North/winter"
instantly); **far from GC/FIP territory** (no flag-leaf/RCAF-roundel problem); built in the
same line language as the seal + outline family; and it reuses the locked palette and the
six area colours. It is *family*, not a rival.

**Honest limits.** (1) **Not a primary mark** — the leaf is the identifier; a second
identifier dilutes (the lesson that retired the classic leaf). (2) **Not a tiny mark** —
line versions collapse ~20–24px; only the disc/solid registers survive small, and the
**seal already owns the tiny slot**. (3) The site already has the footer **north star**;
two stars may be one too many — adopting this likely means it *replaces* the north star
rather than adds to it.

**Recommended use, in priority order:**
1. **About → "Our marks" page centrepiece** — the lowest-risk, highest-value home: show
   `star12-proof` + a leaf→star morph to explain the system. (Owner's own idea; §11.)
2. **Large expressive / social / hero art** — `star12-leaf-navy` (filled) and its line
   sibling `star12-fulloutline-cells-navy` are striking at size.
3. **Per-section / per-area glyph or decorative device** on chart-light pages — the cells
   colourway maps to the six areas.
4. **Footer companion to / replacement for `mark-northstar`** — owner call (the "two
   stars" question).
   **Not** the navbar or favicon (size floor); **not** a co-equal logo.

**Recommended keeper set** (everything else → `_archive/`):
- Expressive/colour: **`star12-leaf-navy`** (owner favourite), **`star12-leaf-light`**.
- Line register (iter-7, thin + consistent): **`star12-fulloutline-navy`**,
  **`star12-fulloutline-seal`**, and the colour version **`star12-fulloutline-cells`**
  (inner-priority, white inner on an off-white disc; iter-10); keep **`star12-outline-cells`**
  (the lighter outer-edge chevron option the owner likes).
- Two-tone: **`star12-duo-navy-gold`**. Explainer: **`star12-proof`**.

**Status: still a study — nothing adopted, nothing wired to the live site.** The decisions
that remain are the owner's: (a) adopt it at all; (b) if so, for which **one** job (which
sets the register + size floor); and (c) its relationship to the north star. The 12-point
count and the structural derivation are settled (§10); a focused true-pixel small-size
board (like `studies/tiny-mark/`) is the only technical step left before anything touches
the kit — and only for whichever single register the chosen job needs.
