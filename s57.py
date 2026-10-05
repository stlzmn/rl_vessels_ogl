import os
import pyproj
import numpy as np
import collections
from osgeo import ogr
from osgeo import osr
from scipy.spatial import Delaunay
from functools import cached_property
from data_preparation import dist_azim

chart_dir = 'maps'
gdynia = 'PL5GDYNA.000'
wybrzeze = 'PL5MP500.000'

LAYER_COLOR = {
'ROADWY': '#0000EE', #Road
'RAILWY': '#000000', #Railway
'LNDARE': '#ffd87d', #Land area
'BCNLAT': '#000000', #Beacon, lateral
'BCNSPP': '#000000', #Beacon, special purpose/general
'BRIDGE': '#000000', #Bridge
'BUISGL': '#000000', #Building, single
'BUAARE': '#F8F48F', #Built-up area
'BOYLAT': '#BBAACC', #Buoy, lateral
'BOYSPP': '#000000', #Buoy, special purpose/general
'CBLSUB': '#ff00ff', #Cable, submarine
'CTNARE': '#000000', #Caution area
'COALNE': '#231f20', #Coastline
'CONVYR': '#000000', #Conveyor
'CRANES': '#EEFFAA', #Crane
'DEPARE': '#045FB7', #Depth area
'DEPCNT': '#2A2CAB', #Depth contour
'DRYDOC': '#ffd87d', #Dry dock
'FLODOC': '#ffd87d', #Floating dock
'HRBARE': '#3FDCFC', #Harbour area
'HRBFAC': '#A1A4A8', #Harbour facility
'HULKES': '#000000', #Hulk
'LNDRGN': '#ffbd33', #Land region
'LNDMRK': '#FF0000', #Landmark
'LIGHTS': '#AAAAAA', #Light
'MORFAC': '#000000', #Mooring/warping facility
'NAVLNE': '#FF00FF', #Navigation line
'OBSTRN': '#000000', #Obstruction
'PILPNT': '#000000', #Pile
'PIPSOL': '#CCCCCC', #Pipeline, submarine/on land
'PONTON': '#000000', #Pontoon
'PYLONS': '#000000', #Pylon/bridge support
'RDOSTA': '#CCCCDD', #Radio station
'RECTRC': '#000000', #Recommended track
'RSCSTA': '#000000', #Rescue station
'RESARE': '#3ed3ed', #Restricted area
'SEAARE': '#aae0fa', #Sea area / named water area
'SLCONS': '#000000', #Shoreline Construction
'SILTNK': '#000000', #Silo / tank
'SLOTOP': '#000000', #Slope topline
'SOUNDG': '#ffffff', #Sounding
'TOPMAR': '#EEAAEE', #Topmark
'UWTROC': '#000000', #Underwater rock / awash rock
'UNSARE': '#000000', #Unsurveyed area
'VEGATN': '#ffd87d', #Vegetation
'WRECKS': '#000000', #Wreck
'TSSBND': '#AA00FF', #TSS boundary
'TSSLPT': '#00FF00', #TSS ??
'TSELNE': '#f21111' #nie wiem co to
}

class Layer2Color(collections.UserDict):
    def __getitem__(self, key):
        item = super().__getitem__(key)
        return self._hex_to_rgb(item)
    
    def _hex_to_rgb(self, color):
        color = color.lstrip('#')
        return tuple(int(color[i: i+2], 16) / 255 for i in (0, 2, 4))
    
    def __enter__(self):
        return self.__class__(LAYER_COLOR)
    
    def __exit__(self, exec_ty, exec_val, tb):
        pass

class Layer:
    def __init__(self, name, layer_source):
        self.name = name
        self.layer_source = layer_source
    
    @cached_property
    def data(self):
        methods = {'POINT': self._point, 'LINESTRING': self._line, 'POLYGON': self._polygon}
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            name = geom.GetGeometryName()
            if 'MULTI' in name:
                name = name[5:]
            break
        return methods[name](), name
    
    def _point(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            if (points := geom.GetPoints()) is not None:
                result.append([*points[0], 0.0])
            else:
                for idx in range(geom.GetGeometryCount()):
                    result.append([geom.GetGeometryRef(idx).GetX(), geom.GetGeometryRef(idx).GetY(), geom.GetGeometryRef(idx).GetZ()])
        result = np.expand_dims(np.array(result, dtype=np.float32), axis=0)

        return result
    
    def _line(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            result.append(np.array(geom.GetPoints(), dtype=np.float32))
        return result
    
    def _polygon(self):
        result = []
        for feature in self.layer_source:
            geom = feature.GetGeometryRef()
            for idx in range(geom.GetGeometryCount()):
                linear_ring = geom.GetGeometryRef(idx)
                poly = np.array(linear_ring.GetPoints(), dtype=np.float32)
                result.append(poly)
        return result
                
class DataSource:
    def __init__(self, path):
        self.path = path
        self.data_source = ogr.Open(self.path, 0)
        self.layers = self._read_ds()

    def _read_ds(self):
        if not os.path.exists(self.path):
            return FileNotFoundError(f'File {self.path} not found.')

        layers_kv = [(layer.GetName(), Layer(layer.GetName(), layer)) for layer in self.data_source]
        return dict(layers_kv)
    
    # def insert_buoy(self, buoy):
    #     del self.data_source
    #     data_source = ogr.Open(self.path, 1)
    #     lyr = data_source.GetLayer('BCNLAT')
    #     print(lyr)


    def geom_cords(self, layer_name):
        if not layer_name in self.layers.keys():
            print(f'Layer {layer_name} not found in the datasource.')
            return []
        return self.layers[layer_name].data
    
class Buoy:
    __slots__ = 'lon', 'lat'
    def __init__(self, lon ,lat):
        self.lon = lon
        self.lat = lat

    def __repr__(self):
        return f'{self.__class__.__name__}(lon={self.lon}, lat={self.lat})'


# if __name__ == '__main__':
#     path = os.path.join('maps', 'PL5GDYNA.000')
#     ogr.UseExceptions() 
#     ds = ogr.Open(path, 0)
#  # 0 for read-only mode

#     # Create a new dataset in memory or a new file
#     new_ds = ogr.GetDriverByName("GTiff").CreateDataSource("GDYNIA_MODIFIED.tif")

#     # Loop through the layers in the existing dataset
#     for i in range(ds.GetLayerCount()):
#         existing_layer = ds.GetLayerByIndex(i)

#         # Create a new layer in the new dataset with the same name and geometry type
#         new_layer = new_ds.CreateLayer(existing_layer.GetName(), geom_type=existing_layer.GetGeomType())

#         # Copy the fields and features from the existing layer to the new layer
#         new_layer.CreateFields(existing_layer.schema)
#         for feature in existing_layer:
#             new_layer.CreateFeature(feature)

#     target_layer = new_ds.GetLayerByName('BCNLAT')
#     target_layer_definition = target_layer.GetLayerDefn()
#     new_feature = ogr.Feature(target_layer_definition)

#     new_buoy_geometry = ogr.Geometry(ogr.wkbPoint)
#     new_buoy_geometry.AddPoint_2D(18.505, 54.505)
#     new_feature.SetGeometry(new_buoy_geometry)

#     new_feature.SetField(1, 'MojaBoja')
#     target_layer.CreateFeature(new_feature)

#     # Cleanup
#     ds = None
#     new_ds = None

#     # path = os.path.join('maps', 'GDYNIA_MODIFIED.000')
#     # ogr.UseExceptions() 
#     # ds = ogr.Open(path, 0)
#     # existing_layer = ds.GetLayer('BCNLAT')

#     # for feature in existing_layer:
#     #     geom = feature.GetGeometryRef()
#     #     name = geom.GetGeometryName()




