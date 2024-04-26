from pyglet.graphics.shader import Shader, ShaderProgram

# create vertex and fragment shader sources
vertex_source_default = """
#version 410
layout(location =0) in vec3 vertices;
layout(location =1) in vec3 normals;
layout(location =2) in vec4 colors;

out vec4 color;
out vec3 newNormal;

// add a view-projection uniform and multiply it by the vertices
uniform mat4 vp;
uniform mat4 model;

void main()
{
    gl_Position = vp * model * vec4(vertices, 1.0f); // local->world->vp
    newNormal = normalize((model * vec4(normals, 0.0f)).xyz);
    color = colors;

    //vec3 lightDir = normalize(vec3(-1, -1, -2));
    //newColor = min(0.5f * dot(lightDir, -newNormal) + 0.5f, 1.0f) * colors;
}
"""

fragment_source_default = """
#version 410
in vec4 color;
in vec3 newNormal;

out vec4 outColor;

void main()
{
    vec3 lightDir = normalize(vec3(1, 1, -2));
    vec4 newColor = min(0.3f * dot(lightDir, -newNormal) + 0.7f, 1.0f) * color;

    outColor = newColor;
}
"""

def create_program(vs_source, fs_source):
    # compile the vertex and fragment sources to a shader program
    vert_shader = Shader(vs_source, 'vertex')
    frag_shader = Shader(fs_source, 'fragment')
    return ShaderProgram(vert_shader, frag_shader)