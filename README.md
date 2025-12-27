# Zero-Carbon-Aviation

A Python-based toolkit for evaluating climate-friendly aviation propulsion systems and energy storage options. This repository combines interactive Colab notebooks with a modular Python package to facilitate research and analysis of zero-carbon aircraft propulsion architectures.

## Overview

The focus of these tools is on evaluating the impact of different propulsion system architectures on aircraft performance, including:
- Traditional turbofan engines
- Electrified propulsion systems
- Hybrid propulsion architectures
- Alternative energy storage solutions

### Energy Storage Options

The toolkit supports analysis of multiple energy storage technologies:
1. **Traditional batteries** (e.g., Li-Ion)
2. **Carbon-neutral liquid fuels** (e.g., sustainable aviation fuels)
3. **Metal-Air batteries**
4. **Hydrogen fuel cells**

### Aircraft Categories

The propulsion systems can be evaluated across four commercial passenger aircraft types:
1. **Regional Turboprop** (e.g., Bombardier Dash 8)
2. **Regional Jet** (e.g., Airbus A220)
3. **Single Aisle** (e.g., Boeing 737)
4. **Twin Aisle** (e.g., Boeing 777)

## Installation

### Prerequisites

Ensure you have Python 3.7+ installed. The package requires the following dependencies:
- numpy
- matplotlib
- pandas
- pint (unit management)
- cantera (combustion modeling)

### Setup

Clone the repository and install the package:

```bash
git clone https://github.com/davetew/Zero-Carbon-Aviation.git
cd Zero-Carbon-Aviation
pip install -e .
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/davetew/Zero-Carbon-Aviation.git
```

## Notebooks

The repository includes several Jupyter notebooks for interactive analysis:

- **`Zero_Carbon_Aviation_Colab_v3.ipynb`** - Latest comprehensive notebook for evaluating zero-carbon aircraft propulsion and energy storage system options (Colab-ready)
- **`Zero_Carbon_Aviation_Colab_v2.ipynb`** - Previous version with comparative analysis capabilities
- **`Zero_Carbon_Aviation_Colab.ipynb`** - Original Colab notebook for basic propulsion system evaluation
- **`SimpleTurboFan.ipynb`** - Analysis of simple turbofan engine performance characteristics
- **`Propulsion_System_Specific_Energy_Contour.ipynb`** - Contour plots and visualization of propulsion system specific energy
- **`Dual_Cycle_Propulsion_System_Integration.ipynb`** - Integration analysis of dual-cycle propulsion architectures
- **`Old_Zero_Carbon_Aircraft.ipynb`** - Legacy notebook with earlier analysis methods

### Running Notebooks

To run notebooks locally:
```bash
jupyter notebook
```

Or open directly in Google Colab by clicking the Colab badge in each notebook.

## Package Structure

The `Zero_Carbon_Aviation` package is organized into several core modules:

### Core Classes

1. **`Fuel`** (`Aircraft.py`)
   - Fuel property calculations and specifications
   - Support for various fuel types including conventional jet fuel, hydrogen, and sustainable aviation fuels
   - Properties: specific cost, liquid density, stored mass fraction
   - Integration with Cantera for combustion modeling

2. **`Aircraft`** (`Aircraft.py`)
   - Aircraft-level performance assessment
   - Mission analysis and range calculations
   - Integration of propulsion systems with airframe

3. **`Propulsor`** (`Propulsor.py`)
   - Fan and propeller performance modeling
   - Thrust and efficiency calculations
   - Velocity ratio and kinetic energy efficiency analysis

4. **`SimpleBraytonCycle`** (`SimpleBraytonCycle.py`)
   - Gas turbine thermodynamic cycle analysis
   - Compressor and turbine performance modeling
   - Support for cooling flow and pressure loss calculations
   - Configurable efficiency and pressure ratios

5. **`compressible_flow`** (`compressible_flow.py`)
   - Compressible flow relations and utilities
   - Mach number calculations
   - Isentropic flow relations

## Usage

### Quick Start Example

```python
from Zero_Carbon_Aviation import Fuel, Aircraft, SimpleBraytonCycle
import pint

# Define unit registry
ureg = pint.UnitRegistry()
Q_ = ureg.Quantity

# Create a fuel instance
fuel = Fuel(
    phase_definition='gri30.yaml',
    specific_cost=Q_(2.50, 'usd/kg'),
    liquid_density=Q_(810, 'kg/m**3'),
    stored_mass_fraction=0.95
)

# Create a simple Brayton cycle for turbine analysis
engine = SimpleBraytonCycle(
    PR=30,
    Turbine_Inlet_Temperature_C=1500,
    ηpoly_compressor=0.90,
    ηpoly_turbine=0.89
)

# Analyze propulsion system performance
print(f"Cycle efficiency: {engine.η_thermal:.3f}")
```

## Contributing

Contributions are welcome! This is an active research project under development. Feel free to:
- Report bugs and issues
- Suggest new features
- Submit pull requests
- Improve documentation

## Author

**David Tew**
- Email: davetew@alum.mit.edu
- GitHub: [@davetew](https://github.com/davetew)

## License

This project is currently under development. Please contact the author for usage and licensing information.

## Acknowledgments

This toolkit is being developed to support research into sustainable aviation technologies and zero-carbon flight solutions. 



