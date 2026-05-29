// Build-time record store loader — the viewer's half of the engine boundary.
// Reads what the engine emits: data/records/<id>.json (one per record).
// Falls back to data/fixtures/records.json (an array) when the engine store is
// empty — so the viewer renders today, before the engine is wired, and swaps to
// live records the instant they appear. Same boundary discipline as Open UAP.

import fs from 'node:fs';
import path from 'node:path';
import { TIER_RANK } from '@/types';
import type { StarRecord, Domain, Tier } from '@/types';

// Build runs from viewer/, so the repo root is one level up. Avoid deriving this
// from import.meta.url; Astro rewrites that path differently across versions.
const REPO_ROOT = path.resolve(process.cwd(), '..');
const DATA_ROOT = process.env.DATA_ROOT
  ? path.resolve(REPO_ROOT, process.env.DATA_ROOT)
  : path.join(REPO_ROOT, 'data');

const RECORDS_DIR = path.join(DATA_ROOT, 'records');
const FIXTURES_FILE = path.join(DATA_ROOT, 'fixtures', 'records.json');
const CATALOG_FILE = path.join(DATA_ROOT, 'catalog', 'tle.json');

export interface TleEntry { norad_id: number; name: string; tle1: string; tle2: string; type: string; }
export interface OrbitalMarker {
  id: string;
  name: string;
  tier: Tier;
  norad_id?: number;
  tle1: string;
  tle2: string;
  anomalyKinds: string[];
}

/** The orbital catalog bundle the globe propagates client-side (satellite.js). */
export function loadCatalog(): TleEntry[] {
  if (!fs.existsSync(CATALOG_FILE)) return [];
  try {
    const a = JSON.parse(fs.readFileSync(CATALOG_FILE, 'utf8'));
    return Array.isArray(a) ? a : [];
  } catch { return []; }
}

const REQUIRED = ['schema_version', 'id', 'domain', 'type', 'tier'] as const;

function valid(r: any, where: string): r is StarRecord {
  for (const k of REQUIRED) {
    if (r?.[k] === undefined || r?.[k] === null) {
      console.warn(`[stars] record missing '${k}' (${where}) — skipped`);
      return false;
    }
  }
  if (!Array.isArray(r.anomalies)) r.anomalies = [];
  if (!Array.isArray(r.topics)) r.topics = [];
  if (!Array.isArray(r.names)) r.names = [r.id];
  return true;
}

let _cache: StarRecord[] | null = null;

function load(): StarRecord[] {
  if (_cache) return _cache;
  const out: StarRecord[] = [];

  // Primary: the engine's live store (one JSON per record).
  if (fs.existsSync(RECORDS_DIR)) {
    for (const f of fs.readdirSync(RECORDS_DIR)) {
      if (!f.endsWith('.json')) continue;
      const full = path.join(RECORDS_DIR, f);
      try {
        const r = JSON.parse(fs.readFileSync(full, 'utf8'));
        if (valid(r, full)) out.push(r);
      } catch (e) {
        console.warn(`[stars] unreadable ${full}: ${(e as Error).message}`);
      }
    }
  }

  // Fallback: fixtures, only if the live store produced nothing.
  if (out.length === 0 && fs.existsSync(FIXTURES_FILE)) {
    try {
      const arr = JSON.parse(fs.readFileSync(FIXTURES_FILE, 'utf8'));
      if (Array.isArray(arr)) for (const r of arr) if (valid(r, FIXTURES_FILE)) out.push(r);
      console.log(`[stars] no engine records yet — rendering ${out.length} fixtures`);
    } catch (e) {
      console.warn(`[stars] unreadable fixtures: ${(e as Error).message}`);
    }
  } else if (out.length) {
    console.log(`[stars] loaded ${out.length} live record(s) from ${RECORDS_DIR}`);
  }

  // Sort: tier (T1 first), then most-recently-updated freshness.
  out.sort((a, b) =>
    TIER_RANK[a.tier] - TIER_RANK[b.tier] ||
    (b.freshness?.last_update ?? '').localeCompare(a.freshness?.last_update ?? ''));

  _cache = out;
  return out;
}

// ── queries ──────────────────────────────────────────────────────────────────
export const allRecords = (): StarRecord[] => load();
export const recordById = (id: string) => load().find((r) => r.id === id);
export const byDomain = (d: Domain) => load().filter((r) => r.domain === d);
export const byTier = (t: Tier) => load().filter((r) => r.tier === t);
export const watchlisted = () => load().filter((r) => r.watchlist);
export const withAnomalies = () => load().filter((r) => r.anomalies.length > 0);

export function orbitalMarkers(): OrbitalMarker[] {
  const catalogByNorad = new Map<number, TleEntry>();
  for (const entry of loadCatalog()) catalogByNorad.set(entry.norad_id, entry);

  const out: OrbitalMarker[] = [];
  for (const r of load()) {
    if (r.domain !== 'orbital' || !r.anomalies?.length) continue;
    const loc = r.location as Record<string, any>;
    const elset = (loc?.elset ?? {}) as Record<string, any>;
    const norad = typeof loc?.norad_id === 'number' ? loc.norad_id : undefined;
    const fallback = norad !== undefined ? catalogByNorad.get(norad) : undefined;
    const tle1 = typeof elset.tle1 === 'string' && elset.tle1 ? elset.tle1 : fallback?.tle1;
    const tle2 = typeof elset.tle2 === 'string' && elset.tle2 ? elset.tle2 : fallback?.tle2;
    if (!tle1 || !tle2) continue;
    out.push({
      id: r.id,
      name: primaryLabel(r),
      tier: r.tier,
      norad_id: norad,
      tle1,
      tle2,
      anomalyKinds: r.anomalies.map((a) => a.kind),
    });
  }
  return out;
}

export interface ConjunctionMarker {
  id: string;
  name: string;
  tier: Tier;
  alertClass: 'alert' | 'close_pass'; // payload-at-risk vs debris near-miss
  tca?: string;
  miss_distance_km?: number;
  pc?: number;
  objects: { name: string; tle1: string; tle2: string }[]; // the two
}

/** Conjunctions for the globe — one tier-styled marker per close approach
 *  (bright = payload-involved ALERT, dim = debris close pass). Needs
 *  location.objects[] carrying both TLEs; skips any that don't.
 *  Sorted alert-first, then tightest miss first, so the most significant
 *  approaches lead the list and survive any display cap. A live CDM feed is
 *  close-dominated (every published CDM is already a near-miss), so the
 *  alert_class sub-tier — not the tier — is what triages the volume. */
export function conjunctionMarkers(): ConjunctionMarker[] {
  const out: ConjunctionMarker[] = [];
  for (const r of load()) {
    if (r.type !== 'conjunction') continue;
    const loc = r.location as Record<string, any>;
    const objs = Array.isArray(loc?.objects) ? loc.objects : [];
    const usable = objs
      .filter((o: any) => o?.tle1 && o?.tle2)
      .map((o: any) => ({ name: o.name ?? String(o.norad_id ?? '?'), tle1: o.tle1, tle2: o.tle2 }));
    if (usable.length < 2) continue;
    out.push({
      id: r.id,
      name: primaryLabel(r),
      tier: r.tier,
      alertClass: loc?.alert_class === 'alert' ? 'alert' : 'close_pass',
      tca: typeof loc?.tca === 'string' ? loc.tca : undefined,
      miss_distance_km: typeof loc?.miss_distance_km === 'number' ? loc.miss_distance_km : undefined,
      pc: typeof loc?.pc === 'number' ? loc.pc : undefined,
      objects: usable.slice(0, 2),
    });
  }
  // alert before close_pass; within each, tightest miss first.
  out.sort((a, b) =>
    (a.alertClass === b.alertClass ? 0 : a.alertClass === 'alert' ? -1 : 1) ||
    ((a.miss_distance_km ?? Infinity) - (b.miss_distance_km ?? Infinity)));
  return out;
}

export function domainsPresent(): Domain[] {
  return [...new Set(load().map((r) => r.domain))];
}

export function stats() {
  const all = load();
  return {
    total: all.length,
    t1: all.filter((r) => r.tier === 'T1').length,
    anomalies: all.reduce((n, r) => n + r.anomalies.length, 0),
    domains: domainsPresent().length,
  };
}

function primaryLabel(r: StarRecord): string {
  return r.names[0] ?? r.id;
}
