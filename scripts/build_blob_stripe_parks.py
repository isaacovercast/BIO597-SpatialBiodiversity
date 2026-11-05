"""Build the park-shape assignment dataset using Lab10's sampling method.

    python scripts/build_blob_stripe_parks.py

Two compact blobs and two 5:1 elliptical stripes each cover 500 km².
All parks are disjoint, within Maine and within the source sample bounds.
The shared sampler retains original records and adds empirical-template
occurrences, including 50 invented species, for 1,500 total points.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory

import geopandas as gpd
import numpy as np
from shapely import affinity
from shapely.geometry import Point, Polygon, box, mapping

if __package__:
    from .augment_imaginary_parks import augment_imaginary_parks
else:
    from augment_imaginary_parks import augment_imaginary_parks

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "docs/data/ME_BlobStripeParks.geojson"
AREA_CRS = "EPSG:5070"
PARK_AREA_KM2 = 500
DEFAULT_CENTERS = {
    "B1": (-70.40, 43.95),
    "B2": (-70.70, 44.30),
    "S1": (-70.60, 43.55),
    "S2": (-69.95, 44.45),
}
SPECS = [
    ("B1", "Alder Crown Preserve", "blob", 15),
    ("B2", "Hemlock Hollow Reserve", "blob", -10),
    ("S1", "Fern Ribbon Preserve", "stripe", 90),
    ("S2", "Silver Brook Reach", "stripe", 0),
]


def build_blob_stripe_parks(centers=None, output_path=DATASET, seed=597):
    """Return parks and occurrences; optionally save them as GeoJSON.

    centers maps B1, B2, S1 and S2 to (longitude, latitude) pairs. Omitted
    centers use the defaults. Areas, shapes and the lab's sampling settings
    stay fixed. Invalid locations raise an error rather than clipping parks.
    Pass output_path=None to experiment without writing a file.
    """
    centers = DEFAULT_CENTERS | (centers or {})
    if set(centers) != set(DEFAULT_CENTERS):
        raise ValueError("Park center IDs must be B1, B2, S1 and S2.")

    angles = np.arange(16) * 2 * np.pi / 16
    radii = np.array([1, .94, 1.1, 1.02, .91, 1.08, .95, 1.04,
                      1, .9, 1.06, 1.03, .96, 1.12, .98, .92])
    blob = Polygon(np.column_stack([np.cos(angles) * radii,
                                    np.sin(angles) * radii]))
    stripe = affinity.scale(Point(0, 0).buffer(1, quad_segs=64), xfact=5, yfact=1)

    source = gpd.read_file(ROOT / "docs/data/amphibians.geojson")
    sample_bounds = box(*source.total_bounds)
    maine = gpd.read_file(
        ROOT / "docs/labs/ME_ShapeFiles/Maine_State_Boundary.shp"
    ).to_crs(AREA_CRS).geometry.union_all()
    polygons = []
    features = []
    for park_id, name, design, rotation in SPECS:
        lon, lat = centers[park_id]
        center = gpd.GeoSeries([Point(lon, lat)], crs=4326).to_crs(AREA_CRS).iloc[0]
        template = blob if design == "blob" else stripe
        size = np.sqrt(PARK_AREA_KM2 * 1e6 / template.area)
        polygon = affinity.scale(template, xfact=size, yfact=size)
        polygon = affinity.rotate(polygon, rotation)
        polygon = affinity.translate(polygon, xoff=center.x, yoff=center.y)
        geographic = gpd.GeoSeries([polygon], crs=AREA_CRS).to_crs(4326).iloc[0]
        if not polygon.is_valid or not maine.covers(polygon):
            raise ValueError(f"{park_id}: park must be valid and entirely inside Maine.")
        if not sample_bounds.covers(geographic):
            raise ValueError(f"{park_id}: park extends beyond the source sample bounds.")
        if any(not polygon.disjoint(other) for other in polygons):
            raise ValueError(f"{park_id}: parks must not overlap or touch.")
        polygons.append(polygon)
        features.append(dict(
            type="Feature", geometry=mapping(geographic),
            properties=dict(
                feature_type="park", park_id=park_id, park_name=name,
                scenario=design, area_km2=PARK_AREA_KM2,
                center_lon=lon, center_lat=lat, fictional=True,
            ),
        ))

    # Use the same sampler as the lab, with a separate set of park polygons.
    with TemporaryDirectory() as temporary:
        park_file = Path(temporary) / DATASET.name
        park_file.write_text(json.dumps(dict(type="FeatureCollection", features=features)))
        return augment_imaginary_parks(
            input_path=park_file, output_path=output_path, seed=seed,
            total_records=1500, imaginary_species_count=50, buffer_km=50,
        )


if __name__ == "__main__":
    result = build_blob_stripe_parks()
    print(f"Saved {DATASET}: four parks and {sum(result.feature_type == 'occurrence')} occurrences.")
