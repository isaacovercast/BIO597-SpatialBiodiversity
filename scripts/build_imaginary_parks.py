"""Create fictional SLOSS reserves and select their amphibian occurrence records.

Run from any directory to rebuild the parks with original occurrences only:
    python scripts/build_imaginary_parks.py

Then augment to 1,500 records with 50 invented species based on observed data:
    python scripts/augment_imaginary_parks.py

From Python in the repository root:
    from scripts.build_imaginary_parks import build_imaginary_parks
    features = build_imaginary_parks({
        "SL": (-70.40, 43.95),
        "SS1": (-70.65, 43.48),
        "SS2": (-69.95, 44.35),
        "SS3": (-70.70, 44.30),
    })

Requires GeoPandas, NumPy, Shapely, and PyProj.
"""
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
from shapely.affinity import rotate, scale, translate
from shapely.geometry import Point, Polygon, box, mapping

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "docs" / "data"
AREA_CRS = "EPSG:5070"  # Equal-area Albers, in meters.
# Group parks in the more densely sampled southern and western interior.
DEFAULT_CENTERS = {
    "SL": (-70.40, 43.95),
    "SS1": (-70.65, 43.48),
    "SS2": (-69.95, 44.35),
    "SS3": (-70.70, 44.30),
}
# ID, name, strategy, area in km², rotation in degrees.
SPECS = [
    ("SL", "Alder Basin Preserve", "single_large", 1000, 15),
    ("SS1", "Fern Hollow Woods", "several_small", 400, -20),
    ("SS2", "Coldwater Ridge Preserve", "several_small", 300, 30),
    ("SS3", "Spruce Lantern Reserve", "several_small", 300, -10),
]


def build_imaginary_parks(centers=None, output_path=None):
    """Return park polygons and their occurrence records as a WGS84 GeoDataFrame.

    centers: dict mapping SL, SS1, SS2, SS3 to (longitude, latitude) in degrees.
        Omit to use DEFAULT_CENTERS. Areas, names, and shapes stay fixed.
    output_path: optional GeoJSON filename, relative to the working directory
        or absolute. Omit to experiment without writing a file.

    Parks must be disjoint and entirely inside Maine and the source sample
    bounding box. Invalid placements raise ValueError before writing anything.
    Parks without occurrence records are allowed. Boundary points are included.
    """
    if centers is None:
        centers = DEFAULT_CENTERS
    if set(centers) != set(DEFAULT_CENTERS):
        raise ValueError("Provide four centers keyed by SL, SS1, SS2, and SS3.")

    source = json.loads((DATA / "amphibians.geojson").read_text())
    occurrences = gpd.GeoDataFrame.from_features(source["features"], crs=4326)
    projected = occurrences.to_crs(AREA_CRS)
    maine = gpd.read_file(
        ROOT / "docs/labs/ME_ShapeFiles/Maine_State_Boundary.shp"
    ).to_crs(AREA_CRS).geometry.union_all()
    sample_bounds = box(*occurrences.total_bounds)
    angles = np.arange(16) * 2 * np.pi / 16
    radii = np.array([1, .94, 1.1, 1.02, .91, 1.08, .95, 1.04,
                      1, .9, 1.06, 1.03, .96, 1.12, .98, .92])
    template = Polygon(np.c_[np.cos(angles) * radii * 1.18,
                             np.sin(angles) * radii * .86])

    parks, park_features, assignments = [], [], {}
    for park_id, name, scenario, area, rotation in SPECS:
        lon, lat = centers[park_id]
        center = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(AREA_CRS).iloc[0]
        factor = np.sqrt(area * 1_000_000 / template.area)
        polygon = translate(rotate(scale(template, xfact=factor, yfact=factor,
                                        origin=(0, 0)), rotation, origin=(0, 0)),
                            center.x, center.y)
        geographic = gpd.GeoSeries([polygon], crs=AREA_CRS).to_crs(4326).iloc[0]
        # Check the same geometry students will load from the exported file.
        roundtrip = gpd.GeoSeries([geographic], crs=4326).to_crs(AREA_CRS).iloc[0]
        if not roundtrip.is_valid or roundtrip.geom_type != "Polygon":
            raise ValueError(f"{name}: invalid polygon; check longitude/latitude order.")
        if not maine.covers(roundtrip):
            raise ValueError(f"{name}: polygon extends outside Maine; move its center inland.")
        if not sample_bounds.covers(geographic):
            raise ValueError(f"{name}: polygon extends outside the sample bounding box.")
        if not np.isclose(roundtrip.area / 1e6, area, rtol=0, atol=1e-6):
            raise ValueError(f"{name}: projected area differs from {area} km².")
        if any(not roundtrip.disjoint(other) for other in parks):
            raise ValueError(f"{name}: overlaps or touches another park; move the centers apart.")
        parks.append(roundtrip)

        properties = dict(feature_type="park", park_id=park_id, park_name=name,
                          scenario=scenario, area_km2=area,
                          center_lon=lon, center_lat=lat, fictional=True)
        park_features.append(dict(type="Feature", properties=properties,
                                  geometry=mapping(geographic)))
        members = projected.index[projected.geometry.intersects(roundtrip)]
        for index in members:
            assignments[index] = properties

    point_features = []
    for index, feature in enumerate(source["features"]):
        if index in assignments:
            feature["properties"].update({
                key: assignments[index][key]
                for key in ["park_id", "park_name", "scenario", "fictional"]
            })
            feature["properties"]["feature_type"] = "occurrence"
            point_features.append(feature)
    result = dict(type="FeatureCollection", name="ME_ImaginaryParks",
                  features=park_features + point_features)
    if output_path is not None:
        Path(output_path).write_text(
            json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
            encoding="utf-8",
        )
    return gpd.GeoDataFrame.from_features(result["features"], crs=4326)


def main():
    output = DATA / "ME_ImaginaryParks.geojson"
    features = build_imaginary_parks(output_path=output)
    parks = features[features.feature_type == "park"]
    records = features[features.feature_type == "occurrence"]
    counts = records.groupby("park_id").size()
    for park in parks.itertuples():
        print(f"{park.park_name}: {park.area_km2:g} km²; "
              f"{counts.get(park.park_id, 0)} records")
    print(f"Wrote {output}: {len(parks)} polygons + {len(records)} original points")


if __name__ == "__main__":
    main()
