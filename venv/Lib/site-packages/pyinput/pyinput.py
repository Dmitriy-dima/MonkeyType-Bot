from time import sleep, time
from pyinput import pyinputkeycodes
import win32gui, win32ui, win32con, win32api

def list_windows():
    def winEnumHandler(hwnd, ctx):
        if win32gui.IsWindowVisible(hwnd):
            print(hex(hwnd), '"' + win32gui.GetWindowText(hwnd) + '"')
    win32gui.EnumWindows(winEnumHandler, None)
    return

def list_inner_windows(whndl):
    def callback(hwnd, hwnds):
        if win32gui.IsWindowVisible(hwnd) and win32gui.IsWindowEnabled(hwnd):
            hwnds[win32gui.GetClassName(hwnd)] = hwnd
        return True
    hwnds = {}
    win32gui.EnumChildWindows(whndl, callback, hwnds)
    print(hwnds)
    return 

def get_handle(windowName):
    return win32gui.FindWindow(None, windowName)

def press_key(hwnd, key, hold_sec = 0.1, force_foreground = True):
    #Todo: threading
    if (force_foreground):
        win32gui.SetForegroundWindow(hwnd)
    
    win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, key, 0)
    sleep(hold_sec);
    win32api.SendMessage(hwnd, win32con.WM_KEYUP, key, 0)