import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import platform
from tkinter import ttk
from click import Context

from .util.helper import create_scrollable_frame, select_directory, weather_features_dict
from outage_map.generate_weather_impact_cli import GENERATE_WEATHER_IMPACT, generate_weather_impact

AVAILABLE_WEATHER_FEATURES = list(weather_features_dict.keys())

def add_feature(parent, feature_list_container, node_feature_container, edge_feature_container, enable_button, add_node_feature_button, add_edge_feature_button):
    frame = tk.Frame(parent)

    feature_label = tk.Label(frame, text="Name:")
    feature_label.pack(side="left", padx=5)

    feature_dropdown = ttk.Combobox(frame, values=AVAILABLE_WEATHER_FEATURES, state="readonly")
    feature_dropdown.pack(side="left", padx=5)
    feature_dropdown.current(0)

    min_label = tk.Label(frame, text="Min Value:")
    min_label.pack(side="left", padx=5)

    min_entry = tk.Entry(frame, width=5)
    min_entry.pack(side="left", padx=5)

    max_label = tk.Label(frame, text="Max Value:")
    max_label.pack(side="left", padx=5)

    max_entry = tk.Entry(frame, width=5)
    max_entry.pack(side="left", padx=5)

    frame.pack(pady=5)
    feature_list_container.append((feature_dropdown, min_entry, max_entry))

    clear_node_edge_features(node_feature_container, edge_feature_container)
    add_node_feature_button.config(state="disabled")
    add_edge_feature_button.config(state="disabled")
    enable_button.config(state="normal")

def get_features_from_container(feature_list_container):
    feature_list = []
    for entry in feature_list_container:
        feature_name = entry[0].get()
        min_value = entry[1].get()
        max_value = entry[2].get()

        if not feature_name or not min_value or not max_value:
            messagebox.showerror("Error", "Feature name, min, and max values cannot be empty.")
            return None
        try:
            min_value = int(min_value)
            max_value = int(max_value)
        except ValueError:
            messagebox.showerror("Error", "Min and Max values must be integers.")
            return None

        # Map the full feature name to its abbreviation
        feature_abbr = weather_features_dict[feature_name]

        feature_list.append((feature_abbr, min_value, max_value))

    return feature_list if len(feature_list) > 0 else None

def add_node_edge_feature(parent, container, num_values, feature_type="Node"):
    frame = tk.Frame(parent)

    feature_label = tk.Label(frame, text=f"{feature_type} Physical Feature Name:")
    feature_label.pack(side="left", padx=5)

    feature_entry = tk.Entry(frame, width=10)
    feature_entry.pack(side="left", padx=5)

    value_entries = []
    for i in range(num_values):
        value_label = tk.Label(frame, text=f"Value {i+1}:")
        value_label.pack(side="left", padx=5)

        value_entry = tk.Entry(frame, width=5)
        value_entry.pack(side="left", padx=5)
        value_entries.append(value_entry)

    frame.pack(pady=5)
    container.append((feature_entry, value_entries))

def get_node_edge_features_from_container(feature_container):
    feature_list = []
    for feature_entry, value_entries in feature_container:
        feature_name = feature_entry.get()
        if not feature_name:
            messagebox.showerror("Error", "Feature name cannot be empty.")

        values = []
        try:
            for entry in value_entries:
                value = entry.get()
                if not value:
                    messagebox.showerror("Error", "All value fields must be filled.")
                    return None
                values.append(float(value))

            if not abs(sum(values) - 1.0) < 1e-6:
                messagebox.showerror("Error", f"Values for {feature_name} must sum to 1.")
                return None

        except ValueError:
            messagebox.showerror("Error", "All values must be numeric.")
            return None

        feature_list.append((feature_name, values))

    return feature_list if len(feature_list) > 0 else None

def check_duplicate_features(feature_list_container):
    feature_names = [entry[0].get() for entry in feature_list_container]
    return len(feature_names) != len(set(feature_names))

def clear_node_edge_features(node_feature_container, edge_feature_container):
    for widget in node_feature_container:
        widget[0].master.destroy()
    for widget in edge_feature_container:
        widget[0].master.destroy()

    node_feature_container.clear()
    edge_feature_container.clear()

def enable_node_edge_features(node_feature_container, edge_feature_container, feature_list_container, scrollable_frame, canvas, add_node_feature_button, add_edge_feature_button, add_feature_button):
    if check_duplicate_features(feature_list_container):
        messagebox.showerror("Error", "Duplicate feature names found. Please ensure all feature names are unique.")
        return

    clear_node_edge_features(node_feature_container, edge_feature_container)

    add_node_feature_button.config(state="normal")
    add_edge_feature_button.config(state="normal")
    add_feature_button.config(state="disabled")

    scrollable_frame.update_idletasks()
    canvas.config(scrollregion=canvas.bbox("all"))

def reset_all(feature_list_container, node_feature_container, edge_feature_container, add_feature_button, add_node_feature_button, add_edge_feature_button, enable_button, input_entry, output_entry, status_label):
    clear_node_edge_features(node_feature_container, edge_feature_container)

    for entry in feature_list_container:
        entry[0].master.destroy()

    feature_list_container.clear()

    add_feature_button.config(state="normal")
    add_node_feature_button.config(state="disabled")
    add_edge_feature_button.config(state="disabled")
    enable_button.config(state="disabled")

    input_entry.delete(0, tk.END)
    output_entry.delete(0, tk.END)
    status_label.config(text="")

def run_generate_weather_impact(feature_list_container, input_path, node_feature_container, edge_feature_container, output_path, status_label, process_button):
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        feature_list = get_features_from_container(feature_list_container)
        if feature_list is None:
            status_label.config(text="Error: Invalid feature entries.")
            process_button.config(state="normal")
            return

        node_features = get_node_edge_features_from_container(node_feature_container)
        edge_features = get_node_edge_features_from_container(edge_feature_container)
        if node_features is None or edge_features is None:
            status_label.config(text="Error: Invalid node or edge feature entries.")
            process_button.config(state="normal")
            return

        if not os.path.exists(input_path):
            status_label.config(text="Error: Input directory does not exist.")
            messagebox.showerror("Error", "Please provide a valid input directory.")
            process_button.config(state="normal")
            return

        if not os.path.exists(output_path):
            status_label.config(text="Error: Output directory does not exist.")
            messagebox.showerror("Error", "Please provide a valid output directory.")
            process_button.config(state="normal")
            return

        try:
            ctx = Context(GENERATE_WEATHER_IMPACT)
            ctx.invoke(generate_weather_impact, feature_list=feature_list, input_path=input_path, node_feature=node_features, edge_feature=edge_features, output_path=output_path)

            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "Weather impact generated and saved successfully!")
        except Exception as e:
            status_label.config(text="Error: Failed to generate weather impact.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            process_button.config(state="normal")

    threading.Thread(target=process_files).start()

def create_tab4(notebook):
    tab4 = tk.Frame(notebook)
    notebook.add(tab4, text="Generate Weather Impact")

    canvas, scrollable_frame = create_scrollable_frame(tab4)

    feature_list_container = []

    feature_label = tk.Label(scrollable_frame, text="Feature List:")
    feature_label.pack(pady=5)

    add_feature_button = tk.Button(scrollable_frame, text="Add Weather Feature", 
                                   command=lambda: add_feature(scrollable_frame, feature_list_container, node_feature_container, edge_feature_container, enable_button, add_node_feature_button, add_edge_feature_button))
    add_feature_button.pack(pady=5)

    node_feature_container = []
    edge_feature_container = []

    add_node_feature_button = tk.Button(scrollable_frame, text="Add Node Feature", state="disabled", 
                                        command=lambda: add_node_edge_feature(scrollable_frame, node_feature_container, len(feature_list_container), "Node"))
    add_node_feature_button.pack(pady=5)

    add_edge_feature_button = tk.Button(scrollable_frame, text="Add Edge Feature", state="disabled", 
                                        command=lambda: add_node_edge_feature(scrollable_frame, edge_feature_container, len(feature_list_container), "Edge"))
    add_edge_feature_button.pack(pady=5)

    enable_button = tk.Button(scrollable_frame, text="Enable Node and Edge Features", state="disabled",
                              command=lambda: enable_node_edge_features(node_feature_container, edge_feature_container, feature_list_container, scrollable_frame, canvas, add_node_feature_button, add_edge_feature_button, add_feature_button))
    enable_button.pack(pady=5)

    input_label = tk.Label(scrollable_frame, text="Select Input Directory to the Folder Containing Weather Feature Folders:")
    input_label.pack(pady=5)

    input_entry = tk.Entry(scrollable_frame, width=50)
    input_entry.pack(pady=5)

    input_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_directory(input_entry))
    input_button.pack(pady=5)

    output_label = tk.Label(scrollable_frame, text="Select Output Directory:")
    output_label.pack(pady=5)

    output_entry = tk.Entry(scrollable_frame, width=50)
    output_entry.pack(pady=5)

    output_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_directory(output_entry))
    output_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=10)

    process_button = tk.Button(scrollable_frame, text="Generate Weather Impact",
                               command=lambda: run_generate_weather_impact(
                                   feature_list_container,
                                   input_entry.get(),
                                   node_feature_container,
                                   edge_feature_container,
                                   output_entry.get(),
                                   status_label,
                                   process_button
                               ))
    process_button.pack(pady=20)

    reset_button = tk.Button(scrollable_frame, text="Reset", 
                             command=lambda: reset_all(feature_list_container, node_feature_container, edge_feature_container, add_feature_button, add_node_feature_button, add_edge_feature_button, enable_button, input_entry, output_entry, status_label))
    reset_button.pack(pady=10)

    return tab4
