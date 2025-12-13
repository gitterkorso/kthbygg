# Här har vi formler från eurokoden beaktande vippning

import math

def Vippningskurva(section_type, h, b):
    # Bestämmer bucklingskurva enligt tabellen
    ratio = h / b
    
    if section_type.lower() == "valsad":
        if ratio <= 2:
            curve = "b"
            print("Knäckningskurva b -> α_LT = 0.34")
        else:
            curve = "c"
            print("Knäckningskurva c -> α_LT = 0.49")
    elif section_type.lower() == "svetsad":
        if ratio <= 2:
            curve = "c"
            print("Knäckningskurva c -> α_LT = 0.49")
        else:
            curve = "d"
            print("Knäckningskurva d -> α_LT = 0.76")
    else:
        return None  # okänt tvärsnitt
    
    # Imperfektionsfaktor enligt kurva
    alpha_values = {
        "a": 0.21,
        "b": 0.34,
        "c": 0.49,
        "d": 0.76
    }
   
    return alpha_values[curve]

#α_LT = Vippningskurva("svetsad", 500, 250)
# print(α_LT)




# λ_LT
def λ_LT(fyd, W_y_pl, M_cr):
    val = math.sqrt((fyd * W_y_pl) / M_cr)
    return val





# Φ_LT
def Φ_LT(α_LT, λ_LT, β):
    # Begränsning för β
    if β <= 0.75:
        β_kalk = 0.75
    else:
        β_kalk = β
    
    # Begränsning för λ_LT0
    if λ_LT >= 0.4:
        λ_LT0 = 0.4
    else: 
        λ_LT0 = λ_LT
    
    Φ_LT_value = 0.5 * (1 + α_LT * (λ_LT - λ_LT0) + β_kalk * λ_LT**2)
    
    return Φ_LT_value

#Φ_LT = Φ_LT(α_LT, λ_LT, β)
#print(f"Φ_LT = {Φ_LT:.3f}")





# χ_LT
def χ_LT(Φ_LT, λ_LT, β):
    # Begränsning för β
    if β <= 0.75:
        β_kalk = 0.75
    else:
        β_kalk = β
    
    # Beräkna χ_LT
    χ_LT_value = 1 / (Φ_LT + math.sqrt(Φ_LT**2 - (β_kalk * λ_LT**2)))
    
    # Applicera begränsningar
    χ_LT_value = min(χ_LT_value, 1.0)
    χ_LT_value = min(χ_LT_value, 1 / λ_LT**2)
    
    return χ_LT_value





def f_faktor(k_c, λ_LT):
    # Beräknar f enligt: f = 1 - 0.5*(1 - k_c) * (1 - 2*(λ_LT - 0.8)**2) men <= 1.0
    f = 1 - 0.5 * (1 - k_c) * (1 - 2.0 * (λ_LT - 0.8)**2)
    return min(f, 1.0)

def χ_LT_mod(χ_LT, f):
    # χ_LT_mod = χ_LT / f men <= 1.0
    value = χ_LT / f
    return min(value, 1.0)

