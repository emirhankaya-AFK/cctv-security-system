# Smart CCTV Security and Zone Intrusion Alerts

[English](README.md) | [Türkçe](README_TR.md)

A real-time security application that monitors a webcam or video file, detects objects with YOLOv8, and sends a Telegram alert with a captured image when an object enters a user-defined polygonal restricted zone.

## Features

- Interactive restricted-zone drawing and editing
- YOLOv8 object detection
- Polygon intrusion checks with OpenCV
- Asynchronous Telegram photo and message alerts
- Local storage of alert frames

## Setup

```bash
pip install ultralytics opencv-python requests numpy
```

Copy `config.example.json` to `config.json`, then add your Telegram bot token, chat ID, model path, and preferred settings. Keep `config.json` private.

## Run

```bash
python main.py
```

Use the mouse to define the restricted area. Press `c` to clear it, `s` or `Enter` to save it, `r` to redraw it, and `q` to quit.

