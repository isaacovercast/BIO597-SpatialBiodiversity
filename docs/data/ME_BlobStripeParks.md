# Blob and stripe parks

`ME_BlobStripeParks.geojson` supports Assignment 11. It contains four fictional
park polygons and 1,500 amphibian occurrence points. Every point has a
`park_id`, `park_name`, and `scenario` (`blob` or `stripe`); no spatial join is
needed in the assignment.

| ID | Fictional park | Design | Area (km²) |
| --- | --- | --- | --- |
| B1 | Alder Crown Preserve | Blob | 500 |
| B2 | Hemlock Hollow Reserve | Blob | 500 |
| S1 | Fern Ribbon Preserve | Stripe | 500 |
| S2 | Silver Brook Reach | Stripe | 500 |

Blobs are roughly round, irregular polygons. Stripes are ellipses with a 5:1
ratio of major to minor axes, with different orientations. Each design protects
1,000 km² across two parks. Parks are disjoint and entirely within Maine and
the bounding box of the source occurrences. Areas are set in EPSG:5070.

## Occurrence sampling

The procedure is the same as for Lab10:

1. Retain every original `amphibians.geojson` record inside a park (629 records).
2. Use **all 14,577 source records** to calculate each observed species' convex
   hull, buffer it by 50 km in EPSG:26919, and obtain its statewide record count.
3. For each of 50 invented species, randomly choose an observed donor species
   uniformly with replacement from donors whose buffered hull intersects a
   park. Inherit both the donor's buffered range and its record-count weight.
4. Reserve one point for each invented species. Allocate the remaining additions
   proportionally to observed and inherited counts using largest-remainder
   rounding. Original records are retained rather than reallocated.
5. Sample added points uniformly within the appropriate buffered range's
   intersection with the parks. Allocate points among parks in proportion to
   eligible intersection area. Stop at 1,500 total records (871 additions).

The seed is 597. There is no preferred park design in the sampler. Geographic
intersections and original reporting patterns can produce differences between
designs. The simulation does not model survival, movement, edge effects, or
population abundance. Buffered hulls are teaching approximations, not fitted
habitat or distribution models. Source species names are retained as supplied.

`synthetic` marks generated points; `imaginary_species` marks invented taxa.
Generated records identify their range template in `donor_species`. The
GeoJSON's top-level `simulation` object records parameters, donor mappings,
source counts, and added counts. The original Lab10 dataset is separate.

## Rebuild

From the repository root, using the lab's Python environment:

```bash
python scripts/build_blob_stripe_parks.py
```

The builder calls `augment_imaginary_parks` with the same settings as Lab10.
Its `build_blob_stripe_parks(centers=None, output_path=..., seed=597)` function
also accepts alternative center coordinates keyed by B1, B2, S1, and S2;
invalid placements are rejected rather than clipped. Use `output_path=None`
to return an experimental dataset without saving it.
