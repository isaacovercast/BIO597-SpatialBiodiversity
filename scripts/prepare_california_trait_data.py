"""Prepare the three California tables used in Assignment 12.

Run from the repository root with the build environment:
    python scripts/prepare_california_trait_data.py
"""

from collections import Counter
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import rasterio
from rasterio.mask import mask
from shapely.geometry import box


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs/data"
OUTPUT = DATA / "Lab12"
TRAITS = ["MaxBody", "MinAgeMat", "MaxClutch", "MinSizeMat", "MinClutch"]
CRS = "EPSG:3310"
WIDTH = 30_000
NAME_CROSSWALK = {
    "Amerana aurora": "Rana aurora",
    "Amerana boylii": "Rana boylii",
    "Amerana cascadae": "Rana cascadae",
    "Amerana draytonii": "Rana draytonii",
    "Amerana muscosa": "Rana muscosa",
    "Amerana pretiosa": "Rana pretiosa",
    "Amerana sierrae": "Rana sierrae",
    "Aquarana catesbeiana": "Lithobates catesbeianus",
}
HABITATS = ["agriculture", "developed", "open_water", "other_natural",
            "upland_forest", "wetland", "introduced", "disturbed"]


def habitat_group(row):
    """Use the supplied USGS vegetation hierarchy, including flooded forests."""
    category = row["NVC_CLASS"]
    if pd.isna(category):
        return None
    direct = {
        "Agricultural & Developed Vegetation": "agriculture",
        "Developed & Other Human Use": "developed",
        "Open Water": "open_water",
        "Introduced & Semi Natural Vegetation": "introduced",
        "Recently Disturbed or Modified": "disturbed",
        "Aquatic Vegetation": "wetland",
    }
    if category in direct:
        return direct[category]
    form = str(row["NVC_FORM"]).lower()
    subclass = str(row["NVC_SUBCL"]).lower()
    wet_words = ["flooded", "swamp", "marsh", "bog", "fen", "mangrove"]
    if "wetland" in subclass or any(word in form for word in wet_words):
        return "wetland"
    if category == "Forest & Woodland":
        return "upland_forest"
    return "other_natural"


def main():
    OUTPUT.mkdir(exist_ok=True)
    records = gpd.read_file(DATA / "CA_amphibians.geojson")
    input_count = len(records)
    records = records[records.coordinateUncertaintyInMeters < 100].copy()
    records = records.dropna(subset=["species", "geometry"])
    records = records[records.species.str.strip() != ""]
    records["species"] = records.species.replace(NAME_CROSSWALK)
    records = records.to_crs(CRS)
    qc_count = len(records)

    # Use a fixed, meter-based California Albers lattice; retain full squares.
    records["col"] = np.floor(records.geometry.x / WIDTH).astype(int)
    records["row"] = np.floor(records.geometry.y / WIDTH).astype(int)
    records["site_id"] = records.col.astype(str) + "_" + records.row.astype(str)
    community = pd.crosstab(records.site_id, records.species)
    richness = (community > 0).sum(axis=1)
    community = community.loc[richness > 2]
    community = community.loc[:, community.sum() > 0]
    locations = records.drop_duplicates("site_id").set_index("site_id")
    locations = locations.loc[community.index]
    cells = []
    for site_id, location in locations.iterrows():
        x, y = location.col * WIDTH, location.row * WIDTH
        cells.append({"site_id": site_id, "xc": x + WIDTH / 2,
                      "yc": y + WIDTH / 2,
                      "geometry": box(x, y, x + WIDTH, y + WIDTH)})
    sites = gpd.GeoDataFrame(cells, crs=CRS).set_index("site_id")
    sites["n_records"] = community.sum(axis=1)
    sites["richness"] = (community > 0).sum(axis=1)
    midpoints = gpd.GeoSeries(gpd.points_from_xy(sites.xc, sites.yc), crs=CRS)
    sites["latitude"] = midpoints.to_crs(4326).y.to_numpy()

    # Means use the existing state-clipped climate layers, as in the Maine lab.
    for number in range(1, 20):
        with rasterio.open(DATA / f"bioclim_CA/wc2.1_2.5m_bio_{number}.tif") as raster:
            raster_sites = sites.to_crs(raster.crs)
            means = []
            for geometry in raster_sites.geometry:
                pixels, _ = mask(raster, [geometry], crop=True,
                                 filled=False, all_touched=True)
                values = pixels[0].compressed()
                means.append(float(values.mean()) if len(values) else np.nan)
            sites[f"bio_{number}"] = means
        print("Summarized BIO", number, flush=True)

    # Count equal-area 30 m pixel centers within the California part of each cell.
    california = gpd.read_file(DATA / "CA_ShapeFiles/California_State_Boundary.shp")
    california = california.to_crs(CRS)
    state_parts = sites.geometry.intersection(california.geometry.union_all())
    state_parts = gpd.GeoSeries(state_parts, crs=CRS)
    attributes = pd.read_csv(DATA / "CAHabitatMap/GAP_LANDFIRE_National_Terrestrial_Ecosystems_2011_Attributes.txt",
                             sep="\t")
    attributes["group"] = attributes.apply(habitat_group, axis=1)
    groups = attributes.set_index("Value")["group"].to_dict()
    habitat_rows = []
    unclassified = Counter()
    with rasterio.open(DATA / "CAHabitatMap/gaplf2011lc_v30_ca.tif") as raster:
        for i, geometry in enumerate(state_parts.to_crs(raster.crs)):
            pixels, _ = mask(raster, [geometry], crop=True, filled=False)
            codes, counts = np.unique(pixels[0].compressed(), return_counts=True)
            totals = Counter()
            for code, count in zip(codes, counts):
                group = groups.get(code)
                if group in HABITATS:
                    totals[group] += int(count)
                else:
                    unclassified[int(code)] += int(count)
            total = sum(totals.values())
            habitat_rows.append({f"habitat_{group}": totals[group] / total if total else np.nan
                                 for group in HABITATS})
            if (i + 1) % 50 == 0:
                print("Summarized habitat:", i + 1, "cells", flush=True)
    fractions = pd.DataFrame(habitat_rows, index=sites.index)
    sites = sites.join(fractions)

    # Export complete profiles only; incomplete species still count toward richness.
    trait_source = pd.read_csv(DATA / "AmphiTraits_Final.csv")
    trait_source["species_name"] = trait_source.Genus + " " + trait_source.species
    lookup = trait_source.set_index("species_name")
    selected = lookup.reindex(community.columns)[TRAITS]
    traits = selected.dropna()
    traits.index.name = "species"
    sites.to_file(OUTPUT / "CA_30KM_grid.geojson", driver="GeoJSON")
    community.to_csv(OUTPUT / "CA_Amphib_site_by_species.csv", index_label="site_id")
    traits.to_csv(OUTPUT / "CA_traits.csv", index_label="species")

    # Keep provenance and missing-trait details outside the student analysis code.
    known = (community[traits.index] > 0).sum(axis=1)
    functional = (known >= 3) & (known / sites.richness >= 0.8)
    unmatched = list(community.columns.difference(lookup.index))
    missing_lines = []
    for name, row in selected[selected.isna().any(axis=1)].iterrows():
        reason = "No matching trait row" if name in unmatched else ", ".join(row.index[row.isna()])
        missing_lines.append(f"| {name} | {int(community[name].sum())} | {reason} |")
    aliases = "\n".join(f"| {old} | {new} |" for old, new in NAME_CROSSWALK.items())
    notes = f"""# California prepared data for Assignment 12

Rebuild from the repository root with `python scripts/prepare_california_trait_data.py`
in the build environment. The script uses existing local data; no download is needed.

## Three analysis inputs

- `CA_30KM_grid.geojson`: {len(sites)} full 30 km squares in California Albers
  (EPSG:3310), keyed by `site_id`. Fields match the Maine grid: `xc`, `yc`,
  `n_records`, `richness`, `latitude`, `bio_1`–`bio_19`, and `habitat_` fractions.
- `CA_Amphib_site_by_species.csv`: {len(community)} site rows and {len(community.columns)}
  species columns, plus `site_id`. Values count occurrence records, not animals.
- `CA_traits.csv`: {len(traits)} species with all five positive traits, keyed by
  `species`: MaxBody, MinAgeMat, MaxClutch, MinSizeMat, MinClutch.

## Occurrences and grid

Start with the provided 71,578-record GBIF GeoJSON (`../CA_amphibians.geojson`).
Keep named occurrences with coordinate uncertainty strictly below 100 m;
missing uncertainty is excluded. This retains {qc_count:,} records. Keep repeated
records, reconcile the exact full names below, and assign points to squares on
a 30,000 m lattice with origin (0, 0) in EPSG:3310. Retain cells with more than
two species: {int(sites.n_records.sum()):,} records remain in the exported cells.
Do not interpret record totals as animal abundance.

All species in these cells remain in the community matrix and richness counts,
including species missing traits. The trait CSV contains complete profiles only.
With a minimum of three trait-covered species and 80% coverage, {int(functional.sum())}
cells qualify for functional analyses. These filters should also be applied in
the assignment. No trait imputation or synthetic occurrences are used.

| Occurrence name | Trait-table name |
| --- | --- |
{aliases}

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
mapped area. Counts of excluded valid codes: `{dict(unclassified)}`.

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
Only {', '.join(unmatched)} have no matching row; the other excluded species
have a row but at least one missing trait.

| Species | Records in retained cells | Missing traits or reason |
| --- | ---: | --- |
{chr(10).join(missing_lines)}

## Sources

- Occurrence sample and boundary/climate preparation: [California data notes](../CA_data_README.md).
- GBIF download: [10.15468/dl.wbj54a](https://doi.org/10.15468/dl.wbj54a).
- Traits: [AmphiTraits](https://doi.org/10.5066/P135WFOE), supplied `../AmphiTraits_Final.csv`.
- Habitat: supplied GAP/LANDFIRE National Terrestrial Ecosystems 2011 raster and legend.
"""
    (OUTPUT / "CA_preprocessing.md").write_text(notes)
    print(f"Wrote {len(sites)} cells, {len(community.columns)} species, {len(traits)} complete profiles; "
          f"{int(functional.sum())} cells pass functional coverage filters.", flush=True)


if __name__ == "__main__":
    main()
