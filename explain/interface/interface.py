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

    # plot line colors
    self.lines = ['r-', 'b-', 'g-', 'c-', 'm-', 'y-', 'k-', 'w-']

    # define a list holding the prop changes
    self.propChanges = []

  def calculate(self, time_to_calculate):
    # calculate the model steps
    no_steps = int(time_to_calculate / self.model.modeling_stepsize)
    print(f'Calculating model run of {time_to_calculate} sec. in {no_steps} steps.')
    self.model.calculate(time_to_calculate)
    run_duration = round(self.model.run_duration, 3)
    step_duration = round(self.model.step_duration, 4)
    print(f'Ready in {run_duration} sec. Average model step in {step_duration} ms.')

  def model_step(self, model_clock):
    self.dc.collect_data(model_clock)
    # process the propchanges
    for change in self.propChanges:
      change.update()
      if change.completed:
        self.propChanges.remove(change)

  def schedule_prop_change(self, prop, new_value, in_time, at_time = 0):
    prop = self.find_model_prop(prop)
    if (prop != None):
      new_prop_change = propChange(prop, new_value, in_time, at_time)
      self.propChanges.append(new_prop_change)
      print(f"{prop['label']} is scheduled to change from {new_prop_change.initial_value} to {new_value} in {in_time} sec. at {at_time} sec. during next model run.")

  def prop_change(self, prop, new_value):
    # first find the correct reference to the property
    prop = self.find_model_prop(prop)
    
    if (prop != None):
      # check whether the type of new_value is the same as the model type
      if type(new_value) == type(getattr(prop['model'], prop['prop'])):
        setattr(prop['model'], prop['prop'], new_value)
        current_value = getattr(prop['model'], prop['prop'])
        label = prop['label']
        print(f'{label} changed from {current_value} to {new_value}.')
      else:
        current_value_type = type(getattr(prop['model'], prop['prop']))
        new_value_type = type(new_value)
        print(f'property type mismatch. model property type = {current_value_type}, new value type = {new_value_type}')
    else:
      print("property not found in model")
  
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
      prop_reference = self.find_model_prop(prop)
      if (prop_reference != None):
        self.dc.add_to_watchlist(prop_reference)

    # calculate the model steps
    self.calculate(time_to_calculate)

    # plot the properties
    self.draw_time_graph(sharey, combined)

  def plot_xy(self, property_x, property_y, time_to_calculate = 2, sampleinterval = 0.0005):
    # first clear the watchllist and this also clears all data
    self.dc.clear_watchlist()

     # set the sample interval
    self.dc.set_sample_interval(sampleinterval)

    prop_reference_x = self.find_model_prop(property_x)
    if (prop_reference_x != None):
      self.dc.add_to_watchlist(prop_reference_x)

    prop_reference_y = self.find_model_prop(property_y)
    if (prop_reference_y != None):
      self.dc.add_to_watchlist(prop_reference_y)

    # calculate the model steps
    self.calculate(time_to_calculate)

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
    
  def find_model_prop(self, prop):
    # split the model from the prop
    t  = prop.split(sep=".")
    if (len(t) == 2):
      # try to find the parameter in the model
      if t[0] in self.model.compliances:
        if (hasattr(self.model.compliances[t[0]], t[1])):
          return { 'label': prop, 'model': self.model.compliances[t[0]], 'prop': t[1]}

      if t[0] in self.model.time_varying_elastances:
        if (hasattr(self.model.time_varying_elastances[t[0]], t[1])):
          return { 'label': prop, 'model': self.model.time_varying_elastances[t[0]], 'prop': t[1]}
      
      if t[0] in self.model.resistors:
        if (hasattr(self.model.resistors[t[0]], t[1])):
          return { 'label': prop, 'model': self.model.resistors[t[0]], 'prop': t[1]}

      if t[0] in self.model.valves:
        if (hasattr(self.model.valves[t[0]], t[1])):
          return { 'label': prop, 'model': self.model.valves[t[0]], 'prop': t[1]}

      if t[0] in self.model.models:
        if (hasattr(self.model.models[t[0]], t[1])):
          return { 'label': prop, 'model': self.model.models[t[0]], 'prop': t[1]}

    return None
    

class propChange:
  def __init__(self, prop, new_value, in_time, at_time = 0, update_interval = 0.0005):

    self.prop = prop
    self.current_value = getattr(prop['model'], prop['prop'])
    self.initial_value = self.current_value
    self.target_value = new_value
    self.at_time = at_time
    self.in_time = in_time

    if (in_time > 0):
      self.step_size = ((self.target_value - self.current_value) / self.in_time) * update_interval
    else:
      self.step_size = 0

    
    self.update_interval = update_interval
    self.running = False
    self.completed = False
    self.running_time = 0
  
  def update (self):
    if self.completed == False:
      # check whether the property should start changing (if the at_time has passed)
      if self.running_time >= self.at_time:
        if (self.running == False):
          print(f"- {self.prop['label']} change started at {self.running_time}. Inital value: {self.initial_value}")
        self.running = True
      else:
        self.running = False

      self.running_time += self.update_interval

      if (self.running):
        self.current_value += self.step_size
        if abs(self.current_value - self.target_value) < abs(self.step_size):
          self.current_value = self.target_value
          self.step_size = 0
          self.running = False
          self.completed = True
          
        if (self.step_size == 0):
          self.current_value = self.target_value
          self.completed = True
          print(f"- {self.prop['label']} change stopped at {self.running_time}. New value: {self.current_value}")

        setattr(self.prop['model'], self.prop['prop'], self.current_value)

  def cancel (self):
    self.step_size = 0
    self.current_value = self.initial_value
    self.completed = True
    setattr(self.prop['model'], self.prop['prop'], self.current_value)

  def complete (self):
    self.step_size = 0
    self.current_value = self.target_value
    self.completed = True
    setattr(self.prop['model'], self.prop['prop'], self.current_value)

  