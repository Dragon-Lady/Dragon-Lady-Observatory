# Research artifact: `it3_atlas`

Public Observatory dossier for **3I/ATLAS** seeding-hypothesis research, cross-referenced with open IT3 / MPC materials.

## Credits (public sources)

| Source | Credit |
|--------|--------|
| **IT3 Framework** | Victor Logvinovich & Jean-Claude Perez — [Zenodo 21792530](https://zenodo.org/records/21792530) |
| **X live-run** | [@dr_logvinovich](https://x.com/dr_logvinovich/status/2086386984897917248) (2026-08-09) |
| **ISO E_ion table** | [@dr_logvinovich](https://x.com/dr_logvinovich/status/2085037477610303532) (2026-08-05) |
| **Orbit catalog** | [Harvard–Smithsonian Minor Planet Center](https://www.minorplanetcenter.net/) (public) |
| **Suite code** | `mp.py` from the Zenodo package |

## Posture

Research only. IT3 numbers are **author claims**, not peer review. “Harvard” here means the **public MPC catalog**, not institutional endorsement of seeding.

## Layout

| Path | Role |
|------|------|
| `record.json` | Unified record + seeding layer (data tab) |
| `KEY_DATA_POINTS.md` | Public claim tables |
| `X_POST_dr_logvinovich_2026-08-09.md` | Public X extract |
| `FILES.md` | Zenodo re-download URLs + SHA-256 |
| `mp.py` | 11-front validation suite (from Zenodo) |

Manuscript PDFs are optional local downloads (gitignored); see `FILES.md`.

Viewer loads `data/artifacts/*/record.json` via `viewer/src/lib/store.ts`.
