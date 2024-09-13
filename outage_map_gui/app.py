# outagemap_gui/outagemap_gui.py

import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

def main():
    root = tk.Tk()
    root.title("Outage Map GUI")
    root.geometry("800x600")  # Set the window to a larger size

    # Create a notebook (tabs container)
    notebook = ttk.Notebook(root)

    # Create 5 frames for each tab
    tab1 = ttk.Frame(notebook)
    tab2 = ttk.Frame(notebook)
    tab3 = ttk.Frame(notebook)
    tab4 = ttk.Frame(notebook)
    tab5 = ttk.Frame(notebook)

    # Add the frames to the notebook
    notebook.add(tab1, text='Tab 1')
    notebook.add(tab2, text='Tab 2')
    notebook.add(tab3, text='Tab 3')
    notebook.add(tab4, text='Tab 4')
    notebook.add(tab5, text='Tab 5')

    # Pack the notebook to make it visible
    notebook.pack(expand=True, fill='both')

    # Add content to the first tab as an example
    label1 = tk.Label(tab1, text="Welcome to Outage Map GUI! This is Tab 1")
    label1.pack(pady=20)

    button1 = tk.Button(tab1, text="Click Me", command=lambda: messagebox.showinfo("Info", "Button Clicked on Tab 1"))
    button1.pack(pady=5)

    # Add placeholder content to the other tabs
    label2 = tk.Label(tab2, text="This is Tab 2")
    label2.pack(pady=20)

    label3 = tk.Label(tab3, text="This is Tab 3")
    label3.pack(pady=20)

    label4 = tk.Label(tab4, text="This is Tab 4")
    label4.pack(pady=20)

    label5 = tk.Label(tab5, text="This is Tab 5")
    label5.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    main()
