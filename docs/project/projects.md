# Final Projects

The final project is an opportunity to ask a question about biodiversity and
spatial patterns, work through an analysis, and communicate what you learned.
You may build on an approach from the course or explore something we have not
covered. The essential requirement is that your project connects biodiversity
to space: where organisms occur, how diversity varies among places, or how
ecological patterns change with distance, environment, or spatial scale.

## Choosing a system, question, and data

The spatial extent and study organism(s) are completely up to you. Projects may 
focus on an individual species or on communities.

Data may come from online repositories, published studies and their associated
datasets, or your own research projects. Please do not reuse any of the datasets
we have used for the coursework, I prefer you to identify and fetch your own data.
Cite your data sources and any code or methods you adapt.

**Data considerations:**

* I expect you to obtain new data for this project (in the sense
that I do not want you reusing data we analysed in class).
* **Bioclim:** Feel free to use the bioclim variables in `shared/bioclim`.
* **Small data files:** If you download small (<25MB) csv files for your project
from online repositories please add/commit/push these files to your `project`
directory.
* **Large data/env files (>25Mb)**: For large datasets do not commit these to your
repository, rather document how you obtained them at the top of your notebook file.
* **Sensitive data:** If you want to use your own research data and prefer not to
publish it publicly on github that is totally fine, just please let me know and we
will come up with a workable solution for privately sharing the data with me.

## Final project deliverables

### 1. Jupyter notebook in your course repository

**The goal is to submit a notebook that I will be able to reproduce!**

Create a new jupyter notebook in the `BIO597-SpatialBiodiversity/docs/project`
directory. Use Markdown cells to explain the analysis alongside the code, figures,
and maps. The notebook should tell a coherent story and should have the following
sections:

1. **Background and question:** Introduce the system including study area and taxa, 
   explain why the spatial pattern matters, and state your question or prediction.
   Include a link here to your final google slides presentation (see below).
2. **Imports:** Make note of the packages needed to run the notebook, and provide
   install instructions if necessary. 
3. **Data loading/QC:** Include data citations, and instructions for
   obtaining any data that are not checked-in to your repository. Justify all relevant
   cleaning or filtering decisions.
4. **Methods:** Explain the analytical approach and why it fits your question.
   Provide explicit documentation in markdown cells for each step of the analysis.
5. **Results:** Show the main findings with readable maps, plots, or tables.
   Include labels, legends, and a brief interpretation of each main result.
6. **Discussion and future directions:** Answer your question as far as the data
   allow. Discuss limitations, relevant sampling or spatial biases, and what
   you would do next with more time or better data.

The notebook is the written project submission; a separate paper or report is
not required.

### 2. Final presentation in Google Slides

Prepare a **presentation of 10 minutes or less** in Google Slides (6-8 slides).
Give the class enough context to understand your system and question, then focus 
on what you did and what you found. Include:

- Background on the system and study area
- The research question or prediction
- Data and methods, with enough detail to understand the analysis
- Main results, emphasizing clear maps and figures
- Interpretation, limitations, and future directions

