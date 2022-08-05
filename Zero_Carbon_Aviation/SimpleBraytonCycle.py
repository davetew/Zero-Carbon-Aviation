class SimpleBraytonCycle:

  # Ambient conditions

  def __init__(self, PR=None, Turbine_Inlet_Temperature_C=1500, 
              ηpoly_compressor=1.0, ηpoly_turbine=1.0,
              T_ambient_C=25, p_ambient_kPa=100, 
              R_J_kgK = 287.058, γ=1.4,
              target_mass_specific_work_kJ_kg=None,
              Turbine_Metal_Temperature_C=1200,
              StantonNumber=0.07,
              burnerPR=0.98, coolingPR=0.95):
    
    self.T_combustor_exit = Turbine_Inlet_Temperature_C + 273.15
    self.ηpoly = {"compressor": ηpoly_compressor,
                  "turbine": ηpoly_turbine}
    self.burnerPR = burnerPR
    self.coolingPR = coolingPR

    if Turbine_Metal_Temperature_C is None:
      self.Turbine_Metal_Temperature = self.T_combustor_exit
    else:
      self.Turbine_Metal_Temperature = Turbine_Metal_Temperature_C + 273.15

    self.StantonNumber=StantonNumber

    self.ambient = {'T_K': T_ambient_C + 273.15,
                    'p_Pa': p_ambient_kPa * 1000,
                    'γ': γ,
                    'R_J_kgK': 287,
                    'cp_J_kgK': R_J_kgK * γ / (γ-1)}
    if PR is None:
      # Calculate the PR that yields the target mass specific work
      if target_mass_specific_work_kJ_kg is None: 
        raise ValueError('Either PR or target_mass_specific_work must be specified.')
      self.PR = self.calcPR(target_mass_specific_work_kJ_kg)
    else:
      self.PR = PR

  def calcPR(self, target_work_kJ_kg):

    def δwork(pr):
      return ( SimpleBraytonCycle(PR=pr, 
                                  Turbine_Inlet_Temperature_C=self.T_combustor_exit - 273.15,
                                  ηpoly_compressor= self.ηpoly["compressor"],
                                  ηpoly_turbine=self.ηpoly["turbine"],
                                  T_ambient_C=self.ambient["T_K"] - 273.15, 
                                  p_ambient_kPa=self.ambient["p_Pa"]/1000, 
                                  R_J_kgK = self.ambient["R_J_kgK"], 
                                  γ=self.ambient["γ"],
                                  target_mass_specific_work_kJ_kg=None,
                                  Turbine_Metal_Temperature_C=self.Turbine_Metal_Temperature - 273.15,
                                  StantonNumber=self.StantonNumber,
                                  burnerPR=self.burnerPR,
                                  coolingPR=self.coolingPR,
                                  ).mass_specific_work/1000 -
                target_work_kJ_kg )

    # Calculate the PR that results in the target mass specific work
    try:
      pr, results = brentq(δwork, 1, 40, full_output=True)
    except ValueError:
      return np.nan

    # Return an answer if the solver converges
    return pr if results.converged else np.nan

  def optimize(self):
    """Optimize the cycle for maximum efficiency subject to the component efficiency and material
    temperature limits provided"""

    def inefficiency(x):
      """Calculate and return the 'inefficiency' or 1 - efficiency"""
      return 1 - SimpleBraytonCycle(PR=x[0], 
                                    Turbine_Inlet_Temperature_C=x[1],
                                    ηpoly_compressor= self.ηpoly["compressor"],
                                    ηpoly_turbine=self.ηpoly["turbine"],
                                    T_ambient_C=self.ambient["T_K"] - 273.15, 
                                    p_ambient_kPa=self.ambient["p_Pa"]/1000, 
                                    R_J_kgK = self.ambient["R_J_kgK"], 
                                    γ=self.ambient["γ"],
                                    target_mass_specific_work_kJ_kg=None,
                                    Turbine_Metal_Temperature_C=self.Turbine_Metal_Temperature - 273.15,
                                    StantonNumber=self.StantonNumber,
                                    burnerPR=self.burnerPR,
                                    coolingPR=self.coolingPR,
                                    ).efficiency

    try:
      results = minimize(inefficiency, [self.PR, self.T_combustor_exit], method='trust-constr', 
                         bounds=Bounds([1, 1273], [60, 2273]))

    except ValueError:
      return None
    
    else:
      if results.status == 1 or results.status == 2:
        self.PR = results.x[0]
        self.T_combustor_exit = results.x[1]
        return self 
      else:
        return None
    
  @property
  def T_compressor_exit(self):
    return self.ambient["T_K"]*self.PR**((self.ambient["γ"]-1)/self.ambient["γ"]/self.ηpoly["compressor"])

  @property
  def βcooling(self):
    """Turbine cooling / inlet mass flow ratio"""
    return ( self.StantonNumber*(self.T_combustor_exit-self.Turbine_Metal_Temperature) /
            (self.Turbine_Metal_Temperature - self.T_compressor_exit) )
    
  @property
  def turbinePR(self):
    """Turbine inlet to exhaust pressure ratio"""
    return self.PR*(self.burnerPR*(1-self.βcooling) + self.coolingPR*self.βcooling)  

  @property
  def T_turbine_inlet(self):
    """Temperature after mixing of combustor exit and cooling flows"""
    return self.T_compressor_exit*self.βcooling + self.T_combustor_exit*(1-self.βcooling)

  @property
  def T_turbine_exit(self):
    return self.T_turbine_inlet*self.turbinePR**(-(self.ambient["γ"]-1)*self.ηpoly["turbine"]/self.ambient["γ"])

  @property
  def mass_specific_heat_addition(self):
    return (self.T_combustor_exit - self.T_compressor_exit)*self.ambient["cp_J_kgK"]*(1-self.βcooling)

  @property
  def mass_specific_work(self):
    return ( self.T_turbine_inlet - self.T_turbine_exit - 
            (self.T_compressor_exit - self.ambient["T_K"]) )*self.ambient["cp_J_kgK"]

  @property
  def efficiency(self):
    return self.mass_specific_work / self.mass_specific_heat_addition

  @property
  def cycleTemperatures(self):
    return np.array([self.ambient["T_K"], self.T_compressor_exit,
                    self.T_combustor_exit, self.T_turbine_inlet,
                    self.T_turbine_exit] )

  @property
  def cyclePressures(self):
    return self.ambient["p_Pa"]* np.array([1, self.PR, self.PR*self.burnerPR, 
                                           self.turbinePR, 1])

  @property
  def cycleEnthalpies(self):
    return np.array([self.enthalpy(T) for T in self.cycleTemperatures])

  @property
  def cycleEntropies(self):
    return np.array( [self.entropy(T, p) for T, p in 
                      zip(self.cycleTemperatures, self.cyclePressures)] )  
    
  def enthalpy(self, T):
    """Calcuate and return the mass-specific enthalpy given the temperature in K"""
    return self.ambient["cp_J_kgK"]*(T - self.ambient["T_K"])

  def entropy(self, T, p):
    """Calcuate and return the mass-specific entropy given the temperature in K
    and pressure in Pa"""
    return ( self.ambient["cp_J_kgK"]*np.log(T/self.ambient["T_K"]) -
            self.ambient["R_J_kgK"]*np.log(p/self.ambient["p_Pa"]) )

  def cycleDiagrams(self):

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14,6))

    # Temperature-Entropy Diagram
    ax1.plot(self.cycleEntropies, self.cycleTemperatures, marker='d')
    ax1.set_xlabel('Entropy (J/kg/K)')
    ax1.set_ylabel('Temperature ($^{\circ}$C)')
    ax1.grid()
    ax1.set_title(f'TS: Efficiency= {self.efficiency*100:0.0f}%')
    
    # Pressure-Enthalpy
    ax2.plot(self.cycleEnthalpies/1000, self.cyclePressures/1000, marker='p')
    ax2.set_xlabel('Enthalpy (kJ/kg)')
    ax2.set_ylabel('Pressure (kPa)')
    ax2.grid()
    ax2.set_title(f'PH: Specific Work={self.mass_specific_work/1000:.0f} kJ/kg')
