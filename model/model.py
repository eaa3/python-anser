import numpy as np
import importlib

class MagneticModel():


    def __init__(self, model_config):
        self.model_name = model_config['model_name']
        self.numcoils = model_config['num_coils']

        # Import functions for coil model calculations
        # self.mod = importlib.import_module(model_name)
        self.mod = importlib.import_module('model.square_model')
        # Import function to calculate field using the coil model. This is ALWAYS required
        self.coil_model = self.mod.CoilModel(model_config)


    # Get the field intensity from ALL transmitter coils at a single point in space
    def getField(self, p=np.array([0,0,0])):

        Hx, Hy, Hz = self.coil_model.coil_field_total(p[0], p[1], p[2])

        return Hx, Hy, Hz

    # Get the field intensity due to a SINGLE transmitter coil at a single point in space
    def getFieldSingle(self, p=np.array([0,0,0]), coilindex=0):

        Hx, Hy, Hz = self.coil_model.coil_field_single(p[0], p[1], p[2], coilindex)

        return Hx, Hy, Hz