# Handy compressible flow relations
γ1 = lambda γ: γ / (γ-1) 

# Ratio of total to static temperature
θ = lambda Mach, γ=1.4: 1 + (γ-1)/2*Mach**2

# Ratio of total to static pressure
δ = lambda Mach, γ=1.4: θ(Mach, γ)**(γ1(γ))

# Handy temperature conversions 

# Kelvin to Celsius
K2C = lambda T_K: T_K - 273.15

# Celsius to Kelvin
C2K = lambda T_C: T_C + 273.15
