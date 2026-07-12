# CONTINUE HERE — Dragon Lady's Observatory

**Authority:** This file wins if other docs disagree for console/pin handoff in this repo.
**Last updated:** 2026-07-12 (Venus/Moon SSO + Inspect + pinfix 16)

---

## Local wrapper (Oracle cheat → Chuck refresh)

**Two wrappers:** Cosmic/Oracle (often `:4321`, old M42 boot) vs Chuck (`./scripts/observatory` on **`:4331`**). See `docs/TWO_WRAPPERS.md`.

```bash
git checkout cursor/console-pins-cleanup-27c8 && git pull
chmod +x scripts/observatory
./scripts/observatory
# open http://127.0.0.1:4331/observatory  — look for · pinfix 16
```

**Litmus:** Atlas bottom-left chip must show `· pinfix 16`. No stamp → you’re still on Oracle’s port/tree.

---

## Tonight’s Atlas wins (2026-07-12) — DONE

- **Venus / Moon / planets:** Sesame cannot resolve SSOs. Atlas uses **Miriade** (`p:Name`) → `gotoRaDec` + persistent gold **plus** reticle (open center). DSS plates do not show tonight’s disk — the plus *is* the find.
- Center **reticle off** by default (it covered tiny SSO targets). **Inspect** button (and Aladin’s SIMBAD control) opt-in for click → description; click again to exit.
- Chip shows `Venus · live sky` / `Moon · live sky` on success.
- Ambient music (Nebula Drift) — dreamy IMAX; `M` / music icon; pref `localStorage.dlo-ambient`.
- Hi 42 (M42) remains a favorite pin, not the boot default.

**Parked:** live telescope camera feeds until sources are vetted (`telescope.astro` keeps cams disabled). Do not fake windows.

## Smoke — SSO

Hard-refresh Atlas → `· pinfix 16` → console/Sky Events click Venus or Moon → chip `· live sky` + gold plus stays → Inspect on → click a star → SIMBAD popup → Inspect off.

## Console pins + cleanup (DONE)

Branch: `cursor/console-pins-cleanup-27c8`

- My Pins cards show sexagesimal **RA / Dec / FOV** when present; lat/lng fallback for older pins
- Source badges: Atlas / Sky Events / Telescope
- `flyToPin` via `buildFlyToPayload` prefers exact `ra`/`dec`/`fov`; card click opens **`/observatory`**
- Hero slimmed (brand + one line + Open the Observatory)
- Removed chip-hint blurbs, vault tip footer, duplicate Observatory card
- Export/Import kept; shared vault UI removed (endpoint already purged from tip)
- Sky Events toast/link routes to Observatory with `label` in payload
- Edit panel no longer yeets into Atlas mid-type

## Smoke — console

Hard-refresh `/` → pins show RA·Dec·FOV + badge → click card → Atlas → Edit stays put.

## Fix — Orion slingshot (2026-07-10)

**Cause:** console PR routed pins to `/observatory`, but this branch still had the old Observatory page with **no `flyToPin` consumer** — Aladin always booted to M42.
**Fix:** restored Atlas `observatory.astro` (Miriade + `applyFlyToPinIfAny`) and only clear `flyToPin` after a successful jump.

**HD 23514 still → Orion:** some saved pins kept **M42’s RA/Dec** under a different label. Coord path won over Sesame. Now: detect M42-poisoned coords when label isn’t M42/Orion, scrub them from `personalPins` on console load, and fly by label (Sesame resolves `HD 23514` → `03 46 38 +22 55`).

## Hero presence + ambient (2026-07-10)

- Quiet crystalline dragon watermark in the console hero (atmosphere, not a sticker)
- Music icon next to Open the Observatory — tap to play/quiet (Android-app style)
- `M` toggles ambient (Dragon Eye–style hotkey); skipped in inputs
- Pref: `localStorage.dlo-ambient` = `on` | `off` (default off)
- Audio: `viewer/public/audio/nebula-drift.mp3` (and/or celestial-harp stand-in)
