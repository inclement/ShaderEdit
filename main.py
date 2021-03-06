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
#from shadertree import ShaderWidget

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
uniform vec2 pos_coord_correction;
'''

with open('ripple.glsl') as fileh:
    ripple_shader = header + shader_uniforms + fileh.read()

with open('tunnel_fly.glsl') as fileh:
    tunnel_fly_shader = header + shader_uniforms + fileh.read()

with open('tunnel.glsl') as fileh:
    tunnel_shader = header + shader_uniforms + fileh.read()

with open('plasma.glsl') as fileh:
    plasma_shader = header + shader_uniforms + fileh.read()

with open('gradient.glsl') as fileh:
    gradient_shader = header + shader_uniforms + fileh.read()


import re
def posify_shader(shader):
    shader = shader.replace('gl_FragCoord', 'fake_gl_FragCoord')

    main_re = re.compile('void\s*main\s*\(\s*void\s*\)\s*{')
    shader = re.sub(main_re,
                    'void main(void)\n{\nvec2 fake_gl_FragCoord = gl_FragCoord.xy - pos_coord_correction;\n',
                    shader)
    return shader

class Preview(FloatLayout):
    fs = StringProperty(plasma_shader)
    text = StringProperty('some text')

class ShaderDisplay(ShaderWidget):
    def on_fs(self, instance, value):
        print 'shader is'
        print '-'*50
        print value
        print '-'*50
        value = posify_shader(value)
        print 'new shader is'
        print '-'*50
        print value
        print '-'*50

        shader = self.canvas.shader
        old_value = shader.fs
        shader.fs = value
        if not shader.success:
            shader.fs = old_value
            raise Exception('failed')
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
    def go_back(self, *args):
        if self.current == 'editor':
            self.current = 'index'
        if self.current == 'fullscreen':
            self.current = 'editor'

class ShaderIndex(BoxLayout):
    def goto_display(self):
        manager = App.get_running_app()
        s = manager.screens('editor')
        # s.children[0].shaderdisplay.fs
        manager.current = 'editor'

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
