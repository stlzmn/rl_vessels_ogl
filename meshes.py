from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import s57
from data_preparation import wgs84_to_xy
import time

class Point:
    def __init__(self, verts, color):
        points = np.array(list((map(lambda x: wgs84_to_xy(*x), verts[:, :2]))), dtype=np.float32)
        points = np.c_[points, verts[:, 2] / 1852]
        self.verts = np.c_[points, np.ones((points.shape[0], 3), dtype=np.float32) * np.array(color, dtype=np.float32)].reshape(-1, 1)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, (GLfloat * len(self.verts))(*self.verts), GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
        
    def __len__(self):
        return len(self.verts)
    
    def __getitem__(self, idx):
        return self.verts[idx]

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_POINTS, 0, len(self) // 5)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))#self.ibo,

class Line:
    def __init__(self, verts, color):
        points = np.array(list((map(lambda x: wgs84_to_xy(*x), verts))), dtype=np.float32)
        print(points)
        # points = np.c_[points, np.zeros((points.shape[0], 1), dtype=np.float32)]
        self.verts = np.c_[points, np.ones((points.shape[0], 3), dtype=np.float32) * np.array(color, dtype=np.float32)].reshape(-1, 1)

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, (GLfloat * len(self.verts))(*self.verts), GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 20, ctypes.c_void_p(8))
        
    def __len__(self):
        return len(self.verts)
    
    def __getitem__(self, idx):
        return self.verts[idx]

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_LINE_STRIP, 0, len(self) // 5)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))#self.ibo,

class Polygon:
    def __init__(self, verts, color, holes=None):
        if holes is None:
            holes = []
        points = np.array(list((map(lambda x: wgs84_to_xy(*x), self._triangulate(verts, holes)))), dtype=np.float32)
        points = np.c_[points, np.zeros((points.shape[0], 1), dtype=np.float32)]
        self.verts = np.c_[points, np.ones((points.shape[0], 3), dtype=np.float32) * np.array(color, dtype=np.float32)].reshape(-1, 1)

        # self.verts.tofile(f'polygons_files/{str(time.time()).replace(".", "_")}.csv', sep=',')

        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)
        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.verts.nbytes, (GLfloat * len(self.verts))(*self.verts), GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
        
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

    def __len__(self):
        return len(self.verts)
    
    def __getitem__(self, idx):
        return self.verts[idx]

    def _triangulate(self, polygon, holes):
        """
        Returns a list of triangles.
        Uses the GLU Tesselator functions!
        """
        vertices = []
        def edgeFlagCallback(param1, param2): pass
        def beginCallback(param=None):
            vertices = []
        def vertexCallback(vertex, otherData=None):
            vertices.append(vertex[:2])
        def combineCallback(vertex, neighbors, neighborWeights, out=None):
            out = vertex
            return out
        def endCallback(data=None): pass

        tess = gluNewTess()
        gluTessProperty(tess, GLU_TESS_WINDING_RULE, GLU_TESS_WINDING_ODD)
        gluTessCallback(tess, GLU_TESS_EDGE_FLAG_DATA, edgeFlagCallback)#forces triangulation of polygons (i.e. GL_TRIANGLES) rather than returning triangle fans or strips
        gluTessCallback(tess, GLU_TESS_BEGIN, beginCallback)
        gluTessCallback(tess, GLU_TESS_VERTEX, vertexCallback)
        gluTessCallback(tess, GLU_TESS_COMBINE, combineCallback)
        gluTessCallback(tess, GLU_TESS_END, endCallback)
        gluTessBeginPolygon(tess, 0)

        #first handle the main polygon
        gluTessBeginContour(tess)
        for point in polygon:
            point3d = (point[0], point[1], 0)
            gluTessVertex(tess, point3d, point3d)
        gluTessEndContour(tess)

        #then handle each of the holes, if applicable
        if holes != []:
            for hole in holes:
                gluTessBeginContour(tess)
                for point in hole:
                    point3d = (point[0], point[1], 0)
                    gluTessVertex(tess, point3d, point3d)
                gluTessEndContour(tess)

        gluTessEndPolygon(tess)
        gluDeleteTess(tess)
        return vertices

    def draw(self):
        glBindVertexArray(self.vao)
        glDrawArrays(GL_TRIANGLES, 0, len(self) // 6)

    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))#self.ibo,

class EncMesh:
    def __init__(self, filepaths):
        self.parts = list(self._load(filepaths))
        # self.parts = self._load(filepaths)

    def render(self):
        for layer_mesh in self.parts:
            layer_mesh.draw()

    def _load(self, filepaths):
        for filepath in filepaths:
            ds = s57.DataSource(filepath)
            with s57.Layer2Color() as l2c:
                for l_name, hex_color in l2c.items():
                    try:
                        crds_batch, layer_dtype = ds.geom_cords(l_name)
                    except ValueError:
                        continue
                    for crd_poly in crds_batch:
                        if layer_dtype == 'POINT':
                            if crd_poly.shape[0] == 0:
                                continue
                            yield Point(crd_poly, hex_color)
                        elif layer_dtype == 'LINESTRING':
                            if crd_poly.ndim != 2:
                                continue
                            yield Line(crd_poly, hex_color)
                        elif layer_dtype == 'POLYGON':
                            yield Polygon(crd_poly, hex_color)
    
    def destroy(self):
        for poly in self.parts:
            poly.destroy()

# if __name__ == '__main__':
#     enc = EncMesh(['maps/PL5GDYNA.000',])#  'maps/PL2MP500.000'
#     for p in enc.polygons:
#         print(p.verts)



class Mesh:
    def __init__(self, file_path):
        self.vertices = self.load_mesh(file_path)
        self.n_verts = len(self.vertices) // 8

        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)
        self.vbo = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
        glBufferData(GL_ARRAY_BUFFER, self.vertices.nbytes, self.vertices, GL_STATIC_DRAW)

        glEnableVertexAttribArray(0)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(0))
        glEnableVertexAttribArray(1)
        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(12))
        glEnableVertexAttribArray(2)
        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 32, ctypes.c_void_p(20))

    def load_mesh(self, file_path):
        v, vt, vn, vertices = [], [], [], []
        with open(file_path, 'r') as f:
            line = f.readline()
            while line:
                first_space = line.find(' ')
                flag = line[0:first_space]
                if flag == 'v':
                    line = line.replace('v ', '')
                    line = line.split(' ')
                    v.append([float(x) for x in line])
                if flag == 'vt':
                    line = line.replace('vt ', '')
                    line = line.split(' ')
                    vt.append([float(x) for x in line])
                if flag == 'vn':
                    line = line.replace('vn ', '')
                    line = line.split(' ')
                    vn.append([float(x) for x in line])
                if flag == 'f':
                    line = line.replace('f ', '')
                    line = line.replace('\n', '')
                    line = line.split(' ')
                    face_verts = []
                    face_texs = []
                    face_norms = []
                    for vertex in line:
                        l = vertex.split('/')
                        pos = int(l[0]) - 1
                        face_verts.append(v[pos])
                        tex = int(l[1]) - 1
                        face_texs.append(vt[tex])
                        norm = int(l[2]) - 1
                        face_norms.append(vn[norm])

                    tri_in_face = len(line) - 2
                    vert_order = []
                    for i in range(tri_in_face):
                        vert_order.append(0)
                        vert_order.append(i + 1)
                        vert_order.append(i + 2)
                    for i in vert_order:
                        for x in face_verts[i]:
                            vertices.append(x)
                        for x in face_texs[i]:
                            vertices.append(x)
                        for x in face_norms[i]:
                            vertices.append(x)
                line = f.readline()
        return np.array(vertices, dtype=np.float32)
    
    def destroy(self):
        glDeleteVertexArrays(1, (self.vao,))
        glDeleteBuffers(1, (self.vbo,))