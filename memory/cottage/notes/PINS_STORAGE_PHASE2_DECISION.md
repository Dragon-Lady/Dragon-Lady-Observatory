# PINS_STORAGE_PHASE2_DECISION.md

**Date:** 2026-06-02  
**Phase:** 2B Decision Prep  
**Status:** For Phase 3 planning

## Current State

- Live storage: `localStorage.personalPins` (array of pin objects)
- Existing but unwired: `pins.ts` + `.local/pins.json` in the Dragon-Lady-Observatory repo
- Thumbnails currently stored as base64 `thumbnailData` on each pin
- No sync, no export, no import in production yet

## Three Options

### Option A — Stay fully localStorage + Export button
**Pros:** Zero backend, instant, no migration risk  
**Cons:** Data lost on browser clear, no cross-device, no git history  
**Best for:** v1 personal use, very low friction

### Option B — Wire simple Astro API to `pins.ts` / `.local/pins.json`
**Pros:** Real persistence, git-trackable, potential for future multi-user  
**Cons:** Requires API routes, careful handling of thumbnail blobs, more surface area  
**Best for:** When we want durability and potential sharing

### Option C — Lightweight hybrid (local first + optional sync)
**Pros:** Best of both worlds, graceful fallback  
**Cons:** More complex logic, conflict resolution needed  
**Best for:** Long-term direction once collections and editing feel solid

## Recommendation for Phase 3

**Start with Option C (hybrid).**  
Keep localStorage as the immediate source of truth for speed and offline use. Add a background “Save to vault” button that writes to `.local/pins.json` via a simple Astro endpoint. This gives us durability without forcing users into a full migration immediately.

## Migration Sketch (no data loss)

1. On first “Save to vault” action, read entire `localStorage.personalPins`
2. Write to `.local/pins.json` with same shape + `lastSynced` timestamp
3. On load, prefer `.local/pins.json` if it exists and is newer; otherwise fall back to localStorage
4. Keep `thumbnailData` as-is (base64) for now — consider external storage only if blobs become a problem
5. Add a one-time migration banner if localStorage pins exist but vault file does not

## Risks to Watch

- Multi-tab conflicts (last write wins is acceptable for v1)
- `.local/` must stay in `.gitignore`
- Thumbnail base64 can bloat the JSON file quickly — monitor size
- Export/Import must always round-trip cleanly before any storage switch

---

**Decision owner:** Tanya + James  
**Next action:** Implement Option C prototype only after 2B collections + editing are stable.