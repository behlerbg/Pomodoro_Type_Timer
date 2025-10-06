#! python3
## PomodoroTimer.py
## A Pomodoro timer
## Brett Behler 12.18.2018


## The pomodoro system is a structured time system designed to help people focus on specific tasks.
## The structure is broken up into intervals of a certain length (20-25 minutes) broken up by shorter length breaks (1-5 minutes)
## with a longer break (15-20 minutes) after the set number of intervals (4) is complete.

from tkinter import *
from tkinter import messagebox
from playsound3 import playsound

import time

UPDATES_PER_SECOND = 1000 //  5   # 5 times per second in miliseconds

class Application(Frame):
    '''A GUI Application for a Pomodoro timer.'''
    def __init__(self, master):
        super(Application, self).__init__(master)
        self.grid()
        self.create_widgets()
        self.active_timer = None
        self.audio_file = "tannoy-chime-04.wav"
        self.playing = None
        self.alerted = False

    def create_widgets(self):
        '''Creates widgets for timer.'''
        Label(self, text='Setup Options:').grid(row=0, column=0, columnspan=2)

        Label(self, text='Number of working periods:').grid(row=1, column=0, sticky=W)
        self.part_option = Entry(self)
        self.part_option.grid(row=1, column=1, sticky=W)
        self.part_option.insert(0, '4')

        Label(self, text='Working period duration (minutes):').grid(row=2, column=0, sticky=W)
        self.part_length_option = Entry(self)
        self.part_length_option.grid(row=2, column=1, sticky=W)
        self.part_length_option.insert(0, '25')

        Label(self, text='Short rest duration (minutes):').grid(row=3, column=0, sticky=W)
        self.short_length_option = Entry(self)
        self.short_length_option.grid(row=3, column=1, sticky=W)
        self.short_length_option.insert(0, '5')

        Label(self, text='Long rest duration (minutes):').grid(row=4, column=0, sticky=W)
        self.long_length_option = Entry(self)
        self.long_length_option.grid(row=4, column=1, sticky=W)
        self.long_length_option.insert(0, '15')

        Label(self).grid(row=5, column=0)

        Label(self, text='Current Part:').grid(row=6, column=0, sticky=W)
        self.parts_text = Text(self, width=2, height=1)
        self.parts_text.grid(row=6, column=0, sticky=E)

        Label(self, text='Completed Sets:').grid(row=7, column=0, sticky=W)
        self.sets_text = Text(self, width=2, height=1)
        self.sets_text.grid(row=7, column=0, sticky=E)

        Label(self, text='Time Remaining:').grid(row=8, column=0, sticky=W)
        self.time_text = Text(self, width=45, height=2, wrap=WORD)
        self.time_text.grid(row=9, column=0, columnspan=5, sticky=W)

        Label(self).grid(row=10, column=0)

        self.start_button = Button(self, text='Start', command=self.start_timer)
        self.start_button.grid(row=11, column=0, sticky=W)
        
        self.pause_button = Button(self, text='Pause', command=self.pause_timer)
        self.pause_button.grid(row=11, column=0)

        self.reset_button = Button(self, text='Reset', command=self.reset_timer)
        self.reset_button.grid(row=11, column=1, sticky=W)

        self.quit_button = Button(self, text='Quit', command=self.end_program)
        self.quit_button.grid(row=11, column=1, sticky=E)

    def start_timer(self):
        if self.active_timer:
            if self.active_timer.is_paused:
                self.active_timer.toggle_pause()
                self.update_self()
            if self.active_timer.time_expired:
                self.active_timer.timer_start()
                
        else:
            self.active_timer = Timer(
                int(self.part_option.get()), 
                float(self.short_length_option.get()),
                float(self.long_length_option.get()),
                float(self.part_length_option.get()) 
                )
            self.update_self()
        self.stop_sound()
    
    def pause_timer(self):
        if self.active_timer:
            self.active_timer.toggle_pause()
            self.update_self()

    def reset_timer(self):
        self.stop_sound()
        self.active_timer = None
        self.time_text.delete(0.0, END)
        self.sets_text.delete(0.0, END)
        self.parts_text.delete(0.0, END)

    def end_program(self):
        if self.active_timer and not self.active_timer.time_expired:
            confirm = messagebox.askyesno(title='Confirm Exit', message='You have a timer running.\nAre you sure you want to quit?')
            if confirm:
                self.stop_sound()
                raise SystemExit
        else:
            self.stop_sound()
            raise SystemExit

    def update_self(self):
        global UPDATES_PER_SECOND
        if self.active_timer and not self.active_timer.is_paused:
            self.active_timer.update_time()
            if self.active_timer.time_expired:
                self.time_text.delete(0.0, END)
                self.time_text.insert(0.0, self.active_timer.expire_message)
                self.play_sound()
            else:
                self.time_text.delete(0.0, END)
                self.time_text.insert(0.0, str(self.active_timer))
            self.sets_text.delete(0.0, END)
            self.sets_text.insert(0.0, str(self.active_timer.sets))
            self.parts_text.delete(0.0, END)
            self.parts_text.insert(0.0, str(self.active_timer.part))
            self.after(UPDATES_PER_SECOND, self.update_self)

    def play_sound(self):
        if self.playing:
            if self.playing.is_alive():
                return
        self.playing = playsound(self.audio_file, block=False)

    def stop_sound(self):
        if self.playing:
            if self.playing.is_alive():
                self.playing.stop()
            self.playing = None
            

class Timer(object):
    def __init__(self, num_parts=4, short_length=5, long_length=15, part_length=25):
        '''A class for tracking a custom pomodoro style timer.
        
        Arguments:
            num_parts (int) : integer of the number of parts before a long break.
            short_length (int) || (float): integer or float of duration of short break in minutes.
            long_length (int) || (float): integer or float of duration of long break in minutes.
            part_length (int) || (float): integer or float of duration of each Pomodoro part.
        
        Returns:
            Timer object
        
        Raises:
            None
        '''
        self.part = 0
        self.sets = 0
        self.num_parts = num_parts
        self.short_length = short_length * 60
        self.long_length = long_length * 60
        self.part_length = part_length * 60
        self.on_short_break = False
        self.on_long_break = False
        self.is_paused = False
        self.time_expired = False
        self.timer_start()

    def __str__(self):
        difference = int(self.end_time - self.start_time)
        minutes = difference // 60
        seconds = difference % 60
        rep =  '{0:02d}:{1:02d}'.format(minutes, seconds)
        return rep

    def timer_start(self):
        self.time_expired = False
        self.start_time = round(time.time())
        if self.on_long_break:
            self.end_time = self.start_time + self.long_length
        elif self.on_short_break:
            self.end_time = self.start_time + self.short_length
        else:
            self.end_time = self.start_time + self.part_length
            self.part += 1

    def update_time(self):
        if not self.time_expired:
            if not self.is_paused:
                self.start_time += round(time.time()) - self.start_time
            if self.start_time >= self.end_time:
                self.time_expire()

    def toggle_pause(self):
        if not self.time_expired:
            self.is_paused = not self.is_paused
            if self.is_paused:
                self.paused_time = round(time.time())
            else:
                self.end_time += round(time.time() - self.paused_time)
        
    def time_expire(self):
        self.time_expired = True
        if self.part < self.num_parts and not self.is_on_break():
            self.on_short_break = True
            self.expire_message = 'Working period {0} of {1} ended. Click "Start" to begin {2:.0f} minute short rest.'.format(self.part, self.num_parts, (self.short_length/60))
        
        elif not self.is_on_break():
            self.on_long_break = True
            self.expire_message = 'Completed set {0}. Click "Start" to begin {1:.0f} minute long rest.'.format((self.sets + 1), (self.long_length/60))

        else:
            self.expire_message = 'Break is now over. Click "Start" to begin next {0:.0f} minute working period.'.format((self.part_length/60))
            if self.on_long_break:
                self.part = 0
                self.sets += 1
            self.on_long_break = False
            self.on_short_break = False

    def is_on_break(self):
        return self.on_long_break or self.on_short_break

if __name__ == '__main__':
    root = Tk()
    root.title('Pomodoro Timer')
    app = Application(root)
    root.mainloop()
