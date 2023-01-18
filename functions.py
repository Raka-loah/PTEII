import ctypes
from ctypes import wintypes
import psutil

##########################################################
# 用于检测窗口标题的WIN32 API
# EnumWindows 列举所有前台窗口
# GetWindowTextW+GetWindowTextLengthW 按窗口句柄获取窗口标题
##########################################################

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL,
                                 wintypes.HWND,
                                 wintypes.LPARAM)
user32 = ctypes.windll.user32
user32.EnumWindows.argtypes = [
    WNDENUMPROC,
    wintypes.LPARAM]
user32.GetWindowTextLengthW.argtypes = [
    wintypes.HWND]
user32.GetWindowTextW.argtypes = [
    wintypes.HWND,
    wintypes.LPWSTR,
    ctypes.c_int]

ignore_process_list = ['', 'svchost.exe', 'explorer.exe', 'dwm.exe']
ignore_title_list = ["''", "'Default IME'", "'MSCTFIME UI'"]

window_titles = []

def get_window_text(hwnd):
    length = user32.GetWindowTextLengthW(hwnd) + 1
    buffer = ctypes.create_unicode_buffer(length)
    user32.GetWindowTextW(hwnd, buffer, length)
    return repr(buffer.value)

def worker(hwnd, lParam):
    title = get_window_text(hwnd)
    pid = wintypes.DWORD()
    ctypes.windll.user32.GetWindowThreadProcessId(hwnd,ctypes.byref(pid))
    try:
        window_process = psutil.Process(pid.value).name()
    except psutil.NoSuchProcess:
        window_process = ''
    if window_process not in ignore_process_list and title not in ignore_title_list:
        window_titles.append({
            'hwnd': hwnd,
            'title': title[1:-1],
            'pid': pid.value,
            'process': window_process,
        })
    return True

def get_all_window_titles():
    global window_titles
    window_titles = []
    cb_worker = WNDENUMPROC(worker)
    if not user32.EnumWindows(cb_worker, 1):
        raise ctypes.WinError()
    return window_titles

##########################################
# 匹配窗口标题
# 支持Foobar格式：%title% - %artist%
# 将其转义到正则表达式
# 内部使用正则
##########################################

import re

def convert_capture_pattern(pattern):
    # 如果有“%blahblah%”这样的格式出现，判定为Foobar格式
    # 写错了则直接raise error
    pre_match = re.search(r'%(.+?)%', pattern)
    if pre_match:
        pre_process = re.escape(pattern)
        converted_pattern = re.sub(r'%(.+?)%', r'(?P<\1>.+)', pre_process)
    else:
        converted_pattern = pattern
    return converted_pattern

def match_title(pattern, title):
    try:
        match = re.search(convert_capture_pattern(pattern), title)
        if match:
            if len(match.groupdict()) > 0:
                return match.groupdict()
            else:
                return { k+1:v for k,v in enumerate(match.groups())}
    except:
        pass
    return {}