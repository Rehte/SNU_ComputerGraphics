from pyglet.math import Mat4, Vec3, Vec4
import math
from pyglet.gl import *

from edgeFriend import *
from cMesh_operations import *

def face_extrude(self, face:cFace):
    newVerts = []
    e0 = Vec3(*self.get_vertex(face.indices[2])) - Vec3(*self.get_vertex(face.indices[0]))
    e1 = Vec3(*self.get_vertex(face.indices[3])) - Vec3(*self.get_vertex(face.indices[1]))
    fn = e0.cross(e1).normalize()
    for i in face.indices:
        pos = Vec3(*self.get_vertex(i)) + fn * 0.1
        newVerts.append(self.vert_create(list(pos)))
    newFace = self.face_create_vert(newVerts)

    l = face.l

    nl = newFace.l

    for i in range(face.len):
        v0 = l.v
        v1 = l.ln.v
        v2 = nl.ln.v
        v3 = nl.v
        self.face_create_vert([v0, v1, v2, v3])
        
        l = l.ln
        nl = nl.ln

    for i in range(face.len):
        (l.e.l).remove(l)
        self.loops.remove(l.lp)
        
        l = l.ln

    self.faces.remove(face)
        
cMesh.face_extrude = face_extrude

a = cMesh()
# a.read_obj('./model/Subdivision/cube.obj')
# a.read_obj('./model/Subdivision/cross_cube.obj')
# a.read_obj('./model/Subdivision/icosahedron.obj')
a.read_obj('./model/Subdivision/cube.obj')

a.face_extrude(a.faces[0])
