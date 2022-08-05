import numpy as np

# Handy compressible flow relations
γ1 = lambda γ: γ / (γ-1) 

# Ratio of total to static temperature
θ = lambda Mach, γ=1.4: 1 + (γ-1)/2*Mach**2

# Ratio of total to static pressure
δ = lambda Mach, γ=1.4: θ(Mach, γ)**(γ1(γ))

class Propulsor():

  def __init__(self, FPR, M0, isenEfficiency, γ=1.4):
    """Initialize an instance of Fan given the pressure ratio, flight Mach number and the isentropic efficiency"""
    self.FPR, self.M0, self.isenEfficiency, self.γ = FPR, M0, isenEfficiency, γ

  @property
  def γ1(self):
    """Convenient function of the ratio of specific heats"""
    return self.γ / (self.γ-1)

  @property
  def M_2n(self):
    """Fully expanded nozzle exit Mach number"""
    return np.sqrt( 2/(self.γ-1) * (self.FPR**(1/self.γ1)*θ(self.M0,self.γ) - 1) )

  @property
  def Tt2_Tt0(self):
    """Fan exit to inlet total temperature ratio"""
    return (self.FPR**(1/self.γ1) - 1)/self.isenEfficiency + 1

  @property
  def T2n_T0(self):
    """Fan nozzle exit to inlet static temperature ratio"""
    return θ(self.M0,self.γ) / θ(self.M_2n,self.γ) * self.Tt2_Tt0

  @property
  def U2n_U0(self):
    """Fan nozzle exit to flight velocity ratio"""
    return self.M_2n / self.M0 * np.sqrt(self.T2n_T0)

  @property
  def Thrust_m0U0(self):
    return self.U2n_U0 - 1

  @property
  def η_KE(self):
    """Fan kinetic energy efficiency = Delta Fan KE / Fan Aerodynamic Work"""
    return self.M0**2*(self.γ-1) / 2 / θ(self.M0,self.γ) * (self.U2n_U0**2 - 1) / (self.Tt2_Tt0-1)

  @property
  def η_propulsive(self):
    return 2*self.Thrust_m0U0 / ( self.U2n_U0**2 - 1)

  @property
  def η_overall(self):
    return self.η_KE*self.η_propulsive
