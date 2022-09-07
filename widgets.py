from api import MathPixAPI
from latex_parser import LatexParser
from kivy.app import App
from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle, Line
from kivy.properties import DictProperty, ListProperty, ObjectProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.uix.behaviors import ButtonBehavior, FocusBehavior
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex as hex_color
from data import log
from urllib.request import urlopen
from kivy.uix.popup import Popup

TEXT_SIZE = Window.height / 26
CURSOR_BLUE = [0.01, 0.33, 0.64, 1]  # Has to be RGBA as the cursor needs to disappear
CLEAR = [1, 1, 1, 0]

MODEL = {
    '00': '(7-5/2-1)=2',
    '01': 'y=2x+c',
    '02': '5=2×1+c',
    '03': 'c=3',
    '04': 'y=2x+3',
    '10': '(22-11/13-2)=1',
    '11': 'y=x+c',
    '12': '11=2+c',
    '13': 'c=9',
    '14': 'y=x+9',
    '20': '(20-4/5-3)=8',
    '21': 'y=8x+c',
    '22': '4=8×3+c',
    '23': 'c=-20',
    '24': 'y=8x-20',
    '30': '(13--5/4-1)=6',
    '31': 'y=6x+c',
    '32': '13=6×4+c',
    '33': 'c=-11',
    '34': 'y=6x-11',
    '40': '(22-2/-3-1)=-5',
    '41': 'y=-5x+c',
    '42': '2=-5×1+c',
    '43': 'c=7',
    '44': 'y=-5x+7',
    '50': '(9--11/-2-3)=-4',
    '51': 'y=-4x+c',
    '52': '9=-4×-2+c',
    '53': 'c=1',
    '54': 'y=-4x+1',
    '60': '(133-58/5-2)=25',
    '61': 'y=25x+c',
    '62': '58=25×2+c',
    '63': 'c=8',
    '64': 'y=25x+8',
    '70': '(23--4/8--1)=3',
    '71': 'y=3x+c',
    '72': '-4=3×-1+c',
    '73': 'c=-1',
    '74': 'y=3x-1',
    '80': '(-17-31/4--2)=-8',
    '81': 'y=-8x+c',
    '82': '31=-8×-2+c',
    '83': 'c=15',
    '84': 'y=-8x+15',
    '90': '(11--13/4--2)=4',
    '91': 'y=4x+c',
    '92': '11=4×4+c',
    '93': 'c=-5',
    '94': 'y=4x-5',
    '100': '(19--16/-3-2)=-7',
    '101': 'y=-7x+c',
    '102': '-16=-7×2+c',
    '103': 'c=-2',
    '104': 'y=-7x-2',
    '110': '(-2--6/-8--4)=-1',
    '111': 'y=-x+c',
    '112': '-6=-1×-4+c',
    '113': 'c=-10',
    '114': 'y=-x-10',
    '120': '(-62--40/-6--4)=11',
    '121': 'y=11x+c',
    '122': '-40=11×-4+c',
    '123': 'c=4',
    '124': 'y=11x+4',
    '130': '(133--7/19--1)=7',
    '131': 'y=7x+c',
    '132': '-7=7×-1+c',
    '133': 'c=0',
    '134': 'y=7x',
    '140': '(5-5/14-6)=0',
    '141': 'y=c',
    '142': '5=0×6+c',
    '143': 'c=5',
    '144': 'y=5',
    '150': '(-3--3/41-77)=0',
    '151': 'y=c',
    '152': '-3=0×41+c',
    '153': 'c=-3',
    '154': 'y=-3',
    '160': '(9-5/10-2)=(1/2)',
    '161': 'y=(x/2)+c',
    '162': '5=(2/2)+c',
    '163': 'c=4',
    '164': 'y=(x/2)+4',
    '170': '(1--7/27-3)=(1/3)',
    '171': 'y=(x/3)+c',
    '172': '-7=(3/3)+c',
    '173': 'c=-8',
    '174': 'y=(x/3)-8',
    '180': '(5-1/7--1)=(1/2)',
    '181': 'y=(x/2)+c',
    '182': '1=(-1/2)+c',
    '183': 'c=(3/2)',
    '184': 'y=(x+3/2)',
    '190': '(10-5/40-20)=(1/4)',
    '191': 'y=(x/4)+c',
    '192': '5=(20/4)+c',
    '193': 'c=0',
    '194': 'y=(x/4)'
 }

COORDINATES = (
    (1, 5, 2, 7),
    (2, 11, 13, 22),
    (3, 4, 5, 20),
    (4, 13, 1, -5),
    (-3, 22, 1, 2),
    (3, -11, -2, 9),
    (5, 133, 2, 58),
    (-1, -4, 8, 23),
    (4, -17, -2, 31),
    (4, 11, -2, -13),
    (2, -16, -3, 19),
    (-8, -2, -4, -6),
    (-4, -40, -6, -62),
    (-1, -7, 19, 133),
    (14, 5, 6, 5),
    (77, -3, 41, -3),
    (2, 5, 10, 9),
    (3, -7, 27, 1),
    (-1, 1, 7, 5),
    (40, 10, 20, 5),
)

MODIFIER = {'8': '×', '9': '(', '0': ')', '=': '+'}

COLORS = ['#29d88e', '#28d792', '#1ed1a0', '#14cbad', '#0bc5b5']

TUTORIAL = ['y=mx+c', '(1/2)', 'y=-3x+c', '5×8=40', '(3/4)']


def counter(func):
    """
    First define the wrapper function. Then create a function attribute 'counter' (everything in Python is an object,
    hence even functions have attributes). When the interpreter defines ExpressionWriter.__init__() it will assign
    __init__ = counter(__init__) and create a counter attribute (only once). Now each time an ExpressionWriter is
    instantiated (and __init__ is called) the function will add one to the counter then return the function (__init__).
    :param func: A function
    """

    def wrapper(*args, **kwargs):
        wrapper.count += 1
        return func(count=wrapper.count, *args, **kwargs)

    wrapper.count = -1  # this statement is executed only once when we wrap a function with the @counter decorator
    return wrapper


class ExpressionWriter(Widget):

    drawing = BooleanProperty(True)

    def __init__(self, **kwargs):
        """
        First the _on_data() method is bound to the data Dictionary Property. This ensures that _on_data is called when
        ExpressionWriter receives data from the MathPixiApi. The allow_drawing property is a Boolean that determines
        whether a user is allowed to draw within the widget region. This is necessary as ALL widgets receive an
        on_touch_move() event when the pen is moved across the screen and so we need to limit lines to just the area
        where the pen was touched down.
        """
        super().__init__(**kwargs)
        self.allow_drawing = False
        self.pen_color = [0, 0, 0, 1]
        self.pen_width = 2

    def on_touch_down(self, touch):
        """
        When touched the widget creates a data entry in the user data dictionary corresponding to the Touch object
        called 'current_line' whose value is a Line object of position touch.x and touch.y.
        :param touch: A Touch object - see https://kivy.org/doc/stable/guide/inputs.html#touch-events for more details
        """
        if self.parent.ids['peek_widget'].visible:
            return
        # Begin drawing only if the touch falls inside the widget and writing is set to True and the user hasn't already
        # submitted an answer
        if self.collide_point(touch.x, touch.y) and self.parent.writing and not self.parent.data_submitted:
            self.allow_drawing = True
            with self.canvas.after:
                Color(*self.pen_color)
                touch.ud['current_line'] = Line(
                    points=(touch.x, touch.y), width=self.pen_width
                )
            if not self.drawing:
                eraser = self.parent.ids['eraser_circle']
                eraser.center = touch.pos  # Move the drawing circle to the location of the touch
                eraser.visible = True  # Show the drawing circle

    def on_touch_move(self, touch):
        """
        Uses the dict.get() method to returns the value for the 'current_line'. If 'current_line' is not None then
        points are added to the line corresponding to the touch's x and y coordinates.
        :param touch: A Touch object - see https://kivy.org/doc/stable/guide/inputs.html#touch-events for more details
        """
        if self.collide_point(touch.x, touch.y) and self.allow_drawing:
            line = touch.ud.get('current_line')
            if line:
                if touch.y < self.top - (self.pen_width / 2):
                    line.points += (touch.x, touch.y)
            if not self.drawing:
                self.parent.ids['eraser_circle'].center = touch.pos  # Move the drawing circle to the location of the touch

    def on_touch_up(self, touch):
        """
        Sets allow_drawing to False
        :param touch: A Touch object - see https://kivy.org/doc/stable/guide/inputs.html#touch-events for more details
        """
        self.allow_drawing = False
        if not self.drawing:
            self.parent.ids['eraser_circle'].visible = False  # Hide the drawing circle

    def clear_canvas(self):
        self.canvas.after.clear()

    def switch_draw_mode(self, use_pen=False):
        """
        This function switches between the pen and the eraser by increaseing the line width and changing the colour from black to white
        """
        if use_pen:
            self.pen_color = [0, 0, 0, 1]
            self.pen_width = 2
            self.drawing = True
            return
        if self.drawing:
            self.pen_color = [1, 1, 1, 1]
            self.pen_width = self.parent.ids['eraser_circle'].eraser_size
        else:
            self.pen_color = [0, 0, 0, 1]
            self.pen_width = 2
        self.drawing = not self.drawing

    def get_image_data(self):
        """
        The function first saves the ExpressionWriter.canvas as a PNG file to the user_data_directory (automatically
        determined depending on the device the user is running the app on). Then this images is sent to the MathPix API
        which then return data on the handwritten answer (see api.py for more details). The api call updates self.data
        which in turn calls self._on_data().
        """
        file_name = f'{App.get_running_app().user_data_dir}/image_{self.parent.id_number}.png'
        self.export_to_png(file_name)
        return MathPixAPI().format_data(file_name)


class ResponseField(FloatLayout):
    background_color = ListProperty()
    text = StringProperty()
    writing = BooleanProperty()  # Bindings occur in KV file
    tutorial_widget = BooleanProperty(False)

    @counter
    def __init__(self, count, **kwargs):
        super().__init__(**kwargs)
        self.data_submitted = False
        self.id_number = count % 6

    def on_touch_down(self, touch):
        """
        Lets the user toggle between viewing the model solution and viewing their own solution if all steps have been
        submitted.
        """
        if not self.tutorial_widget:
            if not self.navigation.ids['next'].disabled:
                # If the NEXT button is on the screen (all solutions accounted for)
                if self.collide_point(*touch.pos):
                    self.view_model()
                    return
        super().on_touch_down(touch)

    def reset_field(self):
        self.data_submitted = False
        self.background_color = self.normal_color  # Change the background to back to its normal colour
        self.ids['expression_writer'].clear_canvas()
        self.ids['keyboard_writer'].reset()
        self.toggle_button_visibility(hidden=False)
        self.ids['expression_writer'].switch_draw_mode(use_pen=True)
        self.render_model()

    def render_model(self):
        if self.tutorial_widget:
            text = TUTORIAL[self.id_number]
        else:
            text = MODEL[f"{self.parent.parent.parent.question_number}{self.id_number}"]
        peek_widget = self.ids['peek_widget']
        peek_widget.visible = False
        peek_widget.show_hide()
        peek_widget.display_text(text)

    def view_model(self, peek_button=False):
        if self.ids['peek_widget'].visible:
            if self.writing:
                self.ids['eraser_button'].disabled = False
            self.ids['keyboard_button'].disabled = False
        else:
            self.ids['eraser_button'].disabled = True 
            self.ids['keyboard_button'].disabled = True
        self.ids['peek_widget'].show_hide()

        if not peek_button:
            @log.TimeStamp('view_model')
            def log_event(self):
                return {'show_model': self.ids['peek_widget'].visible, 'id_number': self.id_number}
            return log_event(self)

    def switch_mode(self):
        """
        Changes whether the user is writing their solution or typing it. Is called by pressing the pertinent IconButton,
        or is called when the MathPix is unsure about the user's handwriting input.
        """
        if not self.data_submitted:  # Only allow the user to switch modes if they haven't already submitted data
            kw = self.ids['keyboard_writer']
            if self.writing:
                kw.width = self.ids['expression_writer'].width
                kw.opacity = 1  # Show the keyboard_writer
                kw.is_focusable = True  # Allow the widget to take focus
                kw.focus = True  # Focus the widget
                self.ids['eraser_button'].disabled = True
            else:
                kw.width = 0
                kw.opacity = 0
                kw.is_focusable = False  # No longer allow the widget to take focus
                self.ids['eraser_button'].disabled = False
            self.writing = not self.writing  # Switch mode

    def toggle_button_visibility(self, hidden):
        """
        A function the toggles the visibility of the buttons. It hides the buttons by disabling them (e.g. keyboard.disabled = True if hidden = True)
        and reducting the opacity to 0.
        """
        keyboard = self.ids['keyboard_button']
        eraser = self.ids['eraser_button']
        keyboard.disabled = hidden
        eraser.disabled = hidden
        keyboard.opacity = 0 if hidden else 1
        eraser.opacity = 0 if hidden else 1

    def retrieve_data(self):
        """
        Function first checks whether or not the user has submitted a handwritten answer or a typed answer. For a typed
        answer the function simply 'gets' what the user has typed and passes the result to self.check. For a
        handwritten data retrieval is predominantly handled by MathPix (see ExpressionWriter.get_image_data for more
        details)
        """
        if self.writing:  # True if ResponseField is in 'handwriting mode'
            return self.ids['expression_writer'].get_image_data()
        return self.ids['keyboard_writer'].get_text()

    @log.TimeStamp('solution')
    def check_answer(self, text: str = None, confidence: float = 1):
        """
        First parses the submitted text then checks whether or not the answer is correct or not. If correct then
        pass the information onto the NavigationPane (see submitted_solutions for more details on how this data is
        processed).  If the solution is incorrect, check the confidence level. If the confidence level is below 80%
        then ask the user to submit a typed solution. Otherwise if the confidence level is 80% or greater then send
        data to the NavigationPane that the solution is incorrect.
        :param text: Solution text - raw
        :param confidence: How confident MathPix is with the answer
        """
        if self.tutorial_widget:
            latex_parser = LatexParser(4, 3, 2, 1)
            result = False if text is None else latex_parser.run_tutorial(text, self.id_number)
        else:
            latex_parser = getattr(self.navigation, 'latex_parser')
            result = False if text is None else latex_parser.run(text, self.id_number)
        self.background_color = self.normal_color       # Super hacky way to have the background change
        if result:  # Answer is correct - pass data onto the navigation
            self.navigation.solutions.update({self.id_number: 1})
        else:
            if confidence < 0.8:
                self.change_background(color=3)
                self.navigation.solutions.update({self.id_number: 3})
                return
            else:
                self.navigation.solutions.update({self.id_number: 2})
        self.data_submitted = True
        self.toggle_button_visibility(hidden=True)
        return {str(self.id_number): {'correct': result, 'confidence': confidence, 'text': text}}

    def change_background(self, color: int):
        """
        1 changes the background_color to green; 2 changes the background_color to red; 3 changes the background_color
        to yellow.
        :param color: An integer either 1, 2 or 3
        """
        if color == 1:
            self.background_color = hex_color('#77cb4f')
            self.navigation.score += 100
        elif color == 2:
            self.background_color = hex_color('#ff7485')
        else:
            self.background_color = hex_color('#fada5e')


class BaseNavigationPane(FloatLayout):
    solutions = DictProperty()
    score = NumericProperty()  # Bindings happen in kv file

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(solutions=self._on_solutions)

    def reset(self):
        self.solutions = {}
        for field in self.fields():
            field.reset_field()
        if isinstance(self, TutorialNavigationPane):
            self.configure_buttons('question')

    @staticmethod
    def show_hide_buttons(but, hide: bool):
        """
        Hides navigation buttons by reducing their height to 0, making them transparent and disabling them. This
        function does NOT remove the widget from the screen (i.e. it's still in the widget tree) it merely gives it a
        height of 0 - effectively making invisible.
        :param but: RoundedButton object
        :param hide: True if the button is to be hidden, False if the button is to be made visible
        """
        but.size_hint_y, but.opacity, but.disabled = (0, 0, True) if hide else (but.y_hint, 1, False)

    def configure_buttons(self, configuration: str):
        """
        Updates the buttons that are visible depending on the configuration 'parameter'.
        :param configuration: 'ready', 'question', 'next' or 'confirm'
        """
        _peek = self.ids['peek']
        _compare = self.ids['compare']
        _confirm = self.ids['confirm']

        if configuration == 'confirm':
            for button in (_peek, _compare):
                self.show_hide_buttons(button, hide=True)
            self.show_hide_buttons(_confirm, hide=False)
            return

        if configuration == 'reset':
            for button in (_peek, _compare, _confirm):
                self.show_hide_buttons(button, hide=True)
            self.show_hide_buttons(self.ids['reset'], hide=False)
            return

        if configuration == 'ready':
            self.show_hide_buttons(self.ids['next'], hide=True)
            self.show_hide_buttons(self.ids['ready'], hide=False)
            return

        if configuration == 'question':
            for button in (_peek, _compare):
                self.show_hide_buttons(button, hide=False)
            if isinstance(self, TutorialNavigationPane):
                self.show_hide_buttons(self.ids['reset'], hide=True)
                _compare.disabled = True
            else:
                self.show_hide_buttons(self.ids['ready'], hide=True)
            return

        if configuration == 'next':
            for button in (_peek, _compare, _confirm):
                self.show_hide_buttons(button, hide=True)
            self.show_hide_buttons(self.ids['next'], hide=False)
            return

        if configuration == 'confirm':
            for button in (_peek, _compare):
                self.show_hide_buttons(button, hide=True)
            self.show_hide_buttons(_confirm, hide=False)
            return

    def _on_solutions(self, *_):
        """
        A callback to a change in the self.solutions dictionary. The function essentially 'waits' until five
        solutions have been submitted then recolours the ResponseFields according to the data in the solutions
        dictionary.
        """
        if len(self.solutions) != 5:
            return
        if 3 in self.solutions.values():  # If one of the values = 3 then answer must be ambiguous - don't recolor
            self.configure_buttons('confirm')
        else:
            for field in self.fields():
                field.change_background(self.solutions[field.id_number])

            if isinstance(self, TutorialNavigationPane):  # If user is doing the tutorial
                self.configure_buttons('reset')
            else:
                self.configure_buttons('next')

    def fields(self):
        """
        A generator that yields each response field (to access a specific widget in the response field use the ID
        property)
        """
        for field in reversed(self.parent.parent.ids['response_fields'].children):
            yield field

    def compare(self):
        payload = {}
        for field in self.fields():
            if not field.data_submitted:  # Check if data has already been submitted - prevents wasteful resubmissions
                payload.update({field.id_number: field.retrieve_data()})

        user_answers = MathPixAPI().post_data(payload)
        print(user_answers)
        if user_answers is None:  # A network error has occured - open the connection popup
            self.parent.parent.parent.connection_popup.open()
            return
        for field in self.fields():
            data = user_answers.get(field.id_number, None)
            if data is not None:
                if type(data) == dict:
                    confidence = data.get('confidence', 1)
                    text = data.get('latex_styled', None)
                    field.check_answer(text=text, confidence=confidence)
                else:
                    field.check_answer(text=data)
        log.save_data()

    @counter
    @log.TimeStamp('peek')
    def peek(self, count):
        for field in self.fields():
            field.view_model(peek_button=True)
        if count % 2 == 0:
            self.score -= 150
        self.ids['compare'].disabled = not self.ids['compare'].disabled
        return {'peeking': count % 2 == 0, 'score': self.score}


class NavigationPane(BaseNavigationPane):

    @log.TimeStamp('ready')
    def ready(self):
        for field in self.fields():
            peek_widget = field.ids['peek_widget']
            peek_widget.visible = True
            peek_widget.show_hide()
            if field.writing:  # Reset button status to prevent them becoming out of sync
                field.ids['eraser_button'].disabled = False
            field.ids['keyboard_button'].disabled = False
        self.configure_buttons('question')

    def next(self):
        """
        First calls update_question() which increases the question_number by one and handles the model rendering. Then
        calls the function configure_buttons() with the parameter 'ready'.
        """
        self.update_question()
        self.configure_buttons('ready')
        log.save_data()

    @log.TimeStamp('next')
    def update_question(self):
        """
        Several things are taken care of in this function. The first is that the question number is increased by one.
        Then the question text is updated. Then any text drawn in the ExpressionWriters are removed, before finally the
        model is rendered. Finally, the function creates an attribute 'latex_parser': a LatexParser object that is
        accessed by all the ResponseFields when the solution is checked (see _on_data()). Finally, finally, the progress
        bar is updated.
        """
        screen = self.parent.parent
        screen.question_number += 1
        # if log.online:
        #     log.online_data_packet.update({str(screen.question_number): {}})  # Add a new question key a to data logger
        log.question_number = screen.question_number
        try:
            x1, y1, x2, y2 = COORDINATES[screen.question_number]
        except IndexError:  # Index error occurs when user has completed all questions
            screen.manager.current = 'completion_screen'
            return
        setattr(self, 'question_text',
                f"Find the equation of a line that goes through the coordinates ({x1}, {y1}) and ({x2}, {y2})")
        self.reset()
        setattr(self, 'latex_parser', LatexParser(x1, y1, x2, y2))
        Animation(completion=screen.question_number/20, d=0.5).start(self.ids['completion_bar'])
        return {'score': self.score}


class TutorialNavigationPane(BaseNavigationPane):
    pass


class TextWidget(Widget):
    cells = ListProperty()
    highlight_color = ListProperty(CLEAR)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.resize()
        self.bind(cells=self.resize)

    def __len__(self):
        return len(self.cells)

    def resize(self, *_):
        """
        A function that resizes the TextWidget. Width equals the width of the number of characters in the TextWidget
        multiplied by the text_size. If there are no characters in self.cells, then the width equals the width 1
        character.
        """
        width = TEXT_SIZE if (len(self) == 0) else TEXT_SIZE * len(self)
        self.size = (width, TEXT_SIZE)

    def add_text(self, text, italic, index):
        entry = Label(text=text,
                      color=(0, 0, 0, 1),
                      size=(TEXT_SIZE, TEXT_SIZE),
                      font_size=TEXT_SIZE,
                      font_name='maths_font',
                      italic=italic)
        self.cells.insert(index, entry)
        self.add_widget(entry)  # Renders Label to screen
        self.reposition(index)  # Will reposition any proceeding characters

    def reposition(self, index=0, *_):
        """
        A function that repositions all characters following the specified index. By specifying an index we don't need
        to reposition characters that are already in the correct position.
        :param index: The index with which
        """
        for i, cell in enumerate(self.cells[index:], index):
            cell.pos = (self.x + TEXT_SIZE * i, self.y)

    def delete_text(self, index):
        """
        Removes a character at a given index from the screen, then internally removes it.
        :param index: The of the character to be removed
        """
        self.remove_widget(self.cells[index - 1])
        del self.cells[index - 1]

    def highlight(self, highlight):
        self.highlight_color = [0.345, 0.42, 0.592, 0.175] if highlight else CLEAR


class Fraction(Widget):
    spacing = NumericProperty()
    numerator = ObjectProperty()
    denominator = ObjectProperty()

    def recenter(self):
        """
        Repositions the numerator / denominator so that it is in the middle of the fraction (whichever is shorter)
        :return:
        """
        if len(self.numerator) != len(self.denominator):
            term = self.numerator if (len(self.numerator) < len(self.denominator)) else self.denominator
            left_spacing = (self.width - term.width) / 2  # Space to the left of the term and the start of the fraction
            term.x = self.x + left_spacing  # Reposition the TextWidget
            term.reposition()
        else:
            self.numerator.x = self.denominator.x = self.x

    def get_text(self):
        numerator = ''.join([char.text for char in self.numerator.cells])
        denominator = ''.join([char.text for char in self.denominator.cells])
        return f'(({numerator})/({denominator}))'


class PeekWidget(Widget):
    visible = True

    def show_hide(self):
        self.height, self.size_hint_y, self.opacity, = (0, None, 0) if self.visible else (1, 1, 1)
        self.visible = not self.visible

    def display_text(self, text: str):
        """
        This function takes a mathematical expression expressed as a string (text argument) and renders it in a
        'mathematical format'. The function is primarily used to display the peek expressions but can be used to
        render any text (such as what the user has hand written).
        :param text: A mathematical expression [e.g. y = 4x + (10/9)]
        :return:
        """
        self.clear_widgets()
        prev = None  # The last widget added (useful for placing current widget on the screen)
        fraction = False  # A boolean indicating whether or not to add character to a fraction
        numerator = True  # True if characters should be added to a fraction's numerator, False if denominator
        _index = 0  # The index where to place a character in the fraction
        for t in text:
            if prev is None:  # Determine the x position of the widget (most widgets have a y position of self.y)
                x_pos = self.x + (self.width * 0.055)
            else:
                x_pos = prev.x + prev.width

            if t == '(':
                fraction = True  # An open bracket indicates the start of a fraction
                numerator = True
                _index = 0  # Reset the fraction index
                fraction_widget = Fraction()
                fraction_widget.pos = (x_pos, self.y + (self.parent.height - fraction_widget.height) / 2)
                continue  # See below for explanation for the use of self.parent.height

            if t == ')':
                fraction = False  # An closed bracket indicates the end of a fraction
                fraction_widget.recenter()  # Ensure that the fraction is the right size and position
                self.add_widget(fraction_widget)
                prev = fraction_widget
                continue

            italics = True if (t not in '0123456789-=×+') else False

            if fraction:
                if t == '/':
                    numerator = False
                    _index = 0  # Reset the fraction index (to start at 0 for the denominator)
                    continue

                if numerator:
                    fraction_widget.numerator.add_text(text=t, italic=italics, index=_index)
                else:
                    fraction_widget.denominator.add_text(text=t, italic=italics, index=_index)
                _index += 1

            else:
                widget = Label(
                    text=t,
                    pos=(x_pos, self.y + (self.parent.height - TEXT_SIZE) / 2),
                    color=(0, 0, 0, 1),
                    size=(TEXT_SIZE, TEXT_SIZE),
                    font_size=TEXT_SIZE,
                    font_name='maths_font',
                    markup=True,
                    italic=italics
                )  # Add the Label directly to the screen (instead of in a TextWidget)
                self.add_widget(widget)
                prev = widget

            # Using self.parent.height instead of self.height always produces the desired effect. In essence the
            # widgets are now draw according to the height of the ResponseField. This is desirable since the
            # height of the ResponseField is consistent (and is always the correct height), whereas the
            # PeekWidget changes its height depending on whether or not it is visible. Using self.height may cause the
            # text to be drawn in the wrong place.


class KeyboardWriter(FocusBehavior, Widget):
    cursor = ObjectProperty()
    starting_x = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.widgets = []
        # Need to be an attribute of the instance as manipulating a mutable class object changes referenced object that
        # all instances are accessing, i.e. if this were a class attribute all instances of the class would share the
        # same widgets. See link below for more details:
        # https://www.toptal.com/python/python-class-attributes-an-overly-thorough-guide

    def new_widget(self, text: str, italic: bool = False):
        """
        A function responsible for creating and positioning new widgets added to KeyboardWriter. This function will
        only be called in response to a Keyboard event.
        :param text: The character to be added
        :param italic: Indicating whether or not the text should be in italics or not.
        """
        if self.cursor.mode > 0:
            fraction = self.widgets[max(0, self.cursor.index - 1)]  # Get the fraction the cursor is located in
            if self.cursor.mode == 1:  # If the cursor is in the numerator
                fraction.numerator.add_text(text=text, italic=italic, index=self.cursor.fraction_index)
            else:
                fraction.denominator.add_text(text=text, italic=italic, index=self.cursor.fraction_index)
            fraction.recenter()
            self.reposition_widgets()
            self.cursor.fraction_index += 1
            return
        if text == '/':
            widget = Fraction()
            self.cursor.fraction_index = 0
        else:
            widget = Label(text=text,
                           color=(0, 0, 0, 1),
                           size=(TEXT_SIZE, TEXT_SIZE),
                           font_size=TEXT_SIZE,
                           font_name='maths_font',
                           italic=italic)
        self.widgets.insert(self.cursor.index, widget)  # Insert the widget wherever the fraction is
        self.add_widget(widget)
        self.reposition_widgets()
        self.cursor.index += 1

        # Have to add the widget first before telling the cursor to enter 'fraction mode'. This is because
        # cursor.mode has a binding to cursor.reposition(). In this case cursor.reposition is called twice
        # (not ideal but functional)
        if text == '/':
            self.cursor.mode = 1

    def reposition_widgets(self, *_):
        y_pos = lambda wid: self.y + (self.height - wid.height) / 2
        for i, widget in enumerate(self.widgets):
            if i == 0:
                widget.pos = self.starting_x, y_pos(widget)
            else:
                widget.pos = self.widgets[i - 1].x + self.widgets[i - 1].width, y_pos(widget)
            if isinstance(widget, Fraction):
                widget.numerator.reposition()
                widget.denominator.reposition()
                widget.recenter()

    def on_touch_down(self, touch):
        """
        A function that handles touches. Will move the cursor if the KeyboardWriter has focus
        :param touch: a Touch object
        """
        if self.parent.data_submitted or self.parent.ids['peek_widget'].visible:
            # Do not allow user to focus the widget if they have already submitted an answer or if the model is visible
            return
        if self.collide_point(*touch.pos) and self.focus:  # If the widget has focus and is touched
            if touch.x <= self.starting_x or len(self.widgets) == 0:
                self.cursor.index = 0  # If the touch left of starting_x or if there are no widgets
            elif self.widgets[-1].right < touch.x:  # A touch was made further right than the right most widget
                self.cursor.mode = 0
                self.cursor.index = len(self.widgets)  # Move cursor to the right
            else:
                for index, widget in enumerate(self.widgets):
                    if widget.collide_point(*touch.pos):

                        if isinstance(widget, Fraction):  # If the touch collides with a fraction
                            self.cursor.index = index + 1  # The index referring to the fraction
                            # The index HAS to be updated before anything else (because of the binding)

                            if touch.y > self.center_y:  # Numerator selected
                                self.cursor.mode = 1
                                term = widget.numerator
                            else:
                                self.cursor.mode = 2  # Denominator selected
                                term = widget.denominator

                            if len(term) == 0:  # No text in widget
                                self.cursor.fraction_index = 0
                            else:
                                for fraction_index, cell in enumerate(term.cells):
                                    if cell.collide_point(*touch.pos):  # Touch collides with a cell
                                        if touch.x > cell.center_x:
                                            self.cursor.fraction_index = fraction_index + 1
                                        else:
                                            self.cursor.fraction_index = fraction_index

                        else:  # If the collision is not with a fraction
                            self.cursor.mode = 0
                            if touch.x > widget.center_x:  # Finds the closest "gap" between widgets
                                self.cursor.index = index + 1
                            else:
                                self.cursor.index = index
                        break  # Stop searching for colliding widgets
        return super().on_touch_down(touch)  # Handle the FocusBehavior

    def keyboard_on_key_down(self, window, keycode, text, modifiers):
        key = keycode[1]
        if key == 'left' or key == 'right' or key == 'up' or key == 'down':
            self.cursor.move_cursor(key)
            return True
        if key == 'escape' or key == 'enter':
            self.focus = False
            return True
        if key == 'backspace':
            self.backspace()
            return True
        if len(self.widgets) > 0:
            if self.widgets[-1].right > self.right * 0.95:  # Do not let new text be added off the screen
                return True
        if modifiers == ['shift'] and text in MODIFIER:
            self.new_widget(text=MODIFIER[text])
            return True
        if not modifiers:  # An empty list always returns False
            if key == 'spacebar':
                key = ' '
            self.new_widget(text=key, italic=key.isalpha())
            return True
        return False

    def backspace(self):
        if self.cursor.index > 0:
            if self.cursor.mode > 0:
                if self.cursor.fraction_index > 0:
                    fraction = self.widgets[self.cursor.index - 1]
                    if self.cursor.mode == 1:
                        fraction.numerator.delete_text(index=self.cursor.fraction_index)
                    else:
                        fraction.denominator.delete_text(index=self.cursor.fraction_index)
                    if len(fraction.numerator) == len(fraction.denominator):
                        self.reposition_widgets()
                        # Fixes bug that maligns the fraction when len(denominator) = len(numerator)
                else:
                    self.remove_widget(self.widgets[self.cursor.index - 1])
                    del self.widgets[self.cursor.index - 1]
                    self.cursor.mode = 0
            else:
                self.remove_widget(self.widgets[self.cursor.index - 1])
                del self.widgets[self.cursor.index - 1]
            self.reposition_widgets()  # Reposition widgets after one has been removed. Prevents ga ps.
            if self.cursor.mode == 0:  # Change cursor index once the widget's have been repositioned
                self.cursor.index -= 1
            else:
                self.cursor.fraction_index -= 1

    def move_cursor_to_end(self, *_):
        self.cursor.mode = 0
        self.cursor.index = len(self.widgets)

    def get_text(self):
        text = []
        for widget in self.widgets:
            if isinstance(widget, Fraction):
                text.append(widget.get_text())
            else:
                text.append(widget.text)
        return ''.join(text)

    def reset(self):
        self.clear_widgets()
        self.add_widget(self.cursor)
        self.cursor.reset()
        self.widgets = []

    def _on_focus(self, instance, value, *args):
        self.cursor.is_visible = value  # If the writer has focus (value = True) then set the cursor to visible
        self.parent.ids['keyboard_writer'].cursor.change_highlight()
        super()._on_focus(instance, value, *args)  # Handle keyboard binding


class Cursor(Widget):
    index = NumericProperty()
    fraction_index = NumericProperty()
    mode = NumericProperty(0)
    #  0 - fraction = False (i.e. the cursor is not in a fraction_
    #  1 - numerator = True (fraction = True)
    #  2 - numerator = False (fraction = True)
    color = ListProperty(CLEAR)
    is_visible = BooleanProperty(False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pause = False  # if True pauses the blinking cursor
        self.blink_event = Clock.schedule_interval(lambda dx: self.blink(), 0.53)
        self.bind(index=self.reposition, fraction_index=self.reposition, mode=self.reposition)
        self.bind(mode=self.change_highlight)
        self.bind(is_visible=self.show_hide_cursor)

    def show_hide_cursor(self, *_):
        """
        A class method bound to the is.visible attribute. When is.visible is changed this function is called which
        modifies the visibility of the cursor accordingly
        """
        self.color = CURSOR_BLUE if self.is_visible else CLEAR

    def blink(self):
        """
        A function that is called every 0.53 seconds as a result of self.blink_event. Simply, if the widget has focus
        then change is_visible to not is_visible. Since is_visible is a BooleanProperty bound to show_hide_cursor() the
        cursor's color property is changed.
        """
        if self.parent.focus:
            if self.pause:
                self.pause = not self.pause
                return
            self.is_visible = not self.is_visible

    def reposition(self, *_):
        if len(self.parent.widgets) == 0:
            self.pos = self.parent.starting_x, self.parent.y + (self.parent.height - self.height) / 2
            return
        i = max(0, self.index - 1)  # Prevents index-1 < 0
        if self.mode > 0:
            fraction = self.parent.widgets[i]
            if self.mode == 1:
                self.pos = (fraction.numerator.x + TEXT_SIZE * self.fraction_index,
                            fraction.numerator.y)
            else:
                self.pos = (fraction.denominator.x + TEXT_SIZE * self.fraction_index,
                            fraction.denominator.y)
        else:
            distance = self.parent.starting_x
            for widget in self.parent.widgets[:self.index]:
                distance += widget.width
            self.pos = distance, self.parent.y + (self.parent.height - self.height) / 2

        self.is_visible = True  # Make the cursor visible
        self.pause = True  # Stop it temporarily from blinking

    def move_cursor(self, direction: str):
        """
        A function that moves the cursor in a given direction.
        :param direction: 'left', 'right', 'up' or 'down'
        """
        if len(self.parent.widgets) == 0:  # Don't move if there is nowhere to move
            return
        widget = self.parent.widgets[self.index - 1]

        if self.mode > 0:
            if direction == 'left':
                if self.fraction_index > 0:  # If there are still characters in the fraction move left
                    self.fraction_index -= 1
                else:
                    self.mode = 0  # Exit 'fraction mode'
                    if self.index > 0:  # If this isn't the first widget then subtract one to the index
                        self.index -= 1
                return
            if direction == 'right':
                if (self.mode == 1 and self.fraction_index < len(widget.numerator) - 1) \
                        or (self.mode == 2 and self.fraction_index < len(widget.denominator) - 1):
                    # In short if there are still widgets in the fraction to the right.
                    self.fraction_index += 1
                else:
                    self.mode = 0
                return
            if self.mode == 1 and direction == 'down':
                self.mode = 2
                self.fraction_index = min(self.fraction_index, len(widget.denominator))
            if self.mode == 2 and direction == 'up':
                self.mode = 1
                self.fraction_index = min(self.fraction_index, len(widget.numerator))
            return
        if direction == 'left':
            if self.index > 0:
                if isinstance(widget, Fraction):
                    self.fraction_index = len(widget.denominator)
                    self.mode = 2
                else:
                    self.index -= 1
            return
        if direction == 'right':
            if self.index < len(self.parent.widgets):  # Only move right if there are widgets to the right
                self.index += 1
                if isinstance(self.parent.widgets[self.index - 1], Fraction):  # Check whether new widget is fraction
                    self.fraction_index = 0
                    self.mode = 1
            return

    def change_highlight(self, *_):
        """
        Function is bound to self.mode. The function attempts to get the last widget, then if the last widget is a
        fraction it changes the highlighting of the numerator and denominator
        """
        try:
            widget = self.parent.widgets[self.index - 1]
        except IndexError:  # Deleting a fraction may temporarily cause misalignment between len(widgets) and self.index
            return
        if isinstance(widget, Fraction):
            # This function is called when mode changes. When a fraction is deleted mode is changed to 0. This causes
            # problems since Labels do not have a property "numerator".
            if self.mode > 0 and self.parent.focus:  # No focus, no highlight
                widget.numerator.highlight(self.mode == 1)
                widget.denominator.highlight(self.mode == 2)
            else:
                widget.numerator.highlight(False)  # Cursor not in fraction
                widget.denominator.highlight(False)

    def reset(self):
        self.index = 0
        self.fraction_index = 0
        self.mode = 0
        self.color = CLEAR


class RoundedButton(ButtonBehavior, Label):

    def on_disabled(self, *args):
        """
        Callback for when self.disabled is changed. If True then disabled reduce saturation and value by 11%, otherwise
        increase saturation and value by 11%.
        :param args: args inherited from callback - not needed
        """
        if self.disabled:
            self.color = [0.75, 0.75, 0.75, 1]
        else:
            self.color = [1, 1, 1, 1]

class IDInput(TextInput):

    def insert_text(self, substring, from_undo=False):
        if substring.isnumeric():
            if len(self.text) < 1:
                super().insert_text(substring, from_undo=from_undo)
                self.focus_next_input()

    def focus_next_input(self):
        self.focus = False
        if self.next_input is not None:
            self.next_input.focus = True

class ConnectionPopup(Popup):

    def connection(self, host='http://google.com'):
        try:
            urlopen(host)
            self.dismiss()
            return True
        except:
            return False

class IDPopup(Popup):
    
    def submit(self):
        user_id = ''
        for id_input in reversed(self.ids['id_boxlayout'].children):
            if id_input.text == '':
                id_input.focus = True
                return
            user_id += id_input.text
        log.user_id = user_id
        self.close_popup()

    @log.TimeStamp('app-start')
    def close_popup(self):
        return super().dismiss()


