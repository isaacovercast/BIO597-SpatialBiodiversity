# Lecture 12: figure provenance

Figures combine course illustrations,
public-domain species photographs, and calculations from the supplied prepared data. The California analytical results
are reserved for the instructor answer key; the lecture uses Maine results and
a California trait-coverage map.

## Rebuild

From the repository root, using the build environment:

```bash
MPLCONFIGDIR=/tmp/lecture12-mpl python docs/lectures/assets/Lecture12-build-figures.py
```

This reads `docs/data/Lab12/ME_30KM_grid.geojson`,
`ME_Amphib_site_by_species.csv`, and `ME_traits.csv`; the analogous California
files; and the existing state boundaries. It does not fetch data or change the
notebooks. PNGs and `Lecture12-example-results.json` are written beside this file.
The frog illustration and downloaded species photographs are retained as separate
assets; the rebuild script does not overwrite them. Visible figure captions and
lecture `<aside>` elements have been removed. This file retains figure provenance.
The correlation figure is extracted from the notebook's saved Step 4 output;
rerun that notebook cell and save the notebook before rebuilding to update it.

## Frog illustration and species photographs

The opening slide and the later mean-versus-spread comparison use
`Lecture12-frog-trait-space.png`, created with the built-in image-generation tool
by editing the original `Lecture12-mean-spread.png` schematic. Frogs illustrate
body size and skin rugosity qualitatively. They are imaginary examples, with no
numerical FDis interpretation. Rugosity is an illustrative axis, not one of the
five measured traits in the lab's supplied table.

The three-species trait slide uses these public-domain photographs, downloaded
without image edits and displayed at a common photograph height, not a common
animal size scale:

- `Lecture12-bullfrog.jpg`: American bullfrog (*Lithobates catesbeianus*),
  Sam Stukel/USFWS. [Source and public-domain designation](https://www.fws.gov/media/american-bullfrog-10).
- `Lecture12-red-backed-salamander.jpg`: red-backed salamander
  (*Plethodon cinereus*), USGS.
  [Source and public-domain designation](https://www.usgs.gov/media/images/red-backed-salamander-plethodon-cinereus).
- `Lecture12-spring-peeper.jpg`: spring peeper (*Pseudacris crucifer*),
  Sara Giles/USFWS.
  [Source and public-domain designation](https://www.fws.gov/media/harbor-island-public-domain-sara-giles-spring-peeper).

### Image-generation prompt

> Edit this classroom figure for a biology graduate lecture. Preserve the clean wide two-panel scientific-diagram layout and pale off-white background (#f7f8f6). Replace all eight teal circular species markers with detailed, anatomically plausible natural-history illustrations of frogs, each frog viewed from the same dorsal three-quarter angle, legs folded, facing the same direction. Make horizontal axis label 'Body size' in both panels, increasing from small at left to large at right. Make vertical axis label 'Rugosity' in both panels, increasing from smooth skin at bottom to rough bumpy skin at top. Add only small 'Small'/'Large' endpoint labels on horizontal axes and 'Smooth'/'Rough' endpoint labels on vertical axes if useful. Left title: 'Four similar species'. Left panel has four distinguishable frogs near the center of the axes, similar medium body sizes and moderately textured skins, arranged compactly but without overlap. Right title: 'Four contrasting species'. Right panel has four widely separated frogs: a small frog on the left, a visibly much larger frog on the right, a medium sized very smooth-skinned frog below, and a medium sized distinctly warty and rugose frog above. All right-panel frogs must have exactly four limbs with natural frog anatomy. The size of each illustrated frog must correspond visibly to its horizontal coordinate, and skin bumpiness must correspond visibly to its vertical coordinate. Olive green and brown natural frog colors, scientific watercolor or field-guide illustration quality, crisp legible text. Keep the small orange centroid star at the same central coordinate in both panels but avoid frog/star overlap. Remove the numerical richness/FDis labels entirely, because the figure is qualitative. No footnote, no caption, no extra explanatory prose, no equations, no photos or wildlife scenery. This is a conceptual illustration, not an empirical result.

## Empirical examples

- **mean-trait-gradients:** the same 99 eligible Maine cells, plotting
  equal-species-weight geometric means in biological units: maximum body length
  against BIO1, minimum maturity age against BIO6, and maximum clutch size
  against developed land area percentage. The pairings motivate biological
  hypotheses; they were not selected as the strongest correlations. The lab
  does not have plant seed mass, specific leaf area, or an elevation column.
- **richness-function:** recorded species richness and five-trait FDis mapped
  for the same 99 eligible cells and compared in a scatterplot. Recorded
  richness includes species without complete traits; FDis uses complete profiles.
  The 80% coverage rule applies to both displayed maps. These are descriptions,
  not tests of ecosystem functioning.
- **five-traits, scaling:** supplied species trait profiles. No body-mass values
  are invented. Frog and salamander measurements are pooled as in the lab.
- **coverage:** California species with all five traits divided by total recorded
  richness, then a minimum of three trait-covered species and 80% coverage. There
  are 259 cells, 70 recorded species, 30 complete profiles, and 127 eligible cells.
- **community-means:** geometric means across present complete-trait species.
  Coverage uses the Maine grid's total recorded richness, including species not
  represented in its complete-trait community columns. This retains 99 of 107
  cells and makes the assignment's intended coverage rule explicit.
- **equal-richness:** four trait-covered species per selected Maine cell. FDis
  uses all five standardized log10 traits. The species PCA is only the displayed
  two-axis projection.
- **null-distributions, fdis-ses:** 1,000 whole-profile permutations, seed 12,
  among the 16 complete-trait Maine species. Cell species lists and shared
  membership stay fixed. Null sample SD uses `ddof=1`. These SES summaries are
  not empirical p-values or tests of a unique ecological mechanism.
- **predictors:** prepared midpoint latitude, BIO1 mean temperature, and the
  mapped upland forest area fraction. See the lab for the source habitat classes.
- **correlations:** the exact saved six-panel output from Lab12's code cell under
  “Step 4. Evaluate correlations between FDis and environmental predictors.” All
  panels show raw functional dispersion against a predictor: latitude, BIO1,
  BIO6, BIO10, upland forest fraction, and developed fraction. The cell uses
  Pearson correlations throughout, with pairwise missing-value removal. These
  are the notebook's displayed communities, not the lecture builder's separate
  coverage-filtered subset. No community mean trait or SES response is plotted.
- **two-pcas, synthesis:** species PCA summarizes standardized log trait profiles;
  community PCA separately standardizes the five log geometric mean traits across
  eligible cells. Map and scatter colors use min–max scaled community PC1 and PC2
  as red and green, with constant blue 0.5. Colors summarize the displayed plane,
  not a biodiversity ordering or a prediction surface.
- **rankings:** mean squared Pearson correlation across all five log community
  mean traits. This is an overlapping univariate association, not unique partial
  variance or statistical significance. Arrows use correlations with only the two
  displayed community PCs. The synthesis figure multiplies both arrow coordinates
  by two solely for visibility.

Maine community PC1 and PC2 retain approximately 51.1% and 36.4% of variation in
this coverage-filtered teaching example. The numerical results JSON records the
actual values and selected predictors. These can differ from an unfiltered PCA
in an edited notebook; the input rows and filtering determine the analysis.

## Hypothetical illustrations

`mean-spread`, `records-to-traits`, `geometric-mean`, `fdis`, `null-shuffle`, and
`workflow` use explicitly invented species labels, profiles, or diagrams. The
geometric-mean example is `(10 × 20 × 80)^(1/3) = 25.2 mm`; the FDis example
has distances 2, 2, 1, 1 and mean 1.5. No hypothetical values are added to the
course datasets. Colored rows in the shuffle illustration move as intact profiles.

The added biological-mechanism figures are also original conceptual illustrations:

- **filtering-hypothesis:** two hypothetical assembly scenarios start from the
  same nine-species regional body-size distribution. Environmental filtering
  retains three similarly sized species; interspecific competition favors three
  widely separated strategies under a resource-partitioning hypothesis. Both
  local communities contain three species. Dotted lines track the selected
  species without changing their trait values; the lower colored segment shows
  local trait range. Sizes are schematic, not measured Maine values. These are
  alternative predictions, not universal consequences or diagnoses of either
  process: competitive dominance can also produce clustering. The diagram
  concerns differences among species, not intraspecific variation or an assumed
  evolutionary change. See Kraft, Godoy & Levine (2015) below.
- **competition-resources:** Gaussian resource-use curves for three hypothetical
  species illustrate overlap versus partitioning along a prey-size axis. The
  curves are neither measured diets nor estimates of interaction strengths.
  The associated notes distinguish niche differences supporting coexistence
  from competitive advantages that can instead produce dominance.
- **competition-experiment:** a proposed replicated factorial experiment crosses
  maintained/drying water with competitor presence/absence. Teal is the focal
  species and orange represents competitors. The tanks depict treatment types,
  not outcomes. Notes explain replication, randomized assignment, conspecific
  density controls, and measuring survival, growth, and metamorphosis.
- **functional-turnover:** two invented pairs of three-species communities have
  no species in common (Jaccard dissimilarity = 1). Species replacement can
  retain nearly identical trait strategies or replace those strategies too.
  Polygons connect illustrative two-trait profiles; no empirical hull-based
  functional beta diversity or formal turnover/nestedness partition is computed.
- **turnover-hypotheses:** hypothetical expectation curves and illustrative
  envelopes, not fitted results or confidence intervals. The geographic and
  climatic hypotheses predict increasing functional dissimilarity; the
  redundancy hypothesis predicts weak functional change despite species
  replacement. Pairwise observations share communities, so ordinary tests
  treating all pairs as independent would be inappropriate. These questions
  extend the lecture without changing required lab or assignment calculations.

## Sources

- [AmphiTraits: USGS data release](https://www.usgs.gov/data/amphitraits-a-database-life-history-traits-amphibian-species-usa),
  [DOI](https://doi.org/10.5066/P135WFOE). Supplied CSV with species-level life-history summaries.
- [Laliberté & Legendre (2010)](https://doi.org/10.1890/08-2244.1), functional dispersion;
  [FD package documentation](https://search.r-project.org/CRAN/refmans/FD/html/dbFD.html).
- [WorldClim variable definitions](https://www.worldclim.org/data/bioclim.html).
- [Scikit-learn PCA documentation](https://scikit-learn.org/stable/modules/generated/sklearn.decomposition.PCA.html).
- [Kraft, Godoy & Levine (2015)](https://doi.org/10.1073/pnas.1413650112),
  *Plant functional traits and the multidimensional nature of species coexistence*.
  Primary experimental motivation for distinguishing resource partitioning and
  competitive dominance when interpreting trait differences.
- [Villéger et al. (2012)](https://doi.org/10.1371/journal.pone.0040679),
  *Low functional β-diversity despite high taxonomic β-diversity among tropical
  estuarine fish communities*. Primary empirical motivation for comparing
  functional and taxonomic dissimilarity.
- [California preprocessing and habitat crosswalk](../../data/Lab12/CA_preprocessing.md).

The diagrams illustrate methods, not empirical demonstrations of environmental
filtering, competition, or causal effects of development. Species ranges,
phylogeny, reporting, trait coverage and the regional null pool can affect all
spatial patterns.
