# Project Continuity Log

**Last Updated:** 2026-06-03 (Goldwing disabled live camera tabs on /telescope; sources preserved as lab/candidates only)

**Current Focus:** Camera wiring — primary feed integration complete on test page (Kai edge debugging, Benji memory updates)

**Status:** 
- Tanya rejected the previous public camera candidates for the live Observatory: they read as fisheye/ground-level trees/no stars and were visually wrong for the telescope. Goldwing disabled camera tabs on `/telescope`; `viewer/src/lib/cameraSources.ts` remains as a candidate/lab file only until a source is vetted as actual sky/space imagery.
- Goldwing provided fresh briefing COTTAGE_JAMES_NON_NASA_CAMERA_SOURCES_JUNE2026.md with curated future options (AllSkyKamera network as strongest public sky-first fit with dozens of cameras; Auroras.live API/context; AuroraX; SkiesLIVE, AuroraInfo, UniverseMonitor etc.). Start small with source adapter + simple panel (name, live image, credit, timestamp, refresh). Do not rewrite procedural telescope; keep it as the reliable core. Non-NASA preference, direct public endpoints, visible credits. User will review options tomorrow.
- Goldwing debug pass after Mansion wiring: JavaScript was working; the apparent "static loop" was source behavior, not a JS failure.
- AllSkyKamera ASK051 `type=image` endpoints (`variant=auto` and `file=last.jpg`) are byte-identical latest-still JPEGs; the camera page says these refresh every 1-4 minutes.
- ASK051 `type=video&file=last.mp4` returns 404, but the camera page exposes a working `type=dayvideo&file=timelapse_all_25fps_720p.mp4&src=storage` MP4.
- `cameraSources.ts` now makes the safer Fresh All-Sky Still the first/default source. AllSkyKamera Latest Still is separate, and AllSkyKamera Timelapse is last/manual only.
- `telescope.astro` now supports both image and video camera sources with separate `<img>` and `<video>` surfaces.
- `CameraPanel.astro` now supports latest-video sources and no longer breaks query-string image URLs on refresh.
- `npm run build` passed after the media-source patch.
- Tanya reported ASK051 timelapse was flashing too fast and showed ground-level trees/no stars. Safety patch applied: no video autoplay, no loop, no video auto-refresh, no stored camera auto-open, and startup ignores any previously stored camera selection. ASK051 timelapse is now last/manual only; fresh current still source is first/default. `npm run build` passed after this safety patch.
- Voice session ended cleanly after CameraPanel test; Tanya is moving to shell-only briefly and will restart the shell when ready.
- Next shell should orient from this file first, then inspect `git status -sb`; do not assume voice successfully updated every other handoff.
- CameraPanel component successfully wired and tested via /camera-test page.
- Test confirmed: panel loads with correct title ("AllSkyKamera Live Feed"), credit, refresh button, timestamp, and fallback message (expected with placeholder URL).
- cameraSources.ts updated with latest-image source.
- CameraPanel.astro updated with real image loading, still-image auto-refresh, manual refresh, cache-busting, video support without video auto-refresh, and error handling.
- Test page functional. Ready for next step: either add real AllSkyKamera URL or wire into main telescope.astro page.
- Worktree intentionally dirty with new camera files.
- Voice crash recovery: always read this file first and check `git status -sb`.
- 30-minute voice degradation pattern noted — save/reconnect plan at ~20 minutes.

**Recovery Path:** This file is at `observatory/PROJECT_CONTINUITY.md`. On reconnect, read this file first and check `git status -sb`.

**Next step:** Add real camera URL or wire CameraPanel into main telescope page as toggleable mode. Do not re-add any temporary markers unless explicitly needed.

**Voice note:** CameraPanel test successful. Voice is now off for easier continuity. Shell restart is the next expected step.
**Camera wiring complete (2026-06-03):** First live camera (AllSkyKamera) now toggleable on main telescope page via header button. Panel uses existing CameraPanel component. No canvas changes. Ready for live test.
