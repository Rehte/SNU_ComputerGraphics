from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

from subdiv import *


class cFace:
    def __init__(self, vertices, mesh):
        self.vertices = vertices
        self.mesh = mesh

        self.faceFriend = [None, ] * 4
        self.isCalled = False
        self.edgeFriend = [None, ] * 2
        self.n = None

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

    def read_obj(self, filename):
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
        self.edgeFriend = edgeFriendMesh(np.array(self.vertices,dtype='f'))
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
        self.edgeFriend.calculateNormal()
        return self.edgeFriend.normals
'''
[-0.5555556 -0.5555556  0.5555556 -1.         0.         0.
 -0.75       0.         0.75      -0.75       0.        -0.75
 -0.5555556  0.5555556  0.5555556  0.         0.         1.
  0.         0.75       0.75       0.        -0.75       0.75
 -0.5555556 -0.5555556 -0.5555556  0.         1.         0.
 -0.75       0.75       0.         0.75       0.75       0.
 -0.5555556  0.5555556 -0.5555556  1.         0.         0.
  0.75       0.        -0.75       0.75       0.         0.75
  0.5555556 -0.5555556  0.5555556  0.         0.        -1.
  0.         0.75      -0.75       0.        -0.75      -0.75
  0.5555556  0.5555556  0.5555556  0.        -1.         0.
  0.75      -0.75       0.        -0.75      -0.75       0.
  0.5555556 -0.5555556 -0.5555556  0.5555556  0.5555556 -0.5555556]
[ 0  2  1 23  4 10  1  2 12  3  1 10  8 23  1  3 20  6  5 15  4  2  5  6
  0  7  5  2 16 15  5  7 12 10  9 18  4  6  9 10 20 11  9  6 25 18  9 11
 24 14 13 22 25 11 13 14 20 15 13 11 16 22 13 15 12 18 17  3 25 14 17 18
 24 19 17 14  8  3 17 19 24 22 21 19 16  7 21 22  0 23 21  7  8 19 21 23]
[ 3 44  5 10  7 16  1 38 11 28 13 18 15  0  9 42 19 32 21  2 23  8 17 26
 27 40 29 34 31 20 25 14 35  4 37 22 39 24 33 46 43 36 45 30 47 12 41  6]
[88  2 21 77 36 18 37 85 92 34  5 53 32 50 69 29 84 66 45 93 40 82 61 13
 80 44]
'''