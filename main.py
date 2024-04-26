import time

import pyglet
from pyglet.math import Mat4, Vec3

from render import RenderWindow
from primitives import Cube,Sphere
from control import Control
from cMesh import cMesh

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

    scale_vec = Vec3(x=1, y=1, z=1)

    myMesh = cMesh()
    myMesh.read_obj('./model/Subdivision/cross_cube.obj')
    myMesh.toEdgeFriend()
    ti = time.time()
    myMesh.subdivide()
    myMesh.subdivide()
    myMesh.subdivide()
    myMesh.subdivide()
    myMesh.subdivide()
    te = time.time()
    print(te - ti)
    cube1 = Cube(scale_vec)
    cube2 = Cube(Vec3(x=1.5, y=1.5, z=1.5))
    sphere = Sphere(30,30)

    #draw shapes
    renderer.add_shape(translate_mat2, myMesh.edgeFriend.vertices, myMesh.getNormals(), myMesh.getIndices(), ((255, 255, 0, 255) * (len(myMesh.edgeFriend.vertices)//3)))

    renderer.run()
