import pyglet
from pyglet import window, app, shapes
from pyglet.window import mouse,key
from pyglet.math import Mat4, Vec3, Vec4

import math

class Control:
    """
    Control class controls keyboard & mouse inputs.
    """
    def __init__(self, window):
        window.on_key_press = self.on_key_press
        window.on_key_release = self.on_key_release
        window.on_mouse_motion = self.on_mouse_motion
        window.on_mouse_drag = self.on_mouse_drag
        window.on_mouse_press = self.on_mouse_press
        window.on_mouse_release = self.on_mouse_release
        window.on_mouse_scroll = self.on_mouse_scroll
        self.window = window
        self.setup()

        self.cam_distance = 5.0  # Initial distance from the origin
        self.cam_yaw = 0.0       # Horizontal rotation angle (yaw)
        self.cam_pitch = 0.0     # Vertical rotation angle (pitch)
        self.rotating = False    # Flag to indicate if rotating with middle mouse button

        self.dragging = False
        self.dragged_vertex_index = None


    def setup(self):
        pass

    def update(self, vector):
        pass

    def on_key_press(self, symbol, modifier):
        if symbol == pyglet.window.key.W:
            self.cam_pitch += 0.5
        if symbol == pyglet.window.key.S:
            self.cam_pitch -= 0.5
        if symbol == pyglet.window.key.A:
            self.cam_yaw += 0.5
        if symbol == pyglet.window.key.D:
            self.cam_yaw -= 0.5
        if symbol == pyglet.window.key.C:
            self.window.meshes[0].export_obj_subdivided('./model/Subdivision/test.obj')
        
        self.update_camera()
    
    def on_key_release(self, symbol, modifier):
        if symbol == pyglet.window.key.ESCAPE:
            pyglet.app.exit()
        elif symbol == pyglet.window.key.SPACE:
            self.window.animate = not self.window.animate
        # TODO:
        pass

    def on_mouse_motion(self, x, y, dx, dy):
        pass

    def on_mouse_press(self, x, y, button, modifier):
        if button == pyglet.window.mouse.MIDDLE:
            self.rotating = True

        if button == pyglet.window.mouse.LEFT:
            self.dragging = True
            self.prev_x = x
            self.prev_y = y
            
            self.dragged_vertex_index = self.get_nearest_vertex(x, y)
            if self.dragged_vertex_index:
                self.prev_vertex_pos = Vec3(*self.window.meshes[0].get_vertex(self.dragged_vertex_index))
                self.distance_ratio = -(self.window.view_mat @ Vec4(*self.prev_vertex_pos.xyz, 1.0)).z
        pass
    

    def on_mouse_release(self, x, y, button, modifier):
        if button == pyglet.window.mouse.MIDDLE:
            self.rotating = False

        if button == pyglet.window.mouse.LEFT:
            self.dragging = False
            self.dragged_vertex_index = None        
        pass


    def on_mouse_drag(self, x, y, dx, dy, button, modifier):
        if self.rotating:
            sensitivity = 0.2
            self.cam_yaw += dx * sensitivity
            self.cam_pitch += dy * sensitivity

            self.cam_pitch = max(-90.0, min(90.0, self.cam_pitch))
            self.update_camera()

        if self.dragging and self.dragged_vertex_index is not None:
            new_vertex_pos = self.prev_vertex_pos
            inv_view_projection = ~(self.window.proj_mat @ self.window.view_mat)
            new_vertex_delta = inv_view_projection @ Vec4(2 * (x - self.prev_x) / self.window.width, 2 * (y - self.prev_y) / self.window.height, 0.0, 0.0)
            new_vertex_pos += new_vertex_delta * (self.distance_ratio)
            
            self.window.meshes[0].set_vertex(self.dragged_vertex_index, list(new_vertex_pos[:3]))
        pass


    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        sensitivity = 0.1
        self.cam_distance -= scroll_y * sensitivity

        self.cam_distance = min(1.0, self.cam_distance)
        
        self.update_camera()
        pass

    def update_camera(self):
        cam_x = self.cam_distance * math.cos(math.radians(self.cam_pitch)) * math.sin(math.radians(self.cam_yaw))
        cam_y = self.cam_distance * math.cos(math.radians(self.cam_pitch)) * math.cos(math.radians(self.cam_yaw))
        cam_z = self.cam_distance * math.sin(math.radians(self.cam_pitch))

        self.window.cam_eye = Vec3(cam_x, cam_y, cam_z)

    def get_nearest_vertex(self, x, y):
        ray_near, ray_far = self.get_ray(x, y)
        ray_dir = (ray_far - ray_near).normalize()
        min_distance = float('inf')
        distance = None
        nearest_vertex_index = None
        
        for i, vert in enumerate(self.window.meshes[0].verts):
            vertex = Vec3(*vert.get_coord())
            distance = (vertex - ray_near).dot(ray_dir)
            projection = ray_dir * distance
            perpendicular = (vertex - ray_near) - projection
            hit_rad = perpendicular.distance(Vec3())
            if distance < min_distance and hit_rad < .1:
                min_distance = distance
                nearest_vertex_index = i
        
        return nearest_vertex_index

    def get_ray(self, x, y):
        ndc_x = (2.0 * x / self.window.width - 1.0)
        ndc_y = (2.0 * y / self.window.height - 1.0) 

        ray_near = Vec4(ndc_x, ndc_y, -1.0, 1.0)
        ray_far = Vec4(ndc_x, ndc_y, 1.0, 1.0)

        inv_view_projection = ~(self.window.proj_mat @ self.window.view_mat)
        ray_near = inv_view_projection @ ray_near
        ray_far = inv_view_projection @ ray_far
        ray_far /= ray_far.w
        ray_near /= ray_near.w

        return Vec3(*ray_near.xyz), Vec3(*ray_far.xyz)
