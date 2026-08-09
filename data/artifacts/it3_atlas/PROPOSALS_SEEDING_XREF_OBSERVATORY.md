# Proposals — Seeding hypothesis × IT3 / Harvard MPC × Observatory

**Date:** 2026-08-09  
**Artifact:** `artifacts/it3_atlas`  
**Bridge:** `CHAT_TO_JAMES_20260809_162838_IT3---3I-ATLAS-Observatory-intake`  
**Posture:** Research brainstorm only. IT3 claims are **author assertions**, not peer-reviewed confirmation. “Appears to confirm” in product copy must stay **hypothesis language** (corroborating frame / independent lattice math / interesting alignment) — never “proven.”

---

## The two stories we want to cross-wire

### A. Medium / personal seeding thread
- Tanya’s seeding read on **3I/ATLAS** (Medium; sparked with *Project Hail Mary* + Dustin; Avi thread / claps noted in bridge).
- Public Loeb-adjacent discourse: interstellar objects as possible intentional “gardeners” / seeders of life, statistical exposure of Earth to interstellar traffic, agenda-dependent intervention — **not** the same claim as IT3, but the **same object family** (ISOs as messengers).

### B. IT3 / @dr_logvinovich “Harvard MPC hack”
- Live public **MPC** audit of ~1.55M orbits → discrete hourglass / \(O_h\) lattice.
- ISOs scored as **free macro-electrons** with positive \(E_{\mathrm{ion}}\): 1I +6.55, 2I +7.29, **3I/ATLAS +9.43** (highest).
- Bound vs free entropy split; Kuiper Cliff 46.77 AU; valence shell 27–48 AU; injection/lattice nodes (Node E-5 predicted).

### The interesting joint claim (for product, not gospel)
If the Solar System is a **quantized lattice with free-electron scattering channels**, then seeding is not “a rock randomly thrown” — it is **traffic on a preferred topological highway**. 3I’s high \(E_{\mathrm{ion}}\) would mark it as the most “unbound / carrier-class” of the three known ISOs under IT3’s ruler. That is a **cool Observatory narrative**, labeled research.

---

## Product principles (keep Observatory calm)

1. **Provenance first** — every card shows Medium vs X vs Zenodo vs MPC.
2. **Hypothesis labels** — `research · author claim · not engine-confirmed`.
3. **No conspiracy chrome** — Dragon Lady tone: quiet sky, clear evidence.
4. **Fits existing grammar** — unified records, tiers, watchlist, Atlas pins, NEO domain.
5. **Non-NASA spine stays** — MPC/Zenodo/X/Medium as sources; ESA NEOCC path for live NEO later.

---

## Proposal map (priority tiers)

### P0 — Ship this week (high signal, low risk)

#### 1. **Seeding × Lattice dossier card on the Data tab**
Extend `artifact-it3-atlas` (or sibling `research-3i-seeding-xref`) with a structured **crosswalk**:

| Medium / seeding idea | IT3 / MPC claim | Observatory field |
|----------------------|-----------------|-------------------|
| ISO as possible carrier / gardener traffic | Free macro-electron, \(E_{\mathrm{ion}}>0\) | `research_metrics.seeding_frame` |
| Why 3I is special | Highest \(E_{\mathrm{ion}}\) (+9.43) | badge on record card |
| Life / chaos needs residual free population | Evaporative tail + free comet entropy | anomaly evidence rows |
| “Where would seeders enter?” | Lattice nodes / Node E-5 RA·Dec | Atlas pin + watchlist |

**UI:** Record detail page section **“Hypothesis crosswalk”** with two-column Medium vs IT3 and a third “What we can observe.”

#### 2. **ISO family shelf (1I / 2I / 3I)**
Three NEO records + one parent **family** record (`iso-family-known-three`) with shared topics `iso`, `free_macro_electron`, `seeding_hypothesis`. Sort by \(E_{\mathrm{ion}}\). 3I watchlisted.

#### 3. **Atlas pins for research sky**
- Pin **Node E-5** (RA 60.5°, Dec +43.2°) labeled `IT3 hypothesis · ETNO-P1` (not “found object”).
- Optional pin for **Kuiper Cliff educational ring** (not a sky point — better as a radial diagram; see P1).
- My Pins badge: **Research** (purple/quiet, not T1 red).

#### 4. **PDF shelf in the artifact drawer**
Data tab already has files; add viewer links: “Open Solar_v16 · Hardware · mp.py notes” so the manuscript is one click from the card (local paths or `/api/artifact/it3_atlas/...` static serve).

---

### P1 — Beautiful science (the cool stuff)

#### 5. **Seeding scoreboard (honest)**
A small panel — not a truth meter:

```
3I/ATLAS research scoreboard
  IT3 E_ion rank among ISOs     ████████░░  3/3 (highest)
  Hyperbolic / unbound orbit    confirmed (public ephemeris)
  Lattice node proximity        unknown — needs operator run
  Medium seeding narrative      linked
  Engine anomaly (engine)       none yet
```

Score only **observable / cited** axes. No “alien %.”

#### 6. **Radial lattice diagram (Observatory-native viz)**
SVG or Canvas on a research page `/research/it3` or a card expand:

- Rings at **27 AU**, **46.77 AU (Cliff)**, **48 AU (tail start)**, **~69.94 AU (tail extent)**
- Plot **1I / 2I / 3I** as free-electron markers outside the bound crystal
- Toggle: “IT3 author claim” watermark always on

This is the single best visual for “seeding rides the free spectrum.”

#### 7. **Entropy / bound–free comet strip**
Sparkline or two-bar: Bound H=1.68 vs Free H=3.81. Caption: “Same dichotomy as Hydrogen bound vs free states (author micro–macro rhyme).”

#### 8. **Injection-node hunter (lightweight)**
Without running full 1.55M audit:

- Parse `mp.py` constants (already in artifact) for shell radii / magic angles (18°, ~54.7°)
- Generate a **checklist of sky regions** IT3 implies for trapping / scattering
- Export as pins JSON for Atlas

Later: optional sandboxed run of `mp.py` offline (Tanya OK required; never auto in viewer).

#### 9. **Medium ↔ X dual timeline**
A vertical timeline on the dossier:

```
[date] Medium seeding piece (Tanya / Avi discourse)
[date] 3I discovery / perihelion
[date] IT3 ISO E_ion post
[date] Harvard MPC live-run post (11k views)
[date] Bridge packet → Observatory intake
```

Makes the narrative human and journal-like — perfect for Dragon Lady tone.

---

### P2 — Alerts & living watch (engine-shaped)

#### 10. **Research alerts (not SSA panic)**
New alert kinds under research namespace:

| Alert | Trigger |
|-------|---------|
| `iso_e_ion_rank` | New ISO scored (manual or mp.py) with \(E_{\mathrm{ion}}\) above threshold |
| `lattice_node_sky` | LSST / MPC new object near Node E-5 cone |
| `seeding_window` | ISO approaches inner system (q, MOID) while free-spectrum flagged |
| `artifact_refresh` | Zenodo version bump on 21792530 |

Store as `anomalies[]` with `state: watch` and `topics: research`.

#### 11. **Watchlist auto-bundle: “ISO Seeding Watch”**
One-click add: 3I + family + Node E-5 + link to artifact. Device-local watchlist already exists (`stars_watchlist`) — extend with research bundles.

#### 12. **Freshness gate for research claims**
If X/Zenodo claim older than N days without re-pull, badge goes **stale claim** (same freshness discipline as SSA).

---

### P3 — Signature experiences (ambitious / delightful)

#### 13. **“Macroscopic atom” night mode on Atlas**
Optional overlay (off by default): faint hourglass watermark + valence shell annotation when viewing outer solar system educational layer. **Not** a sky catalog layer — pedagogical only.

#### 14. **Hail Mary porch mode**
A quiet reading mode: Ambient music + side panel with Medium excerpt + IT3 one-liner + 3I pin on Atlas. Session for “we watch the seeder sky together.” Extremely on-brand.

#### 15. **Compare rulers**
Side-by-side: classical ephemeris card (e, q, i) vs IT3 card (\(E_{\mathrm{ion}}\), free/bound, nearest floor). Teaches users that **two languages** describe the same ISO.

#### 16. **Falsification board**
What would **disconfirm** the joint story?

- New ISO with bound-like entropy despite e≥1  
- Node E-5 empty after deep surveys  
- Kuiper structure not matching 46.77 under independent change-point analysis  

Show these as open tests — scientific integrity theater that builds trust.

#### 17. **James Bridge research reply lane**
Auto-draft `JAMES_TO_CHAT_*` when artifact updates: short card Tanya can paste to Medium replies (“Observatory now tracks 3I with IT3 crosswalk; here’s the scoreboard”).

#### 18. **Export pack for Medium**
One-button: PNG of radial diagram + caption + provenance footer for Medium embed. Observatory → essay loop.

---

## Suggested build order (practical)

| Sprint | Deliverable |
|--------|-------------|
| **S1** | Crosswalk fields on `artifact-it3-atlas` + ISO family records + Atlas Node E-5 research pin |
| **S2** | Radial lattice SVG + entropy strip + PDF shelf links on record page |
| **S3** | Research alert kinds + ISO Seeding Watch bundle + freshness on claims |
| **S4** | Hail Mary porch mode + Medium export + falsification board |

---

## What *not* to do

- Don’t present IT3 as “Harvard confirmed seeding.” Harvard here = **MPC catalog host**, not institutional endorsement.
- Don’t auto-run `mp.py` against live MPC from the viewer without explicit OK (network + CPU + claim liability).
- Don’t mix ShinyHunters-style cyber “Harvard hack” lore into this artifact — different universe.
- Don’t escalate 3I to T1 SSA “threat” — research watch stays T2 / watchlist.

---

## One-sentence product vision

**The Observatory becomes the place where your Medium seeding question and the IT3 free-electron map sit on the same card, under the same sky pin, with the same calm provenance — so 3I/ATLAS is not just a headline, it’s a living research object in Dragon Lady’s house.**
