import math

class Datacollector:
  def __init__(self, model):
    # initialize the super class
    super().__init__()

    # store a reference to the model instance
    self.model = model

    # define the watch list
    self.watch_list = []

    # define the data sample interval
    self.sample_interval = 0.005
    self._interval_counter = 0

    # get the modeling stepsize from the model
    self.modeling_stepsize = model.modeling_stepsize

    # define the data list
    self.collected_data = []

  def clear_data (self):
    self.collected_data = []

  def clear_watchlist(self):
    # first clear all data
    self.clear_data()

    # empty the watch list
    self.watch_list = []

  def set_sample_interval(self, new_interval):
    self.sample_interval = new_interval

  def add_to_watchlist(self, property):
    # first clear all data
    self.clear_data()

    # add to the watchlist
    self.watch_list.append(property)

  def collect_data(self, model_clock):
    self._interval_counter += self.modeling_stepsize
    if (self._interval_counter > self.sample_interval):
      self._interval_counter = 0
      data_object = {
        'time': model_clock
      }
      for parameter in self.watch_list:
        label = parameter['label']
        value = getattr(parameter['model'], parameter['prop'])
        data_object[label] = value
        self.collected_data.append(data_object)