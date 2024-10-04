import tkinter as tk
from tkinter import messagebox, filedialog
import os
import threading
from click import Context
from outage_map.find_extreme_cli import FIND_EXTREME, find_extreme
from .util.helper import create_scrollable_frame
import io
import sys

def select_input_path(input_entry):
    input_path = filedialog.askdirectory()
    if input_path:
        input_entry.delete(0, tk.END)
        input_entry.insert(0, input_path)

def run_find_extreme(input_path, status_label, process_button, output_text):
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        if not os.path.exists(input_path):
            status_label.config(text="Error: Invalid input path provided.")
            messagebox.showerror("Error", "Please check the input path and try again.")
            process_button.config(state="normal")
            return

        try:
            input_path_abs = os.path.abspath(input_path)
            original_cwd = os.getcwd()

            os.chdir(input_path_abs)

            output_buffer = io.StringIO()
            sys.stdout = output_buffer

            ctx = Context(FIND_EXTREME)
            ctx.invoke(find_extreme, input_path=input_path_abs)

            sys.stdout = sys.__stdout__

            output_text.delete(1.0, tk.END)
            output_text.insert(tk.END, output_buffer.getvalue())

            os.chdir(original_cwd)

            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "Extreme weather feature values processed successfully! 🎉")
        except Exception as e:
            os.chdir(original_cwd)
            sys.stdout = sys.__stdout__
            status_label.config(text="Error: Processing failed.")
            messagebox.showerror("Error", f"Oops! Something went wrong: {str(e)}")
        finally:
            process_button.config(state="normal")

    threading.Thread(target=process_files).start()

def create_tab4(notebook):
    tab1 = tk.Frame(notebook)
    notebook.add(tab1, text='Find Extreme Weather Features')

    _, scrollable_frame = create_scrollable_frame(tab1)

    input_label = tk.Label(scrollable_frame, text="Select Input Path (Weather Data):")
    input_label.pack(pady=10)

    input_entry = tk.Entry(scrollable_frame, width=50)
    input_entry.pack(pady=5)

    input_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_input_path(input_entry))
    input_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=5)

    output_text = tk.Text(scrollable_frame, height=10, width=80)
    output_text.pack(pady=10)

    process_button = tk.Button(scrollable_frame, text="Find Extreme Weather Features", 
                               command=lambda: run_find_extreme(input_entry.get(), status_label, process_button, output_text))
    process_button.pack(pady=20)

    return tab1
