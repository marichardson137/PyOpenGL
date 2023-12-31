#version 330 core

layout (location = 0) in vec3 vertexPos;
layout (location = 1) in vec3 vertexNormal;
layout (location = 2) in vec2 vertexTexCoord;

uniform mat4 model;

out vec2 fragmentTexCoord;

void main()
{
    gl_Position = model * vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
}