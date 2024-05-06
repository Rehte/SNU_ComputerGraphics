from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

from subdiv import *
import metalcompute as mc

class cVert:
    def __init__(self, co : list, no, e):
        self.co = co
        self.no = no

        self.e = None

        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

class cEdge:
    def __init__(self, v : list):
        self.v0 = v[0]
        self.v1 = v[1]

        self.l0 = None
        self.l1 = None

        self.e0n = None
        self.e0p = None
        self.e1n = None
        self.e1p = None

        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

class cLoop:
    def __init__(self, v, e, f):
        self.v = v
        self.e = e
        self.f = f

        self.twin = None
        self.ln = None
        self.lp = None

class cFace:
    def __init__(self, vertices : list, mesh):
        self.vertices = vertices
        self.mesh = mesh

        self.faceFriend = [None, ] * 4
        self.isCalled = False
        self.edgeFriend = [None, ] * 2
        self.n = None

        self.l = None

        self.flag_selected = False
        self.flag_visible = True
        self.flag_temp = False

    def findFriend(self, face):
        for i, j in [[0, 3], [1, 0], [2, 1], [3, 2]]:
            for k in range(4):
                if self.vertices[k] == face.vertices[i] and self.vertices[(k + 1) % 4] == face.vertices[j]:
                    face.faceFriend[j] = self
                    self.faceFriend[k] = face

    def BFS(self, face=None):
        if face:
            if self.n is None:
                self.n = len(self.mesh.edgeFriend.i) // 4
                self.mesh.edgeFriend.i += self.vertices
            i = self.faceFriend.index(face)
            j = face.faceFriend.index(self)
            if j % 2 == 0:
                if i % 2 == 0:
                    self.vertices = self.vertices[1:4] + self.vertices[0:1]
                    self.mesh.edgeFriend.i[-4:] = self.vertices
                    self.faceFriend = self.faceFriend[1:4] + self.faceFriend[0:1]
                    i = self.faceFriend.index(face)
                self.edgeFriend[i // 2] = (face.n * 4 + j) // 2
            else:
                if i % 2 == 1:
                    self.vertices = self.vertices[1:4] + self.vertices[0:1]
                    self.mesh.edgeFriend.i[-4:] = self.vertices
                    self.faceFriend = self.faceFriend[1:4] + self.faceFriend[0:1]
                    i = self.faceFriend.index(face)
                face.edgeFriend[j // 2] = (self.n * 4 + i) // 2
        else:
            self.n = 0
            self.mesh.edgeFriend.i += self.vertices

        if self.isCalled:
            return

        self.isCalled = True
        for face in self.faceFriend:
            face.BFS(self)

    def __str__(self):
        return f"{self.n}\t{self.edgeFriend[0]}\t{self.edgeFriend[1]}\n{self.vertices[0]}\t{self.vertices[1]}\t{self.vertices[2]}\t{self.vertices[3]}"


class cMesh:
    def __init__(self):
        self.vertices = []
        self.faces = []

        self.edgeFriend = None
        self.dev = mc.Device()

    def read_obj(self, filename):
        self.vertices = []
        self.faces = []
        self.edgeFriend = None
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

    def BFS(self):
        self.faces[0].BFS()

    def toEdgeFriend(self):
        self.edgeFriend = edgeFriendMesh(np.array(self.vertices,dtype='f'), self.dev)
        # TODO: preprocessing mesh ex) filling hole, first subdiv            
        self.BFS()
        
        self.edgeFriend.g = [None, ] * 2 * len(self.faces)
        self.edgeFriend.l = [None, ] * (len(self.vertices) // 3)
        # for face in self.faces:
        #     print(face)
        #     print(f"{face.n}\t{face.edgeFriend[0]}\t{face.edgeFriend[1]}")
        #     print()
        for face in self.faces:
            self.edgeFriend.g[face.n * 2:face.n * 2 + 2] = face.edgeFriend
            for i, v in enumerate(face.vertices):
                self.edgeFriend.l[v] = face.n * 4 + i

        self.edgeFriend.i = np.array(self.edgeFriend.i, dtype=np.uint32)  # ui32 array
        self.edgeFriend.g = np.array(self.edgeFriend.g, dtype=np.uint32)
        self.edgeFriend.l = np.array(self.edgeFriend.l, dtype=np.uint32)

    def get_indices(self):
        return self.edgeFriend.indices

    def subdivide(self):
        self.edgeFriend.subdivide()

    def get_normals(self):
        self.edgeFriend.calculateNormals()
        return self.edgeFriend.normals
    
    def get_normals_metal(self):
        self.edgeFriend.calculateNormalsMetal()
        return self.edgeFriend.normals