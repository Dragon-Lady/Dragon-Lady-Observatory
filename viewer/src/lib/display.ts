import type { StarRecord, Tier, Domain } from '@/types';
import { DOMAIN_LABEL } from '@/types';

export { DOMAIN_LABEL };

export const TIER_LABEL: Record<Tier, string> = {
  T1: 'T1 · Priority',
  T2: 'T2 · Notable',
  T3: 'T3 · Background',
};

export function tierClass(t: Tier): string {
  return `tier-${t.toLowerCase()}`;
}
export function tierDot(t: Tier): string {
  return `dot-${t.toLowerCase()}`;
}

export function domainSlug(d: Domain): string {
  return d;
}

/** A short, human one-liner about where a record sits (for cards). */
export function placeLabel(r: StarRecord): string {
  const loc = r.location as any;
  if (r.domain === 'orbital') {
    return loc.regime ? `${loc.regime}${loc.norad_id ? ` · #${loc.norad_id}` : ''}` : 'orbital';
  }
  if (r.domain === 'neo') return loc.is_pha ? 'PHA' : 'near-Earth object';
  if (r.domain === 'space_weather') return loc.region ? `${loc.region}` : 'space weather';
  if (r.domain === 'launch_reentry') return loc.site || loc.provider || 'launch site';
  return r.domain;
}

export function topAnomalyKind(r: StarRecord): string | null {
  const a = r.anomalies?.[0];
  return a ? a.kind.replace(/_/g, ' ') : null;
}
