import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
from click import Context

from .util.helper import create_scrollable_frame
from outage_map.import_dss_cli import IMPORT_DSS, import_dss

def select_input_path(input_entry):
    input_path = filedialog.askdirectory()
    if input_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, input_path)

def select_output_path(output_entry):
    output_path = filedialog.askdirectory()
    if output_path:
        output_entry.delete(0, tk.END)
        output_entry.insert(0, output_path)

def run_import_dss(input_path, output_path, status_label, process_button):
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        if not os.path.exists(input_path) or not os.path.exists(output_path):
            status_label.config(text="Error: Invalid paths provided.")
            messagebox.showerror("Error", "Please check the paths and try again. Both input and output directories must be valid.")
            process_button.config(state="normal")  # Re-enable the button if paths are invalid
            return

        try:
            input_path_abs = os.path.abspath(input_path)
            output_path_abs = os.path.abspath(output_path)

            original_cwd = os.getcwd()

            os.chdir(input_path_abs)

            ctx = Context(IMPORT_DSS)
            ctx.invoke(import_dss, input_path=input_path_abs, output_path=output_path_abs)

            os.chdir(original_cwd)

            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "DSS files processed and saved successfully! 🎉")
        except Exception as e:
            os.chdir(original_cwd)
            status_label.config(text="Error: Processing failed.")
            messagebox.showerror("Error", f"Oops! Something went wrong: {str(e)}")
        finally:
            process_button.config(state="normal")

    threading.Thread(target=process_files).start()

def create_tab1(notebook):
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text='Import DSS Files')

    _, scrollable_frame = create_scrollable_frame(tab1)

    input_label = tk.Label(scrollable_frame, text="Select Input Path (DSS Files):")
    input_label.pack(pady=10)

    input_entry = tk.Entry(scrollable_frame, width=50)
    input_entry.pack(pady=5)

    input_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_input_path(input_entry))
    input_button.pack(pady=5)

    output_label = tk.Label(scrollable_frame, text="Select Output Path (CSV Files):")
    output_label.pack(pady=10)

    output_entry = tk.Entry(scrollable_frame, width=50)
    output_entry.pack(pady=5)

    output_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_output_path(output_entry))
    output_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=5)

    process_button = tk.Button(scrollable_frame, text="Process DSS Files", 
                               command=lambda: run_import_dss(input_entry.get(), output_entry.get(), status_label, process_button))
    process_button.pack(pady=20)

    return tab1
