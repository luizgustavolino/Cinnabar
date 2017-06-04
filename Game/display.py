import sys, subprocess

def enterGameEnv():
    if sys.platform.startswith('linux'):
        cmd = "xrandr --output eDP-1 --mode 960x540 --rate 60"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()

def exitGameEnv():
    if sys.platform.startswith('linux'):
        cmd = "xrandr --output eDP-1 --mode 1366x768 --rate 60"
        subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).communicate()
