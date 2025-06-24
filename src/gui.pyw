import tkinter as tk
from tkinter import ttk
from record import *
from dotenv import load_dotenv
import os
from pathlib import Path
import threading

class GUI(tk.Tk):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.r = Record(os.getenv('EMOTIVID'), os.getenv('EMOTIVSECRET'))
        current_directory = Path.cwd().as_posix()
        self.r.record_title = '' # required param and can not be empty
        self.r.record_description = 'CLARKSON_UNIVERSITY_REU_PROGRAM_2025' # optional param
    
        # input params for export_record. Please see on_warn_cortex_stop_all_sub()
        self.r.record_export_folder = current_directory # your place to export, you should have write permission, example on desktop
        self.r.record_export_data_types = ['EEG'] # 'MOTION', 'PM', 'BP'
        self.r.record_export_format = 'CSV'
        self.r.record_export_version = 'V2'

        self.title("EEG Data Collection")
        self.geometry("600x400")
        self.row_count = 0 #! The index for adding new rows start at 0
        self.entry_widgets = {}
        self.start_buttons = {}
        self.stop_buttons = {}

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.container = ttk.Frame(self)
        self.container.grid(row=0, column=0)

        ttk.Label(self.container, text="Participant ID/Name").grid(row=0, column=0, padx=10, pady=5)
        ttk.Label(self.container, text="Start").grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(self.container, text="Stop").grid(row=0, column=2, padx=10, pady=5)

        self.rows_frame = ttk.Frame(self.container)
        self.rows_frame.grid(row=1, column=0, columnspan=3)

        self.add_btn = ttk.Button(self.container, text="Add Participant", command=self.add_row)
        self.add_btn.grid(row=2, column=0, columnspan=3, pady=10)

        self.add_row()

    def add_row(self):
        row = self.row_count
        entry = ttk.Entry(self.rows_frame)
        entry.grid(row=row, column=0, padx=10, pady=5)
        self.entry_widgets[row] = entry

        start_btn = ttk.Button(self.rows_frame, text="Start", command=lambda r=row: self.start_recording(r))
        start_btn.grid(row=row, column=1, padx=10, pady=5)
        self.start_buttons[row] = start_btn

        stop_btn = ttk.Button(self.rows_frame, text="Stop", state="disabled", command=lambda r=row: self.stop_recording(r))
        stop_btn.grid(row=row, column=2, padx=10, pady=5)
        self.stop_buttons[row] = stop_btn

        self.row_count += 1

    def start_recording(self, row:int) -> None:
        """Takes the row's entry field's value then starts a recording session using that entry value as the recording title.
            Disables all buttons in the window besides from the same row's stop button

        Args:
            row (int):  The row index of the button that called function.
        """
        try:
            entry_value = self.entry_widgets[row].get()
            if (not entry_value):
                print("Empty Participant ID/Name")
                return
            if not entry_value.isalnum():
                print("Cannot use non-alphanumerical values")
                return

            print(f"Start recording for row {row}, Participant: {entry_value}")

            for r in self.start_buttons:
                self.start_buttons[r]['state'] = 'disabled'
                self.stop_buttons[r]['state'] = 'disabled'
                self.entry_widgets[r]['state'] = 'disabled'

            self.add_btn['state'] = 'disabled'
            self.stop_buttons[row]['state'] = 'normal'
            self.start = time.time()
            self.r.record_title = entry_value
            threading.Thread(target=self.r.start, daemon=True).start()
        except Exception as e:
            print(e)
            
    def stop_recording(self, row:int) -> None:
        """Stops the recording and returns all the buttons in the windows back to normal(besides from stop buttons)
            #! currently, rows do not matter as theres is only 1 record object 
            

        Args:
            row (int):  The row index of the button that called function.
        """
        try:
            entry_value = self.entry_widgets[row].get()
            print('end recording -------------------------')
            print(f"Total Time:{round(time.time()-self.start)}s")
            print(f"Stop recording for row {row}, Participant: {entry_value}")
            self.r.stop_record()
        except Exception as e:
            print(e)
        finally:
            self.add_btn['state'] = 'normal'
            for r in self.start_buttons:
                self.start_buttons[r]['state'] = 'normal'
                self.stop_buttons[r]['state'] = 'disabled'
                self.entry_widgets[r]['state'] = 'normal'

if __name__ == "__main__":
    app = GUI()
    app.mainloop()
