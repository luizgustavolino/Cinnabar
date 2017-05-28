from engine import *
import display
import sys

if __name__ == '__main__':
    display.enterGameEnv()
    try: Engine().start()
    except Exception as error: print error
    display.exitGameEnv()
