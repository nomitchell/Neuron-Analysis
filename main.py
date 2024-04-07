import tkinter as tk
from tkinter import ttk
from classify import Classify
import warnings
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as pd
from utils import Utils
from tkinter import filedialog
import scipy

class CSVViewerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Marker Tool")
        self.master.geometry("800x600")

        self.file_path = None

        self.label = tk.Label(self.master, text="1: Choose a csv file with expression data.", font=("Arial", 18))
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
        
        self.button_save = tk.Button(self.master, text="Save as CSV File", command=self.save_csv)
        self.button_save.pack_forget()


    def open_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv"), ("MTX files", "*.mtx")])
        if file_path:
            self.file_path = file_path
            
            if '.csv' in self.file_path:
                self.display_csv()
            elif '.mtx' in self.file_path:
                self.display_mtx()
            self.show_hidden_button()
        self.label.config(text="2: Confirm data, and press analyze.")

        self.button.pack_forget()

    def display_mtx(self):
        print(1)
        cell_path = filedialog.askopenfilename(filetypes=[("Cell CSV files", "*.csv")])
        if cell_path:
            self.cell_path = cell_path
        else:
            raise Exception("Choose a file")

        feature_path = filedialog.askopenfilename(filetypes=[("Feature CSV files", "*.csv")])
        if feature_path:
            self.feature_path = feature_path
        else:
            raise Exception("Choose a file")
        
        self.label.config(text='Opening File', font=("Arial", 18))
        df = scipy.io.mmread(self.file_path)
        self.label.config(text='Loading File', font=("Arial", 18))
        df = pd.DataFrame.sparse.from_spmatrix(df).T
        ft = pd.read_csv(self.feature_path)
        cells = pd.read_csv(self.cell_path)
        self.label.config(text='Processing Data', font=("Arial", 18))
        df.columns = ft.iloc[:, 0].values
        with open('resources/features.txt', 'r') as f:
            features = f.readlines()
            features = [i.replace('\n', '') for i in features]
        df = df[df.columns.intersection(features)]
        self.label.config(text='Normalizing Data', font=("Arial", 18))
        df = Utils.normalize(df)
        self.label.config(text='Done Normalization', font=("Arial", 18))
        df = df.reindex(columns=features).fillna(0)
        df.insert(0, "cell", cells['cells'].values)
        self.df = df

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

    def display_csv(self):
        # Read CSV file into pandas DataFrame
        self.df = pd.read_csv(self.file_path)

        #self.label.config(text='Normalizing Data', font=("Arial", 18))
        #normalized_data = Utils.normalize(self.df.iloc[:, 1:])

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

        self.label.config(text='3: Results\nDisplayed as "Marker:Unique" score, with unique score representing the number of classes it is a part of.', font=("Arial", 12))
        self.button_save.pack(side="bottom", pady=10)
        self.button_analyze.pack_forget()

    def save_csv(self):
        data = []

        file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])

        for child in self.table.get_children():
            values = self.table.item(child)["values"]
            data.append(values)

        df = pd.DataFrame(data, columns=["ID", "Class", "Wilcox Markers", "Auroc Markers"])

        try:
            df.to_csv(file_path)
            self.label.config(text='CSV Saved Succesfully', font=("Arial", 18))
        except:
            self.label.config(text='CSV Save Fail', font=("Arial", 18))

def main():
    root = tk.Tk()
    root.tk.call('source', 'resources/forest-light.tcl')
    ttk.Style().theme_use('forest-light')
    app = CSVViewerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
