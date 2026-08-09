# Seeding hypothesis layer (Observatory data tab)

**Record id:** `artifact-it3-atlas`  
**Primary name:** `3I/ATLAS · seeding research`  
**Updated:** 2026-08-09

## What shipped (small / clean)

1. **Intake record** — `location.seeding_hypothesis` with:
   - Medium thesis + questions (URL null until you paste public link)
   - IT3 / Harvard MPC block (X + Zenodo + bridge packet)
   - **Match flags** (supported / it3_claim / hypothesis_only / open)
   - **Scoreboard** (honest axes only)
   - Suite file list + next_watch
2. **Record detail UI** — Seeding analysis section when layer present  
   (`viewer/src/pages/record/[id].astro` + `lib/seeding.ts`)
3. **Data tab strip** — Research section on home listing seeding records  
   (`viewer/src/pages/index.astro`)
4. **Card chip** — “Seeding research” on RecordCard

## Match flags (summary)

| Flag | Status |
|------|--------|
| Unbound ISO | supported |
| Highest E_ion (+9.43) | it3_claim |
| Free channel / entropy | it3_claim |
| Mass trap contrast | it3_claim |
| Kuiper Cliff 46.77 AU | it3_claim |
| Injection nodes (E-5) | hypothesis_only |
| Intentional seeding | open |

## Not done (on purpose)

- No auto mp.py run
- No Node E-5 pin yet
- No Medium export pack
- No “confirmed seeding” language
