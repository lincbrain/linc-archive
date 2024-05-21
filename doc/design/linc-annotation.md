# Add manual annotation tool for the LINC Project

Outlined in this document are the manual annotation use cases for the 5 year LINC project.
As additional use cases and requirements are defined they will be added in follow up design documents.

## Use cases 

### Use case 1 - Manual annotation of axon bundles

Outline axon bundles on 2D slices to create volumetric segmentations.  For example segmentations see [Sundaresan et al., bioRxiv 2023](https://doi.org/10.1101/2023.09.30.560310) which were generated in Neurolucida.

Annotation of axon bundles will occur in the following data modalities:
1. Optical microscopy of histological sections of axon tracers
2. Light-sheet microscopy (LSM) sections of axonal markers
3. Hierarchical Phase-Contrast Tomography (HiP-CT)

### Use case 2 - Manual annotation of individual axons

Pixel-wise classifier of micro-CT images.

Similar segmentations were previously performed on electron microscopy (EM) images.  Labels were created for artifacts, myelin, intracellular spaces, and extracellular spaces.  These manual segmentations were performed in FslView and saved in NIfTI files.  The manuscript for this work is currently being prepared.

## Requirements

1. Cloud-based manual annotation tool
2. Annotation tool should integrate with centralized data on AWS S3
3. Annotate axon bundles
4. Annotate branching axon bundles
5. Store two annotations for a subset of axon bundles
6. Annotate 1-3 unique axon bundles per slice
7. Team-based augmentation of labeled datasets
8. Add landmarks
9. Pixel-wise classifier (i.e. trace individual axons)
10. Interpolate pixel-wise segmentations between slices
11. Create other labels used to evaluate automated methods - Need to specify further.
12. Make annotations available for dissemination
13. Visualize streamlines
14. Filter streamlines that pass through a region of interest
15. View multiple imaging layers in the same view

## Possible solutions

### Neuroglancer

- Web-based, mutli-scale volumetric data visualization
- Source code - https://github.com/google/neuroglancer
- Does not natively include features for voxel-wise segmentation or annotation management.

### NeuroTrALE

### SmartInterpol

- Summary - "Smart Interpol is a semi-automated segmentation tool which, starting from a volume with a sparse subset of manually labelled slices, estimates the corresponding dense segmentation in an automated fashion."
- Source code - https://github.com/aleatzeni/SmartInterpol
- MATLAB-based package
- Input image and label volumes, and output label volumes should be in NIfTI format
- Last updated in May 2022

### Open questions

- Has SmartInterpol been integrated with Neuroglancer or NeuroTrALE?

### WEBKNOSSOS
References
- Web application - [Source code](https://github.com/scalableminds/webknossos)
- Python API - [Source code](https://github.com/scalableminds/webknossos-libs) and [docs](https://docs.webknossos.org/webknossos-py/)
- REST API is deprecated
Skeleton annotations
- Draw line segments with branching
- Stored in [NML file format](https://docs.webknossos.org/webknossos/data_formats.html#nml-files)

#### Open questions

### CAVE
