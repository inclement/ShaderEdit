from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.properties import (StringProperty, ListProperty, ObjectProperty,
                             NumericProperty, ReferenceListProperty,
                             BooleanProperty)
from kivy.metrics import sp
from shaderwidget import ShaderWidget

__version__ = '0.1'

header = '''
#ifdef GL_ES
precision highp float;
#endif

/* Outputs from the vertex shader */
varying vec4 frag_color;
varying vec2 tex_coord0;

/* uniform texture samplers */
uniform sampler2D texture0;
'''
shader_uniforms = '''
uniform vec2 resolution;
uniform float time;
uniform vec2 touch;
uniform vec2 mouse;
'''

tunnel_shader = header + shader_uniforms + '''

vec3 check(vec2 p, float s)
{
	return  vec3(clamp(ceil(sin(p.x/s)*sin(p.y/s))*s * 10., 0.1, 1.0));
}

void main( void ) {
	
	float speed = touch.x * 2.0;
	vec2 position = ( gl_FragCoord.xy / resolution.xy ) + vec2(touch.x, touch.y) - 1.0;
	vec3 col = vec3(1.0);
	vec2 uv;
	vec2 p = position * 2.0;
	
	p *= vec2( resolution.x/resolution.y, 1.0 );
	p = vec2(cos(speed) * p.x + sin(speed) * p.y, -sin(speed) * p.x + cos(speed) *p.y);
	
	float y = length(p);

	uv.x = p.x/y;
	uv.y = 1.0 / abs(y) + time * 1.5;
	col = check(uv, .10);
	float t = pow(abs(y), 1.6);

	gl_FragColor = vec4( col*t, 1.0 );
}
'''

plasma_shader = header + shader_uniforms + '''

void main(void)
{
   float x = gl_FragCoord.x;
   float y = gl_FragCoord.y;
   float mov0 = x+y+cos(sin(time)*2.)*100.+sin(x/100.)*1000.;
   float mov1 = y / resolution.y / 0.2 + time;
   float mov2 = x / resolution.x / 0.2;
   float c1 = abs(sin(mov1+time)/2.+mov2/2.-mov1-mov2+time);
   float c2 = abs(sin(c1+sin(mov0/1000.+time)+sin(y/40.+time)+sin((x+y)/100.)*3.));
   float c3 = abs(sin(c2+cos(mov1+mov2+c2)+cos(mov2)+sin(x/1000.)));
   gl_FragColor = vec4( c1,c2,c3,1.0);
}
'''

class ShaderDisplay(ShaderWidget):
    def on_touch_down(self, touch):
        self.touch = touch
        self.on_touch_move(touch)
    def on_touch_move(self, touch):
        tx = float((touch.x - self.x) / self.width)
        ty = float((touch.y - self.y) / self.width)
        self.canvas['touch'] = [tx, ty]
        self.canvas['mouse'] = [tx, ty]

class ShaderToy(BoxLayout):
    pass

class EditBox(BoxLayout):
    slider_opacity = NumericProperty()

class ShaderApp(App):
    shaderdisplay = ObjectProperty()
    def build(self):

        return ShaderToy()

if __name__ == "__main__":
    ShaderApp().run()
