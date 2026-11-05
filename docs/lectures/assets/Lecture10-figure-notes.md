# Lecture10 figure provenance

Run `python docs/lectures/assets/Lecture10-build-figures.py` with the Lab10
environment to recreate all 18 figures. The script needs GeoPandas, Shapely,
NumPy, SciPy and Matplotlib. No network downloads are used.

## Data figure

`Lecture10-parks.png` maps the unchanged `docs/data/ME_ImaginaryParks.geojson`
with the Maine outline from `docs/labs/ME_ShapeFiles`. It includes original and
generated occurrences. Labels identify imaginary parks, not real protected
areas. The inset locates the parks in Maine. EPSG:5070 is used for plotting and
the 20 km scale bar. The input hash and record totals are saved in
`Lecture10-example-results.json`. Rebuild after changing the input dataset.

`Lecture10-study-area.png` uses the same inputs in separate statewide and
enlarged park panels. The detail panel shows only occurrence points that
intersect the park polygons, including original and generated records. No
inset overlaps the park labels or sample points.

## Numerical teaching examples

- `Lecture10-matrix.svg` and `Lecture10-occupancy.svg` use the same four-park,
  five-species toy matrix saved in the results JSON. Species letters identify
  invented species; icons are schematic rather than identification guides.
- `Lecture10-richness.svg` illustrates the first two rows of that matrix with
  one icon per record: 8 A + 4 B (12 records, 2 species) versus 8 A + 4 B + 3 C
  (15 records, 3 species).
- `Lecture10-evenness.svg` compares [10,10,10] with [28,1,1]. Values come from
  SciPy entropy with natural logs; effective diversity is exp(H).
- `Lecture10-alpha-beta.svg` compares ABC/ABC/ABC with ABC/ADE/AFG. Both have
  mean alpha 3; gamma is 3 or 7; richness beta is gamma/mean alpha.
- `Lecture10-jaccard.svg` compares ABC with ACD: two shared species, union four,
  dissimilarity 0.5. `Lecture10-nestedness.svg` contrasts AB/ABCD with ABC/ACD;
  both have Jaccard 0.5, despite different species-list patterns.
- `Lecture10-bray-curtis.svg` uses [8,1,1] and [1,8,1]: Bray–Curtis 0.7, Jaccard 0.
- `Lecture10-record-totals.svg` uses [10,5,5] and [20,10,10]: raw Bray–Curtis 1/3,
  relative-frequency Bray–Curtis 0.
- `Lecture10-rarefaction.png` uses A=[25,25,25,25] and B=[195,1,1,1,1,1].
  Curves are exact expected richness from uniform draws without replacement:
  sum over species of [1 − choose(N−count,n)/choose(N,n)]. At n=100, the values
  are 4 and 3.5. These are not the Lab10 results. No confidence bands are drawn.
- WE and CWE slide values are calculated from the same toy occupancy matrix:
  Park 2 has WE=1.75, CWE=1.75/3; Park 3 has WE=1.25, CWE=1.25/2.
- `Lecture10-extent.svg` adds three occupied parks to a reference with one
  occupied park. Occupancy becomes four, so inverse occupancy changes from
  one to one quarter. Other species are omitted deliberately.

## Conceptual artwork

`Lecture10-endemism.svg` contrasts a rare island endemic with a rare but widely
distributed mainland species. Three symbols on each side illustrate low
abundance; the island species has a small range, while the mainland species
has a broad range. Symbols are a visual shorthand, not estimates of total
population sizes. The island, mainland and range shading are hypothetical;
no real species range or fitted distribution is shown.

The remaining SVGs illustrate SLOSS, habitat use, complementarity, and shape.
Circles in the SLOSS diagram have areas proportional to 1000, 400, 300 and
300 km². Blob/stripe ellipses have equal areas; stripe aspect ratio is 5:1.
Distances and habitat positions are schematic. These drawings are not the
actual assignment polygons. Habitat arrows are hypotheses about biological
requirements, not inferred movement. No artwork depicts an observed animal or
is taken from a publication. Literature links appear beside relevant claims
and in the lecture's two source slides.
