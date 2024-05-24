# Add manual annotation tool for the LINC Project

Authors: Kabilar Gunalan, Aaron Kanzer

Outlined in this document are the manual annotation use cases for the 5 year LINC project.
With the information at hand, we will select and deploy an annotation framework.
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
16. ?View NIfTI and/or NIfTI-Zarr files

## Possible solutions

### Neuroglancer

- Web-based, mutli-scale volumetric data visualization
- Source code - https://github.com/google/neuroglancer
- Does not natively include features for voxel-wise segmentation or annotation management.

### NeuroTrALE

# NeuroTrALE Data Manager

- [Source code](https://github.com/mit-ll/NeuroTrALE-data-manager)
- The NeuroTrALE Data Manager is also referred to as the NeuroTrALE Precomputed Service.
- "The NeuroTrALE Precomputed Service simply serves up existing imagery and annotations, and allows updating annotations. The imagery (image tiles) are ingested by using MIT's precomputed-tif tool, which takes a stack of tiff images and generates a directory tree of tiff files. Refer to https://github.com/chunglabmit/precomputed-tif."

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
- [Homepage](https://weblium.webknossos.org/)
- [Docs](https://docs.webknossos.org/webknossos/index.html)
- [Roadmap](https://webknossos.org/roadmap)
- Web application
    - [Source code](https://github.com/scalableminds/webknossos)
- Python API
    - [Source code](https://github.com/scalableminds/webknossos-libs)
    - [Docs](https://docs.webknossos.org/webknossos-py/)
- REST API is deprecated

Volume annotations
- [Docs](https://docs.webknossos.org/webknossos/volume_annotation.html)
- Summary - Voxel-wise segmentation
- Features
    - Brush tool
    - Interpolation between slices
    - AI-based quick-select tool with a bounding box. Not available in open-source version.
- [Supported data formats](https://docs.webknossos.org/webknossos/data_formats.html): WKW, OME-Zarr/NGFF, Precomputed, N5, Image Stacks
- "The WEBKNOSSOS-wrap (WKW) container format is used for all internal voxel data representations - both for the raw (microscopy) image datasets and segmentations."

Skeleton annotations
- [Docs](https://docs.webknossos.org/webknossos/skeleton_annotation.html)
- Summary - Draw line segments with branching
- Supported data format: [NML file format](https://docs.webknossos.org/webknossos/data_formats.html#nml-files)

Pricing
- [Plans](https://webknossos.org/pricing#compare-plans)
- [Features for each plan](https://webknossos.org/pricing#custom-4)

Application notes
- Annotations
    - Stored in [FossilDB](https://github.com/scalableminds/fossildb), which is a key-value store that is built on RocksDB.
    - Annotations can be accessed using the webknossos Python API, but should not be accessed directly through the FossilDB CLI.  The Python API will return the volume annotations (as a Zarr), the skeleton annotations, or bounding boxes.
    - Annotations can be backed up by taking a snapshot of the database using the [FossilDB CLI](https://github.com/scalableminds/fossildb?tab=readme-ov-file#installation--usage).
    - Annotations are versioned but each version is not available through the Python API.

Proof of concept notes
- POC available at https://webknossos-staging.lincbrain.org/
- User management on webknossos app is independent from lincbrain.org.
- Set up vendor accounts
    - [Docker Hub](https://hub.docker.com/u/lincbrain])
    - CircleCI
- Local deployment provides faster iteration of testing changes rather than deploying Docker containers via CircleCI pipeline
- AWS credentials are not encrypted in requests, fortunately SSL present, sent over HTTP/2
- Making webknossos instance a “LINC Archive” User so that a valid API Key exists

#### Open questions

1. Deployment
    1. *The EC2 instance type is prescribed by the documentation.  Does WebKNOSSOS have auto-scaling set up? ECS?
    2. *Does webknossos provide monitoring of backend resources? Does it rely on AWS-based metrics with alerts or another mechansim?
    3. Blue/green deployments? Canary releases? Noticed API versioning....
    4. CircleCI consistently fails on "Build webknossos docker image" unless target/is invoked locally first
    5. For local deployment, unable to render remote assets (e.g. Public Zarr asset on S3)
    6. For local deployment, React/TS is not recognized by Chrome browser extensions

1. Application
    1. When fetching assets from S3, why is the server called? Why not just retrieve from S3 directly?
    2. Is there support for visualizing NIfTI files?
    3. *How are annotations stored?  In the database within the container? 
    4. *How are annotations versioned?
    5. *How are the annotations backed up?
    6. *Since a `Reload` can be performed on a `Dataset`, how does a user know that a given annotation corresponds a specific version of the imaging data?

1. Custom development
    1. What would it look like to set up a contract for custom development that we may need on the WEBKNOSSOS backend or frontend?

### CAVE
