import tkinter as tk
from tkinter import ttk
from classify import Classify
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as pd
from utils import Utils
from tkinter import filedialog

class CSVViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("CSV Viewer")
        self.master.geometry("800x600")

        self.file_path = None

        self.label = tk.Label(self.master, text="CSV Viewer", font=("Arial", 18))
        self.label.pack(pady=10)

        self.table = ttk.Treeview(self.master)
        self.table["columns"] = tuple(f"Column_{i}" for i in range(1, 2))
        self.table.pack(expand=True, fill="both", padx=10, pady=10)

        for col in self.table["columns"]:
            self.table.heading(col, text=col)
            self.table.column(col, width=80, stretch=tk.YES)

        self.button = tk.Button(self.master, text="Open CSV File", command=self.open_csv)
        self.button.pack(side="bottom", pady=10)

        self.button_analyze = tk.Button(self.master, text="Analyze", command=self.display_analyze)
        
        self.button_analyze.pack_forget()

        self.xscrollbar = ttk.Scrollbar(self.master, orient="horizontal", command=self.table.xview)
        self.xscrollbar.pack(side="bottom", fill="x")

        self.table2 = ttk.Treeview(self.master)

        self.markers = Utils.loadMarkers()


    def open_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.file_path = file_path
            self.display_csv()
            self.show_hidden_button()

    def display_csv(self):
        # Read CSV file into pandas DataFrame
        self.df = pd.read_csv(self.file_path)

        # Extract the first 10 columns from the DataFrame
        df_first_10 = self.df.iloc[:, :10]

        # Set column names for Treeview widget
        columns = df_first_10.columns
        self.table["columns"] = columns

        for i in self.table["columns"]:
            self.table.heading(i, text=i)

        self.table["show"] = "headings"

        self.table.configure(xscrollcommand=self.xscrollbar.set)

        # Insert data rows into the Treeview widget
        for i, row in df_first_10.iterrows():
            row_values = tuple(row)
            self.table.insert("", "end", values=row_values)
    
    def show_hidden_button(self):
        self.button_analyze.pack(side="bottom", pady=10)

    def classify(self):
        cData = self.df.iloc[:, 1:].values
        
        # Instantiate and initialize the classifier
        classifier = Classify()
        preds = classifier.predict(cData)
        print("Predictions returned")


        # Add results to a list of lists, so that it can be passed into a new table
        results = [[self.df.iloc[i, 0], [preds[i]], self.markers[preds[i]][0], self.markers[preds[i]][1]] for i in range(len(preds))]

        return results
        
    def display_analyze(self):
        columns = ("ID", "Class", "Wilcox Markers", "AUROC Markers")
        
        results = self.classify()

        self.table.delete(*self.table.get_children())
        for col in self.table["columns"]:
            self.table.heading(col, text="")
        self.table["columns"] = columns

        for i in self.table["columns"]:
            self.table.heading(i, text=i)

        for row in results:
            row_values = tuple(row)
            self.table.insert("", "end", values=row_values)

        self.table.config(wrap="word")


def main():
    root = tk.Tk()
    root.tk.call('source', 'forest-light.tcl')
    ttk.Style().theme_use('forest-light')
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
