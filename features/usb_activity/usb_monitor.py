# features/usb_activity/usb_monitor.py

import os
import datetime
import psutil
from pathlib import Path

# Конфигурация
USB_BLACKLIST = ["Kingston_Hack", "EvilCorp_USB"]
WORK_HOURS = (8, 18)
EXECUTABLE_EXTENSIONS = [".exe", ".bat", ".cmd", ".msi"]
ENCRYPTED_VOLUME_HINTS = ["BitLocker", "VeraCrypt"]

_state = {
    "usb_devices_connected": 0,
    "usb_vendor_blacklisted": 0,
    "usb_file_copy_count": 0,
    "usb_copy_volume_MB": 0.0,
    "usb_executable_found": 0,
    "usb_encrypted_volume_found": 0,
    "usb_access_outside_hours": 0
}

def collect_usb_features():
    reset_state()
    now = datetime.datetime.now()
    hour = now.hour

    usb_partitions = [p for p in psutil.disk_partitions(all=False) if 'removable' in p.opts.lower() or 'usb' in p.device.lower()]
    _state["usb_devices_connected"] = len(usb_partitions)

    for part in usb_partitions:
        vendor = os.path.basename(part.device).strip()

        if vendor in USB_BLACKLIST:
            _state["usb_vendor_blacklisted"] = 1

        if hour < WORK_HOURS[0] or hour >= WORK_HOURS[1]:
            _state["usb_access_outside_hours"] = 1

        try:
            root = Path(part.mountpoint)
            file_count = 0
            total_size = 0
            for file in root.rglob("*"):
                if not file.is_file():
                    continue
                file_count += 1
                total_size += file.stat().st_size
                if file.suffix.lower() in EXECUTABLE_EXTENSIONS:
                    _state["usb_executable_found"] = 1
                if any(enc in file.name.lower() for enc in ENCRYPTED_VOLUME_HINTS):
                    _state["usb_encrypted_volume_found"] = 1

            _state["usb_file_copy_count"] += file_count
            _state["usb_copy_volume_MB"] += round(total_size / 1024 / 1024, 2)

        except Exception:
            continue

    return dict(_state)


def reset_state():
    for key in _state:
        _state[key] = 0 if isinstance(_state[key], (int, float)) else ""
