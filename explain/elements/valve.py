import math

class Valve:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()

    # set the independent properties (name, description, type, subtype, no_flow, no_backflow, comp_from, comp_to, r_for, r_back, r_k1, rk2)
    for key, value in args.items():
      setattr(self, key, value)

    comp_from_found = False
    comp_to_found = False

    # store a reference to the compliances which this resistor 'connects'
    if self.comp_from in model.compliances:
      self.comp1 = model.compliances[self.comp_from]
      comp_from_found = True
    
    if self.comp_from in model.time_varying_elastances:
      self.comp1 = model.time_varying_elastances[self.comp_from]
      comp_from_found = True

    if self.comp_to in model.compliances:
      self.comp2 = model.compliances[self.comp_to]
      comp_to_found = True
    
    if self.comp_to in model.time_varying_elastances:
      self.comp2 = model.time_varying_elastances[self.comp_to]
      comp_to_found = True

    if (comp_from_found == False):
      print('Valve', self.name, 'could not find compliance/time_varying_elastance', self.comp_from)

    if (comp_to_found == False):
      print('Valve', self.name, 'could not find compliance/time_varying_elastance', self.comp_to)

    # get the modeling stepsize from the model
    self.t = model.modeling_stepsize

    # initialize the dependent properties
    self.flow = 0
    self.resistance = 0

  def calculate_resistance(self, p1, p2):
    # calculate the flow dependent parts of the resistance
    nonlin_fac1 = self.r_k1 * self.flow
    nonlin_fac2 = self.r_k2 * pow(self.flow, 2)

    if (p1 > p2):
      return self.r_for + nonlin_fac1 + nonlin_fac2
    else:
      return self.r_back + nonlin_fac1 + nonlin_fac2

  def calculate_flow(self):
    # get the pressures from comp1 and comp2
    p1 = self.comp1.pres
    p2 = self.comp2.pres

    # calculate the resistance
    self.resistance = self.calculate_resistance(p1, p2)

    # first check whether the no_flow flag is checked
    if (self.no_flow):
      self.flow = 0
    else:
      self.flow = (p1 - p2) / self.resistance
      # check whether backflow is allowed across this resistor
      if (self.flow < 0 and self.no_backflow):
        self.flow = 0
    
    # now we have the flow in l/sec and we have to convert it to l by multiplying it by the modeling_stepsize
    dvol = self.flow * self.t

    # change the volumes of the compliances
    if (dvol > 0):
      # positive values mean comp1 loses volume and comp2 gains volume
      self.comp1.volume_out(dvol, self.comp2)
      self.comp2.volume_in(dvol, self.comp1)
    else:
      # negative values mean comp1 gains volume and comp2 loses volume
      self.comp1.volume_in(-dvol, self.comp2)
      self.comp2.volume_out(-dvol, self.comp1)
