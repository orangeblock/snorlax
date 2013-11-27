#
#
#   A simple program(w/ GUI) that puts the computer to sleep after a timer has expired.
#
#   Tested under Windows 7.
#   If the computer has hibernation enabled the computer will hibernate instead of sleeping.
#   To prevent this, either run the program as an administrator and follow the prompts,
#   or run "powercfg -H OFF" in a command window with admin rights.
#
import re
import subprocess
import sys
if sys.version_info[0] == 2:
    from Tkinter import *
    import tkMessageBox
else:
    from tkinter import *

class Timer:
    """
        A timer widget.
    """
    def __init__(self, sec):
        self.m = sec//60
        self.s = sec%60

    def __str__(self):
        return '{}:{}'.format('0'+str(self.m) if self.m < 10 else self.m, '0'+str(self.s) if self.s < 10 else self.s)

    def decr(self):
        self.m = self.m-1 if self.s == 0 else self.m
        self.s = 59 if self.s == 0 else self.s-1

    def complete(self):
        return self.s == 0 and self.m == 0


class Frame(Tk):
    """
        The GUI frame.
    """
    def __init__(self, handler):
        Tk.__init__(self)
        self.handler = handler
        self.handler.view = self
        self.initialize()
        self.mainloop()

    def initialize(self):
        """ Sets up the GUI """

        self.title("Snorlax")
        self.resizable(False, False)

        # Timer widget
        self.timer_var = StringVar()
        self.timer_var.set(str(Timer(0)))
        timer = Label(self, textvariable=self.timer_var, font=("Arial", 30, "bold"))
        timer.grid(row=0, columnspan=2, padx=(50,50), pady=(30,5))

        # "Set display:" label
        delay_text = Label(self, text="Set delay:")
        delay_text.grid(row=1, columnspan=2, padx=(50,50), pady=(0,10), sticky=N)

        # Text entry for amount to wait
        self.amount_entry = Entry(self, width=5)
        self.amount_entry.insert(0, 20)
        self.amount_entry.grid(rowspan=3, column=0, padx=(80, 0), pady=(4,0))

        # Bullet list for type of amount (min, sec, hours)
        self.smh = StringVar()
        self.smh.set("m")
        seconds = Radiobutton(self, text="sec", variable=self.smh, value='s')
        minutes = Radiobutton(self, text="min", variable=self.smh, value='m')
        hours = Radiobutton(self, text="hours", variable=self.smh, value='h')
        seconds.grid(row=2, column=1, padx=(20,70), sticky=E)
        minutes.grid(row=3, column=1, padx=(20,66), sticky=E)
        hours.grid(row=4, column=1, padx=(20,57), sticky=E)

        # Sleep button (begin countdown)
        self.sleep_button = Button(self, text='Sleep', command=self.handler.countdownStarted)
        self.sleep_button.configure(width=8)
        self.sleep_button.grid(row=5, columnspan=2, sticky=E, padx=(20,130), pady=(20,30))

        # Cancel button (stop countdown)
        self.cancel_button = Button(self, text="Cancel", command=self.handler.countdownCanceled)
        self.cancel_button.configure(state='disabled', width=8)
        self.cancel_button.grid(row=5, columnspan=2, sticky=E, padx=(20,50), pady=(20,30))

    def tick_timer(self):
        """ 
            Ticks timer down to 0. 
            The variable self.t represents the timer and is set through the handler.
        """
        # set a countdown until tick_timer is called again.
        self._job = self.after(1000, self.tick_timer)

        self.timer_var.set(str(self.t))
        if self.t.complete():
            self.handler.sleep()
        else:
            self.t.decr()
            
    def stop_timer(self):
        self.after_cancel(self._job)

    def show_warning(self, message, title='Warning!'):
        tkMessageBox.showwarning(title, message)

    def ask_yes_no(self, message, title='Snorlax'):
        return tkMessageBox.askyesno(title, message)

    def dispose(self):
        self.destroy()


class Snorlax:
    """
        Event handler.
    """
    def start(self):
        Frame(self)

    def countdownStarted(self):
        m = re.match(r'\d+$', self.view.amount_entry.get())
        if not m:
            self.view.show_warning('Invalid delay amount entered.', title='Format error')
        elif not self.check_hibernation():
            total_secs = int(m.group(0)) * [1, 60, 3600][['s', 'm', 'h'].index(self.view.smh.get())]
            self.view.t = Timer(total_secs) # Set up the timer
            self.change_button_status(sleep_status=False, cancel_status=True)
            self.view.tick_timer()

    def countdownCanceled(self):
        self.stop_timer()

    def sleep(self):
        self.stop_timer()
        subprocess.call(["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"])

    def check_hibernation(self):
        """
            Checks and returns if hibernation is enabled (True = enabled, False = disabled or user agrees for enabled)
        """
        output = subprocess.check_output(['powercfg', '-A'], universal_newlines=True)
        hibernation = re.search(r'are available.*[hH]ibernate.*not available', output, flags=re.DOTALL)
        if hibernation:
            if self.view.ask_yes_no("Hibernation is on. Would you like to disable it? (Pressing No will cause the computer to hibernate instead of going to soft sleep.)", title="Hibernation"):
                if subprocess.call(['powercfg', '-H', 'OFF']) == 1:
                    self.view.show_warning("You must run this program as an administrator.", title="Administrative Rights")
                    return True
        return False

    def change_button_status(self, sleep_status, cancel_status):
        self.view.sleep_button.configure(state='active' if sleep_status else 'disabled')
        self.view.cancel_button.configure(state='active' if cancel_status else 'disabled')

    def stop_timer(self):
        self.view.stop_timer()
        self.change_button_status(sleep_status=True, cancel_status=False)


if __name__ == '__main__':
    Snorlax().start()