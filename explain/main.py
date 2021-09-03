# import the json the module for processing the definition file
import json
# import the perfomance counter module to measure the model performance
from time import perf_counter
# import the model interface module wich is used to interact with the model and to plot graphs
import interface.interface as io
# import the model datacollector module which is used to store and process data coming out of the model
import datacollector.datacollector as dc
# import all models
from models import acidbase, ans, blood, breathing, ecg, gas, heart, lungs, metabolism, oxygenation
# import the elements
from elements import compliance, resistor, time_varying_elastance, valve

# define a model class
class Model:
  # when a model class is instantiated the model loads de normal neonate json definition by default.
  def __init__(self, model_definition_file = './definitions/normal_neonate_24h.json'):
    
    # define a dictionary with all the components
    self.components = {}

    # define a variable holding the current model clock
    self.model_clock = 0

    # load and process the model definition file
    self.model_definition = self.load_definition_JSON(model_definition_file)

    # initialize all model components with the parameters from the JSON file
    self.initialize(self.model_definition)

  # load and process the model definition file
  def load_definition_JSON(self, file_name):
    # open the JSON file
    json_file = open(file_name)

    # convert the JSON file to a python dictionary object
    converted = json.load(json_file)

    # return the dictionary
    return converted

  # initiliaze all elements and models
  def initialize(self, model_definition):
    # get the model stepsize from the model definition
    self.modeling_stepsize = model_definition['modeling_stepsize']
    # get the model name from the model definition
    self.name= model_definition['name']
    # get the model description from the model definition
    self.description = model_definition['description']
    # get the set weight from the model definition
    self.weight = model_definition['weight']
    # intialize a dictionary holding all model elements
    self.compliances = {}
    self.time_varying_elastances = {}
    self.resistors = {}
    self.valves = {}
    self.models = {}

    # process the elements
    for component in model_definition['components']:
      # initialize the compliances
      if component['type'] == 'compliance':
        # instantiate a compliance object, initialize it's properties and add the object to the compliances dictionary
        _class = getattr(compliance, "Compliance")
        self.compliances[component['name']] = _class(self, **component)

      # initialize the time_varying_compliances
      if component['type'] == 'time_varying_elastance':
        # instantiate a time_varying_elastance object, initialize it's properties and add the object to the time_varying_elastance dictionary
        _class = getattr(time_varying_elastance, "TimeVaryingElastance")
        self.time_varying_elastances[component['name']] = _class(self, **component)

      # initialize the connectors
      if component['type'] == 'resistor':
        # instantiate a resistor object, initialize it's properties and add the object to the resistors dictionary
        _class = getattr(resistor, "Resistor")
        self.resistors[component['name']] = _class(self, **component)

      # initialize the valves
      if component['type'] == 'valve':
        # instantiate a valve object, initialize it's properties and add the object to the valves dictionary
        _class = getattr(valve, "Valve")
        self.valves[component['name']] = _class(self, **component)

    # process models
    for model in model_definition['models']:
      # initialize the ecg model
      if model['subtype'] == 'ecg':
        # instantiate a ecg model, initialize it's properties and add the object to the models dictionary
        _class = getattr(ecg, "Ecg")
        self.models[model['name']] = _class(self, **model)
      # initialize the heart model
      if model['subtype'] == 'heart':
        # instantiate a heart model, initialize it's properties and add the object to the models dictionary
        _class = getattr(heart, "Heart")
        self.models[model['name']] = _class(self, **model)
      # initialize the lung model
      if model['subtype'] == 'lungs':
        # instantiate a lung model, initialize it's properties and add the object to the models dictionary
        _class = getattr(lungs, "Lungs")
        self.models[model['name']] = _class(self, **model)
      # initialize the breathing model
      if model['subtype'] == 'breathing':
        # instantiate a breathing model, initialize it's properties and add the object to the models dictionary
        _class = getattr(breathing, "Breathing")
        self.models[model['name']] = _class(self, **model)
      # initialize the ans model
      if model['subtype'] == 'ans':
        # instantiate an ans model, initialize it's properties and add the object to the models dictionary
        _class = getattr(ans, "Ans")
        self.models[model['name']] = _class(self, **model)
      # initialize the metabolism model
      if model['subtype'] == 'metabolism':
        # instantiate a metabolism model, initialize it's properties and add the object to the models dictionary
        _class = getattr(metabolism, "Metabolism")
        self.models[model['name']] = _class(self, **model)
      # initialize the acidbase model
      if model['subtype'] == 'acidbase':
        # instantiate an acidbase model, initialize it's properties and add the object to the models dictionary
        _class = getattr(acidbase, "Acidbase")
        self.models[model['name']] = _class(self, **model)     
      # initialize the oxygenation model
      if model['subtype'] == 'oxygenation':
        # instantiate an oxygenation model, initialize it's properties and add the object to the models dictionary
        _class = getattr(oxygenation, "Oxygenation")
        self.models[model['name']] = _class(self, **model)
      # initialize the blood model
      if model['subtype'] == 'blood':
        # instantiate a blood model, initialize it's properties and add the object to the models dictionary
        _class = getattr(blood, "Blood")
        self.models[model['name']] = _class(self, **model)
      # initialize the gas model  
      if model['subtype'] == 'gas':
        # instantiate a gas model, initialize it's properties and add the object to the models dictionary
        _class = getattr(gas, "Gas")
        self.models[model['name']] = _class(self, **model)

  # calculate a number of seconds
  def calculate(self, time_to_calculate):
    # calculate the number of steps needed (= time in seconds / modeling stepsize in seconds)
    no_steps = int(time_to_calculate / self.modeling_stepsize)
    
    # start the performance counter
    perf_start = perf_counter()

    # execute the model steps
    for step_no in range(no_steps):
      # calculate the transmural pressures of the compliances and time_varying_elastances
      for tve in self.time_varying_elastances:
        self.time_varying_elastances[tve].calculate_pressure()
      
      for comp in self.compliances:
        self.compliances[comp].calculate_pressure()

      # calculate the flows across the resistors and valves and update the volumes of the compliances and time_varying_elastances
      for valve in self.valves:
        self.valves[valve].calculate_flow()

      for res in self.resistors:
        self.resistors[res].calculate_flow()

      # calculate the influence of the models on the elements
      for model in self.models:
        self.models[model].model_step()

      # increase the model clock
      self.model_clock += self.modeling_stepsize

    # stop the performance counter
    perf_stop = perf_counter()

    # print status messages
    print('ready in {} sec.'.format(perf_stop - perf_start))
    print('average model step in {} ms'.format(((perf_stop - perf_start) / no_steps) * 1000))
    print('model clock at {} sec'.format(int(self.model_clock)))

# this is the main module
if __name__ == "__main__":
    neo = Model()
    print("normal neonate model ready and stored in variable 'neo'.")