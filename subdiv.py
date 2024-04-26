import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *


class edgeFriendMesh:
    def __init__(self, vertices, indices=[], normals=[], colors=None, ):
        self.vertices = vertices
        self.normals = normals
        self.faceNormals = []
        self.colors = colors
        self.i = indices
        self.g = []
        self.l = []

    def getVertex(self, v):
        return Vec3(*self.vertices[v*3:v*3 + 3])

    def c2q(self, c):
        return c // 4

    def e2q(self, e):
        return e // 2

    def diagC(self, c):
        return c ^ 2

    def offC(self, c):
        return c ^ 3

    def subdivide(self):
        newEdgeFriendMesh = edgeFriendMesh([None,] * (12 * len(self.l) - 18))
        newEdgeFriendMesh.i = [None,] * 4 * len(self.i)
        newEdgeFriendMesh.g = [None,] * 4 * len(self.g)
        newEdgeFriendMesh.l = [None,] * (4 * len(self.l) - 6)
        for i in range(len(self.l)):
            if i < len(self.l) - 2:
                q = i
                g0, g1 = self.g[2*q:2*q+2]
                v0 = self.i[2 * g1 + 0]
                v1 = self.i[2 * g0 + 1]
                v2 = self.i[2 * g0 + 0]
                v3 = self.i[2 * g1 + 1]

                v0p = self.i[self.offC(2 * g1 + 0)]
                v1p = self.i[self.offC(2 * g0 + 1)]
                v2p = self.i[self.offC(2 * g0 + 0)]
                v3p = self.i[self.offC(2 * g1 + 1)]

                vert_f = (self.getVertex(v0) + self.getVertex(v1) + self.getVertex(v2) + self.getVertex(v3)) / 4
                vert_e0 = vert_f/4 + (self.getVertex(v1p) + self.getVertex(v1)*5 + self.getVertex(v2)*5 + self.getVertex(v2p)) / 16
                vert_e1 = vert_f/4 + (self.getVertex(v0p) + self.getVertex(v0)*5 + self.getVertex(v3)*5 + self.getVertex(v3p)) / 16

                f = 4 * q + 1
                e0 = 4 * self.e2q(g0) + 2 + g0%2
                e1 = 4 * self.e2q(g1) + 2 + g1%2

                newEdgeFriendMesh.vertices[3*f:3*f+3] = list(vert_f)
                newEdgeFriendMesh.vertices[3*e0:3*e0+3] = list(vert_e0)
                newEdgeFriendMesh.vertices[3*e1:3*e1+3] = list(vert_e1)

                v0 = (4 * v0) if v0 < len(self.i) // 4 else (3 * len(self.i) // 4 + v0)
                v1 = (4 * v1) if v1 < len(self.i) // 4 else (3 * len(self.i) // 4 + v1)
                v2 = (4 * v2) if v2 < len(self.i) // 4 else (3 * len(self.i) // 4 + v2)
                v3 = (4 * v3) if v3 < len(self.i) // 4 else (3 * len(self.i) // 4 + v3)

                q0 = 4*q; q1 = 4*q+1; q2 = 4*q+2; q3 = 4*q+3
                newEdgeFriendMesh.i[4*q0:4*q1] = [v0, 4 * q + 2, f, e1]
                newEdgeFriendMesh.i[4*q1:4*q2] = [v1, e0, f, 4 * q + 2]
                newEdgeFriendMesh.i[4*q2:4*q3] = [v2, 4 * q + 3, f, e0]
                newEdgeFriendMesh.i[4*q3:16*q+16] = [v3, e1, f, 4 * q + 3]

                n0 = 4 * self.e2q(g1) + 2 * (g1 % 2) + 0
                n1 = 4 * self.e2q(g0) + 2 * (g0 % 2) + 1
                n2 = 4 * self.e2q(g0) + 2 * (g0 % 2) + 0
                n3 = 4 * self.e2q(g1) + 2 * (g1 % 2) + 1

                newEdgeFriendMesh.g[2*q0 + 0] = 2 * q1 + 1
                newEdgeFriendMesh.g[2*q0 + 1] = 2 * n0 + 0
                newEdgeFriendMesh.g[2*q1 + 0] = 2 * q2 + 1
                newEdgeFriendMesh.g[2*n1 + 1] = 2 * q1 + 0
                newEdgeFriendMesh.g[2*q2 + 0] = 2 * q3 + 1
                newEdgeFriendMesh.g[2*q2 + 1] = 2 * n2 + 0
                newEdgeFriendMesh.g[2*q3 + 0] = 2 * q0 + 1
                newEdgeFriendMesh.g[2*n3 + 1] = 2 * q3 + 0

                newEdgeFriendMesh.l[f] = 4 * q0 + 2
                newEdgeFriendMesh.l[e0] = 4 * q1 + 1
                newEdgeFriendMesh.l[e1] = 4 * q3 + 1

            n = 0
            c_first = self.l[i]
            c = c_first
            eSum = Vec3(); fSum = Vec3()
            while True:
                n += 1
                q = self.c2q(c)
                eSum += self.getVertex(self.i[self.offC(c)])
                fSum += self.getVertex(self.i[self.diagC(c)])
                c = 2 * self.g[2 * q + (0 if(c % 4 == 1 or c % 4 == 2) else 1)] + c%2
                if c == c_first:
                    break

            beta = 3 / (2 * n)
            gamma = 1 / (4 * n)
            alpha = 1 - beta - gamma
            newVert = self.getVertex(i) * alpha + eSum * beta / n + fSum * gamma / n

            w = (4 * i) if i < len(self.i)//4 else (3 * len(self.i)//4 + i)
            newEdgeFriendMesh.vertices[3*w:3*w+3] = list(newVert)
            newEdgeFriendMesh.l[w] = 4 * self.l[i]

        self.vertices = newEdgeFriendMesh.vertices
        self.i = newEdgeFriendMesh.i
        self.g = newEdgeFriendMesh.g
        self.l = newEdgeFriendMesh.l

    def printFace(self, q):
        print(q, self.i[4*q:4*q+4])
        print([self.getVertex(i) for i in self.i[4*q:4*q+4]])

    def calculateNormal(self):
        self.faceNormals = []
        for i in range(len(self.i) // 4):
            e1 = self.getVertex(self.i[4 * i + 0]) - self.getVertex(self.i[4 * i + 2])
            e2 = self.getVertex(self.i[4 * i + 3]) - self.getVertex(self.i[4 * i + 1])
            self.faceNormals.append(e2.cross(e1).normalize())

        for c in self.l:
            n = 0
            c_first = c
            normalSum = Vec3()
            while True:
                n += 1
                q = self.c2q(c)
                if normalSum.dot(self.faceNormals[q]) < 0:
                    print(n, self.i[c], normalSum, self.faceNormals[q])
                normalSum += self.faceNormals[q]
                c = 2 * self.g[2 * q + (0 if(c % 4 == 1 or c % 4 == 2) else 1)] + c%2
                if c == c_first:
                    break
            normalSum = normalSum.normalize()
            if n>=5:
                print(n, self.getVertex(self.i[c]), normalSum)
            self.normals += list(normalSum)
