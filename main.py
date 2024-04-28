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

    myMesh2 = cMesh()
    renderer.meshes.append(myMesh2)
    myMesh2.read_obj('./model/Subdivision/cross_cube.obj')
    myMesh2.toEdgeFriend()

    ti = time.time()
    myMesh2.edgeFriend.subdivide()
    myMesh2.edgeFriend.subdivide()
    myMesh2.edgeFriend.subdivideMetal()
    myMesh2.edgeFriend.subdivideMetal()
    myMesh2.edgeFriend.subdivideMetal()
    te = time.time()
    print(te - ti)
    print()

    cube2 = Cube(Vec3(x=1.5, y=1.5, z=1.5))
    sphere = Sphere(30,30)

    #draw shapes
    renderer.add_shape(translate_mat2, myMesh2.edgeFriend.vertices, myMesh2.get_normals_metal(), myMesh2.get_indices(), ((255, 255, 0, 255) * (len(myMesh2.edgeFriend.vertices) // 3)))

    renderer.run()

'''
<class 'list'> <class 'numpy.ndarray'> True
366 480 240 122
1446 1920 960 482
WORKING
SUCCESS
<class 'numpy.ndarray'>
1446 1920 960 482
5766 7680 3840 1922
WORKING
SUCCESS
<class 'numpy.ndarray'>
5766 7680 3840 1922
23046 30720 15360 7682
WORKING
SUCCESS
<class 'numpy.ndarray'>
23046 30720 15360 7682
92166 122880 61440 30722
WORKING
SUCCESS
<class 'numpy.ndarray'>
0.010073184967041016

Shader :  <module 'shader' from '/Users/chu/Documents/GitHub/SNU_ComputerGraphics/shader.py'>
WORKING
SUCCESS
WORKING
SUCCESS
Shader :  <module 'shader' from '/Users/chu/Documents/GitHub/SNU_ComputerGraphics/shader.py'>
inside event loop!
<class 'list'> <class 'numpy.ndarray'> True
366 480 240 122
1446 1920 960 482
WORKING
SUCCESS
<class 'numpy.ndarray'>
subdivide clear!
WORKING
SUCCESS
WORKING
SUCCESS
inside event loop!
<class 'list'> <class 'numpy.ndarray'> True
366 480 240 122
1446 1920 960 482
WORKING
SUCCESS
<class 'numpy.ndarray'>
subdivide clear!
WORKING
SUCCESS
WORKING
SUCCESS
inside event loop!
<class 'list'> <class 'numpy.ndarray'> True
366 480 240 122
1446 1920 960 482
WORKING'''