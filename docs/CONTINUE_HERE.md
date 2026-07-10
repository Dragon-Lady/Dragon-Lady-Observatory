# CONTINUE HERE — Dragon Lady's Observatory

**Authority:** This file wins if other docs disagree for console/pin handoff in this repo.
**Last updated:** 2026-07-10 (console My Pins pass)

---

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

## Smoke

Hard-refresh `/` → pins show RA·Dec·FOV + badge → click card → Atlas → Edit stays put.
