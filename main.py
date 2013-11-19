from kivy.app import App
from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.actionbar import ActionBar
from kivy.uix.screenmanager import ScreenManager, Screen, RiseInTransition
from kivy.core.window import Window
from kivy.graphics import RenderContext
from kivy.animation import Animation
from kivy.properties import (StringProperty, ListProperty, ObjectProperty,
                             NumericProperty, ReferenceListProperty,
                             BooleanProperty)
from kivy.metrics import sp
from kivy.utils import platform
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

with open('ripple.glsl') as fileh:
    ripple_shader = header + shader_uniforms + fileh.read()

with open('tunnel.glsl') as fileh:
    tunnel_fly_shader = header + shader_uniforms + fileh.read()

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

class Preview(FloatLayout):
    fs = StringProperty(plasma_shader)
    text = StringProperty('some text')

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
    actionbar = ObjectProperty()

class EditBox(BoxLayout):
    slider_opacity = NumericProperty()
    height_pos_hint = NumericProperty(0.06)

    def keyboard_response(self, keyboard_open):
        if keyboard_open:
            animation = Animation(height_pos_hint=0.5, size_hint_y=0.5,
                                  duration=0.2, t='out_cubic')
        else:
            animation = Animation(height_pos_hint=0.1, size_hint_y=0.8,
                                  duration=0.2, t='out_cubic')
        animation.start(self)

    def go_fullscreen(self):
        s = Screen(name='fullscreen')
        sw = ShaderDisplay(fs=self.fs_text)
        s.add_widget(sw)
        App.get_running_app().root.add_widget(s)
        App.get_running_app().root.current = 'fullscreen'

class ShaderActionBar(ActionBar):
    editbox = ObjectProperty()

class ShaderManager(ScreenManager):
    pass

class ShaderIndex(BoxLayout):
    pass

class ShaderApp(App):
    shaderdisplay = ObjectProperty()
    manager = ObjectProperty()
    def build(self):
        manager = ShaderManager()
        self.manager = manager
        
        self.bind(on_start=self.post_build_init)

        return manager

    def on_pause(self):
        return True

    def post_build_init(self,ev):
        if platform() == 'android':
            import android
            android.map_key(android.KEYCODE_BACK,1001)
        win = Window
        win.bind(on_keyboard=self.my_key_handler)

    def my_key_handler(self,window,keycode1,keycode2,text,modifiers):
        if keycode1 == 27 or keycode1 == 1001:
            self.manager.go_back()
            return True
        return False


if __name__ == "__main__":
    ShaderApp().run()
