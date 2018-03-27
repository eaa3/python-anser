import numpy as np
import importlib

class MagneticModel():


    def __init__(self, model_config):
        model_name = model_config['model_name']

        # Import functions for coil model calculations
        # self.mod = importlib.import_module(model_name)
        self.mod = importlib.import_module('model.square_model')
        # Import function to calculate field using the coil model. This is ALWAYS required
        self.coil_model = self.mod.CoilModel(model_config)


    def getField(self, p=np.array([0,0,0])):

        Hx, Hy, Hz = self.coil_model.coil_field(p[0], p[1], p[2])

        return Hx, Hy, Hz
