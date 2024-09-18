import tkinter as tk
from tkinter import filedialog
import platform

weather_features_dict = {
    'Temperature': 'temp',
    'Dew Point': 'dwpt',
    'Relative Humidity': 'rhum',
    'Precipitation': 'prcp',
    'Snowfall': 'snow',
    'Wind Direction': 'wdir',
    'Wind Speed': 'wspd',
    'Wind Gust': 'wpgt',
    'Pressure': 'pres',
    'Sunshine': 'tsun'
}

def select_directory(entry):
    dir_path = filedialog.askdirectory()
    if dir_path:
        entry.delete(0, tk.END)
        entry.insert(0, dir_path)

def on_mouse_wheel(event, canvas):
    if platform.system() == 'Windows':
        canvas.yview_scroll(-1 * (event.delta // 120), "units")
    else:
        canvas.yview_scroll(-1 * (event.delta), "units")

def create_scrollable_frame(parent):
    canvas = tk.Canvas(parent)
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)

    scrollable_frame = tk.Frame(canvas)

    window_id = canvas.create_window((0, 0), window=scrollable_frame, anchor="n")

    def on_resize(event):
        canvas.itemconfig(window_id, width=event.width)

    canvas.bind("<Configure>", on_resize)

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    return canvas, scrollable_frame
