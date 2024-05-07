import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key

import imgui
from imgui.integrations.pyglet import PygletRenderer

from pyglet.graphics.shader import Shader, ShaderProgram
from pyglet.gl import GL_TRIANGLES
from pyglet.math import Mat4, Vec3
from pyglet.gl import *

import math
import sys
from cMesh import cMesh
from cMesh_extrusion import *

import shader
from primitives import CustomGroup

class UI:
    def __init__(self, window):
        imgui.create_context()
        # self.renderer = PygletRenderer(window)
        self.impl = PygletRenderer(window)
        imgui.new_frame()  
        imgui.end_frame()

        # Window variables
        self.test_input = 0

    def render(self):
        imgui.render()
        self.impl.render(imgui.get_draw_data())
        imgui.new_frame()

        imgui.begin("Test Window")
        imgui.text("This is the test window.")
        changed, self.test_input = imgui.input_int("Integer Input Test", self.test_input)

        imgui.end()

        imgui.end_frame()

glBindImageTextures
class RenderWindow(pyglet.window.Window):
    '''
    inherits pyglet.window.Window which is the default render window of Pyglet
    '''
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.batch = pyglet.graphics.Batch()

        # self.UI_test = UI(self)
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
        self.doExtrusion = False
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
        print(round(1/dt))

        for mesh in self.meshes:
            if self.doExtrusion:
                for face in mesh.faces:
                    if face.flag_selected:
                        mesh.face_extrude(face)
                self.doExtrusion = False
                mesh.update_mesh = True
            
            # mesh.vertices[78:80] = [-0.5 * math.cos(self.t) + -0.5, -3 - 0.5 * math.sin(self.t)]
            # mesh.vertices[45:47] = [0.5 * math.cos(self.t) + 0.5, 3 - 0.5 * math.sin(self.t)]
            # mesh.update_vertices = True 

            if mesh.update_vertices or mesh.update_mesh:
                mesh.toEdgeFriend()
                for i in range(mesh.subdivision_level-1):
                    mesh.subdivide()
                # print("subdivided")
                # print("")
        
                vertice = mesh.quadMesh.edgeFriend.vertices
                normal = mesh.get_normals()
                indice = mesh.get_indices()
            
                if mesh.update_mesh:
                    color = (255, 255, 0, 255) * (len(mesh.quadMesh.edgeFriend.vertices) // 3)
                    mesh.subdivision_shape.indexed_vertices_list.delete()
                    mesh.subdivision_shape.indexed_vertices_list = mesh.subdivision_shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                                batch = self.batch,
                                group = mesh.subdivision_shape,
                                indices = indice,
                                vertices = ('f', vertice),
                                normals = ('f', normal),
                                colors = ('Bn', color))
                    
                    mesh.shape.indexed_vertices_list.delete()

                    colors = (255, 0, 255, 255) * (len(mesh.vertices) // 3)
                    indices = []
                    for edge in mesh.edges:
                        indices.append(edge.v0.i)
                        indices.append(edge.v1.i)
                    mesh.shape.indexed_vertices_list = mesh.shape.shader_program.vertex_list_indexed(len(mesh.vertices)//3, GL_LINES,
                                batch = self.batch,
                                group = mesh.subdivision_shape,
                                indices = indices,
                                vertices = ('f', mesh.vertices),
                                colors = ('Bn', colors))

                    colors = ((255, 255, 255, 255) * (len(mesh.controllPoint.vertices) // 3))
                    for vert in mesh.verts[len(mesh.shape_controllPoints):]:
                        loc = Mat4() @ Mat4.from_translation(Vec3(*vert.get_coord()))
                        mesh.shape_controllPoints.append(self.add_shape(loc, mesh.controllPoint.vertices, None, mesh.controllPoint.indices, colors, True))



                    mesh.update_mesh = False
                    mesh.update_vertices = False

                else:
                    selected_color = (255, 137, 0, 255) * (len(mesh.shape_controllPoints[0].indexed_vertices_list.colors) // 4)
                    deselected_color = (255, 255, 255, 255) * (len(mesh.shape_controllPoints[0].indexed_vertices_list.colors) // 4)
                    transform = mesh.shape.transform_mat
                    for i, vert in enumerate(mesh.verts):
                        loc = transform @ Mat4.from_translation(Vec3(*vert.get_coord()))
                        mesh.shape_controllPoints[i].transform_mat = loc
                        if vert.flag_selected:
                            mesh.shape_controllPoints[i].indexed_vertices_list.colors = selected_color
                        else:
                            mesh.shape_controllPoints[i].indexed_vertices_list.colors = deselected_color
    
                    mesh.shape.indexed_vertices_list.vertices = mesh.vertices
                    mesh.subdivision_shape.indexed_vertices_list.vertices = vertice
                    mesh.subdivision_shape.indexed_vertices_list.normals = normal
                    mesh.subdivision_shape.indexed_vertices_list.indices = indice

                    mesh.update_vertices = False


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

        # self.UI_test.render()


    def on_resize(self, width, height):
        glViewport(0, 0, *self.get_framebuffer_size())
        self.proj_mat = Mat4.perspective_projection(
            aspect = width/height, z_near=self.z_near, z_far=self.z_far, fov = self.fov)
        return pyglet.event.EVENT_HANDLED

    def add_shape(self, transform, vertice, normal, indice, color, flatShader = False):
        
        '''
        Assign a group for each shape
        '''
        if normal is None:
            if flatShader:
                shape = CustomGroup(transform, len(self.shapes), self, True)
                shape.indexed_vertices_list = shape.shader_program.vertex_list_indexed(len(vertice)//3, GL_TRIANGLES,
                            batch = self.batch,
                            group = shape,
                            indices = indice,
                            vertices = ('f', vertice),
                            colors = ('Bn', color))
            else:
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

    