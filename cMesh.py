from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *
import numpy as np

from edgeFriend import *
import metalcompute as mc

class cVert:
    def __init__(self, i, n = None):
        self.i = i
        self.n = n

        self.e = []

        self.mesh = None
        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

    def get_coord(self):
        return self.mesh.get_vertex(self.i)
    
    def set_coord(self, co):
        self.mesh.set(self.i, co)

class cEdge:
    def __init__(self, v : list):
        self.v0 = v[0]
        self.v1 = v[1]

        self.l = []

        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

    def get_loop(self, v):
        for l in self.l:
            if l.v == v:
                return l

class cLoop:
    def __init__(self, v, e, f):
        self.v = v
        self.e = e
        self.f = f

        self.twin = None
        self.ln = None
        self.lp = None

class cFace:
    def __init__(self, indices : list, mesh = None):
        self.mesh = mesh

        self.indices = indices
        self.len = len(indices)
        self.l = None
        

        #For quad mesh only
        self.quad_indices = indices if len(indices) == 4 else None
        self.faceFriend = [None, ] * 4
        self.isCalled = False
        self.edgeFriend = [None, ] * 2
        self.n = None

        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

    def findFriend(self, face):
        for i, j in [[0, 3], [1, 0], [2, 1], [3, 2]]:
            for k in range(4):
                if self.quad_indices[k] == face.quad_indices[i] and self.quad_indices[(k + 1) % 4] == face.quad_indices[j]:
                    face.faceFriend[j] = self
                    self.faceFriend[k] = face

    def BFS(self, face=None):
        if face:
            if self.n is None:
                self.n = len(self.mesh.edgeFriend.i) // 4
                self.mesh.edgeFriend.i += self.quad_indices
            i = self.faceFriend.index(face)
            j = face.faceFriend.index(self)
            if j % 2 == 0:
                if i % 2 == 0:
                    self.quad_indices = self.quad_indices[1:4] + self.quad_indices[0:1]
                    self.mesh.edgeFriend.i[-4:] = self.quad_indices
                    self.faceFriend = self.faceFriend[1:4] + self.faceFriend[0:1]
                    i = self.faceFriend.index(face)
                self.edgeFriend[i // 2] = (face.n * 4 + j) // 2
            else:
                if i % 2 == 1:
                    self.quad_indices = self.quad_indices[1:4] + self.quad_indices[0:1]
                    self.mesh.edgeFriend.i[-4:] = self.quad_indices
                    self.faceFriend = self.faceFriend[1:4] + self.faceFriend[0:1]
                    i = self.faceFriend.index(face)
                face.edgeFriend[j // 2] = (self.n * 4 + i) // 2
        else:
            self.n = 0
            self.mesh.edgeFriend.i += self.quad_indices

        if self.isCalled:
            return

        self.isCalled = True
        for face in self.faceFriend:
            face.BFS(self)

    def __str__(self):
        return f"{self.n}\t{self.edgeFriend[0]}\t{self.edgeFriend[1]}\n{self.quad_indices[0]}\t{self.quad_indices[1]}\t{self.quad_indices[2]}\t{self.quad_indices[3]}"


class cMesh:
    def __init__(self):
        self.vertices = []
        self.verts = []
        self.edges = []
        self.loops = []
        self.faces = []

        self.quadMesh = None
        self.edgeFriend = None
        self.dev = mc.Device()

    def read_obj_quad(self, filename):
        self.vertices = []
        self.faces = []
        with open(filename, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    parts = line.strip().split()[1:]
                    vertex = [float(part) for part in parts]
                    self.vertices += vertex
                elif line.startswith('f '):
                    parts = line.strip().split()[1:]
                    indices = [int(part.split('/')[0]) - 1 for part in parts]
                    if len(indices) != 4:
                        raise ValueError("Only quads are supported")
                    newFace = cFace(indices, self)
                    for face in self.faces:
                        newFace.findFriend(face)
                    self.faces.append(newFace)

    def get_vertex(self, n):
        return self.vertices[n * 3:n * 3 + 3]

    def set_vertex(self, n, co):
        self.vertices[n * 3:n * 3 + 3] = co

    def BFS(self):
        self.faces[0].BFS()

    def get_indices(self):
        return self.edgeFriend.indices

    def subdivide(self):
        if len(self.edgeFriend.l) < 750:
            self.edgeFriend.subdivide()
        else:
            self.edgeFriend.subdivideMetal()

    def get_normals(self):
        if len(self.edgeFriend.l) < 750:
            self.edgeFriend.calculateNormals()
        else:
            self.edgeFriend.calculateNormalsMetal()
        return self.edgeFriend.normals
    
    def get_normals_metal(self):
        self.edgeFriend.calculateNormalsMetal()
        return self.edgeFriend.normals
    
    def export_obj_subdivided(self, filepath):
        mesh = self.quadMesh.edgeFriend
        with open(filepath, 'w') as f:
            # Write vertices
            for vert in np.reshape(mesh.vertices, (-1, 3)):
                vert_str = " ".join([str(round(i, 7)) for i in vert])
                f.write(f"v {vert_str}\n")

            # Write faces (assuming faces are represented as lists of vertex indices)
            for face in np.reshape(mesh.i, (-1, 4)):
                # OBJ file format uses 1-based indexing for vertices
                face_str = " ".join([str(i+1) for i in face])
                f.write(f"f {face_str}\n")

        print(f"Subdivided Mesh exported to {filepath}")
