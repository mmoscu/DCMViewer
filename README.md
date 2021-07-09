# DCMViewer
Web-based app for viewing DICOM files in 2D/3D with annotations.

Uses the streamlit Python-based library for web apps: https://docs.streamlit.io/en/stable/

For interactive image visualization, uses Plotly, a Python graphing library: https://plotly.com/python/

App structure based on dicom-labeling-tool project: https://github.com/angelomenezes/dicom-labeling-tool

Image used as icon: https://www.maxpixel.net/See-Icon-Eye-Viewing-1103593

## Features 
1. Loading of possibly multiple .dcm series, each stored in a folder, all folders archived in a .zip. Can be loaded either from GDrive or directly.
2. Selection between 2D-3D views. The 2D views offer axial, coronal and sagittal views, with color thresholding.
3. The axial view allows interactive visualization with limited annotation possibilites. Annotated files can be saved as .png files.
4. The 3D view is interactive. It also offers a thresholding option.
5. The sidebar allows for selecting (or adding) of anomalies and associatied axial slices. These annotations can be be saved as .json file for further use. 

## Prospects
1. Creation of streamlit components able to recover the coordinates of the mouse cursor. Usable in developping further figure interaction.
2. Posibility of loading other file extensions (either .rar archives) and single-file visualization.
3. Add a text area for report writing and exportation as .pdf.

## Currently hosted at https://share.streamlit.io/mmoscu/dcmviewer/main/DCMViewer.py

## How to use
Use `pip install` to install streamlit and the packages from requirements.txt, then use `streamlit run DCMViewer.py` to run the app locally.
