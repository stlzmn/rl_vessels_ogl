# AIS OpenGL Renderer

Real-time OpenGL visualization of AIS vessel traffic over S-57 electronic navigational chart data.

## What it does

- Reads live AIS traffic from a TCP/NMEA source and decodes it with `pyais`.
- Parses S-57 chart cells (via GDAL/OGR) and renders coastlines, depth areas, buoys and other chart objects.
- Draws vessels and chart layers in a GLFW/OpenGL 3.3 core-profile window, with an optional PySide UI panel.
- Converts between WGS84 and local XY coordinates for rendering and distance/azimuth calculations.

## Project layout

- `application.py` / `pyside_ui_application.py` - app entry points and window setup
- `renderer.py`, `scene.py`, `meshes.py`, `shaders/` - OpenGL rendering pipeline
- `s57.py` - S-57 chart cell parsing and layer styling
- `report_flow.py`, `entity.py`, `data_preparation.py` - AIS message ingestion and vessel state
- `dependencies/requirements.txt` - pip requirements used by the Dockerfile (does not include GDAL)

## GDAL

GDAL/OGR (`osgeo` Python bindings) is required but is not installed by this repo or its
Dockerfile - install it yourself, matching your platform and Python version. This project
was developed against **GDAL 3.4.1** on Linux and **GDAL 3.2.3** on Windows, both for
Python 3.8 (cp38). Options:

- Linux: install the `libgdal-dev` system package for a matching GDAL version, then
  `pip install GDAL==<version>` (must match the installed `libgdal` version).
- Windows: use a prebuilt wheel, e.g. from
  [cgohlke's GDAL wheels](https://github.com/cgohlke/geospatial-wheels).
- conda/mamba (any platform): `conda install -c conda-forge gdal=3.4.1`

## Chart data

This repository does not ship S-57 ENC chart cells. Official ENC data (e.g. from a national
hydrographic office or a RENC/PRIMAR/IC-ENC distributor) is copyrighted and licensed, not
freely redistributable. Place your own licensed `.000` cells under a local `maps/` directory
(ignored by git) before running the app; see `s57.py` for the expected directory/filenames.

## Running

```bash
# install GDAL yourself first, see the GDAL section above
pip install -r dependencies/requirements.txt
python application.py
```

Or build the provided Docker image:

```bash
docker build -t ais-opengl-renderer .
```

## License

MIT - see [LICENSE](LICENSE). Keep the copyright notice and give credit if you reuse this code.
