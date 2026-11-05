"""Rebuild the original teaching diagrams and data figures for Lecture10.

Run from the repository root with the Lab10 Python environment:
    python docs/lectures/assets/Lecture10-build-figures.py

SVG examples are invented. The map uses the unchanged Lab10 park dataset.
The rarefaction plot uses explicitly stated toy counts, not lab results.
"""
from html import escape
import hashlib
import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from scipy.special import gammaln
from scipy.stats import entropy
from scipy.spatial.distance import jaccard, braycurtis

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
INK, MUTED, TEAL, CORAL = "#18212b", "#52606d", "#087e8b", "#d95d39"
PAPER, LINE, PALE = "#f7f8f6", "#ccd3d7", "#e6eeed"
SPECIES = ["#087e8b", "#c48d21", "#8660a4", "#d95d39", "#3f6ca8", "#527b3d", "#ad5476"]
TOY = np.array([[8, 4, 0, 0, 0], [8, 4, 3, 0, 0],
                [8, 0, 0, 12, 0], [8, 0, 0, 0, 2]])


class Drawing:
    def __init__(self, name, title, height=500):
        self.name = name
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1296 {height}" role="img" aria-labelledby="title">',
                      f'<title id="title">{escape(title)}</title>',
                      '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0 L10 5 L0 10 Z" fill="#087e8b"/></marker></defs>']

    def add(self, markup):
        self.parts.append(markup)

    def text(self, x, y, text, size=27, color=INK, weight=400, anchor="start"):
        self.add(f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial,Helvetica,sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(text))}</text>')

    def rect(self, x, y, w, h, fill="none", stroke=LINE, radius=0):
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="2" rx="{radius}"/>')

    def ellipse(self, x, y, rx, ry, fill=PALE, stroke=TEAL):
        self.add(f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="{fill}" stroke="{stroke}" stroke-width="3"/>')

    def line(self, x1, y1, x2, y2, color=LINE, width=3, arrow=False):
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{width}"'+(' marker-end="url(#arrow)"' if arrow else '')+'/>')

    def animal(self, x, y, species=0, size=1, label=False):
        color = SPECIES[species]
        self.add(f'<g transform="translate({x} {y}) scale({size})" fill="{color}" stroke="{color}" stroke-width="3" stroke-linecap="round">')
        if species % 3 == 0:  # Schematic frog, viewed from above.
            self.add('<path d="M-12 2 L-25 14 L-30 7 M12 2 L25 14 L30 7 M-9 -7 L-21 -14 M9 -7 L21 -14" fill="none"/>')
            self.add('<ellipse cy="1" rx="15" ry="17"/><ellipse cy="-14" rx="14" ry="9"/>')
            self.add('<circle cx="-8" cy="-18" r="3" fill="white" stroke="none"/><circle cx="8" cy="-18" r="3" fill="white" stroke="none"/>')
        else:  # Schematic tailed amphibian.
            self.add('<path d="M0 14 Q26 26 30 3 Q18 18 3 7" stroke="none"/>')
            self.add('<path d="M-6 -8 L-20 -16 M6 -8 L20 -16 M-6 9 L-20 17 M6 9 L20 17" fill="none"/>')
            self.add('<ellipse rx="8" ry="19"/><ellipse cy="-22" rx="10" ry="9"/>')
            self.add('<circle cx="-4" cy="-24" r="2" fill="white" stroke="none"/><circle cx="4" cy="-24" r="2" fill="white" stroke="none"/>')
        self.add('</g>')
        if label:
            self.text(x, y+44*size, chr(65+species), 23, color, 700, "middle")

    def species_row(self, x, y, species, gap=75, size=1):
        for i, sp in enumerate(species):
            self.animal(x+i*gap, y, sp, size, True)

    def save(self):
        (OUT / f"Lecture10-{self.name}.svg").write_text("\n".join(self.parts)+"\n</svg>\n")


def sloss():
    d = Drawing("sloss", "Equal protected area: one 1000 square kilometer park or three parks of 400, 300 and 300 square kilometers.")
    d.text(280, 45, "Single large", 35, TEAL, 700, "middle")
    d.text(950, 45, "Several small", 35, CORAL, 700, "middle")
    d.ellipse(280, 250, 165, 165)
    d.text(280, 245, "1,000 km²", 37, TEAL, 700, "middle")
    d.text(280, 290, "one park", 28, MUTED, anchor="middle")
    for x, y, area in [(825, 185, 400), (1080, 185, 300), (950, 350, 300)]:
        r = 165*np.sqrt(area/1000)
        d.ellipse(x, y, r, r, "#f3e7d9", CORAL)
        d.text(x, y+10, f"{area} km²", 29, CORAL, 700, "middle")
    d.text(648, 265, "or", 38, MUTED, anchor="middle")
    d.text(280, 480, "1,000 km² total", 28, TEAL, 700, "middle")
    d.text(950, 480, "1,000 km² total", 28, CORAL, 700, "middle")
    d.save()


def habitats():
    d = Drawing("habitats", "A hypothetical amphibian landscape contains breeding ponds, surrounding forest and a stream; reserve placement captures different habitats.")
    d.rect(10, 15, 1275, 465, "#e8eddd", "#cbd4bf", 30)
    for x, y in [(90,100),(160,320),(300,70),(420,380),(610,90),(740,400),(940,80),(1190,360)]:
        d.add(f'<path d="M{x} {y-32} l-28 60 h56 Z" fill="#a6ba95"/><path d="M{x} {y+20} v30" stroke="#71856a" stroke-width="5"/>')
    d.ellipse(310, 215, 132, 72, "#c5e4e9", "#72aab7")
    d.ellipse(760, 320, 82, 50, "#c5e4e9", "#72aab7")
    d.add('<path d="M1110 25 C910 140 1220 225 1025 360 S1050 470 1160 480" fill="none" stroke="#88bbc7" stroke-width="35"/>')
    d.animal(312, 208, 0, 1.5)
    d.animal(550, 230, 1, 1.5)
    d.animal(1070, 280, 2, 1.5)
    d.text(310, 335, "Breeding pond", 31, TEAL, 700, "middle")
    d.text(550, 320, "Forest refuge", 31, SPECIES[1], 700, "middle")
    d.text(1060, 400, "Stream habitat", 31, SPECIES[2], 700, "middle")
    d.line(410, 220, 500, 220, TEAL, 4, True)
    d.text(450, 170, "movement", 23, MUTED, anchor="middle")
    d.save()


def matrix():
    d = Drawing("matrix", "A toy community matrix has four park rows and five species columns. Counts become presence or absence when values greater than zero become one.")
    for j in range(5):
        d.animal(355+j*178, 65, j, 1, True)
    for i, row in enumerate(TOY):
        d.text(120, 175+i*76, f"Park {i+1}", 29, weight=700)
        for j, count in enumerate(row):
            d.rect(285+j*178, 128+i*76, 140, 62, "#dbe9e7" if count else "#ffffff")
            d.text(355+j*178, 170+i*76, count, 32, INK if count else "#87939b", 700, "middle")
    d.text(648, 478, "A zero is no record here; it does not prove absence.", 30, CORAL, 700, "middle")
    d.save()


def richness():
    d = Drawing("richness", "Park 1 has eight A records and four B records: twelve records, two species. Park 2 adds three C records: fifteen records, three species.")
    for park, counts in enumerate(TOY[:2]):
        x = 25 + park*660
        d.text(x+280, 42, f"Park {park+1}", 35, weight=700, anchor="middle")
        for species in range(3):
            y = 135 + species*90
            d.text(x+16, y+8, chr(65+species), 27,
                   SPECIES[species] if counts[species] else MUTED, 700)
            for record in range(int(counts[species])):
                d.animal(x+80+record*58, y, species, .85)
            if counts[species] == 0:
                d.text(x+80, y+8, "—", 30, MUTED, anchor="middle")
        d.text(x+280, 410, f"{int(counts.sum())} records", 28, MUTED, anchor="middle")
        d.text(x+280, 475, f"Richness = {np.count_nonzero(counts)} species", 36, TEAL, 700, "middle")
    d.save()


def evenness():
    d = Drawing("evenness", "Two invented communities each have 30 records and three species. Counts are 10,10,10 or 28,1,1.")
    for x, name, counts in [(35, "Even records", [10,10,10]), (690, "Dominated records", [28,1,1])]:
        d.text(x+280, 40, name, 35, weight=700, anchor="middle")
        sequence = [sp for sp, n in enumerate(counts) for _ in range(n)]
        for k, sp in enumerate(sequence):
            d.animal(x+40+(k%10)*54, 105+(k//10)*88, sp, .68)
        d.text(x+280, 365, "Counts: "+", ".join(map(str,counts)), 31, anchor="middle")
        h = entropy(counts)
        d.text(x+280, 420, f"Richness = 3     Shannon H′ = {h:.3f}", 30, TEAL, 700, "middle")
        d.text(x+280, 470, f"Effective species = {np.exp(h):.2f}", 28, MUTED, anchor="middle")
    d.save()


def alpha_beta():
    d = Drawing("alpha-beta", "Three parks have richness three each. Identical species lists give pooled richness three and beta one. Complementary lists give pooled richness seven and beta seven thirds.")
    for y, name, lists, gamma in [(35,"Repeated communities",[[0,1,2]]*3,3),
                                 (280,"Complementary communities",[[0,1,2],[0,3,4],[0,5,6]],7)]:
        d.text(24, y, name, 30, weight=700)
        for i, species in enumerate(lists):
            x=38+i*295
            d.rect(x, y+30, 270, 125, "#ffffff", LINE, 18)
            d.species_row(x+58, y+84, species, 76, .8)
        d.text(1030,y+57,"Mean α = 3",29,anchor="middle")
        d.text(1030,y+107,f"Pooled γ = {gamma}",29,TEAL,700,"middle")
        d.text(1030,y+157,f"β = {gamma/3:.2f}",29,CORAL,700,"middle")
    d.save()


def complementarity():
    d = Drawing("complementarity", "An existing reserve has A B C. A candidate with A B C D adds one species; a candidate with D E F adds three despite lower local richness.")
    d.text(260,45,"Already protected",32,weight=700,anchor="middle")
    d.rect(45,100,430,285,"#ffffff",TEAL,25)
    d.species_row(155,225,[0,1,2],100,1.15)
    d.line(510,245,625,245,TEAL,4,True)
    for y,label,species,added in [(35,"Candidate 1",[0,1,2,3],1),(285,"Candidate 2",[3,4,5],3)]:
        d.text(700,y+5,label,30,weight=700)
        d.species_row(730,y+83,species,90,.95)
        d.text(1175,y+80,f"+{added}",47,CORAL,700,"middle")
        d.text(1175,y+120,"new species",22,MUTED,anchor="middle")
    d.text(260,445,"Richness = 3",30,TEAL,700,"middle")
    d.save()


def jaccard_sets():
    d=Drawing("jaccard","Parks X and Y contain A B C and A C D. Two shared species among four in the union give Jaccard dissimilarity 0.5.")
    d.text(60,105,"Park X",33,weight=700)
    d.text(60,255,"Park Y",33,weight=700)
    for y,species in [(90,[0,1,2]),(240,[0,2,3])]:
        for j in range(4):
            d.rect(280+j*170,y-50,135,110,"#dbe9e7" if j in species else "#ffffff",LINE,12)
            if j in species: d.animal(348+j*170,y,j,.9,True)
            else: d.text(348+j*170,y+9,"—",35,MUTED,anchor="middle")
    d.text(1100,106,"3 species",30,anchor="middle")
    d.text(1100,256,"3 species",30,anchor="middle")
    d.text(648,380,"Shared: A, C      Union: A, B, C, D",33,TEAL,700,"middle")
    d.text(648,455,"Jaccard = 1 − 2/4 = 0.50",38,CORAL,700,"middle")
    d.save()


def nestedness():
    d=Drawing("nestedness","A subset pattern and a replacement pattern can both yield Jaccard dissimilarity one half.")
    for x,title,rows in [(15,"A subset",[[0,1],[0,1,2,3]]),(675,"Replacement",[[0,1,2],[0,2,3]])]:
        d.text(x+290,45,title,34,weight=700,anchor="middle")
        for k,species in enumerate(rows):
            d.text(x+35,155+k*140,"X" if k==0 else "Y",30,MUTED,700)
            d.species_row(x+130,140+k*140,species,108,1.1)
        d.text(x+290,425,"Jaccard = 0.50",35,TEAL,700,"middle")
        d.text(x+290,480,"No replacement needed" if x==15 else "B replaced by D",27,MUTED,anchor="middle")
    d.save()


def bray():
    d=Drawing("bray-curtis","The same three species have counts 8 1 1 versus 1 8 1. Jaccard is zero, but Bray Curtis is 0.7.")
    for y,name,counts in [(125,"Park X",[8,1,1]),(285,"Park Y",[1,8,1])]:
        d.text(30,y+25,name,33,weight=700)
        x=250
        for sp,n in enumerate(counts):
            d.rect(x,y-35,n*75,100,SPECIES[sp],PAPER)
            if n*75>60: d.text(x+n*75/2,y+26,n,35,INK if sp==1 else "#ffffff",700,"middle")
            x+=n*75
    for i in range(3):
        d.animal(350+i*280,375,i,.75,True)
    d.text(648,475,"Jaccard = 0     Bray–Curtis = (7 + 7 + 0) / 20 = 0.70",33,TEAL,700,"middle")
    d.save()


def totals():
    d=Drawing("record-totals","Counts 10 5 5 and 20 10 10 have identical relative frequencies. Raw Bray Curtis is one third and normalized Bray Curtis is zero.")
    d.text(330,40,"Record counts",33,weight=700,anchor="middle")
    d.text(1000,40,"Relative frequencies",33,weight=700,anchor="middle")
    for y,label,counts in [(145,"X",[10,5,5]),(300,"Y",[20,10,10])]:
        d.text(20,y+10,label,30,MUTED,700)
        x=95
        for sp,n in enumerate(counts):
            d.rect(x,y-45,n*12,90,SPECIES[sp],PAPER)
            d.text(x+n*6,y+12,n,27,INK if sp==1 else "white",700,"middle")
            x+=n*12
        x=790
        for sp,p in enumerate([.5,.25,.25]):
            d.rect(x,y-45,p*440,90,SPECIES[sp],PAPER)
            d.text(x+p*220,y+12,f"{p:.2f}",26,INK if sp==1 else "white",700,"middle")
            x+=p*440
    d.line(630,215,735,215,TEAL,4,True)
    d.text(340,440,"Bray–Curtis = 0.33",32,CORAL,700,"middle")
    d.text(1010,440,"Bray–Curtis = 0",32,TEAL,700,"middle")
    d.save()


def endemism():
    d=Drawing("endemism", "Two hypothetical species are both rare. Three green amphibian symbols illustrate low abundance within a small island range. Three purple symbols spread across a broad mainland range illustrate a rare but widely distributed species.")
    d.text(310,35,"Rare endemic species",32,weight=700,anchor="middle")
    d.text(975,35,"Rare, widely distributed species",30,weight=700,anchor="middle")

    # An island contains the full range of the green species.
    d.rect(20,70,575,325,"#e4f0f3","none",24)
    d.add('<path d="M245 145 L302 110 L348 148 L340 195 L372 239 L325 285 L267 276 L222 215 Z" fill="#d9e6cf" stroke="#527b3d" stroke-width="3"/>')
    d.add('<path d="M510 70 L595 70 L595 395 L526 395 L490 343 L518 289 L488 225 L524 157 L495 115 Z" fill="#ebece5" stroke="#a2aaa0" stroke-width="2"/>')
    for x,y in [(284,158),(311,207),(283,246)]:
        d.animal(x,y,5,.65)
    d.text(296,339,"Island",27,MUTED,anchor="middle")
    d.text(550,375,"Mainland",20,MUTED,anchor="middle")
    d.text(310,447,"Small geographic range",32,SPECIES[5],700,"middle")
    d.text(310,490,"Low abundance",26,MUTED,anchor="middle")

    # The same sparse symbols illustrate rarity across a much larger range.
    d.rect(690,70,585,325,"#ebece5","none",24)
    d.add('<path d="M735 115 L860 90 L1000 110 L1115 90 L1235 140 L1225 265 L1195 365 L1040 375 L915 350 L760 370 L710 260 Z" fill="#e4d9ee" stroke="#8660a4" stroke-width="2"/>')
    for x,y in [(780,150),(980,230),(1170,310)]:
        d.animal(x,y,2,.65)
    d.text(975,340,"Mainland",27,MUTED,anchor="middle")
    d.text(975,447,"Large geographic range",32,SPECIES[2],700,"middle")
    d.text(975,490,"Low abundance",26,MUTED,anchor="middle")
    d.save()


def occupancy():
    d=Drawing("occupancy","Across four toy parks, species A is in four parks, B in two and C D E in one each. Their inverse occupancy weights are one quarter, one half, one, one and one.")
    for j in range(5):
        x=360+j*185
        d.animal(x,50,j,.9,True)
        for i,row in enumerate(TOY):
            d.rect(x-49,115+i*58,98,45,SPECIES[j] if row[j] else "white",LINE,5)
        r=int((TOY[:,j]>0).sum())
        d.text(x,395,r,31,anchor="middle")
        d.text(x,467,f"{1/r:g}",34,TEAL,700,"middle")
    for i in range(4): d.text(40,147+i*58,f"Park {i+1}",26)
    d.text(40,395,"Parks recorded (r)",26,weight=700)
    d.text(40,467,"Weight (1/r)",26,TEAL,700)
    d.save()


def extent():
    d=Drawing("extent","A species recorded in only one of four surveyed parks is subsequently recorded in three additional parks. Its inverse occupancy weight changes from one to one quarter.")
    for x,title,n in [(20,"Four-park reference",1),(690,"Expanded reference",4)]:
        d.text(x+280,45,title,32,weight=700,anchor="middle")
        for i in range(7 if n==4 else 4):
            xx=x+80+(i%4)*130; yy=150+(i//4)*135
            d.ellipse(xx,yy,48,45,"white",LINE)
            if i==0 or (n==4 and i>=4): d.animal(xx,yy,2,.7)
        d.text(x+280,390,f"C recorded in {n} park"+('s' if n>1 else ''),29,anchor="middle")
        d.text(x+280,460,f"Weight = {1/n:g}",38,TEAL,700,"middle")
    d.line(580,220,670,220,TEAL,4,True)
    d.save()


def shapes():
    d=Drawing("shapes","Two 500 square kilometer compact blobs and two equal area elliptical stripes, with aspect ratio five to one, motivate a separate shape comparison.")
    d.text(320,45,"Two blobs",35,TEAL,700,"middle")
    d.text(990,45,"Two stripes",35,CORAL,700,"middle")
    r=100
    for x,y in [(200,190),(440,340)]: d.ellipse(x,y,r,r,PALE,TEAL)
    rx,ry=r*np.sqrt(5),r/np.sqrt(5)
    for x,y in [(980,160),(980,340)]: d.ellipse(x,y,rx,ry,"#f3e7d9",CORAL)
    d.text(320,480,"1,000 km² total",29,TEAL,700,"middle")
    d.text(990,480,"1,000 km² total",29,CORAL,700,"middle")
    d.save()


def actual_map():
    dataset=ROOT/"docs/data/ME_ImaginaryParks.geojson"
    features=gpd.read_file(dataset).to_crs(5070)
    parks=features[features.feature_type=="park"]
    records=features[features.feature_type=="occurrence"]
    maine=gpd.read_file(ROOT/"docs/labs/ME_ShapeFiles/Maine_State_Boundary.shp").to_crs(5070)
    fig,ax=plt.subplots(figsize=(10.8,6.8),layout="constrained")
    fig.patch.set_facecolor(PAPER);ax.set_facecolor(PAPER)
    maine.plot(ax=ax,color="#ebece5",edgecolor="#a2aaa0",linewidth=.8)
    colors={"single_large":TEAL,"several_small":"#b56b32"}
    for scenario,group in parks.groupby("scenario"):
        group.plot(ax=ax,color=colors[scenario],alpha=.55,edgecolor=INK,linewidth=1.2)
    records.plot(ax=ax,color=INK,markersize=2,alpha=.35)
    for p in parks.itertuples():
        xy=p.geometry.representative_point()
        ax.annotate(p.park_id,(xy.x,xy.y),ha="center",va="center",fontsize=15,
                    weight="bold",bbox=dict(facecolor="white",alpha=.9,edgecolor="none",pad=3))
    xmin,ymin,xmax,ymax=parks.total_bounds
    ax.set_xlim(xmin-18000,xmax+18000);ax.set_ylim(ymin-12000,ymax+16000)
    ax.set_aspect("equal");ax.set_axis_off()
    x,y=xmin-7000,ymin-7000
    ax.plot([x,x+20000],[y,y],color=INK,lw=3)
    ax.text(x+10000,y+2200,"20 km",ha="center",fontsize=12,color=INK)
    inset=ax.inset_axes([.72,.61,.25,.37]);inset.set_facecolor("white")
    maine.plot(ax=inset,color="#ebece5",edgecolor="#8a948a",linewidth=.7)
    parks.plot(ax=inset,color=TEAL);inset.set_axis_off()
    fig.savefig(OUT/"Lecture10-parks.png",dpi=180,facecolor=PAPER)
    plt.close(fig)
    return dict(dataset="docs/data/ME_ImaginaryParks.geojson",
                sha256=hashlib.sha256(dataset.read_bytes()).hexdigest(),
                records=len(records),original_records=int((records.synthetic==False).sum()),
                imaginary_species=int(records[records.imaginary_species==True].species.nunique()),
                species=int(records.species.nunique()))


def study_area_map():
    features=gpd.read_file(ROOT/"docs/data/ME_ImaginaryParks.geojson").to_crs(5070)
    parks=features[features.feature_type=="park"]
    records=features[features.feature_type=="occurrence"]
    records=records[records.intersects(parks.geometry.union_all())]
    maine=gpd.read_file(ROOT/"docs/labs/ME_ShapeFiles/Maine_State_Boundary.shp").to_crs(5070)
    fig,axes=plt.subplots(1,2,figsize=(10.2,5.6),layout="constrained")
    fig.patch.set_facecolor(PAPER)
    colors={"single_large":TEAL,"several_small":"#b56b32"}
    for ax,title in zip(axes,["Maine","Parks and occurrence records"]):
        ax.set_facecolor(PAPER)
        maine.plot(ax=ax,color="#ebece5",edgecolor="#a2aaa0",linewidth=.7)
        for scenario,group in parks.groupby("scenario"):
            group.plot(ax=ax,color=colors[scenario],alpha=.65,edgecolor=INK,linewidth=.8)
        ax.set_title(title,fontsize=16,color=INK,pad=12)
        ax.set_aspect("equal")
        ax.set_axis_off()
    detail=axes[1]
    records.plot(ax=detail,color=INK,markersize=2,alpha=.5)
    for park in parks.itertuples():
        point=park.geometry.representative_point()
        detail.annotate(park.park_id,(point.x,point.y),ha="center",va="center",
                        fontsize=12,weight="bold",
                        bbox=dict(facecolor="white",alpha=.85,edgecolor="none",pad=2))
    xmin,ymin,xmax,ymax=parks.total_bounds
    detail.set_xlim(xmin-10000,xmax+10000)
    detail.set_ylim(ymin-12000,ymax+10000)
    x,y=xmin-4000,ymin-7000
    detail.plot([x,x+20000],[y,y],color=INK,lw=2.5)
    detail.text(x+10000,y+2200,"20 km",ha="center",fontsize=10,color=INK)
    fig.savefig(OUT/"Lecture10-study-area.png",dpi=180,facecolor=PAPER)
    plt.close(fig)


def rarefaction():
    counts_a=np.array([25,25,25,25]);counts_b=np.array([195,1,1,1,1,1])
    fig,ax=plt.subplots(figsize=(11.6,4.6),layout="constrained")
    fig.patch.set_facecolor(PAPER);ax.set_facecolor(PAPER)
    for counts,color,label in [(counts_a,TEAL,"A: 100 records, 4 species"),
                               (counts_b,CORAL,"B: 200 records, 6 species")]:
        total=int(counts.sum());ns=np.arange(1,total+1);means=[]
        for n in ns:
            p_absent=[]
            for count in counts:
                available=total-int(count)
                if available<n: p_absent.append(0)
                else:
                    logratio=(gammaln(available+1)-gammaln(n+1)-gammaln(available-n+1)
                              -gammaln(total+1)+gammaln(n+1)+gammaln(total-n+1))
                    p_absent.append(np.exp(logratio))
            means.append(sum(1-np.array(p_absent)))
        ax.plot(ns,means,lw=3.5,color=color,label=label)
        ax.scatter([total],[len(counts)],s=80,color=color,zorder=4)
    ax.axvline(100,color=MUTED,ls="--",lw=1.5)
    ax.annotate("Compare at 100 records",(100,3.5),xytext=(115,2.3),
                arrowprops=dict(arrowstyle="->",color=MUTED),fontsize=15,color=MUTED)
    ax.set(xlabel="Records drawn without replacement",ylabel="Expected recorded richness",
           xlim=(0,205),ylim=(0,6.5))
    ax.tick_params(labelsize=14);ax.xaxis.label.set_size(17);ax.yaxis.label.set_size(17)
    ax.legend(loc="upper left",fontsize=14,frameon=False)
    ax.spines[["top","right"]].set_visible(False)
    fig.savefig(OUT/"Lecture10-rarefaction.png",dpi=180,facecolor=PAPER);plt.close(fig)
    return dict(A=counts_a.tolist(),B=counts_b.tolist(),
                method="exact hypergeometric expectation; uniform draws without replacement",
                common_n=100,expected_A=4.0,expected_B=3.5)


def main():
    for function in [sloss,habitats,matrix,richness,evenness,alpha_beta,complementarity,
                     jaccard_sets,nestedness,bray,totals,endemism,occupancy,extent,shapes]:
        function()
    study_area_map()
    provenance=dict(map=actual_map(),rarefaction=rarefaction(),
                    toy_matrix=TOY.tolist(),
                    even_counts=[10,10,10],dominated_counts=[28,1,1],
                    jaccard_example=float(jaccard([1,1,1,0],[1,0,1,1])),
                    bray_example=float(braycurtis([8,1,1],[1,8,1])))
    (OUT/"Lecture10-example-results.json").write_text(json.dumps(provenance,indent=2)+"\n")
    print("Built 15 schematic SVGs, two park maps, a rarefaction figure, and provenance JSON.")


if __name__=="__main__":
    main()
