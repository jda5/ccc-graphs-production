from kivy.app import App
from kivy.network.urlrequest import UrlRequest
from json import dumps
from os.path import join
from time import time
import csv


class DataLogger:

    user_id = '0000'
    t0 = time()
    local_data_packet = []
    question_number = -1

    def __init__(self):
        self.total_peeks = []
        self.total_correct = []
        self.total_time = []

        self.current_peeks = 0
        self.current_time = 0
        self.current_start_time = 0
        self.current_correct = 0

        self.solution_number = 0
        self.question_number = -1

        self.pause_time = 0
        self.enter_time = 0
        
    class TimeStamp:

        def __init__(self, event_type, *args):
            self.event_type = event_type
            self.args = args

        def __call__(self, function):
            """
            The TimeStamp class is used as a class decorator. A timestamp is created by subtracting the current time by
            t0. Then data is added to the numerically largest key in the DataLogger dictionary.
            :param function: The function to be called
            """
            def wrapper(*args, **kwargs):
                time_log = "%.5f" % (time() - DataLogger.t0)
                result = function(*args, **kwargs)
                DataLogger.local_data_packet.append([time_log, log.question_number, self.event_type, result])

                if self.event_type == 'peek':           # Keeps an internal record on the number of peeks
                    log.current_peeks += 1
                elif self.event_type == 'solution':     # Keeps an internal record on the number of correct responses
                    if result is not None:              # Result may be None 
                        for event_data in result.values():
                            if event_data['correct']:
                                log.current_correct += 1
                    log.solution_number += 1
                    if log.solution_number % 5 == 0:    # Avoids updating the time per question 5 times (one for each response field)
                        log.current_time = float(time_log) - log.current_start_time
                elif self.event_type == 'next':         # Save data and reset counters
                    log.current_time -= log.pause_time
                    log.total_peeks.append(log.current_peeks // 2)
                    log.total_correct.append(log.current_correct)
                    log.total_time.append(log.current_time)
                    log.current_start_time = float(time_log)
                    log.current_peeks = 0
                    log.current_correct = 0
                    log.pause_time = 0
                elif self.event_type == 'enter-data-screen':
                    log.enter_time = float(time_log)
                elif self.event_type == 'enter-ccc-screen':
                    log.pause_time += float(time_log) - log.enter_time    

            return wrapper

    def save_data(self, *args):
        print(App.get_running_app().user_data_dir)
        file_path = join(App.get_running_app().user_data_dir, f'{self.user_id}-data.csv')
        with open(file_path, 'w') as data_file:
            csv_writer = csv.writer(data_file)
            csv_writer.writerows(self.local_data_packet)

log = DataLogger()
