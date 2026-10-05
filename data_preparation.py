import pyproj
import numpy as np
from constants import SCREEN_WIDTH, SCREEN_HEIGHT, DISPLAY_RANGE

def dist_azim(batch):
        ref_point = (54.56, 18.5)
        wgs84 = pyproj.Geod(ellps='WGS84')
        for crds in batch:
            try:
                ref_pt = np.tile(np.array(ref_point), crds.shape[0]).reshape(-1, 2)
                fwd_azimuths, _, dists = wgs84.inv(ref_pt[:, 0], ref_pt[:, 1], crds[:, 1], crds[:, 0])
            except Exception:
                 continue
            fwd_azimuths = np.deg2rad(fwd_azimuths)
            dists /= 1852.0

            yield dists, fwd_azimuths

def wgs84_to_xy(lon, lat):
    ref_point = (18.5, 54.56)
    wgs84 = pyproj.Geod(ellps='WGS84')
    fwd_azim, _, dist = wgs84.inv(lon, lat, *ref_point)
    fwd_azim = np.deg2rad(fwd_azim)
    dist = dist / 1852
    x = (dist / DISPLAY_RANGE) * SCREEN_WIDTH * np.cos(fwd_azim)
    y = (dist / DISPLAY_RANGE) * SCREEN_HEIGHT * np.sin(fwd_azim)
    # x = (x - SCREEN_WIDTH) / SCREEN_WIDTH
    # y = (y - SCREEN_HEIGHT) / SCREEN_HEIGHT
    return x, y
