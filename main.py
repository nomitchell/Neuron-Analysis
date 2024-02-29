import PySimpleGUI as sg
import numpy as np
from classify import classify
import pickle
import warnings
# To stop pandas from giving warning about next release dependency
warnings.simplefilter(action='ignore', category=DeprecationWarning)
import pandas as pd

print("Main libraries loaded")

sg.theme('DarkAmber')

# Empty data for initializing the table
data = [[]]

# Default window layout
layout = [[sg.Text("Select a file to open:")],
         [sg.Input(key="FILE_PATH", enable_events=True), sg.FileBrowse()],
         [sg.Table(data, key="TABLE", headings=[], auto_size_columns=True, display_row_numbers=False)]]

# Loads a dictionary that maps class name to known markers
with open('markers.pkl', 'rb') as f:
    markers = pickle.load(f)
    print("Markers loaded")

# Window for selecting data
window = sg.Window('Select Data', layout)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel':
        print("Program terminated")
        break
    elif event == "FILE_PATH":
        fp = values["FILE_PATH"]
        print("File", fp, "loaded")

        # Round the values since they can be large, high precision not important when displaying visually
        tmpData = pd.read_csv(fp).round(6)
        data = tmpData.iloc[0:, :10].values.tolist()

        # Build layout again since the data variable based to table has changed
        layout2 = [[sg.Text("Select a file to open:")],
                    [sg.Input(key="FILE_PATH", enable_events=True), sg.FileBrowse()],
                    [sg.Table(data, key="TABLE", headings=tmpData.columns.values.tolist()[:10])],
                    [sg.Button("Classify", key="CLASSIFY")],]
        
        # Switch to next window displaying the updated table
        window.close()
        window = sg.Window('File Display', layout2)
    elif event == "CLASSIFY":
        # Assuming the data is set up in a certain way, we want all the rows, but not the first column since it contains ids
        cData = tmpData.iloc[:, 1:].values
        
        # Instantiate and initialize the classifier
        classifier = classify()
        preds = classifier.predict(cData)
        print("Predictions returned")
        
        # Add results to a list of lists, so that it can be passed into a new table
        results = [[tmpData.iloc[i, 0], [preds[i]], markers[preds[i]][0], markers[preds[i]][1]] for i in range(len(preds))]
        
        # Another layout to display the new table information
        layout3 = [[sg.Text("Labelled cell results:")],
                  [sg.Table(results, key="TABLE_RESULTS", headings=["ID", "Class", "Wilcox Markers", "AUROC Markers"], auto_size_columns=True, row_height=30, display_row_numbers=False)],]
        
        # Switch to final screen. Todo add option to return to beginning
        window.close()
        window = sg.Window('Results', layout3)
        
window.close()