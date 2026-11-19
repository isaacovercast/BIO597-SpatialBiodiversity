# California prepared data for Assignment 12

Rebuild from the repository root with `python scripts/prepare_california_trait_data.py`
in the build environment. The script uses existing local data; no download is needed.

## Three analysis inputs

- `CA_30KM_grid.geojson`: 259 full 30 km squares in California Albers
  (EPSG:3310), keyed by `site_id`. Fields match the Maine grid: `xc`, `yc`,
  `n_records`, `richness`, `latitude`, `bio_1`–`bio_19`, and `habitat_` fractions.
- `CA_Amphib_site_by_species.csv`: 259 site rows and 70
  species columns, plus `site_id`. Values count occurrence records, not animals.
- `CA_traits.csv`: 30 species with all five positive traits, keyed by
  `species`: MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch.

## Occurrences and grid

Start with the provided 71,578-record GBIF GeoJSON (`../CA_amphibians.geojson`).
Keep named occurrences with coordinate uncertainty strictly below 100 m;
missing uncertainty is excluded. This retains 21,303 records. Keep repeated
records, reconcile the exact full names below, and assign points to squares on
a 30,000 m lattice with origin (0, 0) in EPSG:3310. Retain cells with more than
two species: 20,812 records remain in the exported cells.
Do not interpret record totals as animal abundance.

All species in these cells remain in the community matrix and richness counts,
including species missing traits. The trait CSV contains complete profiles only.
With a minimum of three trait-covered species and 80% coverage, 127
cells qualify for functional analyses. These filters should also be applied in
the assignment. No trait imputation or synthetic occurrences are used.

| Occurrence name | Trait-table name |
| --- | --- |
| Amerana aurora | Rana aurora |
| Amerana boylii | Rana boylii |
| Amerana cascadae | Rana cascadae |
| Amerana draytonii | Rana draytonii |
| Amerana muscosa | Rana muscosa |
| Amerana pretiosa | Rana pretiosa |
| Amerana sierrae | Rana sierrae |
| Aquarana catesbeiana | Lithobates catesbeianus |

The aliases reconcile these supplied tables; they do not revise taxonomy generally.
No related species are substituted for missing trait profiles.

## Climate, latitude, and habitat

The midpoint latitude is calculated from the full square center in EPSG:4326.
WorldClim 2.1 2.5 arc-minute `../bioclim_CA` rasters contain 1970–2000 normals.
Each BIO field averages valid pixels intersecting the square, with edge pixels
included equally (`all_touched=True`), as in the Maine data. Native values and
units are retained; BIO4 is temperature SD multiplied by 100.

Habitat is from `../CAHabitatMap/gaplf2011lc_v30_ca.tif` and the supplied
`GAP_LANDFIRE_National_Terrestrial_Ecosystems_2011_Attributes.txt` legend.
Count equal-area 30 m pixel centers within each cell's intersection with the
California boundary. Fractions sum to one over classified pixels, including
mapped water. NoData and code 0 are excluded. These are fractions of mapped
habitat area, not fractions of occurrence records. Coastal cells have less
mapped area. Counts of excluded valid codes: `{0: 1303}`.

The map uses a different classification and date from Maine's. The explicit
broad crosswalk is:

| Field | Supplied USGS classification |
| --- | --- |
| habitat_agriculture | Agricultural & Developed Vegetation |
| habitat_developed | Developed & Other Human Use, including mines |
| habitat_open_water | Open Water |
| habitat_wetland | Aquatic Vegetation; wetland subclasses; flooded, swamp, marsh, bog, fen, and mangrove formations |
| habitat_upland_forest | Remaining Forest & Woodland |
| habitat_other_natural | Remaining shrub/herb, desert, alpine, rock and barren classes |
| habitat_introduced | Introduced & Semi Natural Vegetation |
| habitat_disturbed | Recently Disturbed or Modified |

The first six fields follow the Maine structure. Two additional fields retain
introduced and recently disturbed vegetation without calling them natural habitat.
These broad groups support analogous analyses, not exact equivalence between maps.

## Species without complete profiles

Missing values are not zeros. A matching trait row may still be incomplete.
Only Osteopilus septentrionalis, Xenopus laevis have no matching row; the other excluded species
have a row but at least one missing trait.

| Species | Records in retained cells | Missing traits or reason |
| --- | ---: | --- |
| Ambystoma mavortium | 3 | MinSizeMat |
| Ambystoma tigrinum | 3 | MinAgeMat, MinSizeMat |
| Anaxyrus punctatus | 99 | MinClutch |
| Anaxyrus woodhousii | 19 | MinSizeMat |
| Aneides flavipunctatus | 194 | MinSizeMat |
| Aneides iecanus | 21 | MinAgeMat, MaxClutch, MinClutch |
| Aneides klamathensis | 7 | MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Aneides lugubris | 953 | MinSizeMat |
| Aneides niger | 4 | MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps altasierrae | 11 | MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps bramei | 13 | MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps campi | 11 | MaxClutch, MinClutch |
| Batrachoseps diabolicus | 40 | MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps gavilanensis | 111 | MaxClutch, MinClutch |
| Batrachoseps incognitus | 3 | MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps kawia | 7 | MaxBody, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps luciae | 27 | MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps minor | 12 | MaxClutch, MinClutch |
| Batrachoseps regius | 5 | MaxBody, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps relictus | 3 | MaxBody, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps robustus | 10 | MaxBody, MaxClutch, MinSizeMat, MinClutch |
| Batrachoseps simatus | 5 | MaxClutch, MinSizeMat, MinClutch |
| Hydromantes brunus | 24 | MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Hydromantes platycephalus | 54 | MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Hydromantes samweli | 13 | MinAgeMat, MaxClutch, MinClutch |
| Hydromantes shastae | 4 | MinAgeMat |
| Hydromantes wintu | 2 | MinAgeMat, MaxClutch, MinClutch |
| Lithobates berlandieri | 5 | MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Osteopilus septentrionalis | 1 | No matching trait row |
| Plethodon asupak | 1 | MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch |
| Plethodon elongatus | 27 | MinAgeMat |
| Rana aurora | 5 | MinSizeMat |
| Rana sierrae | 40 | MinAgeMat |
| Rhyacotriton variegatus | 2 | MinSizeMat |
| Spea hammondii | 21 | MinAgeMat, MinSizeMat |
| Spea intermontana | 12 | MinAgeMat, MinSizeMat |
| Taricha granulosa | 824 | MaxClutch, MinClutch |
| Taricha rivularis | 11 | MaxClutch, MinClutch |
| Taricha sierrae | 193 | MinClutch |
| Xenopus laevis | 166 | No matching trait row |

## Sources

- Occurrence sample and boundary/climate preparation: [California data notes](../CA_data_README.md).
- GBIF download: [10.15468/dl.wbj54a](https://doi.org/10.15468/dl.wbj54a).
- Traits: [AmphiTraits](https://doi.org/10.5066/P135WFOE), supplied `../AmphiTraits_Final.csv`.
- Habitat: supplied GAP/LANDFIRE National Terrestrial Ecosystems 2011 raster and legend.
