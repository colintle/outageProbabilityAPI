import tkinter as tk
from tkinter import filedialog, messagebox
import os
import threading
import platform
from click import Context

from .util.helper import select_directory, create_scrollable_frame
from outage_map.generate_outage_map_cli import GENERATE_OUTAGE_MAP, generate_outage_map

def add_feature_entry(parent, feature_container, feature_type):
    frame = tk.Frame(parent)

    feature_label = tk.Label(frame, text=f"{feature_type} Feature:")
    feature_label.pack(side="left", padx=5)
    feature_entry = tk.Entry(frame, width=10)
    feature_entry.pack(side="left", padx=5)

    mean_min_label = tk.Label(frame, text="Mean Min:")
    mean_min_label.pack(side="left", padx=5)
    mean_min_entry = tk.Entry(frame, width=5)
    mean_min_entry.pack(side="left", padx=5)

    mean_max_label = tk.Label(frame, text="Mean Max:")
    mean_max_label.pack(side="left", padx=5)
    mean_max_entry = tk.Entry(frame, width=5)
    mean_max_entry.pack(side="left", padx=5)

    std_min_label = tk.Label(frame, text="Std Min:")
    std_min_label.pack(side="left", padx=5)
    std_min_entry = tk.Entry(frame, width=5)
    std_min_entry.pack(side="left", padx=5)

    std_max_label = tk.Label(frame, text="Std Max:")
    std_max_label.pack(side="left", padx=5)
    std_max_entry = tk.Entry(frame, width=5)
    std_max_entry.pack(side="left", padx=5)

    entry_tuple = (feature_entry, mean_min_entry, mean_max_entry, std_min_entry, std_max_entry)

    remove_button = tk.Button(frame, text="Remove", command=lambda: remove_feature_entry(frame, feature_container, entry_tuple))
    remove_button.pack(side="left", padx=5)

    frame.pack(pady=5)
    
    feature_container.append(entry_tuple)

def remove_feature_entry(frame, feature_container, entry_tuple):
    frame.destroy()
    feature_container.remove(entry_tuple)

def get_features_from_container(feature_container):
    features = []
    for entry in feature_container:
        feature_name = entry[0].get()
        mean_min = entry[1].get()
        mean_max = entry[2].get()
        std_min = entry[3].get()
        std_max = entry[4].get()

        if not feature_name or not mean_min or not mean_max or not std_min or not std_max:
            messagebox.showerror("Error", "Node and/or Edge feature fields must be filled.")
            return None

        try:
            mean_min = float(mean_min)
            mean_max = float(mean_max)
            std_min = float(std_min)
            std_max = float(std_max)
        except ValueError:
            messagebox.showerror("Error", "Mean and Std values must be numbers.")
            return None

        features.append((feature_name, mean_min, mean_max, std_min, std_max))
    return features if len(features) > 0 else None

def run_generate_outage_map(node_feature_container, edge_feature_container, list_folders, datasets, status_label, process_button):
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        node_features = get_features_from_container(node_feature_container)
        edge_features = get_features_from_container(edge_feature_container)

        if node_features is None or edge_features is None:
            status_label.config(text="Error: Invalid node or edge feature entries.")
            process_button.config(state="normal")
            return

        if not os.path.exists(list_folders) or not os.path.exists(datasets):
            messagebox.showerror("Error", "Invalid directory paths.")
            process_button.config(state="normal")
            return

        try:
            ctx = Context(GENERATE_OUTAGE_MAP)
            ctx.invoke(generate_outage_map, node_feature=node_features, edge_feature=edge_features, list_folders=list_folders, datasets=datasets)

            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "Outage map generated successfully!")
        except Exception as e:
            status_label.config(text="Error: Failed to generate outage map.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            process_button.config(state="normal")

    threading.Thread(target=process_files).start()

# Create GUI for Tab 6
def create_tab6(notebook):
    tab5 = tk.Frame(notebook)
    notebook.add(tab5, text='Generate Outage Map')

    _, scrollable_frame = create_scrollable_frame(tab5)

    node_feature_container = []
    edge_feature_container = []

    node_features_label = tk.Label(scrollable_frame, text="Node Features:")
    node_features_label.pack(pady=10)

    add_node_feature_button = tk.Button(scrollable_frame, text="Add Node Feature", command=lambda: add_feature_entry(scrollable_frame, node_feature_container, "Node"))
    add_node_feature_button.pack(pady=5)

    edge_features_label = tk.Label(scrollable_frame, text="Edge Features:")
    edge_features_label.pack(pady=10)

    add_edge_feature_button = tk.Button(scrollable_frame, text="Add Edge Feature", command=lambda: add_feature_entry(scrollable_frame, edge_feature_container, "Edge"))
    add_edge_feature_button.pack(pady=5)

    list_folders_label = tk.Label(scrollable_frame, text="Select List Folder where each folder is a distribution network.")
    list_folders_label.pack(pady=10)

    list_folders_entry = tk.Entry(scrollable_frame, width=50)
    list_folders_entry.pack(pady=5)

    list_folders_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_directory(list_folders_entry))
    list_folders_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=10)

    datasets_label = tk.Label(scrollable_frame, text="Select Folder to store datasets.hdf5:")
    datasets_label.pack(pady=10)

    datasets_entry = tk.Entry(scrollable_frame, width=50)
    datasets_entry.pack(pady=5)

    datasets_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_directory(datasets_entry))
    datasets_button.pack(pady=5)

    process_button = tk.Button(scrollable_frame, text="Generate Outage Map",
                               command=lambda: run_generate_outage_map(
                                   node_feature_container,
                                   edge_feature_container,
                                   list_folders_entry.get(),
                                   datasets_entry.get(),
                                   status_label,
                                   process_button
                               ))
    process_button.pack(pady=20)

    return tab5
