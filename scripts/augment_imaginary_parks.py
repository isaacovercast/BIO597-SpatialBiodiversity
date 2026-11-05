"""Augment amphibian records and invented species using observed species templates.

    python scripts/augment_imaginary_parks.py

Park polygons are read unchanged from ME_ImaginaryParks.geojson. All source
records in amphibians.geojson determine species hulls and proportional sample
sizes. Invented species inherit a sampled observed species' buffered hull and
abundance weight. The result contains 1,500 in-park occurrences, including all
original in-park records and 50 invented species. Previous simulations are
discarded on every run.
"""
import copy
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.geometry import Point, mapping

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "docs/data/ME_ImaginaryParks.geojson"
SOURCE = ROOT / "docs/data/amphibians.geojson"
DISTANCE_CRS = "EPSG:26919"  # NAD83 / UTM zone 19N; meters, appropriate for Maine.
SEED = 597
TOTAL_RECORDS = 1500
BUFFER_KM = 50
IMAGINARY_SPECIES_COUNT = 50
IMAGINARY_SPECIES = [
    "Imaginarana aurora", "Imaginarana betulina", "Imaginarana caliginosa",
    "Imaginarana dewfalli", "Imaginarana emberi", "Imaginarana fernensis",
    "Imaginarana granitica", "Imaginarana humicola", "Imaginarana iris",
    "Imaginarana juniperi", "Imaginarana lacustrina", "Imaginarana muscosa",
    "Imaginarana nebulosa", "Imaginarana opalina",
    "Fictotriton alderi", "Fictotriton brookii", "Fictotriton copperi",
    "Fictotriton duskensis", "Fictotriton evergreenii", "Fictotriton foggi",
    "Fictotriton hemlocki", "Fictotriton ivoryi", "Fictotriton lanterni",
    "Fictotriton moonensis", "Fictotriton northwoodi", "Fictotriton peatensis",
    "Fictotriton quartzicola", "Fictotriton rainensis",
    "Sylvophantoma argentea", "Sylvophantoma brumalis", "Sylvophantoma cedrina",
    "Sylvophantoma dolina", "Sylvophantoma echinata", "Sylvophantoma flammea",
    "Sylvophantoma glacialina", "Sylvophantoma hazelii", "Sylvophantoma inverna",
    "Sylvophantoma kettleii", "Sylvophantoma lichenosa", "Sylvophantoma mapleii",
    "Sylvophantoma noctiluca", "Sylvophantoma sprucea",
    "Imaginarana rivularis", "Imaginarana starlighti", "Fictotriton thorni",
    "Fictotriton vernalensis", "Sylvophantoma willowii", "Sylvophantoma zephyra",
    "Fictotriton wetlandii", "Imaginarana umbrina",
]


def augment_imaginary_parks(input_path=DATASET, output_path=None, seed=SEED,
                            total_records=TOTAL_RECORDS, buffer_km=BUFFER_KM,
                            source_path=SOURCE, imaginary_species_count=IMAGINARY_SPECIES_COUNT):
    """Return park polygons and augmented records as a WGS84 GeoDataFrame.

    Keep the four input park polygons. Restore their real records directly
    from source_path, ignoring all existing input occurrences. Use ALL source
    records to build each species' convex hull and buffer it by buffer_km.
    Each invented species samples an observed donor uniformly with replacement,
    inheriting BOTH its buffered hull and statewide count as an abundance weight.
    Only donors whose buffered hull intersects a park are eligible.
    Reserve one point per invented species, then allocate the remaining extra
    points proportionally to the real and inherited abundance weights using
    largest-remainder rounding. Sample uniformly within each buffered hull's
    intersection with the parks. All original in-park records are retained.

    Omitting output_path returns the result without saving. Repeated runs
    with the same parks, source, parameters and seed produce the same result.
    """
    if not np.isfinite(buffer_km) or buffer_km <= 0:
        raise ValueError("buffer_km must be finite and positive.")
    if total_records != int(total_records) or total_records < 0:
        raise ValueError("total_records must be a nonnegative integer.")
    total_records = int(total_records)
    if imaginary_species_count != int(imaginary_species_count) or not 0 <= imaginary_species_count <= len(IMAGINARY_SPECIES):
        raise ValueError(f"imaginary_species_count must be an integer from 0 to {len(IMAGINARY_SPECIES)}.")
    imaginary_species_count = int(imaginary_species_count)
    dataset = json.loads(Path(input_path).read_text(encoding="utf-8"))
    park_features = [copy.deepcopy(f) for f in dataset["features"]
                     if f["properties"].get("feature_type") == "park"]
    parks = gpd.GeoDataFrame.from_features(park_features, crs=4326).set_index("park_id")
    if len(parks) != 4 or not parks.index.is_unique or parks.index.hasnans:
        raise ValueError("Expected four parks with unique, nonmissing park IDs.")
    projected_parks = parks.to_crs(DISTANCE_CRS)

    source_features = json.loads(Path(source_path).read_text(encoding="utf-8"))["features"]
    source = gpd.GeoDataFrame.from_features(source_features, crs=4326).to_crs(DISTANCE_CRS)
    if source.empty:
        raise ValueError("The source occurrence dataset is empty.")

    # Restore the original in-park records from the real source dataset.
    assignments = {}
    for park_id, park in projected_parks.iterrows():
        members = source.index[source.geometry.intersects(park.geometry)]
        for index in members:
            if index in assignments:
                raise ValueError("An original record belongs to overlapping parks.")
            assignments[index] = park_id
    originals = []
    for index, feature in enumerate(source_features):
        if index in assignments:
            park_id = assignments[index]
            original = copy.deepcopy(feature)
            original["properties"].update(
                park_id=park_id, park_name=parks.loc[park_id, "park_name"],
                scenario=parks.loc[park_id, "scenario"], fictional=True,
                feature_type="occurrence", synthetic=False, imaginary_species=False,
                record_source=Path(source_path).name,
            )
            originals.append(original)
    if total_records < len(originals):
        raise ValueError(f"total_records must include all {len(originals)} original in-park records.")

    source_counts = source.species.value_counts().sort_index()
    park_ids = list(projected_parks.index)
    pieces_by_source = {}
    eligible_areas = {}
    for species in source_counts.index:
        observed = source[source.species == species]
        buffered_hull = observed.geometry.union_all().convex_hull.buffer(buffer_km * 1000)
        pieces = [buffered_hull.intersection(projected_parks.loc[p, "geometry"])
                  for p in park_ids]
        pieces_by_source[species] = pieces
        eligible_areas[species] = sum(piece.area for piece in pieces) / 1e6

    rng = np.random.default_rng(seed)
    imaginary = IMAGINARY_SPECIES[:imaginary_species_count]
    donor_pool = [species for species in source_counts.index if eligible_areas[species] > 0]
    if imaginary and not donor_pool:
        raise ValueError("No observed species' buffered hull intersects the parks.")
    donor_species = dict(zip(imaginary, rng.choice(donor_pool, len(imaginary), replace=True)))
    abundance_weights = source_counts.copy()
    for species, donor in donor_species.items():
        abundance_weights.loc[species] = source_counts[donor]

    n_added = total_records - len(originals)
    if n_added < imaginary_species_count:
        raise ValueError(f"Need at least {len(originals) + imaginary_species_count} records to retain originals and include every invented species.")
    # Guarantee representation of all invented taxa, then apportion the rest.
    proportional_budget = n_added - imaginary_species_count
    expected = proportional_budget * abundance_weights / abundance_weights.sum()
    added_counts = np.floor(expected).astype(int)
    remainder = proportional_budget - added_counts.sum()
    order = np.argsort(-(expected - added_counts).to_numpy(), kind="stable")
    added_counts.iloc[order[:remainder]] += 1
    for species in imaginary:
        added_counts.loc[species] += 1

    simulated = []
    for species, count in added_counts.items():
        donor = donor_species.get(species, species)
        pieces = pieces_by_source[donor]
        areas = np.array([piece.area for piece in pieces])
        if count == 0:
            continue
        if areas.sum() == 0:
            raise ValueError(f"{species}: the donor's buffered hull does not intersect any park.")
        # Area-weighted pieces give uniform sampling across the intersection.
        allocations = rng.multinomial(int(count), areas / areas.sum())
        for park_id, polygon, n_points in zip(park_ids, pieces, allocations):
            if n_points == 0:
                continue
            xmin, ymin, xmax, ymax = polygon.bounds
            locations = []
            while len(locations) < n_points:
                point = Point(rng.uniform(xmin, xmax), rng.uniform(ymin, ymax))
                if polygon.contains(point):
                    locations.append(point)
            geographic = gpd.GeoSeries(locations, crs=DISTANCE_CRS).to_crs(4326)
            for point in geographic:
                serial = len(simulated) + 1
                properties = dict(
                    gbifID=-serial, occurrenceID=f"SYNTH-ME-{serial:06d}",
                    species=species, decimalLongitude=point.x, decimalLatitude=point.y,
                    coordinateUncertaintyInMeters=None, year=None,
                    park_id=park_id, park_name=parks.loc[park_id, "park_name"],
                    scenario=parks.loc[park_id, "scenario"], fictional=True,
                    feature_type="occurrence", synthetic=True, imaginary_species=species in donor_species,
                    donor_species=donor,
                    record_source="convex_hull_buffer_simulation",
                )
                simulated.append(dict(type="Feature", properties=properties,
                                      geometry=mapping(point)))

    result = dict(
        type="FeatureCollection", name=Path(input_path).stem,
        simulation=dict(
            method="empirical_species_templates_and_buffered_hulls", seed=seed,
            buffer_km=buffer_km, distance_crs=DISTANCE_CRS,
            source_file=Path(source_path).name, source_records=len(source),
            original_in_park_records=len(originals), synthetic_records=len(simulated),
            total_records=total_records, imaginary_species_count=imaginary_species_count,
            donor_sampling="observed species sampled uniformly with replacement; buffered hull must intersect parks; range and abundance inherited together",
            donor_species=donor_species,
            allocation="one point per invented species; remaining additions proportional to observed and donor counts; largest-remainder rounding",
            abundance_weights={species: int(count) for species, count in abundance_weights.items()},
            spatial_sampling="uniform within buffered species hull intersected with the four parks",
            source_species_counts={species: int(count) for species, count in source_counts.items()},
            added_species_counts={species: int(count) for species, count in added_counts.items()},
            eligible_area_km2={species: float(eligible_areas[donor_species.get(species, species)])
                               for species in abundance_weights.index},
        ),
        features=park_features + originals + simulated,
    )
    if output_path is not None:
        Path(output_path).write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    return gpd.GeoDataFrame.from_features(result["features"], crs=4326)


def main():
    features = augment_imaginary_parks(output_path=DATASET)
    records = features[features.feature_type == "occurrence"]
    print(records.groupby("park_id").agg(records=("species", "size"), species=("species", "nunique")))
    print(records.groupby("scenario").agg(records=("species", "size"), species=("species", "nunique")))
    print(f"Wrote {DATASET}: {len(records)} records and {records.species.nunique()} species")


if __name__ == "__main__":
    main()
