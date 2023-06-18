#version 330 core

in vec3 fragmentVertexNormal;
in vec2 fragmentTexCoord;

out vec4 color;

uniform sampler2D imageTexture;

void main()
{
    color = vec4(1.0, 1.0, 1.0, 1.0);
    // color = texture(imageTexture, fragmentTexCoord);
}