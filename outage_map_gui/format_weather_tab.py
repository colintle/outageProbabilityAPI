import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import pandas as pd
from click import Context

from outage_map.format_weather_cli import FORMAT_WEATHER, format_weather
from .util.helper import create_scrollable_frame, weather_features_dict, select_directory

def select_file(entry, filetypes=[("CSV Files", "*.csv")]):
    file_path = filedialog.askopenfilename(filetypes=filetypes)
    if file_path:
        entry.delete(0, tk.END)
        entry.insert(0, file_path)

def run_format_weather(events_file, nodelist, edgelist, output_path, features, status_label, process_button):
    total_events = pd.read_csv(events_file).shape[0]
    
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        if not events_file or not os.path.exists(events_file):
            status_label.config(text="Error: Events file path is invalid.")
            messagebox.showerror("Error", "Please provide a valid events file path.")
            process_button.config(state="normal")
            return

        if not nodelist or not os.path.exists(nodelist):
            status_label.config(text="Error: Nodelist file path is invalid.")
            messagebox.showerror("Error", "Please provide a valid nodelist file path.")
            process_button.config(state="normal")
            return

        if not edgelist or not os.path.exists(edgelist):
            status_label.config(text="Error: Edgelist file path is invalid.")
            messagebox.showerror("Error", "Please provide a valid edgelist file path.")
            process_button.config(state="normal")
            return

        if not output_path or not os.path.exists(output_path):
            status_label.config(text="Error: Output directory does not exist.")
            messagebox.showerror("Error", "Please provide a valid output directory.")
            process_button.config(state="normal")
            return

        if not features:
            status_label.config(text="Error: No features selected.")
            messagebox.showerror("Error", "Please select at least one weather feature.")
            process_button.config(state="normal")
            return

        try:
            ctx = Context(FORMAT_WEATHER)
            ctx.invoke(format_weather, events_file=events_file, nodelist=nodelist, edgelist=edgelist, output_path=output_path, features=features)
            
            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "Weather features formatted and saved successfully!")
        except Exception as e:
            status_label.config(text="Error: Failed to format weather features.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            process_button.config(state="normal")

    def check_progress():
        csv_count = 0
        for feature in features:
            node_dir = os.path.join(output_path, f'{feature}/nodes/')
            csv_count += len([f for f in os.listdir(node_dir) if f.endswith(".csv")])

        progress = (csv_count / total_events) * 100
        status_label.config(text=f"Processing: {csv_count} of {total_events} events completed ({progress:.2f}%)")

        if csv_count < total_events:
            status_label.after(1000, check_progress)

    threading.Thread(target=process_files).start()

    check_progress()

def create_tab3(notebook):
    tab3 = tk.Frame(notebook)
    notebook.add(tab3, text='Format Weather Events')

    _, scrollable_frame = create_scrollable_frame(tab3)

    events_file_label = tk.Label(scrollable_frame, text="Select Events CSV File:")
    events_file_label.pack(pady=5)

    events_file_entry = tk.Entry(scrollable_frame, width=50)
    events_file_entry.pack(pady=5)

    events_file_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_file(events_file_entry))
    events_file_button.pack(pady=5)

    nodelist_label = tk.Label(scrollable_frame, text="Select Nodelist CSV File:")
    nodelist_label.pack(pady=5)

    nodelist_entry = tk.Entry(scrollable_frame, width=50)
    nodelist_entry.pack(pady=5)

    nodelist_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_file(nodelist_entry))
    nodelist_button.pack(pady=5)

    edgelist_label = tk.Label(scrollable_frame, text="Select Edgelist CSV File:")
    edgelist_label.pack(pady=5)

    edgelist_entry = tk.Entry(scrollable_frame, width=50)
    edgelist_entry.pack(pady=5)

    edgelist_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_file(edgelist_entry))
    edgelist_button.pack(pady=5)

    feature_label = tk.Label(scrollable_frame, text="Select Weather Features (required):")
    feature_label.pack(pady=5)

    features_listbox = tk.Listbox(scrollable_frame, selectmode="multiple", height=8)
    for feature_full_name in weather_features_dict.keys():
        features_listbox.insert(tk.END, feature_full_name)
    features_listbox.pack(pady=5)

    output_label = tk.Label(scrollable_frame, text="Select Output Directory:")
    output_label.pack(pady=5)

    output_entry = tk.Entry(scrollable_frame, width=50)
    output_entry.pack(pady=5)

    output_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_directory(output_entry))
    output_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=10)

    process_button = tk.Button(
        scrollable_frame,
        text="Format Weather Events",
        command=lambda: run_format_weather(
            events_file_entry.get(),
            nodelist_entry.get(),
            edgelist_entry.get(),
            output_entry.get(),
            [weather_features_dict[features_listbox.get(i)] for i in features_listbox.curselection()],
            status_label,
            process_button
        )
    )
    process_button.pack(pady=20)

    return tab3
