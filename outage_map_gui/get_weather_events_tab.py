import tkinter as tk
from tkinter import messagebox, filedialog, Toplevel
from tkcalendar import Calendar
import os
import threading
import platform
from click import Context

from .util.helper import create_scrollable_frame
from outage_map.get_weather_events_cli import GET_WEATHER_EVENTS, get_weather_events, state_fips, events

def select_nodelist_file(entry):
    nodelist_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
    if nodelist_path:
        entry.delete(0, tk.END)
        entry.insert(0, nodelist_path)

def select_output_path(entry):
    output_path = filedialog.askdirectory()
    if output_path:
        entry.delete(0, tk.END)
        entry.insert(0, output_path)

def open_calendar(entry):
    def on_date_selected():
        selected_date = cal.get_date()
        entry.delete(0, tk.END)
        entry.insert(0, selected_date)
        cal_window.destroy()

    cal_window = Toplevel()
    cal_window.grab_set()
    cal = Calendar(cal_window, selectmode='day', date_pattern='yyyy-mm-dd')
    cal.pack(pady=10)
    select_button = tk.Button(cal_window, text="Select", command=on_date_selected)
    select_button.pack(pady=5)

def run_get_weather_events(state, event_choices, nodelist, county, start_date, end_date, output_path, status_label, process_button):
    def process_files():
        process_button.config(state="disabled")
        status_label.config(text="Processing...")

        if not event_choices:
            status_label.config(text="Error: No event types selected.")
            messagebox.showerror("Error", "Please select at least one event type.")
            process_button.config(state="normal")
            return

        if not start_date or not end_date:
            status_label.config(text="Error: Start and End dates are required.")
            messagebox.showerror("Error", "Please provide both start and end dates.")
            process_button.config(state="normal")
            return

        if not ((state and county) or nodelist):
            status_label.config(text="Error: Please provide either a state and county or a nodelist.")
            messagebox.showerror("Error", "You must provide either a state and county or a nodelist.")
            process_button.config(state="normal")
            return

        if not os.path.exists(output_path):
            status_label.config(text="Error: Output path does not exist.")
            messagebox.showerror("Error", "Please provide a valid output path.")
            process_button.config(state="normal")
            return

        try:
            ctx = Context(GET_WEATHER_EVENTS)
            ctx.invoke(
                get_weather_events,
                state=state if state else None,
                events=event_choices,
                nodelist=nodelist if nodelist else None,
                county=county if county else None,
                start_date=start_date,
                end_date=end_date,
                output_path=os.path.join(output_path, 'weather_events.csv')
            )

            status_label.config(text="Completed!")
            messagebox.showinfo("Success", "Weather events retrieved and saved successfully!")
        except Exception as e:
            status_label.config(text="Error: Failed to retrieve weather events.")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
        finally:
            process_button.config(state="normal")

    threading.Thread(target=process_files).start()

def create_tab2(notebook):
    tab2 = tk.Frame(notebook)
    notebook.add(tab2, text='Get Weather Events')

    _, scrollable_frame = create_scrollable_frame(tab2)

    event_label = tk.Label(scrollable_frame, text="Select Event Types (required):")
    event_label.pack(pady=5)

    event_listbox = tk.Listbox(scrollable_frame, selectmode="multiple", height=8)
    for event in events:
        event_listbox.insert(tk.END, event)
    event_listbox.pack(pady=5)

    state_label = tk.Label(scrollable_frame, text="Select State (optional):")
    state_label.pack(pady=5)

    state_var = tk.StringVar()
    state_dropdown = tk.OptionMenu(scrollable_frame, state_var, "None", *list(state_fips.keys()))
    state_var.set("None")
    state_dropdown.pack(pady=5)

    county_label = tk.Label(scrollable_frame, text="Enter County (optional):")
    county_label.pack(pady=5)

    county_entry = tk.Entry(scrollable_frame, width=50)
    county_entry.pack(pady=5)

    nodelist_label = tk.Label(scrollable_frame, text="Select Nodelist (optional):")
    nodelist_label.pack(pady=5)

    nodelist_entry = tk.Entry(scrollable_frame, width=50)
    nodelist_entry.pack(pady=5)

    nodelist_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_nodelist_file(nodelist_entry))
    nodelist_button.pack(pady=5)

    start_date_label = tk.Label(scrollable_frame, text="Start Date (YYYY-MM-DD, required):")
    start_date_label.pack(pady=5)

    start_date_entry = tk.Entry(scrollable_frame, width=50)
    start_date_entry.pack(pady=5)

    start_date_button = tk.Button(scrollable_frame, text="Select Start Date", command=lambda: open_calendar(start_date_entry))
    start_date_button.pack(pady=5)

    end_date_label = tk.Label(scrollable_frame, text="End Date (YYYY-MM-DD, required):")
    end_date_label.pack(pady=5)

    end_date_entry = tk.Entry(scrollable_frame, width=50)
    end_date_entry.pack(pady=5)

    end_date_button = tk.Button(scrollable_frame, text="Select End Date", command=lambda: open_calendar(end_date_entry))
    end_date_button.pack(pady=5)

    output_label = tk.Label(scrollable_frame, text="Select Output Path (required):")
    output_label.pack(pady=5)

    output_entry = tk.Entry(scrollable_frame, width=50)
    output_entry.pack(pady=5)

    output_button = tk.Button(scrollable_frame, text="Browse", command=lambda: select_output_path(output_entry))
    output_button.pack(pady=5)

    status_label = tk.Label(scrollable_frame, text="")
    status_label.pack(pady=10)

    process_button = tk.Button(
        scrollable_frame,
        text="Get Weather Events",
        command=lambda: run_get_weather_events(
            state_var.get() if state_var.get() != "None" else None,
            [event_listbox.get(i) for i in event_listbox.curselection()],
            nodelist_entry.get(),
            county_entry.get(),
            start_date_entry.get(),
            end_date_entry.get(),
            output_entry.get(),
            status_label,
            process_button
        )
    )
    process_button.pack(pady=20)

    return tab2
