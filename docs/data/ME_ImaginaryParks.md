# Imaginary Maine parks for Lab 10

`ME_ImaginaryParks.geojson` contains **four fixed imaginary park polygons and
1,500 occurrence points representing 67 species**: 17 observed species names
and **50 invented species**. It preserves all **846 real in-park records** from
`amphibians.geojson` and adds **654 simulated points**. Coordinates are WGS84
longitude/latitude (EPSG:4326).

| Park | Strategy | Area (km²) | Records | Species |
| --- | --- | ---: | ---: | ---: |
| SL — Alder Basin Preserve | single_large | 1,000 | 819 | 55 |
| SS1 — Fern Hollow Woods | several_small | 400 | 252 | 42 |
| SS2 — Coldwater Ridge Preserve | several_small | 300 | 192 | 49 |
| SS3 — Spruce Lantern Reserve | several_small | 300 | 237 | 47 |
| Three small parks pooled | several_small | 1,000 | 681 | 60 |

Park boundaries and locations are unchanged. Every occurrence has its
`park_id`, `park_name`, and `scenario` assignment already stored.

## Empirical range and abundance templates

1. Load all **14,577 real occurrences** in `amphibians.geojson`. Retain the 846
   in-park records with their coordinates, GBIF IDs, species names, and other
   source attributes unchanged.
2. For every observed species, calculate the convex hull of all its source
   points and buffer it by **50 km** in EPSG:26919 (NAD83 / UTM zone 19N).
   One-point hulls become circles and two-point hulls become buffered lines.
3. For each invented species, **sample one observed donor species uniformly
   with replacement**. Donors must have a buffered hull intersecting at least
   one park. The invented species inherits the donor's **buffered geographic
   range and statewide record count together**. This samples the empirical
   species-level distribution, including rare species, without imposing a
   separate lognormal model or weighting common donors twice.
4. Reserve **one point per invented species**, ensuring that all 50 appear.
   Allocate the remaining **604 points** proportionally among real and invented
   species using observed record counts and inherited donor counts as weights.
   Use largest-remainder rounding to make the final total exactly 1,500.
5. Sample uniformly within each species' buffered range intersected with the
   four parks. Choose among park pieces in proportion to eligible area and
   sample uniformly inside the chosen piece. Invented species use their
   donor's range; simulated records of real species use their own range.

The abundance weights come from the observations, while the minimum of one
record per invented species guarantees representation at this small sample
size. Final species totals also include the original local observations.
Some observed species receive zero added points after rounding. No park
richness targets are imposed. Range overlap, geometry and sampling determine
which parks share species.

Seed **597** makes the bootstrap and point sampling reproducible. Invented
names use the genera `Imaginarana`, `Fictotriton`, and `Sylvophantoma`.
The added points are an instructional simulation, not new observations or a
habitat-suitability model.

The FeatureCollection's `simulation` metadata records the donor for each invented
species, abundance weights, source and added counts, eligible areas, CRS, buffer
distance, and seed. Buffered hulls are not added as features to this file; it
still contains only four park polygons and the occurrence points.

## Provenance

- `feature_type`: `park` or `occurrence`.
- `synthetic`: `false` for the 846 source occurrences, `true` for added points.
- `imaginary_species`: `true` only for the 50 invented taxa. Simulated points
  using an observed species name have `synthetic=true`, `imaginary_species=false`.
- `donor_species`: the observed range/abundance template for each added point;
  for simulated records of an observed taxon, this is its own species name.
- `record_source`: `amphibians.geojson` or `convex_hull_buffer_simulation`.
- Synthetic `occurrenceID` values start with `SYNTH-ME-`; synthetic `gbifID`
  values are unique negative placeholders, not real GBIF keys.
- Synthetic `year` and `coordinateUncertaintyInMeters` are `null` because
  there is no survey event or measured coordinate uncertainty.

The `fictional` field refers to the park design. Park properties include
`area_km2`, `center_lon`, and `center_lat`.

## Rebuild and experiment

To regenerate records while keeping the current parks fixed:

```sh
python scripts/augment_imaginary_parks.py
```

The function always reloads real records from `amphibians.geojson`; existing
occurrences in the input park file are ignored. Rerunning replaces the previous
augmentation rather than adding to it.

```python
from scripts.augment_imaginary_parks import augment_imaginary_parks

features = augment_imaginary_parks(
    total_records=1500,
    imaginary_species_count=50,
    buffer_km=50,
)
```

This returns a GeoDataFrame without saving. Supply `output_path` to save an
experiment separately. Other parameters are `input_path` (the park file),
`source_path` (real occurrences), and `seed`. Set `imaginary_species_count=0`
to use observed species only. Up to 50 invented species names are available.

The requested total must accommodate all original in-park records plus one
record for every invented species. Invalid totals or a positive allocation
without eligible park area raise `ValueError` before saving.

The park-building function remains available for separate placement experiments:

```python
from scripts.build_imaginary_parks import build_imaginary_parks

centers = {
    "SL": (-70.40, 43.95),
    "SS1": (-70.65, 43.48),
    "SS2": (-69.95, 44.35),
    "SS3": (-70.70, 44.30),
}
features = build_imaginary_parks(centers, output_path="park_experiment.geojson")
```

Centers are `(longitude, latitude)` in degrees. Areas and shapes stay fixed.
The builder checks validity, area, non-overlap, and containment inside Maine
and the sample bounds. The Maine boundary source is documented in
[`../labs/ME_ShapeFiles/README.md`](../labs/ME_ShapeFiles/README.md).
