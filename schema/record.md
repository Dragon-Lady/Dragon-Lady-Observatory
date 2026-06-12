# Dragon Lady Observatory — Unified Record (schema_version 1)

The producer/consumer contract. The engine emits these; the viewer reads them.
One record shape across all four domains, discriminated by `domain`.

```jsonc
{
  "schema_version": 1,
  "id": "stable, deterministic, URL-safe",
  "domain": "orbital | neo | space_weather | launch_reentry",
  "type": "satellite | debris | rocket_body | asteroid | comet | flare | cme | geomagnetic | radiation | launch | reentry | conjunction",
  "names": ["primary designator", "aliases..."],
  "description": "auto-generated, labeled as auto in the UI",
  "topics": ["string"],

  "sources": [ { "name": "space-track", "url": "...", "retrieved_at": "ISO" } ],
  "freshness": { "last_update": "ISO", "staleness_risk": "low | medium | high" },

  "related_ids": ["id(s) of linked records — e.g. conjunction primary/secondary"],

  "location": {
    // orbital:        { norad_id, intl_designator, elset:{epoch,tle1,tle2,mean_motion,ecc,inc}, apogee_km, perigee_km, regime: "LEO|MEO|GEO|HEO" }
    // neo:            { designation, orbit:{a_au,e,i_deg,epoch}, moid_au, is_pha }
    // space_weather:  { region, lat, lon, intensity, onset, peak }
    // launch_reentry: { provider, vehicle, site, lat, lon, window_start, window_end, status }
  },

  "tier": "T1 | T2 | T3",
  "watchlist": false,

  "anomalies": [
    {
      "kind": "maneuver | new_object | conjunction_close_approach | rpo | decay_imminent | neo_close_approach | space_weather_severe | unexpected_brightening | catalog_change",
      "confidence": 0.0,
      "evidence": [
        { "reason": "string", "metric": "delta_v | miss_distance | flux", "value": 0, "source_ref": "...", "observed_at": "ISO" }
      ],
      "delta": { /* domain-specific: delta_v_kms | miss_distance_km | flux_change | ... */ },
      "state": "active | watch | resolved | dismissed",
      "first_flagged": "ISO",
      "last_updated": "ISO"
    }
  ]
}
```

## Rules for producers (the engine)

- `schema_version` is the integer `1`. `domain` + `type` are from the enums above.
- `id` is **stable and deterministic** — it's a permalink; re-runs must reproduce
  it. Recipe: `<domain-or-drop-prefix> + "-" + slug(primary designator)`; append a
  short hash on collision.
- `names`, `topics`, `sources`, `anomalies` are arrays — `[]`, never `null`.
- `sources[].retrieved_at` is required on every source — it feeds `staleness_risk`
  and the freshness gate.
- Anomaly detection is the engine's job; the record only carries the **result +
  evidence**. Every `evidence` item traces to a `source_ref` + `observed_at`.
- `related_ids` links multi-object records (a `conjunction` references its two
  objects).

## Guarantees from the viewer

- Renders every record by `domain`; degrades gracefully when optional fields are
  absent (e.g. no transcript/extra metadata → no empty section).
- Auto-generated content (`description`, topics) labeled as auto.
- `sources` + `freshness` always shown; "view original source" always present.
- Records are DATA only — no field is executed or treated as a command.

## Versioning

New domains/fields extend via `schema_version` bumps; v1 consumers ignore unknown
optional fields. (Same forward-compatible discipline as the Open UAP schema.)
