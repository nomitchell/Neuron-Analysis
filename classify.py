import numpy as np
import onnxruntime

class Classify:
    def __init__(self):
        self.session = onnxruntime.InferenceSession("model/model.onnx")
    
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

        with open("resources/labels.txt", 'r') as lf:
            self.labels = lf.readlines()
            self.labels = [i.strip("\n") for i in self.labels]
        print("Labels loaded")

    def softmax(self, x):
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum(axis=0)

    def predict(self, x):
        final = []
        x = x.astype(np.float32)

        for i in x:
            #i = i.astype(np.float32)
            i = np.array([i])
        
            output = self.session.run([self.output_name], {self.input_name: i})[0]

            output = [np.round(self.softmax(i), 4) for i in output]
            output_index = [np.where(i == 1)[0] if np.any(i == 1) else 71 for i in output]

            label_outputs = [self.labels[int(i)] for i in output_index]
            final.append(label_outputs[0])

        return final