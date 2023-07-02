#version 330 core

in vec2 fragmentTexCoord;

out vec4 color;

uniform sampler2D imageTexture;

void main()
{
    vec4 texColor = texture(image, fragmentTexCoord);
    if (texColor.a < 0.1)
        discard;
    else
        texColor.rgb = vec3(0.9, 0.9, 0.9);
    color = texColor;
}