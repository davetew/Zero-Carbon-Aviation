import pint
ureg = pint.Registry(); Q_ = ureg.Quantity()



class Aircraft:
    """Aircraft class for data storage and estimation of flight performance characteristics.
    The inputs required for initialization include 
      1. the aircraft type as string,
      2. aircraft performance data as a pandas dataframe,
      3. engine performance data as a pandas dataframe, and
      4. the nominal fuel type specification (e.g. JetA())
      
    The type specified must be a column name in the aircraft dataframe.  The aircraft and engine
    dataframes must have the structure specified earlier in this notebook."""
    
    # Gravitational acceleration
    _g = Q_( constants.g, ureg['m/s**2'])
    
    def __init__(self,Type, AircraftData=AircraftData, EngineData=EngineData, Fuel=JetA()):
        """Initialize the class by extracting performance data of interest for the aircraft specified by
        Type from AircraftData"""
        
        if Type not in AircraftData.columns:
            raise TypeError(f"Invalid aircraft type valid types include: {AircraftData.columns}")
        
        # Save the name
        self.Type = Type
        
        # Save the aircraft performance data for the specified aircraft
        self.Aircraft = AircraftData[Type]
        
        # Save the engine performance data for the specified engine
        self.Engines = EngineData[AircraftData[Type]['Engine Type']]
        
        # Save the fuel class specification
        self.Fuel = Fuel
    
    @property
    def OverallEfficiency(self):
        return ( self.Aircraft['Cruise Speed']/self.Engines['TSFC']/ 
                self.Fuel.lower_heating_value ).to(ureg[''])
    
    @property
    def Isp(self):
        """Calculate the specific impulse in seconds"""
        return (1 / self.Engines['TSFC'] / self._g ).to(ureg['s'])
      
    @property
    def FinalWeight(self):
        """Calculate the final aircraft weight"""
        return self.Aircraft['Max Take Off Weight'] - self.Aircraft['Fuel Weight']
    
    @property
    def Lift2Drag(self):
        """Estimate the aircraft lift to drag ratio from the available range 
        & weight performance data"""
        return ( self.Aircraft['Range'] / self.Aircraft['Cruise Speed'] / self.Isp / 
                np.log(self.Aircraft['Max Take Off Weight']/ self.FinalWeight) ).to(ureg[''])
    
    @property
    def CruiseThrust(self):
        """Return the cruise thrust in kN"""
        return (( self.Aircraft['Max Take Off Weight'] - self.Aircraft['Fuel Weight']/2 ) *
                 self._g / self.Lift2Drag ).to(ureg['kN'])
      
    @property
    def CruiseFuelBurn(self):
      """Return the cruise fuel consumption in kg/hr"""
      return ( self.CruiseThrust * self.Engines['TSFC'] ).to(ureg['kg/hr'])
      
    @property
    def CruiseThrustPower(self):
      """Return the cruise thust power in MW"""
      return ( self.CruiseThrust * self.Aircraft['Cruise Speed'] ).to(ureg['MW'])
    
    @property
    def SpecificPower(self):
      "Return the propulsion system specific power in W/kg"
      return ( self.CruiseThrustPower / self.Aircraft['Engine Number'] / 
               self.Engines['Weight'] ).to(ureg['W/kg'])
    
    @property
    def CruiseCO2Emissions(self):
      """Calculate the passenger-specific cruise CO2 emissions (kg CO2 / km / passenger)"""
      return ( self.CruiseFuelBurn * self.Fuel.emissions_factor * 
               self.Fuel.lower_heating_value / self.Aircraft['Cruise Speed'] / 
               self.Aircraft['Max Seats'] / ureg['passenger']).to('kg/km/passenger')
    
    @property
    def CruiseEnergyConsumption(self):
      """Calculate the passenger-specific cruise energy consumption (kWh / km / passenger)"""
      return ( self.CruiseFuelBurn *  
         self.Fuel.lower_heating_value / self.Aircraft['Cruise Speed'] / 
         self.Aircraft['Max Seats'] / ureg['passenger'] ).to('kWh/km/passenger')
      
    @property 
    def FinalWeightEstimate(self):
        """Estimate the final weight given the lift to drag ratio """
        return np.nan
   
  
    def _drawFuelLines(self, η_overall):
      """Draw fuel heating value lines on payload or range contour charts.
          Assumed x -- Lower Heating Value (Wh/kg)
          """
   
      #Fuels = [Ammonia(), Ethanol(), JetA(), Hydrogen(stored_mass_fraction=1.0)]
      Fuels = [Ammonia(), Ethanol(), Methane(), JetA(), Hydrogen()]
      linestyles = ['-.', '--', ':', '-', ':']
      colors = ['y','magenta','orange','w','r']
      
      for fuel, linestyle, color in zip(Fuels, linestyles, colors):
        plt.plot(fuel.stored_lower_heating_value.to('kWh/kg')*np.ones(2), 
                 [np.min(η_overall),np.max(η_overall)], 
                linestyle=linestyle, linewidth=2.0, color=color)
        plt.text(fuel.stored_lower_heating_value.to('kWh/kg').magnitude-1.5, 
                 np.min(η_overall)+0.02,
                 fuel.name, rotation=90, color=color, 
                 verticalalignment='bottom', fontsize=18)
        
    def RangeContourChart(self, 
                          η_overall = np.linspace(0.1,0.8,20), 
                          ϵ_fuel = Q_( np.linspace(.150,35,21), ureg['kWh/kg']),
                          range_units='km', show_title=True):
        """Draw range contours as functions of the overall propulsion system efficiency
        and the specific energy of the storage media"""
    
        Range = lambda η_o, ϵ_f: ( np.log( self.Aircraft['Max Take Off Weight'] /
                                           self.FinalWeight ) / self._g *
                                           self.Lift2Drag * η_o * ϵ_f ).to(ureg[range_units])
      
        #Range2DArray = np.array([[Range(η, ϵ).magnitude for ϵ in ϵ_fuel] for η in η_overall])
        Range2DArray = np.array([[ (Range(η, ϵ) / self.Aircraft['Range']).to('') for ϵ in ϵ_fuel] for η in η_overall])

        plt.figure(figsize=(10,8))
        plt.contourf(ϵ_fuel.magnitude, η_overall, Range2DArray, 20)
        plt.colorbar()
        cs=plt.contour(ϵ_fuel.magnitude, η_overall, Range2DArray, 
                    #levels=[self.Aircraft['Range'].to(ureg(range_units)).magnitude], colors=['w'])
                    levels=[0.5, 0.75, 1], colors=['w'], linestyles=[':','--','-'])
        plt.clabel(cs)
        plt.xlabel('Unstored Mass-Specific Energy of Storage Media (kWh/kg)', fontsize=18)
        plt.ylabel('Overall Propulsion System Efficiency', fontsize=18)
        plt.xticks(fontsize=14); plt.yticks(fontsize=14)
        if show_title:
          plt.title(self.Type + ':  Range / Current Range Contours', fontsize=18)
        
        # Plot current fuel & efficiency point
        plt.plot(self.Fuel.lower_heating_value.to('kWh/kg'), self.OverallEfficiency, marker='o', markeredgecolor='w', 
         markerfacecolor='w', markersize=14)
        
        # Plot fuel lines
        self._drawFuelLines(η_overall)
        
        plt.show()
        


    def PayloadContourChart(self, CustomRange=None,
                            η_overall = np.linspace(0.1,0.8,50), 
                            ϵ_fuel = Q_( np.linspace(.150,35,100), ureg['kWh/kg']),
                            payload_units='kg'):
      """Draw payload contours as functions of the overall propulsion system efficiency
      and the specific energy of the storage media at constant range"""
      
      # Use the default aircraft range unless specified
      Range = self.Aircraft['Range'] if CustomRange is None else CustomRange
      
      # Initial to final aircraft weight ratio
      ϕ = lambda η_o, ϵ_f: np.exp( Range * self._g / self.Lift2Drag / 
                                   η_o / ϵ_f ).to(ureg[''])
      
      # Payload weight
      PayloadWeight = lambda η_o, ϵ_f: ( self.Aircraft['Max Take Off Weight'] /
                                         ϕ(η_o, ϵ_f) - 
                                         self.Aircraft['Operating Empty Weight'] ).to(ureg[payload_units])   


      #PLW_2DArray = np.array([[(PayloadWeight(η, ϵ) 
      #                          if PayloadWeight(η, ϵ) > 0 else 0*ureg[payload_units]).magnitude 
      #                          for ϵ in ϵ_fuel] for η in η_overall])
      
      PLW_2DArray = np.array([[(PayloadWeight(η, ϵ) / self.Aircraft['Max Payload Weight']
                                if PayloadWeight(η, ϵ) > 0 else 0*ureg[payload_units]).magnitude 
                                for ϵ in ϵ_fuel] for η in η_overall])
      
      
      plt.figure(figsize=(10,8))
      plt.contourf(ϵ_fuel.magnitude, η_overall, PLW_2DArray, 20)
      plt.colorbar()
      plt.xlabel('Specific Energy of Storage Media (kWh/kg)', fontsize=18)
      plt.contour(ϵ_fuel.magnitude, η_overall, PLW_2DArray, 
                  #levels=[self.Aircraft['Max Payload Weight'].to(ureg[payload_units]).magnitude], colors=['w'])
                  levels=[1], colors=['w'])
      plt.ylabel('Overall Propulsion System Efficiency', fontsize=18)
      plt.xticks(fontsize=14); plt.yticks(fontsize=14)
      plt.title(self.Type + ':  Payload / Current Payload Contours', fontsize=18)
      
      # Plot current fuel & efficiency point
      plt.plot(self.Fuel.lower_heating_value.to('kWh/kg'), self.OverallEfficiency, marker='o', markeredgecolor='w', 
         markerfacecolor='w', markersize=14)
      
      # Plot fuel lines
      self._drawFuelLines(η_overall)
   
      plt.show()
  
    def PayloadTechnologyContour(self, CustomRange=None, Fuel=JetA(),
                                 η_overall = np.linspace(0.2,0.8,50), 
                                 Spec_Pow = Q_( np.linspace(100,5000), ureg['W/kg']),
                                 payload_units='kg'):
      """Draw payload contours as functions of the propulsion system overall efficiency
      and specific power"""
      
      # Use the default aircraft range unless specified
      Range = self.Aircraft['Range'] if CustomRange is None else CustomRange
      
      # Initial to final aircraft weight ratio
      ϕ = lambda η_o : np.exp( Range * self._g / self.Lift2Drag / 
                               η_o / Fuel.lower_heating_value ).to(ureg[''])

      # Propulsion System Weight as a function of the specific power
      PropulsionWeight = lambda σ: ( self.CruiseThrustPower / σ ).to('kg')
      
      # Updated Empty Weight as a function of the propulsion system specific power (σ) 
      OEW = lambda σ: (self.Aircraft['Operating Empty Weight'] - 
                       self.Engines['Weight'] * self.Aircraft['Engine Number'] 
                       + PropulsionWeight(σ)).to(ureg(payload_units))
      
      # Payload Weight as a function of the propulsion system overall efficiency and the specific power
      PayloadWeight = lambda η_o, σ: ( self.Aircraft['Max Take Off Weight'] /
                                       ϕ(η_o) - OEW(σ) ).to(ureg[payload_units])   


      PLW_2DArray = np.array([[(PayloadWeight(η, σ) / self.Aircraft['Max Payload Weight']
                          if PayloadWeight(η, σ) > 0 else 0*ureg[payload_units]).magnitude 
                          for σ in Spec_Pow] for η in η_overall])
      
      plt.figure(figsize=(10,8))
      plt.contourf(Spec_Pow.magnitude, η_overall, PLW_2DArray, 20)
      plt.colorbar()
      plt.xlabel('Cruise Specific Power of Propulsion System (W/kg)', fontsize=18)
      plt.contour(Spec_Pow.magnitude, η_overall, PLW_2DArray, 
                  levels=[1], colors=['w'])
      plt.ylabel('Overall Propulsion System Efficiency', fontsize=18)
      plt.xticks(fontsize=14); plt.yticks(fontsize=14)
      plt.title(self.Type + ':  Payload / Current Payload Contours, Fuel = ' + str(Fuel.name), fontsize=18)
      
      # Plot current fuel and efficiency point
      plt.plot(self.SpecificPower, self.OverallEfficiency, marker='o', markeredgecolor='w', 
         markerfacecolor='w', markersize=14)
      
      plt.show()     
      
    def RangeTechnologyContour(self, CustomPayload=None, Fuel=JetA(),
                                 η_overall = np.linspace(0.2,0.8,50), 
                                 Spec_Pow = Q_( np.linspace(100,5000), ureg['W/kg']),
                                 range_units='km'):
      """Draw range as functions of the propulsion system overall efficiency
      and specific power"""
      
      if CustomPayload is None:
        # Use nominal payload
        Payload = self.FinalWeight - self.Aircraft['Operating Empty Weight']

      # Propulsion System Weight as a function of the specific power
      PropulsionWeight = lambda σ: ( self.CruiseThrustPower / σ ).to('kg')
      
      # Updated Empty Weight as a function of the propulsion system specific power (σ) 
      OEW = lambda σ: (self.Aircraft['Operating Empty Weight'] - 
                       self.Engines['Weight'] * self.Aircraft['Engine Number'] 
                       + PropulsionWeight(σ) )

      # Final aircraft weight
      FinalWeight = lambda σ: OEW(σ) + Payload
      
      # Initial to final aircraft weight ratio
      ϕ = lambda σ: np.max( (self.Aircraft['Max Take Off Weight'] / FinalWeight(σ), 1) )

      # Aircraft range
      Range = lambda η_o, σ: ( np.log( ϕ(σ) ) / self._g *
                                   self.Lift2Drag * η_o * Fuel.lower_heating_value ).to(range_units)
      
      Range2DArray = np.array([[ (Range(η, σ) / self.Aircraft['Range']).to('') for σ in Spec_Pow] for η in η_overall])
                    
      plt.figure(figsize=(10,8))
      plt.contourf(Spec_Pow.magnitude, η_overall, Range2DArray, 20)
      plt.colorbar()
      plt.xlabel('Cruise Specific Power of Propulsion System (W/kg)', fontsize=18)
      cs=plt.contour(Spec_Pow.magnitude, η_overall, Range2DArray, 
                  levels=[0.5,0.75,1], colors=['w'], linestyles=[':','--','-'])
      plt.clabel(cs)
      plt.ylabel('Overall Propulsion System Efficiency', fontsize=18)
      plt.xticks(fontsize=14); plt.yticks(fontsize=14)
      plt.title(self.Type + ':  Range / Current Range Contours, Fuel = ' + str(Fuel.name), fontsize=18)
      
      # Plot current fuel and efficiency point
      plt.plot(self.SpecificPower, self.OverallEfficiency, marker='o', markeredgecolor='w', 
         markerfacecolor='w', markersize=14)
      
      plt.show()
      
    def MultiFuelPayloadTechContour(self, CustomRange=None, Fuels= [Ammonia(), Ethanol(), JetA(), Hydrogen()],
                                 η_overall = np.linspace(0.2,0.8,50), 
                                 Spec_Pow = Q_( np.linspace(100,5000,100), ureg['W/kg']),
                                 payload_units='kg', show_title=True):
      
      linestyles = ['-.', '--', ':', '-']
      colors = ['y','orange','k','r']

      contour_coords = {}
      plt.figure(figsize=(10,8))
      
      for fuel, linestyle, color in zip(Fuels, linestyles, colors):
  
        # Use the default aircraft range unless specified
        Range = self.Aircraft['Range'] if CustomRange is None else CustomRange

        # Initial to final aircraft weight ratio
        ϕ = lambda η_o : np.exp( Range * self._g / self.Lift2Drag / 
                                 η_o / fuel.stored_lower_heating_value ).to(ureg[''])

        # Propulsion System Weight as a function of the specific power
        PropulsionWeight = lambda σ: ( self.CruiseThrustPower / σ ).to('kg')

        # Updated Empty Weight as a function of the propulsion system specific power (σ) 
        OEW = lambda σ: (self.Aircraft['Operating Empty Weight'] - 
                         self.Engines['Weight'] * self.Aircraft['Engine Number'] 
                         + PropulsionWeight(σ)).to(ureg(payload_units))

        # Payload Weight as a function of the propulsion system overall efficiency and the specific power
        PayloadWeight = lambda η_o, σ: ( self.Aircraft['Max Take Off Weight'] /
                                         ϕ(η_o) - OEW(σ) ).to(ureg[payload_units])   


        PLW_2DArray = np.array([[(PayloadWeight(η, σ) / self.Aircraft['Max Payload Weight']
                            if PayloadWeight(η, σ) > 0 else 0*ureg[payload_units]).magnitude 
                            for σ in Spec_Pow] for η in η_overall])

        cs = plt.contour(Spec_Pow.magnitude, η_overall, PLW_2DArray, 
                        levels=[1], colors=[color])
        
        contour_coords[fuel.name] = cs.allsegs[0][0]
        
        plt.text(contour_coords[fuel.name][0,0],contour_coords[fuel.name][0,1],
                 fuel.name, rotation=90, verticalalignment='top', 
                 fontsize=18, color=color)
        
        plt.xlabel('Cruise Specific Power of Propulsion System (W/kg)', fontsize=18)
        plt.ylabel('Overall Propulsion System Efficiency', fontsize=18)
        
        plt.xticks(fontsize=14); plt.yticks(fontsize=14)
      
      # Plot current fuel and efficiency point
      plt.plot(self.SpecificPower, self.OverallEfficiency, marker='o', markeredgecolor='k', 
         markerfacecolor='k', markersize=14)
      plt.grid(True)
      
      if show_title:
        plt.title(self.Type + ':  Nominal Payload Contour for Various Fuels', fontsize=18)


      plt.show()
      
      return contour_coords
      
    def Summary(self):
      """Return & display an aircraft Performance Summary"""
      Summary = pd.DataFrame.from_dict({self.Type: {'η_overall': self.OverallEfficiency,
                                                   'I_sp': self.Isp,
                                                   'L/D': self.Lift2Drag,
                                                   'Cruise / Max SL Thrust': self.CruiseThrust/self.Engines['Thrust Take Off']/self.Aircraft['Engine Number'], 
                                                   'Cruise Thrust Power': self.CruiseThrustPower,
                                                   'Cruise CO2 Emissions': self.CruiseCO2Emissions,
                                                   'Cruise Energy Consumption': self.CruiseEnergyConsumption,
                                                   'Cruise Specific Power (W/kg)': self.SpecificPower}})
      display(Summary)
      return Summary
      
