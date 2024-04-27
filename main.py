import time

import pyglet
from pyglet.math import Mat4, Vec3
import numpy as np

from render import RenderWindow
from primitives import Cube,Sphere
from control import Control
from cMesh import cMesh
from subdiv import edgeFriendMesh
if __name__ == '__main__':
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "Hello Pyglet", resizable = True)   
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    translate_mat1 = Mat4.from_translation(vector=Vec3(x=-2, y=0, z=0))
    translate_mat2 = Mat4.from_translation(vector=Vec3(x=0, y=0, z=0))
    translate_mat3 = Mat4.from_translation(vector=Vec3(x=2, y=0, z=0))

    myMesh = cMesh()
    myMesh.read_obj('./model/Subdivision/cross_cube.obj')
    myMesh.toEdgeFriend()

    myMesh2 = cMesh()
    myMesh2.read_obj('./model/Subdivision/cross_cube.obj')
    myMesh2.toEdgeFriend()

    ti = time.time()
    myMesh.edgeFriend.subdivide()
    myMesh.edgeFriend.subdivide()
    te = time.time()
    print(te - ti)
    print()

    ti = time.time()
    myMesh2.edgeFriend.subdivide()
    myMesh2.edgeFriend.subdivideMetal()
    te = time.time()
    print(te - ti)

    cube2 = Cube(Vec3(x=1.5, y=1.5, z=1.5))
    sphere = Sphere(30,30)

    #draw shapes
    renderer.add_shape(translate_mat1, myMesh.edgeFriend.vertices, myMesh.get_normals(), myMesh.get_indices(), ((255, 255, 0, 255) * (len(myMesh.edgeFriend.vertices) // 3)))
    renderer.add_shape(translate_mat3, myMesh2.edgeFriend.vertices, myMesh2.get_normals(), myMesh2.get_indices(), ((255, 0, 0, 255) * (len(myMesh2.edgeFriend.vertices) // 3)))

    renderer.run()
