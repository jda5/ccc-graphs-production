from kivy.config import Config

Config.set('kivy', 'keyboard_mode', '')  # Need to set before loading everything else

from kivy.app import App
from kivy.core.text import LabelBase
from kivy.core.window import Window
import widgets
import screens


class MainApp(App):
    pass


if __name__ == '__main__':
    LabelBase.register(name='maths_font',
                       fn_regular='./fonts/maths-font-regular.ttf',
                       fn_italic='./fonts/maths-font-italic.ttf')
    LabelBase.register(name='poppins',
                       fn_regular='./fonts/poppins-regular.ttf',
                       fn_bold='./fonts/poppins-bold.ttf')
    Window.clearcolor = (1, 1, 1, 1)
    Window.size = [768, 1024]
    MainApp().run()
