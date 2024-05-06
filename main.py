import time

import pyglet
from pyglet.math import Mat4, Vec3
import numpy as np

from render import RenderWindow
from primitives import Cube,Sphere
from control import Control
from cMesh import cMesh
from cMesh_operations import *

import cSpline

if __name__ == '__main__':
    width = 1280
    height = 720

    # Render window.
    renderer = RenderWindow(width, height, "Hello Pyglet", resizable = True)   
    renderer.set_location(200, 200)

    # Keyboard/Mouse control. Not implemented yet.
    controller = Control(renderer)

    translate_mat1 = Mat4.from_translation(vector=Vec3(x=-4, y=0, z=0))
    translate_mat2 = Mat4.from_translation(vector=Vec3(x=0, y=0, z=0))
    # translate_mat2 = translate_mat2 @ Mat4.from_scale(Vec3(3, 3, 3))
    translate_mat3 = Mat4.from_translation(vector=Vec3(x=2, y=0, z=0))

    translate_mat_bezier = Mat4.from_translation(vector=Vec3(x=3, y=5, z=0)) @ Mat4.from_rotation(math.pi, Vec3(0, 0, 1))
    translate_mat_bspline = Mat4.from_translation(vector=Vec3(x=0, y=5, z=0)) @ Mat4.from_rotation(math.pi, Vec3(0, 0, 1))

    myMesh2 = cMesh()
    renderer.meshes.append(myMesh2)
    # myMesh2.read_obj('./model/Subdivision/cube.obj')
    myMesh2.read_obj('./model/Subdivision/cross_cube.obj')
    # myMesh2.read_obj('./model/Subdivision/icosahedron.obj')
    myMesh2.toEdgeFriend()

    ti = time.time()
    myMesh2.subdivide()
    myMesh2.subdivide()
    if sys.platform == 'darwin':
        myMesh2.subdivide()
        myMesh2.subdivide()
    te = time.time()
    print(te - ti)

    cube2 = Cube(Vec3(x=1.5, y=1.5, z=1.5))
    sphere = Sphere(30,30)

    #draw shapes
    myMesh2.add_shape_renderer(translate_mat2, renderer)
    # renderer.add_shape(translate_mat_bezier, cSpline.bezier_vertices, cSpline.bezier_normals, cSpline.bezier_surface_indices, (0, 255, 255, 255) * (len(cSpline.bezier_vertices) // 3))
    # renderer.add_shape(translate_mat_bspline, cSpline.b_spline_vertices, cSpline.b_spline_normals, cSpline.b_spline_surface_indices, (255, 0, 255, 255) * (len(cSpline.b_spline_vertices) // 3))

    renderer.run()