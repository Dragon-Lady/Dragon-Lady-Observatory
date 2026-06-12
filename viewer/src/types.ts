// Observatory record types — mirror ../../schema/record.md (the contract).
// Producer: the engine. Consumer: this viewer.

export type Domain = 'orbital' | 'neo' | 'space_weather' | 'launch_reentry';
export type Tier = 'T1' | 'T2' | 'T3';
export type StalenessRisk = 'low' | 'medium' | 'high';

export interface Source {
  name: string;
  url: string;
  retrieved_at: string;
}

export interface EvidenceItem {
  reason: string;
  metric?: string;
  value?: number | string;
  source_ref?: string;
  observed_at?: string;
}

export interface Anomaly {
  kind: string;
  confidence: number;
  evidence: EvidenceItem[];
  delta?: Record<string, unknown>;
  state: 'active' | 'watch' | 'resolved' | 'dismissed';
  first_flagged: string;
  last_updated: string;
}

export interface StarRecord {
  schema_version: 1;
  id: string;
  domain: Domain;
  type: string;
  names: string[];
  description: string;
  topics: string[];
  sources: Source[];
  freshness: { last_update: string; staleness_risk: StalenessRisk };
  related_ids?: string[];
  location: Record<string, unknown>;
  tier: Tier;
  watchlist: boolean;
  anomalies: Anomaly[];
}

export const TIER_RANK: Record<Tier, number> = { T1: 0, T2: 1, T3: 2 };

export const DOMAIN_LABEL: Record<Domain, string> = {
  orbital: 'Orbital',
  neo: 'Near-Earth',
  space_weather: 'Space Weather',
  launch_reentry: 'Launch / Reentry',
};

export function primaryName(r: StarRecord): string {
  return r.names[0] ?? r.id;
}

export function activeAnomalies(r: StarRecord): Anomaly[] {
  return (r.anomalies ?? []).filter((a) => a.state === 'active' || a.state === 'watch');
}
