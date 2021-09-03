import math
from typing import ChainMap
from matplotlib import lines
import matplotlib.pyplot as plt
import numpy as np

import warnings
warnings.filterwarnings("ignore")

from interface.datacollector import Datacollector

class Interface:
  def __init__(self, model):
    # initialize the super class
    super().__init__()

    # store a reference to the model instance
    self.model = model

    # get the modeling stepsize from the model
    self.t = model.modeling_stepsize

    # initialize a datacollector
    self.dc = Datacollector(model)

    self.lines = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-', 'w-']

  def model_step(self, model_clock):
    self.dc.collect_data(model_clock)

  def change_property(self, property, new_value, time):
    self.model.resistors['DA'].is_enabled = True
  
  def plot_heart_pres(self):
    self.plot_time(["LV.pres","RV.pres","LA.pres", "RA.pres", "AA.pres"], 5, 0.0005, True, True)

  def plot_heart_vol(self):
    self.plot_time(["LV.vol","RV.vol","LA.vol", "RA.vol", "AA.vol"], 5, 0.0005, True, True)

  def plot_time (self, properties, time_to_calculate = 10, sampleinterval = 0.005, combined = True, sharey = True):
    # first clear the watchllist and this also clears all data
    self.dc.clear_watchlist()

    # set the sample interval
    self.dc.set_sample_interval(sampleinterval)

    # add the property to the watchlist
    if (isinstance(properties, str)):
      properties = [properties]

    # add the properties to the watch_list
    for prop in properties:
      self.dc.add_to_watchlist(prop)

    # calculate the model steps
    self.model.calculate(time_to_calculate)

    # plot the properties
    self.draw_time_graph(sharey, combined)

  def plot_xy(self, property_x, property_y, time_to_calculate = 2, sampleinterval = 0.0005):
    # first clear the watchllist and this also clears all data
    self.dc.clear_watchlist()

     # set the sample interval
    self.dc.set_sample_interval(sampleinterval)

    self.dc.add_to_watchlist(property_x)
    self.dc.add_to_watchlist(property_y)

    # calculate the model steps
    self.model.calculate(time_to_calculate)

    self.draw_xy_graph(property_x, property_y)

  def draw_xy_graph(self, property_x, property_y):
    no_dp = len(self.dc.collected_data)
    x = np.zeros(no_dp)
    y = np.zeros(no_dp)

    for index,t in enumerate(self.dc.collected_data):
      x[index] = t[property_x]
      y[index] = t[property_y]

    plt.figure( figsize=(18, 5), dpi=300)
    # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
    plt.plot(x, y, self.lines[0], linewidth=1 )
    plt.xlabel(property_x)
    plt.ylabel(property_y)

    plt.show()

  def draw_time_graph(self, sharey = False, combined = True):
    parameters = []
    no_parameters = 0
    # get the watch list of the datacollector
    for watched_parameter in self.dc.watch_list:
      parameters.append(watched_parameter['label'])

    no_dp = len(self.dc.collected_data)
    x = np.zeros(no_dp)
    y = []

    for parameter in enumerate(parameters):
      y.append(np.zeros(no_dp))
      no_parameters += 1

    for index,t in enumerate(self.dc.collected_data):
      x[index] = t['time']

      for idx, parameter in enumerate(parameters):
        y[idx][index] = t[parameter]

    # determine number of needed plots
    if (combined == False):
      fig, axs = plt.subplots(nrows=no_parameters, ncols=1, figsize=(18,5), sharex=True, sharey=sharey, constrained_layout=True)
      # fig.tight_layout()
      if (no_parameters > 1):
        for i, ax in enumerate(axs):
          ax.plot(x, y[i], self.lines[i], linewidth=1)
          ax.set_title(parameters[i])
          ax.set_ylabel('mmHg')
      else:
          axs.plot(x, y[0], lines[0], linewidth=1)
          axs.set_title(parameters[0])
          axs.set_ylabel('mmHg')
    
    if (combined):
      plt.figure( figsize=(18, 5), dpi=300)
      for index, parameter in enumerate(parameters):
        # Subplot of figure 1 with id 211 the data (red line r-, first legend = parameter)
        plt.plot(x, y[index], self.lines[index], linewidth=1, label = parameter)
        plt.xlabel('time (s)')
        plt.ylabel('mmHg')
        # Add a legend
        plt.legend()

    plt.show()
    

