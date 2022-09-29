'''
A library for Hebbian-like learning implementations on MZI meshes based on the
work of O'Reilly et al. [1] in computation.

REFERENCES:
[1] O'Reilly, R. C., Munakata, Y., Frank, M. J., Hazy, T. E., and
    Contributors (2012). Computational Cognitive Neuroscience. Wiki Book,
    4th Edition (2020). URL: https://CompCogNeuro.org

[2] R. C. O'Reilly, “Biologically Plausible Error-Driven Learning Using
    Local Activation Differences: The Generalized Recirculation Algorithm,”
    Neural Comput., vol. 8, no. 5, pp. 895-938, Jul. 1996, 
    doi: 10.1162/neco.1996.8.5.895.
'''

from collections.abc import Iterator

import numpy as np
np.random.seed(seed=0)

import activations
import metrics

# library constants
DELTA_TIME = 0.1

class Net:
    '''Base class for neural networks with Hebbian-like learning
    '''
    def __init__(self, layers: iter) -> None:
        '''Instanstiates an ordered list of layers that will be
            applied sequentially during inference.
        '''
        self.layers = layers

    def Predict(self, data):
        '''Inference method called 'prediction' in accordance with a predictive
            error-driven learning scheme of neural network computation.
        '''
        for layer in self.layers:
            data = layer.Predict(data)

        return data

    def Observe(self, data):
        '''Training method called 'observe' in accordance with a predictive
            error-driven learning scheme of neural network computation.
        '''
        for layer in self.layers:
            data = layer.Observe(data)

        return data

class Mesh:
    def __init__(self, size) -> None:
        self.size = size
        self.matrix = np.eye(size)

    def set(self):
        self.matrix

    def get(self):
        return self.matrix

    def apply(self, data):
        try:
            return self.matrix @ data
        except ValueError as ve:
            print(f"Attempted to apply {data} (shape: {data.shape}) to mesh of dimension: {self.matrix}")

class fbMesh(Mesh):
    def __init__(self, mesh: Mesh) -> None:
        super.__init__(mesh.size)
        self.mesh = mesh

    def set(self):
        raise Exception("Feedback mesh has no 'set' method.")

    def get(self):
        return self.mesh.matrix.T

    def apply(self, data):
        matrix = self.mesh.matrix.T
        try:
            return matrix @ data
        except ValueError as ve:
            print(f"Attempted to apply {data} (shape: {data.shape}) to mesh of dimension: {matrix}")

class Layer:
    '''Base class for a layer that includes input matrices and activation
        function pairings. Each layer retains a seperate state for predict
        and observe phases, along with a list of input meshes applied to
        incoming data.
    '''
    def __init__(self, length: int, activation: function) -> None:
        self.preAct = np.zeros(length)
        self.obsAct = np.zeros(length)
        self.act = activation
        self.meshes = [] #empty initial mesh

    def addMesh(self, mesh: Mesh):
        self.meshes.append(mesh)

    def Predict(self, data):
        linAct = np.zeros(len(self))
        for mesh in self.meshes:
            linAct += mesh.apply(data)
        self.preAct += DELTA_TIME*(self.act(linAct)-self.preAct)
        return self.preAct

    def Observe(self, *data):
        linAct = np.zeros(len(self))
        for index, mesh in enumerate(self.meshes):
            linAct += mesh.apply(data[index])

        self.obsAct += DELTA_TIME*(self.act(linAct)-self.obsAct)
        return self.preAct

    def __len__(self):
        return len(self.preAct)

class FFFB(Net):
    '''A network with feed forward and feedback meshes between each
        layer. Based on ideas presented in [2]
    '''
    def __init__(self, layers: iter) -> None:
        super().__init__(layers)

    def Predict(self, data):
        for index, layer in self.layers:
            if index == 0:
                data = layer.Predict(data)
            else:
                data = layer.Predict(data, self.layers[index-1].preAct)
        return data