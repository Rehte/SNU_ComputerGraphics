import time

import pyglet
from pyglet import window, app, shapes
from pyglet.math import Mat4, Vec3, Vec4
from pyglet.gl import *
import numpy as np
import metalcompute as mc

class edgeFriendMesh:
    def __init__(self, vertices, dev, indices=[], normals=[], colors=None):
        self.vertices = vertices
        self.normals = normals
        self.faceNormals = []
        self.colors = colors
        self.i = []
        self.g = []
        self.l = []

        self.dev = dev

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
        newEdgeFriendMesh = edgeFriendMesh(([None,] * (12 * len(self.l) - 18)), self.dev)
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

    def subdivideMetal(self):

        kernel = self.dev.kernel("""
        #include <metal_stdlib>

        #define getVertex(vertices,v) (float3(vertices[3 * v], vertices[3 * v + 1], vertices[3 * v + 2]))

        using namespace metal;

        inline void setVertex(device float* vertices,  uint v, float3 vert) {
            vertices[3 * v] = vert.x;
            vertices[3 * v + 1] = vert.y;
            vertices[3 * v + 2] = vert.z;
        }

        inline void setQuadIndices(device uint* indices,  uint q,  uint v0,  uint v1,  uint v2,  uint v3) {
            indices[4 * q] = v0;
            indices[4 * q + 1] = v1;
            indices[4 * q + 2] = v2;
            indices[4 * q + 3] = v3;
        }

        inline  uint c2q( uint c) {
            return c/4;
        }

        inline  uint e2q( uint e) {
            return e/2;
        }

        inline  uint diagC( uint c) {
            return c^2;
        }

        inline  uint offC( uint c) {
            return c^3;
        }

        kernel void subdivide(
            // These are the two input arrays, const as we will not write to them
            const device float* v [[ buffer(0) ]],
            const device  uint* i [[ buffer(1) ]],
            const device  uint* g [[ buffer(2) ]],
            const device  uint* l [[ buffer(3) ]],
            device float* vp [[ buffer(4) ]],
            device  uint* ip [[ buffer(5) ]],
            device  uint* gp [[ buffer(6) ]],
            device  uint* lp [[ buffer(7) ]],
            const device  uint& lenF [[buffer(8)]],
            // This is the index of the current kernel instance
            uint id [[ thread_position_in_grid ]]) 
        {
            uint n = 0;
            uint c_first = l[id];
            uint c = c_first;
            float3 eSum = float3(0);
            float3 fSum = float3(0);
            do{
                n += 1;
                 uint q = c2q(c);
                eSum += getVertex(v, i[offC(c)]);
                fSum += getVertex(v, i[diagC(c)]);
                c = 2 * g[2 * q + ((c % 4 == 1 or c % 4 == 2) ? 0 : 1)] + c % 2;
            } while(c != c_first || n > 10);
            float beta = 3.0f / (2.0f * n);
            float gamma = 1.0f / (4.0f * n);
            float alpha = 1.0f - beta - gamma;
            float3 newVert = getVertex(v, id) * alpha + eSum * beta / n + fSum * gamma / n;
             uint w = (id < lenF) ? (4 * id) : (3 * lenF + id);
            setVertex(vp, w, newVert);
            lp[w] = 4 * l[id];
            
            if (id < lenF)
            {
                 uint q = id;
                 uint g0 = g[2*q], g1 = g[2*q+1];

                 uint v0 = i[2 * g1 + 0];
                 uint v1 = i[2 * g0 + 1];
                 uint v2 = i[2 * g0 + 0];
                 uint v3 = i[2 * g1 + 1];

                 uint v0p = i[offC(2 * g1 + 0)];
                 uint v1p = i[offC(2 * g0 + 1)];
                 uint v2p = i[offC(2 * g0 + 0)];
                 uint v3p = i[offC(2 * g1 + 1)];

                float3 vert_f = (getVertex(v, v0) + getVertex(v, v1) + getVertex(v, v2) + getVertex(v, v3)) / 4;
                float3 vert_e0 = vert_f / 4 + (getVertex(v, v1p) + getVertex(v, v1) * 5 + getVertex(v, v2) * 5 + getVertex(v, v2p)) / 16;
                float3 vert_e1 = vert_f / 4 + (getVertex(v, v0p) + getVertex(v, v0) * 5 + getVertex(v, v3) * 5 + getVertex(v, v3p)) / 16;

                 uint  f = 4 * q + 1;
                 uint e0 = 4 * e2q(g0) + 2 + g0 % 2;
                 uint e1 = 4 * e2q(g1) + 2 + g1 % 2;

                setVertex(vp, f, vert_f);
                setVertex(vp, e0, vert_e0);
                setVertex(vp, e1, vert_e1);

                v0 = (v0 < lenF) ? (4 * v0) : (3 * lenF + v0);
                v1 = (v1 < lenF) ? (4 * v1) : (3 * lenF + v1);
                v2 = (v2 < lenF) ? (4 * v2) : (3 * lenF + v2);
                v3 = (v3 < lenF) ? (4 * v3) : (3 * lenF + v3);

                 uint q0 = 4 * q;
                 uint q1 = 4 * q + 1;
                 uint q2 = 4 * q + 2;
                 uint q3 = 4 * q + 3;

                setQuadIndices(ip, q0, v0, 4 * q + 2, f, e1);
                setQuadIndices(ip, q1, v1, e0, f, 4 * q + 2);
                setQuadIndices(ip, q2, v2, 4 * q + 3, f, e0);
                setQuadIndices(ip, q3, v3, e1, f, 4 * q + 3);

                 uint n0 = 4 * e2q(g1) + 2 * (g1 % 2) + 0;
                 uint n1 = 4 * e2q(g0) + 2 * (g0 % 2) + 1;
                 uint n2 = 4 * e2q(g0) + 2 * (g0 % 2) + 0;
                 uint n3 = 4 * e2q(g1) + 2 * (g1 % 2) + 1;

                gp[2 * q0 + 0] = 2 * q1 + 1;
                gp[2 * q0 + 1] = 2 * n0 + 0;
                gp[2 * q1 + 0] = 2 * q2 + 1;
                gp[2 * n1 + 1] = 2 * q1 + 0;
                gp[2 * q2 + 0] = 2 * q3 + 1;
                gp[2 * q2 + 1] = 2 * n2 + 0;
                gp[2 * q3 + 0] = 2 * q0 + 1;
                gp[2 * n3 + 1] = 2 * q3 + 0;

                lp[f] = 4 * q0 + 2;
                lp[e0] = 4 * q1 + 1;
                lp[e1] = 4 * q3 + 1;
            }
            lp[w] = 4 * l[id];
        }
        """)

        subdivide_fn = kernel.function("subdivide")

        if not type(self.vertices) == type(np.zeros(3)):
            # print(type(self.vertices), type(np.zeros(3)), "True")
            v_np = np.array(self.vertices, dtype='f')
            i_np = np.array(self.i, dtype=np.uint32)  # ui32 array
            g_np = np.array(self.g, dtype=np.uint32)
            l_np = np.array(self.l, dtype=np.uint32)
        else:
            v_np = self.vertices
            i_np = self.i
            g_np = self.g
            l_np = self.l

        # Create mc buffer
        v = self.dev.buffer(v_np)
        i = self.dev.buffer(i_np)
        g = self.dev.buffer(g_np)
        l = self.dev.buffer(l_np)

        vertSize = v_np.size // 3 + i_np.size // 4 * 3
        faceSize = i_np.size
        vp = self.dev.buffer(vertSize * 3 * 4)
        ip = self.dev.buffer(4 * faceSize * 4)
        gp = self.dev.buffer(2 * faceSize * 4)
        lp = self.dev.buffer(vertSize * 4)
        lenF = self.dev.buffer(np.array([i_np.size//4, ], dtype=np.uint32))
        # print(v_np.size, i_np.size, g_np.size, l_np.size)
        # print(vertSize * 3, 4 * faceSize, 2 * faceSize, vertSize)

        handle = subdivide_fn(len(l_np), v, i, g, l, vp, ip, gp, lp, lenF)
        # print("WORKING")
        del handle
        # print("SUCCESS")

        self.vertices = np.frombuffer(vp, dtype='f')
        # print(type(self.vertices))
        self.i = np.frombuffer(ip, dtype=np.uint32)
        self.g = np.frombuffer(gp, dtype=np.uint32)
        self.l = np.frombuffer(lp, dtype=np.uint32)

    def printFace(self, q):
        # print(q, self.i[4*q:4*q+4])
        print([self.getVertex(i) for i in self.i[4*q:4*q+4]])

    def calculateNormals(self):
        self.faceNormals = []
        self.normals = []
        self.indices = []
        for i in range(len(self.i) // 4):
            e1 = self.getVertex(self.i[4 * i + 2]) - self.getVertex(self.i[4 * i + 0])
            e2 = self.getVertex(self.i[4 * i + 3]) - self.getVertex(self.i[4 * i + 1])
            self.faceNormals.append(e1.cross(e2).normalize())
            if e1.mag > e2.mag:
                self.indices += [self.i[i * 4 + 0], self.i[i * 4 + 1], self.i[i * 4 + 2]]
                self.indices += [self.i[i * 4 + 2], self.i[i * 4 + 3], self.i[i * 4]]
            else:
                self.indices += [self.i[i * 4 + 3], self.i[i * 4 + 0], self.i[i * 4 + 1]]
                self.indices += [self.i[i * 4 + 1], self.i[i * 4 + 2], self.i[i * 4 + 3]]

        for c in self.l:
            n = 0
            c_first = c
            normalSum = Vec3()
            while True:
                n += 1
                q = self.c2q(c)
                normalSum += self.faceNormals[q]
                c = 2 * self.g[2 * q + (0 if(c % 4 == 1 or c % 4 == 2) else 1)] + c%2
                if c == c_first:
                    break
            normalSum = normalSum.normalize()
            self.normals += list(normalSum)

    def calculateFaceNormals(self):
        self.faceNormals = None
        self.indices = None

        kernel = self.dev.kernel("""
        #include <metal_stdlib>

        #define getVertex(vertices,v) (float3(vertices[3 * v], vertices[3 * v + 1], vertices[3 * v + 2]))
        
        inline void setVertex(device float* vertices,  uint v, float3 vert) {
            vertices[3 * v] = vert.x;
            vertices[3 * v + 1] = vert.y;
            vertices[3 * v + 2] = vert.z;
        }

        inline void setIndices(device uint* indices,  uint v, uint i0, uint i1, uint i2) {
            indices[3 * v] = i0;
            indices[3 * v + 1] = i1;
            indices[3 * v + 2] = i2;
        }

        kernel void calculateFaceNormal(
            const device float* v [[ buffer(0) ]],
            const device  uint* i [[ buffer(1) ]],
            device float* fn [[ buffer(2) ]],
            device  uint* in [[ buffer(3) ]],
            uint id [[ thread_position_in_grid ]]) 
        {
            float3 d0 = getVertex(v, i[4*id+2]) - getVertex(v, i[4*id]);
            float3 d1 = getVertex(v, i[4*id+3]) - getVertex(v, i[4*id+1]);
            setVertex(fn, id, metal::normalize(metal::cross(d0, d1)));
            if (metal::length(d0) > metal::length(d1)) {
                setIndices(in, 2*id+0, i[4*id+0], i[4*id+1], i[4*id+2]);
                setIndices(in, 2*id+1, i[4*id+2], i[4*id+3], i[4*id+0]);
            }
            else {
                setIndices(in, 2*id+0, i[4*id+1], i[4*id+2], i[4*id+3]);
                setIndices(in, 2*id+1, i[4*id+3], i[4*id+0], i[4*id+1]);

            }
        }        
        """)

        subdivide_fn = kernel.function("calculateFaceNormal")

        if not type(self.vertices) == type(np.zeros(3)):
            # print(type(self.vertices), type(np.zeros(3)), "True")
            v_np = np.array(self.vertices, dtype='f')
            i_np = np.array(self.i, dtype=np.uint32)  # ui32 array
        else:
            v_np = self.vertices
            i_np = self.i

        # Create mc buffer
        v = self.dev.buffer(v_np)
        i = self.dev.buffer(i_np)

        faceSize = i_np.size // 4
        fN = self.dev.buffer(faceSize * 3 * 4)
        iN = self.dev.buffer(faceSize * 6 * 4)

        handle = subdivide_fn(faceSize, v, i, fN, iN)
        # print("WORKING")
        del handle
        # print("SUCCESS")

        self.faceNormals = np.frombuffer(fN, dtype='f')
        self.indices = np.frombuffer(iN, dtype=np.uint32)

    def calculateNormalsMetal(self):
        self.calculateFaceNormals()
        self.normals = None

        kernel = self.dev.kernel("""
        #include <metal_stdlib>

        #define getVertex(vertices,v) (float3(vertices[3 * v], vertices[3 * v + 1], vertices[3 * v + 2]))
        
        inline void setVertex(device float* vertices,  uint v, float3 vert) {
            vertices[3 * v] = vert.x;
            vertices[3 * v + 1] = vert.y;
            vertices[3 * v + 2] = vert.z;
        }
        
        inline  uint c2q( uint c) {
            return c/4;
        }

        kernel void calculateNormal(
            const device float* fn [[ buffer(0) ]],
            const device  uint* i [[ buffer(1) ]],
            const device  uint* g [[ buffer(2) ]],
            const device  uint* l [[ buffer(3) ]],
            device float* vn [[ buffer(4) ]],
            uint id [[ thread_position_in_grid ]])
        {
            uint n = 0;
            uint c_first = l[id];
            uint c = c_first;
            float3 nSum = float3(0);
            do{
                n += 1;
                 uint q = c2q(c);
                nSum += getVertex(fn, q);
                c = 2 * g[2 * q + ((c % 4 == 1 or c % 4 == 2) ? 0 : 1)] + c % 2;
            } while(c != c_first || n > 10);

            setVertex(vn, id, metal::normalize(nSum));
        }
        """)

        subdivide_fn = kernel.function("calculateNormal")

        if not type(self.vertices) == type(np.zeros(3)):
            fn_np = np.array(self.faceNormals, dtype='f')
            i_np = np.array(self.i, dtype=np.uint32)  # ui32 array
            g_np = np.array(self.g, dtype=np.uint32)  # ui32 array
            l_np = np.array(self.l, dtype=np.uint32)  # ui32 array
        else:
            fn_np = self.faceNormals
            i_np = self.i
            g_np = self.g
            l_np = self.l

        # Create mc buffer
        fn = self.dev.buffer(fn_np)
        i = self.dev.buffer(i_np)
        g = self.dev.buffer(g_np)
        l = self.dev.buffer(l_np)

        vertSize = l_np.size
        vn = self.dev.buffer(vertSize * 3 * 4)

        handle = subdivide_fn(vertSize, fn, i, g, l, vn)
        # print("WORKING")
        del handle
        # print("SUCCESS")

        self.normals = np.frombuffer(vn, dtype='f')
