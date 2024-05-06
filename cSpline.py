import numpy as np
from pyglet.math import Mat4, Vec3, Vec4

from cMesh_operations import * 

spline_control_mesh = cMesh()
spline_control_mesh.read_obj('./model/Spline/grid.obj')
spline_control_points = spline_control_mesh.verts

def vert_create_bezier(control_points, u, v):
    newPos = Vec3()
    
    for i in range(4):
        for j in range(4):
            newPos += Vec3(*control_points[4 * i + j].get_coord()) * bernstein_bases(i, u) * bernstein_bases(j, v)

    return newPos

def bernstein_bases(i, t):
    return np.math.comb(3, i) * (t ** i) * ((1 - t) ** (3 - i))

num_samples = 10
u_values = np.linspace(0, 1, num_samples)
v_values = np.linspace(0, 1, num_samples)

bezier_surface_points = []
bezier_surface_indices = []
bezier_surface_normals = []     

for u in u_values:
    for v in v_values:
        point = vert_create_bezier(spline_control_points, u, v)
        bezier_surface_points.append(point)
        bezier_surface_normals.append(Vec3())

for i in range(num_samples - 1):
    for j in range(num_samples - 1):
        e0 = bezier_surface_points[(i + 1) * num_samples + j + 1] - bezier_surface_points[i * num_samples + j]
        e1 = bezier_surface_points[(i + 1) * num_samples + j] - bezier_surface_points[i * num_samples + j + 1]
        faceNormal = e0.cross(e1).normalize()

        bezier_surface_normals[(i) * num_samples + j] += faceNormal
        bezier_surface_normals[(i) * num_samples + j + 1] += faceNormal
        bezier_surface_normals[(i + 1) * num_samples + j] += faceNormal
        bezier_surface_normals[(i + 1) * num_samples + j + 1] += faceNormal
        
        if e0.mag > e1.mag:
            bezier_surface_indices += [(i) * num_samples + j, (i) * num_samples + j + 1, (i+1) * num_samples + j + 1]
            bezier_surface_indices += [(i+1) * num_samples + j + 1, (i+1) * num_samples + j, (i) * num_samples + j]
        else:
            bezier_surface_indices += [(i+1) * num_samples + j, (i) * num_samples + j, (i) * num_samples + j + 1]
            bezier_surface_indices += [(i) * num_samples + j + 1, (i+1) * num_samples + j + 1, (i+1) * num_samples + j]

bezier_vertices = []
bezier_normals = []
for i in range(num_samples):
    for j in range(num_samples):
        bezier_vertices += list(bezier_surface_points[i * num_samples + j])
        bezier_normals += list(bezier_surface_normals[i * num_samples + j].normalize())
    
filepath = "./model/Subdivision/test_bezier.obj"
with open(filepath, 'w') as f:
    for vert in np.reshape(np.array(bezier_vertices), (-1, 3)):
        vert_str = " ".join([str(round(i, 7)) for i in vert])
        f.write(f"v {vert_str}\n")

    for i in range(num_samples-1):
        for j in range(num_samples-1):
            indices = [(i) * num_samples + j, (i) * num_samples + j+1, (i+1) * num_samples + j+1, (i+1) * num_samples + j]
            face_str = " ".join([str(k+1) for k in indices])
            f.write(f"f {face_str}\n")
        
print(f"Subdivided Mesh exported to {filepath}")


# -----------------------------------

def vert_create_bspline(control_points, u, v):
    newPos = Vec3()
    
    for i in range(4):
        for j in range(4):
            basis_u = bspline_basis(i, u)
            basis_v = bspline_basis(j, v)
            # print(basis_u, basis_v)
            newPos += Vec3(*control_points[4 * i + j].get_coord()) * basis_u * basis_v

    return newPos

def bspline_basis(i, t):
    if i == 0:
        return ((1-t) ** 3) / 6
    if i == 1:
        return (3 * (t ** 3) - 6 * (t ** 2) + 4) / 6
    if i == 2:
        return (-3 * (t ** 3) + 3 * (t ** 2) + 3 * t + 1) / 6
    if i == 3:
        return t ** 3 / 6

b_spline_surface_points = []
b_spline_surface_indices = []
b_spline_surface_normals = []     

for u in u_values:
    for v in v_values:
        point = vert_create_bspline(spline_control_points, u, v)
        # print(point)
        b_spline_surface_points.append(point)
        b_spline_surface_normals.append(Vec3())

for i in range(num_samples - 1):
    for j in range(num_samples - 1):
        e0 = b_spline_surface_points[(i + 1) * num_samples + j + 1] - b_spline_surface_points[i * num_samples + j]
        e1 = b_spline_surface_points[(i + 1) * num_samples + j] - b_spline_surface_points[i * num_samples + j + 1]
        faceNormal = e0.cross(e1).normalize()

        b_spline_surface_normals[(i) * num_samples + j] += faceNormal
        b_spline_surface_normals[(i) * num_samples + j + 1] += faceNormal
        b_spline_surface_normals[(i + 1) * num_samples + j] += faceNormal
        b_spline_surface_normals[(i + 1) * num_samples + j + 1] += faceNormal
        
        if e0.mag > e1.mag:
            b_spline_surface_indices += [(i) * num_samples + j, (i) * num_samples + j + 1, (i+1) * num_samples + j + 1]
            b_spline_surface_indices += [(i+1) * num_samples + j + 1, (i+1) * num_samples + j, (i) * num_samples + j]
        else:
            b_spline_surface_indices += [(i+1) * num_samples + j, (i) * num_samples + j, (i) * num_samples + j + 1]
            b_spline_surface_indices += [(i) * num_samples + j + 1, (i+1) * num_samples + j + 1, (i+1) * num_samples + j]

b_spline_vertices = []
b_spline_normals = []
for i in range(num_samples):
    for j in range(num_samples):
        b_spline_vertices += list(b_spline_surface_points[i * num_samples + j])
        b_spline_normals += list(b_spline_surface_normals[i * num_samples + j].normalize())

filepath = "./model/Subdivision/test_bspline.obj"
with open(filepath, 'w') as f:
    for vert in np.reshape(np.array(b_spline_vertices), (-1, 3)):
        vert_str = " ".join([str(round(i, 7)) for i in vert])
        f.write(f"v {vert_str}\n")

    for i in range(num_samples-1):
        for j in range(num_samples-1):
            indices = [(i) * num_samples + j, (i) * num_samples + j+1, (i+1) * num_samples + j+1, (i+1) * num_samples + j]
            face_str = " ".join([str(k+1) for k in indices])
            f.write(f"f {face_str}\n")
        
print(f"Subdivided Mesh exported to {filepath}")
