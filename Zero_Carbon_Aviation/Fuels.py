"""Define fuel property classes"""

# Combustion modeling
import cantera as ct

# Unit management
import pint

# Define unit registry and short hand for Quantity 
ureg = pint.UnitRegistry(); Q_ = ureg.Quantity

class Fuel:
    """Fuel specification class"""
    def __init__(self, phase_definition=None, 
                 specific_cost=None,
                 liquid_density=None,
                 stored_mass_fraction=1):
      
        self.phase_definition = phase_definition
        self.phase = ct.Solution(source=phase_definition)
        self.specific_cost = specific_cost
        self.liquid_density = liquid_density
        self.stored_mass_fraction = stored_mass_fraction
    
    @property
    def cost_liquid_volume_specific(self, unit_string='usd/liter'):
      """Calculate and return the liquid volume specific cost"""
      if self.specific_cost.to_base_units().units == ureg['usd/meters**3']:
        
        # Input specfic cost is already liquid volume specific - convert to specified units
        return self.specific_cost.to(ureg[unit_string])
      
      elif self.specific_cost.to_base_units().units == ureg['usd/kg']:
        
        # Input specific cost is mass-specific - calculate & return volumetric cost
        return (self.specific_cost * self.liquid_density).to(ureg[unit_string])
 
    @property
    def cost_mass_specific(self, unit_string='usd/kg'):
      """Calculate and return the mass specific cost"""
      if self.specific_cost.to_base_units().units == ureg['usd/kg']:
        
        # Input specfic cost is already mass specific - convert to specified units
        return self.specific_cost.to(ureg[unit_string])
      
      elif self.specific_cost.to_base_units().units == ureg['usd/meters**3']:
        
        # Input specific cost is volume-specific - calculate & return mass-specific cost
        return (self.specific_cost / self.liquid_density).to(ureg[unit_string])
        
    @property
    def lower_heating_value(self):
      """Calculate and return the lower heating value"""
      
      # Specify the reactant state
      reactants = ct.Solution(source=self.phase_definition)
      reactants.TP = 298, ct.one_atm
      reactants.set_equivalence_ratio(1.0, self.phase.name, 'O2:1.0')
      
      # Calculate the fuel mass fraction
      Y_fuel = reactants[self.phase.name].Y[0]
      
      # Complete combustion product mole fractions
      X_products = {'CO2': reactants.elemental_mole_fraction('C'),
                    'H2O': 0.5 * reactants.elemental_mole_fraction('H'),
                    'N2': 0.5 * reactants.elemental_mole_fraction('N')}
      
      # Calculate the product enthalpy at 298 K, 1 atm
      products = ct.Solution(source=self.phase_definition)
      products.TPX = 298, ct.one_atm, X_products
      
      return Q_( (reactants.enthalpy_mass - products.enthalpy_mass) / Y_fuel,
                ureg['J/kg'] )
      
    @property
    def stored_lower_heating_value(self):
      return self.lower_heating_value * self.stored_mass_fraction
    
    @property
    def cost_energy_specific(self, unit_string='usd/kWh'):
        """Calculate the energy-specific cost of fuel on a lower-heating-value basis."""
        return (self.cost_mass_specific / self.lower_heating_value).to(ureg[unit_string])
      
    @property
    def emissions_factor(self, unit_string='kg/kWh'):
      """Calculate the LHV-specific CO2 emisions factor (eg. kg CO2/kWh)"""
      
      # Specify the reactant state
      reactants = ct.Solution(source=self.phase_definition)
      reactants.TP = 298, ct.one_atm
      reactants.set_equivalence_ratio(1.0, self.phase.name, 'O2:1.0')
      
      if reactants.elemental_mole_fraction('C') == 0:
        return 0*ureg[unit_string]
      
      else:
        
        # Calculate the fuel mass fraction
        Y_fuel = reactants[self.phase.name].Y[0]

        # Complete combustion product mole fractions
        X_products = {'CO2': reactants.elemental_mole_fraction('C'),
                      'H2O': 0.5 * reactants.elemental_mole_fraction('H'),
                      'N2': 0.5 * reactants.elemental_mole_fraction('N')}

        # Calculate the product enthalpy at 298 K, 1 atm
        products = ct.Solution(source=self.phase_definition)
        products.TPX = 298, ct.one_atm, X_products

        return ( products['CO2'].Y[0] / Y_fuel / 
                 self.lower_heating_value ).to(ureg[unit_string])
    
 
class Methane(Fuel):
    """Methane per the NASA CEA Code Specification"""
    def __init__(self, specific_cost=Q_(0.25, ureg['usd/kg'])):
      
      # Fuel name
      self.name = 'Methane'
      
      # Initialize the superclass using the below Cantera phase definition
      Fuel.__init__(self, phase_definition=
                    '''ideal_gas(name='CH4',
                        elements='C O H N',
                        species='nasa_gas:CH4 H2O CO2 O2 N2',
                        options=['skip_undeclared_elements'],
                        initial_state=state(temperature=300, pressure=101325))''', 
                    specific_cost=specific_cost,
                    liquid_density=Q_(423, ureg['kg/meter**3']))
      
class JetA(Fuel):
    """Jet Fuel per the NASA CEA Code Specification"""
    def __init__(self, specific_cost=Q_(1.4, ureg['usd/liter'])):
      
      # Fuel name
      self.name = 'Jet-A'
      
      # Initialize the superclass using the below Cantera phase definition
      Fuel.__init__(self, phase_definition=
                    '''ideal_gas(name='Jet-A(g)',
                        elements='C O H N',
                        species='nasa_gas:Jet-A(g) H2O CO2 O2 N2',
                        options=['skip_undeclared_elements'],
                        initial_state=state(temperature=300, pressure=101325))''', 
                    specific_cost=specific_cost,
                    liquid_density=Q_(804, ureg['kg/meter**3']))

class Ammonia(Fuel):
    """Ammonia per the NASA CEA Code Specification"""
    def __init__(self, specific_cost=Q_(500, ureg['usd/tonne'])):
      
      # Fuel name
      self.name = 'Ammonia'
      
      # Initialize the superclass using the below Cantera phase definition
      Fuel.__init__(self, phase_definition=
                    '''ideal_gas(name='NH3',
                        elements='C O H N',
                        species='nasa_gas:NH3 H2O CO2 O2 N2',
                        options=['skip_undeclared_elements'],
                        initial_state=state(temperature=300, pressure=101325))''', 
                    specific_cost=specific_cost,
                    liquid_density=Q_(682, ureg['kg/meter**3']))    

class Hydrogen(Fuel):
    """Hydrogen per the NASA CEA Code Specification"""
    def __init__(self, specific_cost=Q_(4, ureg['usd/kg']), 
                 stored_mass_fraction=1):
      
      self.name = 'Hydrogen'
      
      # Initialize the superclass using the below Cantera phase definition
      Fuel.__init__(self, phase_definition=
                    '''ideal_gas(name='H2',
                        elements='C O H N',
                        species='nasa_gas:H2 H2O CO2 O2 N2',
                        options=['skip_undeclared_elements'],
                        initial_state=state(temperature=300, pressure=101325))''', 
                    specific_cost=specific_cost,
                    liquid_density=Q_(71, ureg['kg/meter**3']),
                    stored_mass_fraction=stored_mass_fraction) 
      
class Ethanol(Fuel):
    """Ethanol per the NASA CEA Code Specification"""
    def __init__(self, specific_cost=Q_(1.74, ureg['usd/gallon'])):
      
      # Fuel name
      self.name = 'Ethanol'
      
      # Initialize the superclass using the below Cantera phase definition
      Fuel.__init__(self, phase_definition=
                    '''ideal_gas(name='C2H5OH',
                        elements='C O H N',
                        species='nasa_gas:C2H5OH H2O CO2 O2 N2',
                        options=['skip_undeclared_elements'],
                        initial_state=state(temperature=300, pressure=101325))''', 
                    specific_cost=specific_cost,
                    liquid_density=Q_(789, ureg['kg/meter**3']))  
