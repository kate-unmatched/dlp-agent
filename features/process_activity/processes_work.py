# features/process_activity.py

import psutil
import time
import re

# Программы, запуск которых считаем "неразрешёнными"
UNKNOWN_PROCESSES = ["tor.exe", "python.exe", "hacker_tool.exe"]

# Средства администрирования (Windows)
ADMIN_TOOLS = ["regedit.exe", "cmd.exe", "mmc.exe", "taskmgr.exe"]

# Инструменты автоматизации (и возможной симуляции)
AUTOMATION_TOOLS = ["autohotkey.exe", "selenium.exe", "macrorecorder.exe"]

# Средства захвата экрана
SCREEN_CAPTURE_TOOLS = ["snippingtool.exe", "obs64.exe", "screenrecorder.exe"]

# Командные оболочки (для учёта времени)
TERMINALS = ["cmd.exe", "powershell.exe", "wt.exe", "terminal.exe"]

_state = {
    "process_count": 0,
    "unknown_processes_started": 0,
    "admin_tools_used": 0,
    "time_in_terminal_sec": 0,
    "automation_tool_detected": 0,
    "screen_capture_tools_used": 0
}

TERMINAL_ACTIVITY_CACHE = {}


def collect_process_features():
    reset_state()
    current_time = time.time()

    for proc in psutil.process_iter(["name", "create_time"]):
        try:
            name = proc.info["name"].lower()
            create_time = proc.info["create_time"]
            _state["process_count"] += 1

            if name in UNKNOWN_PROCESSES:
                _state["unknown_processes_started"] += 1
            if name in ADMIN_TOOLS:
                _state["admin_tools_used"] = 1
            if name in AUTOMATION_TOOLS:
                _state["automation_tool_detected"] = 1
            if name in SCREEN_CAPTURE_TOOLS:
                _state["screen_capture_tools_used"] = 1

            if name in TERMINALS:
                runtime = current_time - create_time
                if runtime <= 30:
                    TERMINAL_ACTIVITY_CACHE[name] = runtime

        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    _state["time_in_terminal_sec"] = int(sum(TERMINAL_ACTIVITY_CACHE.values()))
    return dict(_state)


def reset_state():
    for key in _state:
        _state[key] = 0 if isinstance(_state[key], int) else 0.0
    TERMINAL_ACTIVITY_CACHE.clear()
