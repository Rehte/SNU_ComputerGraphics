from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

from edgeFriend import *
from cMesh import * 



def vert_create(self: cMesh, co = None):
    if co == None:
        self.vertices += [0.0, 0.0, 0.0]
    else:
        self.vertices += co

    i = len(self.vertices)//3 - 1  
    v = cVert(i)
    v.mesh = self
    self.verts.append(v)

    return v
  
cMesh.vert_create = vert_create



def edge_create(self, v0: cVert, v1: cVert, ensure_new_edge = False):    
    if not ensure_new_edge:
        for edge in self.edges:
            if (edge.v0 == v0 and edge.v1 == v1) or (edge.v1 == v0 and edge.v0 == v1):
                return edge
            
    e = cEdge([v0, v1])

    self.edges.append(e)

    v0.e.append(e)
    v1.e.append(e)

    return e

cMesh.edge_create = edge_create



def loop_create(self, v: cVert, e: cEdge, f: cFace):
  l = cLoop(v, e, f)
  self.loops.append(l)

  return l

cMesh.loop_create = loop_create



def face_create(self, verts, edges, ensure_new_face = False):
    indices = [vert.i for vert in verts]
    
    if not ensure_new_face:
        for face in self.faces:
            for i in range(len(indices)):
                if indices[i:len(indices)] + indices[:i] == face.indices:
                    return face
    
    verts = [self.verts[i] for i in indices]

    f = cFace(indices, self)
    self.faces.append(f)

    startl = lastl = loop_create(self, verts[0], edges[0], f)
    edges[0].l.append(startl)

    f.l = startl

    for i in range(1, len(indices)):
        l = loop_create(self, verts[i], edges[i], f)
        edges[i].l.append(l)

        l.lp = lastl
        lastl.ln = l
        lastl = l

    startl.lp = lastl
    lastl.ln = startl

    return f
      
cMesh.face_create = face_create



def face_create_vert(self, verts, ensure_new_face = False):
    edges = []

    for i in range(len(verts)):
       edges.append(edge_create(self, verts[i], verts[i + 1 if not i == len(verts)-1 else 0]))
    
    return face_create(self, verts, edges, ensure_new_face)

cMesh.face_create_vert = face_create_vert



def face_create_idx(self, indices, ensure_new_face = True):
    
    return face_create_vert(self, [self.verts[i] for i in indices], ensure_new_face)

cMesh.face_create_idx = face_create_idx



def read_obj(self, filename):
    self.vertices = []
    self.verts = []
    self.edges = []
    self.edges = []
    self.faces = []

    with open(filename, 'r') as file:
        for line in file:
            if line.startswith('v '):
                parts = line.strip().split()[1:]
                vertex = [float(part) for part in parts]
                self.vert_create(vertex)

            elif line.startswith('f '):
                parts = line.strip().split()[1:]
                indices = [int(part.split('/')[0]) - 1 for part in parts]
                
                self.face_create_idx(indices)
    
cMesh.read_obj = read_obj



def vert_create_centroid(self, f:cFace):
    sum = Vec3()
    for i in f.indices:
        sum += Vec3(*self.get_vertex(i))
    return self.vert_create(list(sum/f.len))

cMesh.vert_create_centroid = vert_create_centroid



def subdivide_halfEdge(self):
    newMesh = cMesh()
    for v in self.verts:
        newMesh.vert_create(self.get_vertex(v.i))

    centroids = {}
    edgePoints = {}

    for face in self.faces:
        centroids[face] = newMesh.vert_create_centroid(face)
        # print(face.indices, centroids[face].get_coord())

    for edge in self.edges:
        sum = Vec3()
        sum += Vec3(*edge.v0.get_coord())
        sum += Vec3(*edge.v1.get_coord())
        sum += Vec3(*centroids[edge.l[0].f].get_coord())
        sum += Vec3(*centroids[edge.l[1].f].get_coord())

        edgePoints[edge] = newMesh.vert_create(list(sum / 4))

    for vert in self.verts:
        F = Vec3()
        R = Vec3()
        n = len(vert.e)
        for e in vert.e:
            R += Vec3(*edgePoints[e].get_coord())
            F += Vec3(*e.v0.get_coord())
            F += Vec3(*e.v1.get_coord())
        
        newCo = (F / 2 / n + R * 2 / n + Vec3(*vert.get_coord()) * (n - 3)) / n
        newMesh.set_vertex(vert.i, list(newCo))
    
    for face in self.faces:
        l = startl = face.l

        for i in face.indices:
            centroids[face]
            newFace = newMesh.face_create_vert([newMesh.verts[l.v.i], edgePoints[l.e], centroids[face], edgePoints[l.lp.e]], True)
            l = l.ln

            for face_newMesh in newMesh.faces:
                newFace.findFriend(face_newMesh)


    self.quadMesh = newMesh
    return newMesh

cMesh.subdivide_halfEdge = subdivide_halfEdge



def QuadMesh2EdgeFriend(self):
    self.edgeFriend = edgeFriendMesh(np.array(self.vertices,dtype='f'), DEV)
    
    self.BFS()
    
    self.edgeFriend.g = [None, ] * 2 * len(self.faces)
    self.edgeFriend.l = [None, ] * (len(self.vertices) // 3)
    # for face in self.faces:
    #     print(face)
    #     print(f"{face.n}\t{face.edgeFriend[0]}\t{face.edgeFriend[1]}")
    #     print()
    for face in self.faces:
        self.edgeFriend.g[face.n * 2:face.n * 2 + 2] = face.edgeFriend
        for i, v in enumerate(face.quad_indices):
            self.edgeFriend.l[v] = face.n * 4 + i

    self.edgeFriend.i = np.array(self.edgeFriend.i, dtype=np.uint32)  # ui32 array
    self.edgeFriend.g = np.array(self.edgeFriend.g, dtype=np.uint32)
    self.edgeFriend.l = np.array(self.edgeFriend.l, dtype=np.uint32)

cMesh.QuadMesh2EdgeFriend = QuadMesh2EdgeFriend



def toEdgeFriend(self):
    # TODO: preprocessing mesh ex) filling hole, first subdiv      
    self.subdivide_halfEdge()

    self.quadMesh.QuadMesh2EdgeFriend()

cMesh.toEdgeFriend = toEdgeFriend
