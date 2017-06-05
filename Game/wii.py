"""
- WIIMote Thread
- Projeto Cinnabar, BCC SENAC 2017
- Baseado na implementacao de Gary Bishop, 2008
"""

from threading import Thread
from Queue import Queue, Empty
import time

wiiuse = None 

class wiimote_thread(Thread):
   
    def __init__(self, nmotes=1, timeout=5):

        Thread.__init__(self, name='wiimote')

        self.queue = Queue()
        self.startup = Queue()
        self.nmotes = nmotes
        self.timeout = timeout
        self.setDaemon(1)
        self.start()
        self.startup.get(True) 

    def run(self):

        global wiiuse
        import wiiuse
        
        self.wiimotes = wiiuse.init(self.nmotes)
        found = wiiuse.find(self.wiimotes, self.nmotes, self.timeout)
        self.actual_nmotes = wiiuse.connect(self.wiimotes, self.nmotes)

        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], wiiuse.LED[i])

        self.go = self.actual_nmotes != 0

        self.startup.put(self.go)

        while self.go:
            try:
                if wiiuse.poll(self.wiimotes, self.nmotes):
                    for i in range(self.nmotes):
                        wm = self.wiimotes[i][0]
                        if wm.event:
                            self.event_cb(wm)

            except Exception as error: 
                print error
                self.quit()

            while True:
                try:
                    func, args = self.queue.get_nowait()
                except Empty:
                    break
                func(*args)

    def do(self, func, *args):
        self.queue.put((func, args))

    def event_cb(self, wm):

        if wm.btns:
            for name,b in wiiuse.button.items():
                if wiiuse.is_just_pressed(wm, b):
                    print "press", name 

        if wm.btns_released:
            for name,b in wiiuse.button.items():
                if wiiuse.is_released(wm, b):
                    print "release", name

        print "acell", wm.orient.pitch


    def quit(self):
        for i in range(self.nmotes):
            wiiuse.set_leds(self.wiimotes[i], 0)
            wiiuse.disconnect(self.wiimotes[i])
        self.go = False

WT = None

def init(nmotes, timeout):

    global WT
    if WT:
        return
    WT = wiimote_thread(nmotes, timeout)

def get_count():
    return WT.actual_nmotes

def quit():
    WT.quit()
    WT.join()

class wiimote(object):

    def __init__(self, n):
        self.wm = WT.wiimotes[n]

    def enable_leds(self, m):
        WT.do(wiiuse.set_leds, self.wm, sum([wiiuse.LED[i] for i in range(4) if m & (1<<i)]))

    def enable_rumble(self, on):
        WT.do(wiiuse.rumble, self.wm, on)

    def enable_accels(self, on):
        WT.do(wiiuse.motion_sensing, self.wm, on)

    def enable_ir(self, on, vres=None, position=None, aspect=None):
        WT.do(wiiuse.set_ir, self.wm, on)
        if vres is not None:
            WT.do(wiiuse.set_ir_vres, self.wm, vres[0], vres[1])
        if position is not None:
            WT.do(wiiuse.set_ir_position, self.wm, position)
        if aspect is not None:
            WT.do(wiiuse.set_aspect_ratio, self.wm, aspect)

    def set_flags(self, smoothing=None, continuous=None, threshold=None):
        enable = disable = 0
        if smoothing is not None:
            if smoothing:
                enable |= wiiuse.SMOOTHING
            else:
                disable |= wiiuse.SMOOTHING
        if continuous is not None:
            if continuous:
                enable |= wiiuse.CONTINUOUS
            else:
                disable |= wiiuse.CONTINUOUS
        if threshold is not None:
            if threshold:
                enable |= wiiuse.ORIENT_THRESH
            else:
                disable |= wiiuse.ORIENT_THRESH
        print enable, disable
        WT.do(wiiuse.set_flags, self.wm, enable, disable)

    def set_orient_thresh(self, thresh):
        WT.do(wiiuse.set_orient_threshold, self.wm, thresh)

    def status(self):
        WT.do(wiiuse.status, self.wm)

    def disconnect(self):
        WT.do(wiiuse.disconnect(self.wm))

def Wiimote(n):
    return wiimote(n)

