import math
from interface.datacollector import Datacollector

class Interface:
  def __init__(self, model):
    # initialize the super class
    super().__init__()

    # store a reference to the model instance
    self.model = model

    # initialize a datacollector
    self.datacollector = Datacollector(model)

  def model_step(self, model_clock):
    pass