import math

class Datacollector:
  def __init__(self, model):
    # initialize the super class
    super().__init__()

    # store a reference to the model instance
    self.model = model

  def model_step(self, model_clock):
    pass