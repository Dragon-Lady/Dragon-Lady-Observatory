// Optional research layer on records (location.seeding_hypothesis).
// Not part of core SSA schema — viewer-only helpers for clean display.

import type { StarRecord } from '@/types';

export type MatchStatus = 'supported' | 'it3_claim' | 'hypothesis_only' | 'open';

export interface MatchFlag {
  id: string;
  label: string;
  status: MatchStatus;
  medium_side?: string;
  it3_side?: string;
  note?: string;
}

export interface ScoreAxis {
  axis: string;
  value: string;
  basis?: string;
}

export interface SeedingHypothesis {
  layer?: string;
  status?: string;
  posture?: string;
  medium?: {
    title?: string;
    author?: string;
    url?: string | null;
    url_note?: string;
    related_discourse?: string;
    thesis?: string;
    questions?: string[];
  };
  it3_harvard_mpc?: {
    label?: string;
    meaning?: string;
    x_post?: string;
    zenodo?: string;
    bridge_packet?: string;
  };
  match_flags?: MatchFlag[];
  scoreboard?: ScoreAxis[];
  files?: { name: string; role?: string; path?: string }[];
  next_watch?: string[];
}

export function getSeeding(r: StarRecord): SeedingHypothesis | null {
  const loc = r.location as Record<string, unknown> | undefined;
  const s = loc?.seeding_hypothesis;
  if (!s || typeof s !== 'object') return null;
  return s as SeedingHypothesis;
}

export function hasSeeding(r: StarRecord): boolean {
  return getSeeding(r) !== null || (r.topics ?? []).includes('seeding_hypothesis');
}

export function statusLabel(status: string): string {
  switch (status) {
    case 'supported':
      return 'Supported';
    case 'it3_claim':
      return 'IT3 claim';
    case 'hypothesis_only':
      return 'Hypothesis';
    case 'open':
      return 'Open';
    default:
      return status.replace(/_/g, ' ');
  }
}

export function statusClass(status: string): string {
  switch (status) {
    case 'supported':
      return 'text-emerald-300 border-emerald-800/60 bg-emerald-950/40';
    case 'it3_claim':
      return 'text-signal-300 border-signal-800/50 bg-indigo-950/30';
    case 'hypothesis_only':
      return 'text-amber-200/90 border-amber-900/50 bg-amber-950/20';
    case 'open':
      return 'text-mist-300 border-void-700 bg-void-900';
    default:
      return 'text-mist-300 border-void-700 bg-void-900';
  }
}
