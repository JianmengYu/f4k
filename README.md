# Massive Parallel Dataset Cleaning

My 4th year Honours project. 
The project adapts the decision algorithm developed by Matthew A. Pugh on a massive parallel scale.  
https://github.com/mattalexpugh  
This aims to remove a large amount of False Positive fish detections in the Fish4Knowledge (F4K) dataset, without losing too many True Positives.  
http://groups.inf.ed.ac.uk/f4k/  

## Contents

---

`run______.py` - mpi script for each stage of processing.

`f4klib.py` - contains necessary functions for extraction and processing.

`f4klib2.py` - contains optional functions for plotting and statistics.

`old-processing-scripts\` - contains outdated mpi processing scripts.

`old-scripts\` - contains outdated I/O processing scripts for parsing data.

---

`f4k notebook.ipynb` - Main experiment notebook.

`ML.ipynb` and `GroundTruth.ipynb` - Ground Truthing and Machine Learning experiments.

`SVM parameter find.ipynb` - Support Vector Machine experiments.

`Job partition stuff.ipynb` - For generating files necessary for extractions.

`final cleaning.ipynb` - Voting Strategy experiments.

`dissplots.ipynb` - Plotting for Dissertation.

---

`newgt\` - Additional Ground Truth Set

`mpi\` - `mpi-master-slave` library.

`lua\` - `Neural Network developed by Pugh.

`benchmarking\` - Performance testing. 

`workspace\` - Miscellaneous files needed for extraction.

---

