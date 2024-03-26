import torch
import torch.nn as nn
import numpy as np
print("Classify libraries loaded")

class Classify:
    def __init__(self):
        # gpu not needed, runs fast on cpu for inference
        self.device="cpu"
        
        # Create frame for the model, must match the trained model for loading trained weights
        self.model = nn.Sequential(
        nn.Linear(in_features=2000, out_features=256),
        nn.ReLU(),
        nn.Linear(in_features=256, out_features=256),
        nn.ReLU(),
        nn.Linear(in_features=256, out_features=86)
        ).to(self.device)

        # loading the pretrained weights
        self.model.load_state_dict(torch.load("modelBasicV1.pt", map_location=torch.device('cpu')))
        print("Model loaded")

        # this is the names of the possible labels, for mapping number to actual class name
        with open("labels.txt", 'r') as lf:
            self.labels = lf.readlines()
            self.labels = [i.strip("\n") for i in self.labels]
        print("Labels loaded")
    
    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)
    
    def predict(self, x):
        # the model needs dtype to be float32
        x = torch.tensor(x).to(self.device).to(torch.float32)
        
        # Get the predictions based on the inputted data
        print("Predicting labels")
        pred = self.model(x).detach().numpy()

        # Map the predictions from large array to index to string
        pred = [np.round(self.softmax(i), 4) for i in pred]
        pred_index = [np.where(i == 1)[0] for i in pred]
        label_preds = [self.labels[int(i)] for i in pred_index]
        
        return label_preds




