"""Rebuild Lecture12 figures from prepared course tables; no network required.

Run: MPLCONFIGDIR=/tmp/lecture12-mpl python docs/lectures/assets/Lecture12-build-figures.py
"""
from pathlib import Path
import base64
import json
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Ellipse, Polygon
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
DATA = ROOT / 'docs/data'
INK, MUTED, TEAL, CORAL, PAPER = '#18212b', '#52606d', '#087e8b', '#d95d39', '#f7f8f6'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 15,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'axes.labelcolor': INK, 'text.color': INK,
                     'figure.facecolor': PAPER, 'axes.facecolor': PAPER,
                     'savefig.facecolor': PAPER})

def save(fig, name):
    fig.savefig(OUT / f'Lecture12-{name}.png', dpi=165, bbox_inches='tight', pad_inches=.12)
    plt.close(fig)

def region(name):
    sites = gpd.read_file(DATA / f'Lab12/{name}_30KM_grid.geojson').set_index('site_id')
    counts = pd.read_csv(DATA / f'Lab12/{name}_Amphib_site_by_species.csv', index_col='site_id')
    traits = pd.read_csv(DATA / f'Lab12/{name}_traits.csv', index_col='species')
    presence = counts[traits.index] > 0
    coverage = presence.sum(axis=1) / sites.richness
    keep = (coverage >= .8) & (presence.sum(axis=1) >= 3)
    logs = presence.astype(float).dot(np.log10(traits)).div(presence.sum(axis=1), axis=0)
    return sites, traits, presence, coverage, keep, logs.loc[keep]

def backdrop(ax, boundary, sites):
    boundary.plot(ax=ax, color='#e5e7e6', edgecolor='none')
    sites.plot(ax=ax, color='#d4d6d5', edgecolor='none')
    ax.set_axis_off()

me, traits, presence, coverage, keep, mean_logs = region('ME')
ca, ca_traits, ca_presence, ca_coverage, ca_keep, _ = region('CA')
maine = gpd.read_file(ROOT / 'docs/labs/ME_ShapeFiles/Maine_State_Boundary.shp').to_crs(me.crs)
california = gpd.read_file(DATA / 'CA_ShapeFiles/California_State_Boundary.shp').to_crs(ca.crs)
functional = me.loc[keep].copy()
trait_z = pd.DataFrame(StandardScaler().fit_transform(np.log10(traits)), index=traits.index, columns=traits.columns)
species_pca = PCA(n_components=2)
species_scores = pd.DataFrame(species_pca.fit_transform(trait_z), index=traits.index, columns=['PC1','PC2'])

def fdis(array):
    return np.linalg.norm(array-array.mean(axis=0), axis=1).mean()

groups = [np.flatnonzero(row) for row in presence.loc[functional.index].to_numpy()]
functional['fdis'] = [fdis(trait_z.to_numpy()[group]) for group in groups]
rng = np.random.default_rng(12)
null = np.array([[fdis(shuffled[group]) for group in groups]
                 for shuffled in (rng.permutation(trait_z.to_numpy()) for _ in range(1000))])
functional['ses'] = (functional.fdis-null.mean(axis=0))/null.std(axis=0,ddof=1)
community_pca = PCA(n_components=2)
community_scores = pd.DataFrame(community_pca.fit_transform(StandardScaler().fit_transform(mean_logs)),
                                index=mean_logs.index, columns=['PC1','PC2'])
colors = np.column_stack([MinMaxScaler().fit_transform(community_scores), np.full(len(community_scores), .5)])

# Conceptual pictures use invented communities, never empirical amphibian measurements.
fig, axes = plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
for ax, radius, title in zip(axes,[.45,1.6],['Four similar species','Four contrasting species']):
    xy = np.array([[-1,0],[1,0],[0,-1],[0,1]])*radius
    ax.scatter(xy[:,0],xy[:,1],s=150,color=TEAL)
    ax.scatter(0,0,marker='*',s=240,color=CORAL,zorder=3)
    ax.axhline(0,color='#c9cecd',lw=1);ax.axvline(0,color='#c9cecd',lw=1)
    ax.set(xlim=(-2,2),ylim=(-2,2),xlabel='Trait axis 1',ylabel='Trait axis 2',title=title)
    ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
    ax.text(0,-1.9,f'Richness = 4     FDis = {radius:.2f}',ha='center',fontsize=16)
save(fig,'mean-spread')

fig, axes = plt.subplots(1,5,figsize=(14,4.2),layout='constrained')
examples = ['Lithobates catesbeianus','Plethodon cinereus','Pseudacris crucifer']
names = ['Bullfrog','Red-backed\nsalamander','Spring peeper']
labels = ['Adult length\n(mm)','Maturity age\n(years)','Maximum clutch\n(offspring)','Maturity size\n(mm)','Minimum clutch\n(offspring)']
for ax,col,label in zip(axes,traits.columns,labels):
    values = traits.loc[examples,col]
    ax.barh(range(3),values,color=[TEAL,CORAL,'#7c6ba5'])
    ax.set_xscale('log');ax.set_title(label,fontsize=16)
    ax.set_yticks(range(3), names if col==traits.columns[0] else [])
    ax.invert_yaxis()
    for i,value in enumerate(values): ax.text(value*1.08,i,f'{value:g}',va='center',fontsize=12)
    ax.set_xlim(max(.1,values.min()/2),values.max()*4)
    ax.set_xticks([])
    ax.set_xticks([],minor=True)
save(fig,'five-traits')

fig, ax = plt.subplots(figsize=(13,4.2));ax.set_axis_off();ax.set(xlim=(0,13),ylim=(0,4.2))
texts = [('Occurrence records','A  A  A  A\nB  B\nC'),('Species present','A     B     C'),('Trait profiles','A: 10 mm\nB: 20 mm\nC: 80 mm')]
for x,(title,body) in zip([.1,4.7,9.1],texts):
    ax.add_patch(Rectangle((x,.5),3.7,3.1,facecolor='white',edgecolor='#c9cecd',lw=1.5))
    ax.text(x+1.85,3.15,title,ha='center',fontsize=18,weight='bold')
    ax.text(x+1.85,1.75,body,ha='center',va='center',fontsize=23,color=TEAL)
for x in [4.1,8.5]:ax.add_patch(FancyArrowPatch((x-.1,2),(x+.4,2),arrowstyle='->',mutation_scale=24,color=CORAL,lw=2))
save(fig,'records-to-traits')

fig, axes = plt.subplots(1,2,figsize=(10,6),layout='constrained')
for ax in axes:backdrop(ax,california,ca)
ca.assign(coverage=ca_coverage).plot(ax=axes[0],column='coverage',vmin=0,vmax=1,legend=True,cmap='viridis')
axes[0].set_title('Fraction of species with complete traits')
ca.loc[ca_keep].plot(ax=axes[1],color=TEAL)
axes[1].set_title(f'{int(ca_keep.sum())} of {len(ca)} cells retained')
save(fig,'coverage')

fig, axes = plt.subplots(1,3,figsize=(13,4.1),layout='constrained')
arrays = [traits, np.log10(traits), trait_z]
for ax,data,title in zip(axes,arrays,['Original units','Log10 traits','Standardized log traits']):
    ax.scatter(data.MaxBody,data.MaxClutch,color=TEAL,s=45)
    ax.set(title=title,xlabel='Maximum adult length',ylabel='Maximum clutch size')
save(fig,'scaling')

fig, ax = plt.subplots(figsize=(12,3.4),layout='constrained')
values=np.array([10,20,80]);gm=10**np.log10(values).mean()
ax.scatter(values,[0,0,0],s=160,color=TEAL,zorder=3)
for x,name in zip(values,['Species A','Species B','Species C']):ax.text(x,.13,name,ha='center',fontsize=16)
ax.axvline(gm,color=CORAL,lw=3,label=f'Geometric mean: {gm:.1f} mm')
ax.axvline(values.mean(),color=MUTED,lw=2,ls='--',label=f'Arithmetic mean: {values.mean():.1f} mm')
ax.set_xscale('log');ax.set(xlim=(7,120),ylim=(-.4,.5),xlabel="Species' maximum adult length (mm)")
ax.set_yticks([]);ax.set_xticks(values,labels=['10','20','80']);ax.legend(loc='upper left',fontsize=14)
save(fig,'geometric-mean')

fig, axes = plt.subplots(1,3,figsize=(12,5.6),layout='constrained')
for ax,col,title in zip(axes,['MaxBody','MinAgeMat','MaxClutch'],['Typical maximum length (mm)','Typical maturity age (years)','Typical maximum clutch size']):
    backdrop(ax,maine,me)
    table=functional.copy();table['mean']=10**mean_logs[col]
    table.plot(ax=ax,column='mean',legend=True,cmap='viridis')
    ax.set_title(title,fontsize=16)
save(fig,'community-means')

fig, ax=plt.subplots(figsize=(10,4.7),layout='constrained')
points=np.array([[-2,0],[2,0],[0,-1],[0,1]])
ax.scatter(points[:,0],points[:,1],color=TEAL,s=150,zorder=3)
for (x,y),length in zip(points,[2,2,1,1]):
    ax.plot([0,x],[0,y],color=MUTED,lw=2)
    ax.text(x*1.14,y*1.2,f'd = {length}',ha='center',va='center',fontsize=18)
ax.scatter(0,0,marker='*',s=250,color=CORAL,zorder=4)
ax.text(.1,.15,'Centroid',color=CORAL,fontsize=17)
ax.set(xlim=(-3,3),ylim=(-1.6,1.9),xlabel='Standardized trait axis 1',ylabel='Standardized trait axis 2')
ax.set_xticks([]);ax.set_yticks([]);ax.set_aspect('equal')
ax.text(0,1.65,'FDis = (2 + 2 + 1 + 1) / 4 = 1.5',ha='center',fontsize=19)
save(fig,'fdis')

known=presence.loc[functional.index].sum(axis=1)
candidates=functional.loc[known==4]
extreme_ids=[candidates.fdis.idxmin(),candidates.fdis.idxmax()]
fig,axes=plt.subplots(1,2,figsize=(12,4.9),layout='constrained')
for ax,site_id in zip(axes,extreme_ids):
    row=presence.loc[site_id];names=row[row].index;selected=species_scores.loc[names]
    ax.scatter(species_scores.PC1,species_scores.PC2,color='#d2d4d3',s=45)
    ax.scatter(selected.PC1,selected.PC2,color=TEAL,s=80)
    ax.scatter(selected.PC1.mean(),selected.PC2.mean(),marker='*',color=CORAL,s=210)
    for name,point in selected.iterrows():ax.annotate(name.split()[1],(point.PC1,point.PC2),xytext=(3,5),textcoords='offset points',fontsize=12)
    ax.set(title=f'4 species · FDis = {functional.loc[site_id,"fdis"]:.2f}',xlabel='Species trait PC1',ylabel='Species trait PC2')
save(fig,'equal-richness')

fig,axes=plt.subplots(1,2,figsize=(13,4.2),layout='constrained')
toy=np.array([[60,1,800,20,100],[90,2,2000,40,500],[140,3,20,50,5],
              [180,4,100,80,20],[50,1,500,25,90],[120,2,30,45,6]])
palette=['#aad7d2','#eebca8','#c4b6db','#d0d990','#9fc3df','#e6cf98']
for ax,order,title in zip(axes,[np.arange(6),np.array([3,0,5,1,2,4])],['Observed trait assignments','One shuffled assignment']):
    ax.set_axis_off()
    table=ax.table(cellText=toy[order],rowLabels=list('ABCDEF'),
                   colLabels=['Length','Age','Max clutch','Size','Min clutch'],
                   cellColours=[[palette[j]]*5 for j in order],loc='center',cellLoc='center')
    table.auto_set_font_size(False);table.set_fontsize(12);table.scale(1,1.8)
    ax.set_title(title,fontsize=19)
    ax.text(.5,-.03,'Cell 1: A, B, C      Cell 2: C, D, E',ha='center',transform=ax.transAxes,fontsize=15)
save(fig,'null-shuffle')

ids=[functional.ses.idxmin(),functional.ses.idxmax()]
fig,axes=plt.subplots(1,2,figsize=(12,4.4),layout='constrained')
for ax,site_id in zip(axes,ids):
    position=functional.index.get_loc(site_id)
    ax.hist(null[:,position],bins=24,color='#bac4c7',edgecolor=PAPER)
    ax.axvline(functional.loc[site_id,'fdis'],color=CORAL,lw=3,label='Observed')
    ax.set(title=f'Cell {site_id} · SES = {functional.loc[site_id,"ses"]:.2f}',xlabel='Functional dispersion',ylabel='Shuffles')
    ax.legend(fontsize=14)
save(fig,'null-distributions')

fig,axes=plt.subplots(1,2,figsize=(10,5.8),layout='constrained')
for ax,col,title in zip(axes,['fdis','ses'],['Observed functional dispersion','FDis relative to the null (SD)']):
    backdrop(ax,maine,me)
    kwargs={'cmap':'viridis'} if col=='fdis' else {'cmap':'RdBu_r','vmin':-3,'vmax':3}
    functional.plot(ax=ax,column=col,legend=True,**kwargs);ax.set_title(title,fontsize=16)
save(fig,'fdis-ses')

fig,axes=plt.subplots(1,3,figsize=(12,5.4),layout='constrained')
for ax,col,title in zip(axes,['latitude','bio_1','habitat_upland_forest'],['Midpoint latitude (°N)','Mean annual temperature (°C)','Upland forest area fraction']):
    backdrop(ax,maine,me);me.plot(ax=ax,column=col,legend=True,cmap='viridis');ax.set_title(title,fontsize=16)
save(fig,'predictors')

# Reuse the exact saved six-panel Pearson/FDis figure from Lab12 Step 4.
notebook = json.loads((ROOT / 'docs/labs/Lab12-SpatialTraitVariation.ipynb').read_text())
correlation_cell = next(cell for cell in notebook['cells']
                        if 'Fdis_corrs = {}' in ''.join(cell.get('source', [])))
correlation_plot = next(output['data']['image/png'] for output in correlation_cell['outputs']
                        if 'image/png' in output.get('data', {}))
(OUT / 'Lecture12-correlations.png').write_bytes(base64.b64decode(correlation_plot))

fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
axes[0].scatter(species_scores.PC1,species_scores.PC2,color=TEAL,s=70)
for name in ['Lithobates catesbeianus','Pseudacris crucifer','Plethodon cinereus']:
    point=species_scores.loc[name];axes[0].annotate(name.split()[1],(point.PC1,point.PC2),xytext=(4,4),textcoords='offset points',fontsize=13)
axes[0].set(title='Species PCA: one dot = one species',xlabel='Species PC1',ylabel='Species PC2')
axes[1].scatter(community_scores.PC1,community_scores.PC2,c=colors,s=40)
axes[1].set(title='Community PCA: one dot = one cell',xlabel='Community PC1',ylabel='Community PC2')
save(fig,'two-pcas')

predictors=['latitude']+[f'bio_{n}' for n in range(1,20)]+[c for c in me if c.startswith('habitat_')]
ranking=pd.Series({p:np.mean([me[p].corr(mean_logs[t])**2 for t in traits]) for p in predictors}).sort_values(ascending=False)
best_climate=ranking[[p for p in ranking.index if p.startswith('bio_')]].idxmax()
best_habitat=ranking[[p for p in ranking.index if p.startswith('habitat_')]].idxmax()
fig,axes=plt.subplots(1,2,figsize=(12,6.2),layout='constrained')
backdrop(axes[0],maine,me);functional.plot(ax=axes[0],color=colors)
axes[0].set_title('Observed community trait combinations')
axes[1].scatter(community_scores.PC1,community_scores.PC2,c=colors,s=40)
for predictor,color,label in zip(['latitude',best_climate,best_habitat],['black',CORAL,'#326bb0'],
                                ['Latitude','BIO'+best_climate.split('_')[1],best_habitat.replace('habitat_','').replace('_',' ')+' fraction']):
    x=2*me[predictor].corr(community_scores.PC1);y=2*me[predictor].corr(community_scores.PC2)
    axes[1].arrow(0,0,x,y,head_width=.1,length_includes_head=True,color=color,label=label)
axes[1].legend(fontsize=12)
axes[1].set(xlabel=f'PC1 ({community_pca.explained_variance_ratio_[0]:.0%})',ylabel=f'PC2 ({community_pca.explained_variance_ratio_[1]:.0%})')
save(fig,'synthesis')

fig,axes=plt.subplots(1,2,figsize=(12,4.8),layout='constrained')
top=ranking.head(6).iloc[::-1]
axes[0].barh([p.replace('habitat_','').replace('_',' ') for p in top.index],top.values,color=TEAL)
axes[0].set(xlabel='Mean squared correlation',title='Rank using all five trait means')
for predictor,color,label in zip(['latitude',best_climate,best_habitat],['black',CORAL,'#326bb0'],
                                ['Latitude','BIO'+best_climate.split('_')[1],'Leading habitat']):
    x=me[predictor].corr(community_scores.PC1);y=me[predictor].corr(community_scores.PC2)
    axes[1].arrow(0,0,x,y,head_width=.04,length_includes_head=True,color=color,label=label)
axes[1].axhline(0,color='#c8cece',lw=1);axes[1].axvline(0,color='#c8cece',lw=1)
axes[1].set(xlim=(-1,1),ylim=(-1,1),xlabel='Correlation with PC1',ylabel='Correlation with PC2',title='Arrows use only two axes')
axes[1].legend(fontsize=12)
save(fig,'rankings')

fig,ax=plt.subplots(figsize=(13,4.3));ax.set_axis_off();ax.set(xlim=(0,13),ylim=(0,4.3))
for x,title,question in zip([.1,3.4,6.7,10],['Typical traits','Trait spread','Null model','PCA map'],
                          ['Which trait values\ncharacterize a cell?','How different are\nits species?','Different from\nwhich expectation?','Where do trait\ncombinations occur?']):
    ax.add_patch(Rectangle((x,.7),2.9,2.8,facecolor='white',edgecolor='#c8cece',lw=2))
    ax.text(x+1.45,2.9,title,ha='center',weight='bold',fontsize=19,color=TEAL)
    ax.text(x+1.45,1.9,question,ha='center',va='center',fontsize=16)
save(fig,'workflow')

# Biological questions: empirical Maine comparisons, followed by conceptual examples.
fig, axes = plt.subplots(1, 3, figsize=(13, 4.5), layout='constrained')
for ax, predictor, trait, xlabel, ylabel, title in zip(
        axes, ['bio_1', 'bio_6', 'habitat_developed'],
        ['MaxBody', 'MinAgeMat', 'MaxClutch'],
        ['Mean annual temperature (°C)', 'Minimum temperature\nof coldest month (°C)',
         'Developed land (%)'],
        ['Typical maximum length (mm)', 'Typical maturity age (years)',
         'Typical maximum clutch size'],
        ['Body size and temperature', 'Maturity and winter cold', 'Reproduction and land use']):
    x = functional[predictor]
    if predictor == 'habitat_developed':
        x = 100 * x
    ax.scatter(x, 10**mean_logs[trait], color=TEAL, s=36, alpha=.7)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.title.set_fontsize(16)
save(fig, 'mean-trait-gradients')

fig, axes = plt.subplots(1, 3, figsize=(13, 5), layout='constrained',
                         gridspec_kw={'width_ratios': [1, 1, 1.15]})
for ax, column, title in zip(axes[:2], ['richness', 'fdis'],
                             ['Recorded species richness', 'Functional dispersion']):
    backdrop(ax, maine, me)
    functional.plot(ax=ax, column=column, legend=True, cmap='viridis')
    ax.set_title(title, fontsize=16)
axes[2].scatter(functional.richness, functional.fdis, color=TEAL, s=38, alpha=.7)
axes[2].set(xlabel='Recorded species richness', ylabel='Functional dispersion',
            title='Where do the summaries disagree?')
axes[2].title.set_fontsize(15)
save(fig, 'richness-function')

# Contrasting assembly hypotheses, with three coexisting species in each panel.
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), layout='constrained')
pool = np.arange(1, 10)
for ax, selected, title, mechanism, color in zip(
        axes, [np.array([4, 5, 6]), np.array([1, 5, 9])],
        ['Environmental filtering', 'Interspecific competition'],
        ['Similar abiotic tolerances', 'Different resource-use strategies'], [TEAL, CORAL]):
    ax.scatter(pool, np.full(9, 1.6), s=120, color='#b3bbbf', zorder=3)
    for value in selected:
        ax.plot([value, value], [.35, 1.6], color=color, alpha=.35, lw=1.5, ls='--')
    ax.scatter(selected, np.full(3, .35), s=200, color=color, zorder=4)
    ax.plot([selected.min(), selected.max()], [.06, .06], color=color, lw=5)
    ax.text(5, 1.96, 'Regional species pool', ha='center', fontsize=15, color=MUTED)
    ax.text(5, 1.05, mechanism, ha='center', fontsize=15, color=color,
            bbox={'facecolor': PAPER, 'edgecolor': 'none', 'pad': 4})
    ax.text(5, -.3, 'Three coexisting species', ha='center', fontsize=15)
    ax.set(title=title, xlim=(.4, 9.6), ylim=(-.55, 2.2), yticks=[],
           xlabel='Body size', xticks=[1, 5, 9], xticklabels=['Small', 'Medium', 'Large'])
    ax.title.set_fontsize(20)
    ax.spines['left'].set_visible(False)
save(fig, 'filtering-hypothesis')

# Resource-use curves illustrate a competition hypothesis, not measured diets.
fig, axes = plt.subplots(1, 2, figsize=(13, 4.6), layout='constrained')
resource = np.linspace(0, 10, 350)
for ax, centers, title in zip(axes, [[4.3, 5, 5.7], [2, 5, 8]],
                              ['Strong overlap in resource use', 'Partitioning the available resources']):
    for center, color, label in zip(centers, [TEAL, CORAL, '#7c6ba5'],
                                     ['Species A', 'Species B', 'Species C']):
        use = np.exp(-.5*((resource-center)/1.1)**2)
        ax.plot(resource, use, color=color, lw=3, label=label)
        ax.fill_between(resource, use, color=color, alpha=.13)
    ax.set(title=title, xlabel='Prey size', ylabel='Relative resource use',
           ylim=(0, 1.3), yticks=[], xticks=[1, 9], xticklabels=['Small', 'Large'])
    ax.title.set_fontsize(17)
axes[0].legend(loc='upper left', fontsize=12, frameon=False)
save(fig, 'competition-resources')

# A replicated factorial experiment could test the two processes separately.
def tadpole(ax, x, y, color):
    ax.add_patch(Ellipse((x, y), .095, .065, facecolor=color, edgecolor='none'))
    ax.plot([x-.04, x-.11, x-.15], [y, y-.025, y+.005], color=color, lw=3)

fig, axes = plt.subplots(2, 2, figsize=(12, 5.6), layout='constrained')
for row in range(2):
    for col in range(2):
        ax = axes[row, col]
        ax.set(xlim=(0, 1), ylim=(0, 1)); ax.set_axis_off()
        ax.add_patch(Polygon([[.1, .8], [.17, .12], [.83, .12], [.9, .8]],
                             closed=False, fill=False, edgecolor=MUTED, lw=3))
        ax.add_patch(Polygon([[.13, .65], [.17, .12], [.83, .12], [.87, .65]],
                             color='#d9eaf0'))
        tadpole(ax, .52, .46, TEAL)
        ax.text(.52, .24, 'Focal species', ha='center', fontsize=14, color=TEAL)
        if row == 1:
            tadpole(ax, .3, .53, CORAL); tadpole(ax, .72, .52, CORAL)
        if row == 0:
            ax.set_title(['Maintain water', 'Allow water to dry'][col], fontsize=20)
        if col == 0:
            ax.text(-.01, .48, ['Alone', 'With\ncompetitors'][row], ha='right',
                    va='center', fontsize=18)
save(fig, 'competition-experiment')

# Different species can occupy similar or different parts of trait space.
fig, axes = plt.subplots(1, 2, figsize=(13, 4.8), layout='constrained')
community_a = np.array([[1, 1], [3, 1.5], [1.5, 3]])
for ax, community_b, title in zip(
        axes, [community_a + [.15, .05], community_a + [3.3, 2.7]],
        ['Species replaced; strategies retained', 'Species and strategies replaced']):
    for points, color, marker, label in zip(
            [community_a, community_b], [TEAL, CORAL], ['o', '^'],
            ['Species A, B, C', 'Species D, E, F']):
        ax.add_patch(Polygon(points, facecolor=color, edgecolor=color, alpha=.16))
        ax.scatter(points[:, 0], points[:, 1], c=color, s=100, marker=marker, label=label)
    ax.set(title=title, xlim=(0, 7), ylim=(0, 7), xlabel='Body size', ylabel='Age at maturity',
           xticks=[], yticks=[])
    ax.title.set_fontsize(17)
    ax.legend(loc='upper left', fontsize=12, frameon=False)
save(fig, 'functional-turnover')

# Hypothetical expectations only: no empirical distances or fitted results.
fig, axes = plt.subplots(1, 3, figsize=(13, 4.4), layout='constrained')
x = np.linspace(0, 1, 100)
for ax, title, xlabel in zip(
        axes, ['Distance hypothesis', 'Climate hypothesis', 'Redundancy hypothesis'],
        ['Geographic distance', 'Climatic difference', 'Species dissimilarity (Jaccard)']):
    if title == 'Redundancy hypothesis':
        ax.fill_between(x, .1*x, .3*x, color=TEAL, alpha=.2)
        ax.plot(x, .2*x, color=TEAL, lw=3)
        ax.text(.06, .78, 'Species can change\nwhile strategies persist', fontsize=15)
    else:
        y = .85*(1-np.exp(-2*x))
        ax.fill_between(x, y-.1*x, y+.1*x, color=TEAL, alpha=.2)
        ax.plot(x, y, color=TEAL, lw=3)
    ax.set(title=title, xlabel=xlabel, ylabel='Functional dissimilarity',
           xlim=(0, 1), ylim=(0, 1), xticks=[0, 1], yticks=[0, 1])
    ax.title.set_fontsize(17)
    if title == 'Distance hypothesis':
        ax.set_xticklabels(['Near', 'Far'])
    elif title == 'Climate hypothesis':
        ax.set_xticklabels(['Similar', 'Different'])
save(fig, 'turnover-hypotheses')

results={'maine_sites':len(me),'maine_functional_sites':len(functional),'maine_traits':len(traits),
         'community_pca_variance':community_pca.explained_variance_ratio_.tolist(),
         'species_pca_variance':species_pca.explained_variance_ratio_.tolist(),
         'selected_predictors':['latitude',best_climate,best_habitat],
         'mean_length_latitude_spearman':functional.latitude.corr(10**mean_logs.MaxBody,method='spearman'),
         'null_extremes':functional.loc[ids,['fdis','ses']].to_dict(orient='index')}
(OUT/'Lecture12-example-results.json').write_text(json.dumps(results,indent=2))
print('Created Lecture12 figures',json.dumps(results,indent=2))
