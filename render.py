import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3
from pyglet.gl import *

import math
import sys
from cMesh import cMesh

import shader
from primitives import CustomGroup


glBindImageTextures
class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()
        '''
        View (camera) parameters
        '''
        self.cam_eye = Vec3(0,-4,3)
        self.cam_target = Vec3(0,0,0)
        self.cam_vup = Vec3(0,0,1)
        self.view_mat = None
        '''
        Projection parameters
        '''
        self.z_near = 0.1
        self.z_far = 100
        self.fov = 60
        self.proj_mat = None

        self.shapes = []
        self.setup()

        self.animate = False
        self.t = 0
        self.meshes = []

    def setup(self) -> None:
        self.set_minimum_size(width = 400, height = 300)
        self.set_mouse_visible(True)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)

        # 1. Create a view matrix
        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)
        
        # 2. Create a projection matrix 
        self.proj_mat = Mat4.perspective_projection(
            aspect = self.width/self.height, 
            z_near=self.z_near, 
            z_far=self.z_far, 
            fov = self.fov)

    def on_draw(self) -> None:
        self.clear()
        self.batch.draw()

    def update(self,dt) -> None:
        self.t += dt
        # print(round(1/dt))

        for mesh in self.meshes:
            
            mesh.vertices[78:80] = [-0.5 * math.cos(self.t) + -0.5, -3 - 0.5 * math.sin(self.t)]
            mesh.vertices[45:47] = [0.5 * math.cos(self.t) + 0.5, 3 - 0.5 * math.sin(self.t)]

            mesh.toEdgeFriend()
            mesh.subdivide()
            mesh.subdivide()
            if sys.platform == 'darwin':
                mesh.subdivide()
                mesh.subdivide()
                
            transform = mesh.shape.transform_mat
            for i, vert in enumerate(mesh.verts):
                loc = transform @ Mat4.from_translation(Vec3(*vert.get_coord()))
                mesh.shape_controllPoints[i].transform_mat = loc

            mesh.shape.indexed_vertices_list.vertices = mesh.vertices
        
            vertice = mesh.quadMesh.edgeFriend.vertices
            normal = mesh.get_normals()
            indice = mesh.get_indices()
            
            color = (255, 0, 0, 255) * (len(mesh.quadMesh.edgeFriend.vertices) // 3)
            
            mesh.subdivision_shape.indexed_vertices_list.vertices = vertice
            mesh.subdivision_shape.indexed_vertices_list.normals = normal
            mesh.subdivision_shape.indexed_vertices_list.indices = indice

        self.view_mat = Mat4.look_at(
            self.cam_eye, target=self.cam_target, up=self.cam_vup)

        view_proj = self.proj_mat @ self.view_mat
        for i, shape in enumerate(self.shapes):
            '''
            Update position/orientation in the scene. In the current setting, 
            shapes created later rotate faster while positions are not changed.
            '''
            if self.animate:
                rotate_angle = dt
                rotate_axis = Vec3(0,0,1)
                rotate_mat = Mat4.from_rotation(angle = rotate_angle, vector = rotate_axis)
                
                shape.transform_mat @= rotate_mat

                # # Example) You can control the vertices of shape.
                # shape.indexed_vertices_list.vertices[0] += 0.5 * dt

            '''
            Update view and projection matrix. There exist only one view and projection matrix 
            in the program, so we just assign the same matrices for all the shapes
            '''
            shape.shader_program['vp'] = view_proj

    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov)
        return pyglet.event.EVENT_HANDLED

    def add_shape(self, transform, vertice, normal, indice, color):
        
        '''
        Assign a group for each shape
        '''
        if normal is None:
            shape = CustomGroup(transform, len(self.shapes), self, True)
            shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_LINES,
                            batch = self.batch,
                            group = shape,
                            indices = indice,
                            vertices = ('f', vertice),
                            colors = ('Bn', color))
        else:
            shape = CustomGroup(transform, len(self.shapes), self)
            shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                            batch = self.batch,
                            group = shape,
                            indices = indice,
                            vertices = ('f', vertice),
                            normals = ('f', normal),
                            colors = ('Bn', color))
        self.shapes.append(shape)

        return shape
         
    def run(self):
        pyglet.clock.schedule_interval(self.update, 1/120)
        pyglet.app.run()

    