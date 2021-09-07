import math

class Compliance:
  def __init__(self, model, **args):
    # initialize the super class
    super().__init__()

    # set the independent properties (name, description, type, subtype, is_enabled, vol, u_vol, el_base, el_k)
    for key, value in args.items():
      setattr(self, key, value)

    # initialize the dependent properties
    self.pres = 0
    self.recoil_pressure = 0
    self.pres_outside = 0

  def calculate_pressure (self):
    if self.is_enabled:
      # calculate the volume above the unstressed volume
      vol_above_unstressed = self.vol - self.u_vol

      # calculate the elastance, which is volume dependent in a non-linear way
      elastance = self.el_base + self.el_k * pow(vol_above_unstressed, 2)

      # calculate pressure in the compliance
      self.recoil_pressure = vol_above_unstressed * elastance

      # calculate the transmural pressure
      self.pres = self.recoil_pressure + self.pres_outside


  def volume_in (self, dvol, comp_from):
    if self.is_enabled:
      # add volume
      self.vol += dvol

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def volume_out (self, dvol, comp_from):
    if self.is_enabled:
      # add volume
      self.vol -= dvol

      # guard against negative volumes (will probably never occur in this routine)
      return self.protect_mass_balance

  def protect_mass_balance (self):
    if (self.vol < 0):
      # if there's a negative volume it might corrupt the mass balance of the model so we have to return the amount of volume which could not be displaced to the caller of this function
      _nondisplaced_volume = -self.vol
      # set the current volume to zero
      self.vol = 0
      # return the amount volume which could not be removed
      return _nondisplaced_volume
    else:
      # massbalance is guaranteed
      return 0
