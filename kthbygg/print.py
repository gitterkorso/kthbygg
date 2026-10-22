# Namn: print

# Skriver ut en kraft (N) i kilonewton [N]
def N(name, value, decimals=2):
    print(f"{name:<5} = {value:.{decimals}f} [N]")

# Skriver ut en kraft (N) i kilonewton [kN]
def kN(name, value, decimals=2):
    print(f"{name:<5} = {value / 1000:.{decimals}f} [kN]")

# Skriver ut en kraft (N) i meganewton [MN]
def MN(name, value, decimals=2):
    print(f"{name:<5} = {value / 10**6:.{decimals}f} [MN]")

# Skriver ut ett moment (Nm) i newtonmeter [Nm]
def Nm(name, value, decimals=2):
    print(f"{name:<5} = {value:.{decimals}f} [Nm]")

# Skriver ut ett moment (Nm) i kilonewton [kNm]
def kNm(name, value, decimals=2):
    print(f"{name:<5} = {value / 10**6:.{decimals}f} [kNm]")

# Skriver ut ett moment (Nm) i meganewton [MNm]
def MNm(name, value, decimals=2):
    print(f"{name:<5} = {value / 10**9:.{decimals}f} [MNm]")
    
# Skriver ut en spänning eller modul (N/mm² eller Pa) i pascal [Pa]
def Pa(name, value, decimals=2):
    print(f"{name:<10} = {value * 1e6:.{decimals}f} [Pa]")

# Skriver ut en spänning eller modul (N/mm² eller MPa) i megapascal [MPa]
def MPa(name, value, decimals=2):
    print(f"{name:<10} = {value:.{decimals}f} [MPa]")

# Skriver ut en spänning eller modul (N/mm² eller GPa) i gigapascal [GPa]
def GPa(name, value, decimals=2):
    print(f"{name:<10} = {value / 1000:.{decimals}f} [GPa]")

# Skriver ut en längd (mm) i centimeter [cm]
def cm(name, value, decimals=2):
    print(f"{name:<10} = {value / 10:.{decimals}f} [cm]")

# Skriver ut en area (mm²) i kvadratcentimeter [cm²]
def cm2(name, value, decimals=2):
    print(f"{name:<10} = {value / 100:.{decimals}f} [cm²]")
    
# Skriver ut sektionsmodul (mm³) i kubikcentimeter [cm³]
def cm3(name, value, decimals=2):
    print(f"{name:<10} = {value / 1000:.{decimals}f} [cm³]")

# Skriver ut andra ytmoment (mm⁴) i centimeter till fjärde [cm⁴]
def cm4(name, value, decimals=2):
    print(f"{name:<10} = {value / 10000:.{decimals}f} [cm⁴]")
    
# Skriver ut Warping/Torsion Konstant (mm⁶) i centimeter till sjätte [cm⁶]
def cm6(name, value, decimals=2):
    print(f"{name:<10} = {value / 1000000:.{decimals}f} [cm⁶]")
    
# Skriver ut längd (mm) i millimeter [mm]
def mm(name, value, decimals=2):
    print(f"{name:<10} = {value:.{decimals}f} [mm]")

# Skriver ut en längd (mm) i centimeter [cm]
def cm(name, value, decimals=2):
    print(f"{name:<10} = {value / 10:.{decimals}f} [cm]")

# Skriver ut en längd (mm) i meter [m]
def m(name, value, decimals=2):
    print(f"{name:<10} = {value / 1000:.{decimals}f} [m]")

# Skriver ut area (mm²) i millimeterkvadrat [mm²]
def mm2(name, value, decimals=2):
    print(f"{name:<10} = {value:.{decimals}f} [mm²]")

# Skriver ut area (mm²) i meterkvadrat [m²]
def m2(name, value, decimals=4):
    print(f"{name:<10} = {value / 1e6:.{decimals}f} [m²]")

    
# Skriver ut ett generiskt värde i valfri enhet
def generic(name, value, unit, decimals=2):
    print(f"{name:<10} = {value:.{decimals}f} [{unit}]")



# Exempel

#N_cr_res = 85278.43  # N
#L_cr_res = 3500.0    # mm
#E = 210000.0         # N/mm² (MPa)
#I_z = 4000000.0      # mm⁴
#A = 5000.0           # mm²
#W_y_el = 120000.0    # mm³

#print("\n--- Strukturella Resultat (Konverterade) ---")
#kN("N_cr", N_cr_res)
#cm("L_cr", L_cr_res)
#MPa("E-modul", E)
#cm4("I_z", I_z)
#cm2("Area", A)
#cm3("W_el_y", W_y_el)
#mm("Tjocklek", 5.0)