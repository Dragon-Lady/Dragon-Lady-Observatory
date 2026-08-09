# Research artifact: `it3_atlas` (IT3_Atlas)

Committed Observatory research dossier for **3I/ATLAS seeding hypothesis** cross-referenced with the IT3 / Harvard–Smithsonian MPC live-audit materials.

## Credits & sources

| Source | Credit / link |
|--------|----------------|
| **IT3 Framework** | Victor Logvinovich & Jean-Claude Perez — [Zenodo 21792530](https://zenodo.org/records/21792530) (open preprint / suite) |
| **X live-run post** | [@dr_logvinovich](https://x.com/dr_logvinovich/status/2086386984897917248) (2026-08-09) — public MPC audit narrative |
| **ISO E_ion table** | [@dr_logvinovich](https://x.com/dr_logvinovich/status/2085037477610303532) (2026-08-05) |
| **MPC catalog** | [Harvard–Smithsonian Minor Planet Center](https://www.minorplanetcenter.net/) (public orbits) |
| **Suite code** | `mp.py` from Zenodo package (authors above; open suite) |
| **Manuscripts** | `Solar_v16.pdf`, `Hardware.pdf` — download from Zenodo (not stored in git; see `FILES.md` SHA-256) |
| **Bridge intake** | James Bridge packet `CHAT_TO_JAMES_20260809_162838_IT3---3I-ATLAS-Observatory-intake` (copy under `provenance/`) |
| **Seeding hypothesis** | User Medium thesis (URL optional in `record.json` → `seeding_hypothesis.medium`) |
| **Observatory packaging** | Dragon Lady Observatory / James intake layer |

## Posture

Research only. IT3 claims are **author assertions**, not peer-reviewed or engine-confirmed. “Harvard” here means the **public MPC catalog host**, not institutional endorsement of seeding.

## Layout

| Path | Role |
|------|------|
| `record.json` | Unified record + seeding layer (data tab) |
| `SEEDING_LAYER.md` | What shipped in the UI |
| `KEY_DATA_POINTS.md` / `FULL_HARVARD_MPC_AUDIT_LOG.md` | Claim tables |
| `X_POST_…md` | Primary X extract |
| `FILES.md` | Suite file checksums + Zenodo re-download URLs |
| `mp.py` | 11-front validation suite (small; from Zenodo) |
| `provenance/` | Bridge packet copy |

Viewer loads `data/artifacts/*/record.json` via `viewer/src/lib/store.ts`.
