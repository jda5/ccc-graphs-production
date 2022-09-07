from kivy.clock import Clock
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.properties import BooleanProperty
from data import log
from statistics import mean
from time import time
from widgets import ConnectionPopup, IDPopup


def custom_mean(data_list):
    if len(data_list) == 0:
        return 0
    return round(mean(data_list))


class Manager(ScreenManager):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.update_question = True
        self.connection_popup = ConnectionPopup()

class HomeScreen(Screen):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.show_popup = True
        self.id_popup = IDPopup()

    def on_enter(self, *args):
        if self.show_popup:
            Clock.schedule_once(lambda dt: self.id_popup.open())
            self.show_popup = False
        if not self.parent.connection_popup.connection():
            Clock.schedule_once(lambda dt: self.parent.connection_popup.open())   
        
    def on_leave(self, *args):
        log.pause_time = 0         # conveniently on_leave is fired AFTER on_enter so we can reset values here


class CCCScreen(Screen):
    question_number = -1

    @log.TimeStamp('enter-ccc-screen')
    def on_enter(self, *args):
        if self.manager.update_question:
            self.ids['_navigation'].update_question()
            log.question_start_time = time() - log.t0


class CompletionScreen(Screen):

    @log.TimeStamp('enter-completion-screen')
    def on_pre_enter(self, *args):
        score = self.manager.get_screen('ccc_screen').ids['_navigation'].score
        self.ids['score'].text = str(score)
        for label_name, data_list in zip(('peek', 'correct', 'time'), (log.total_peeks, log.total_correct, log.total_time)):
            self.ids[label_name].text = str(sum(data_list[1:]) if label_name != 'time' else custom_mean(data_list[1:]))

class TutorialScreen(Screen):

    @log.TimeStamp('enter-tutorial-screen')
    def on_enter(self, *args):
        for i, response_field in enumerate(self.ids['response_fields'].children):
            response_field.reset_field()
            if i < 3:
                response_field.switch_mode()
        self.ids['_navigation'].ids['compare'].disabled = True


class InfoScreen(Screen):

    @log.TimeStamp('enter-data-screen')
    def on_pre_enter(self, *args):
        self.manager.update_question = False
        ccc_screen = self.manager.get_screen('ccc_screen')
        self.ids['score'].text = str(ccc_screen.ids['_navigation'].score)
        self.ids['completion'].completion = ccc_screen.question_number / 20
        for label_name, data_list in zip(('peek', 'correct', 'time'), (log.total_peeks, log.total_correct, log.total_time)):
            self.ids[label_name].prev = str(round(data_list[-1])) if len(data_list) > 1 else 'N/A'
            self.ids[label_name].total = str(sum(data_list[1:]) if label_name != 'time' else custom_mean(data_list[1:]))

    
