# Dependencies
import math
from sympy import init_printing
init_printing(use_latex='mathjax')
from IPython.display import display, Math
import numpy as np

# ---- klasskonstanter ----
GL22c="GL22c"; GL24c="GL24c"; GL26c="GL26c"; GL28c="GL28c"
GL28cs="GL28cs"; GL30c="GL30c"; GL32c="GL32c"

GL22h="GL22h"; GL24h="GL24h"; GL26h="GL26h"; GL28h="GL28h"
GL28hs="GL28hs"; GL30h="GL30h"; GL32h="GL32h"

# ---- databas ----
_GL_DATA = {

# ----- C -----
"GL22c":[22,16,0.5,20,2.5,3.5,1.2,8600,250,540,10400,300,650,355,390],
"GL24c":[24,17,0.5,21.5,2.5,3.5,1.2,9100,250,540,11000,300,650,365,400],
"GL26c":[26,19,0.5,23.5,2.5,3.5,1.2,10000,250,540,12000,300,650,385,420],
"GL28c":[28,19.5,0.5,24,2.5,3.5,1.2,10400,250,540,12500,300,650,390,420],
"GL28cs":[28,19.5,0.5,24,2.5,3.5,1.2,10400,250,540,12500,300,650,390,430],
"GL30c":[30,19.5,0.5,24.5,2.5,3.5,1.2,10800,250,540,13000,300,650,390,430],
"GL32c":[32,19.5,0.5,24.5,2.5,3.5,1.2,11200,250,540,13500,300,650,400,440],

# ----- H -----
"GL22h":[22,17.6,0.5,22,2.5,3.5,1.2,8800,250,540,10500,300,650,370,410],
"GL24h":[24,19.2,0.5,24,2.5,3.5,1.2,9600,250,540,11500,300,650,385,420],
"GL26h":[26,20.8,0.5,26,2.5,3.5,1.2,10100,250,540,12100,300,650,405,445],
"GL28h":[28,22.4,0.5,28,2.5,3.5,1.2,10500,250,540,12600,300,650,425,460],
"GL28hs":[28,22.4,0.5,28,2.5,3.5,1.2,10500,250,540,13100,300,650,430,480],
"GL30h":[30,24,0.5,30,2.5,3.5,1.2,11300,250,540,13600,300,650,430,480],
"GL32h":[32,25.6,0.5,32,2.5,3.5,1.2,11800,250,540,14200,300,650,440,490],
}


def glulam(klass):
    if klass not in _GL_DATA:
        raise ValueError(f"Okänd GL-klass: {klass}")
    return np.array(_GL_DATA[klass], dtype=float)




def k_mod(Material, Klimatklass, Lastvaraktighet):
    if Material == 'Konstruktionsvirke':
        if Klimatklass == 1:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 2:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 3:
            if Lastvaraktighet == 'Permanent':
                val = 0.5
            elif Lastvaraktighet == 'Lång':
                val = 0.55
            elif Lastvaraktighet == 'Medel':
                val = 0.65
            elif Lastvaraktighet == 'Kort':
                val = 0.7
            elif Lastvaraktighet == 'Momentan':
                val = 0.9
        
    if Material == 'Limträ':
        if Klimatklass == 1:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 2:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 3:
            if Lastvaraktighet == 'Permanent':
                val = 0.5
            elif Lastvaraktighet == 'Lång':
                val = 0.55
            elif Lastvaraktighet == 'Medel':
                val = 0.65
            elif Lastvaraktighet == 'Kort':
                val = 0.7
            elif Lastvaraktighet == 'Momentan':
                val = 0.9
    if Material == 'Fanerträ':
        if Klimatklass == 1:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 2:
            if Lastvaraktighet == 'Permanent':
                val = 0.6
            elif Lastvaraktighet == 'Lång':
                val = 0.7
            elif Lastvaraktighet == 'Medel':
                val = 0.8
            elif Lastvaraktighet == 'Kort':
                val = 0.9
            elif Lastvaraktighet == 'Momentan':
                val = 1.1
        elif Klimatklass == 3:
            if Lastvaraktighet == 'Permanent':
                val = 0.5
            elif Lastvaraktighet == 'Lång':
                val = 0.55
            elif Lastvaraktighet == 'Medel':
                val = 0.65
            elif Lastvaraktighet == 'Kort':
                val = 0.7
            elif Lastvaraktighet == 'Momentan':
                val = 0.9

    display(Math(f"k_{{mod}} = {val}"))

    return val


# I förband mellan trämaterial med olika värden på k_mod:
# Använder *args så funktionen kan ta emot godtyckligt k_mod
def k_mod_flera(*k_mod_values):
    # Kontrollera att minst två värden finns
    if len(k_mod_values) < 2:
        raise ValueError("Minst två k_mod-värden krävs")

    # Multiplicera alla värden
    produkt = 1
    for val in k_mod_values:
        produkt *= val

    # Geometriskt medelvärde
    return math.sqrt(produkt)






# Gamma M för olika trämaterial
def gamma_M(Material):
    if Material == 'Konstruktionsvirke':
        val = 1.3
    elif Material == 'Limträ':
        val = 1.25
    elif Material == 'LVL':
        val = 1.2
    elif Material == 'Plywood':
        val = 1.2
    elif Material == 'OSB':
        val = 1.2
    elif Material == 'Spånskiva':
        val = 1.3
    elif Material == 'Träfiberskiva':
        val = 1.3
    elif Material == 'Träförband':
        val = 1.3
    elif Material == 'Spikförband':
        val = 1.25
    
    display(Math(f"\\gamma_M = {val}"))
    return val


# Dimensionerande hållfasthetsparameter
def f_d(k_mod, f_k, gamma_M):        
    val = k_mod * f_k / gamma_M
    return val


# För en del material och brottmoder kan storlekseffekter, även kallat volymeffekter, beaktas, se SS-EN 1995-1-1, 3.2-3.4
def k_h(Material, h, l=None, s=None, lasttyp=None):
    if Material == 'Konstruktionsvirke':
        if h < 150:
            val = min((150 / h)**0.2, 1.3)
        elif h >= 150:
            val = 1.0
    elif Material == 'Limträ':
        if h < 600:
            val = min((600/h)**0.1, 1.1)
        elif h >= 600:
            val = 1.0
    elif Material == 'LVL':
        if h != 300:
            if s is None:
                print("Ange värde på s (3.4.3)")
            elif s is not None and lasttyp == 'Böjning':
                val = min((300/h)**s, 1.2)
            elif s is not None and lasttyp == 'Dragning':
                val = min((300/l)**(s/2), 1.1)
        else:
                val = 1.0
    
    display(Math(f"k_h = {val}"))

    return val




# Böjning

def M_Rd(W, f_m_d):
    not_finished = W
    return None







# Axiell belastning

# Dragning

# f_t_0_d är dim. draghållf.
# A är tvärsnittsarea, med hänsyn taget till eventurella borrhål och slitsar
def N_t_0_Rd(f_t_0_d, A):
    val = f_t_0_d * A
    return val

# Bärförmågan drag vinkelrätt fiberrikningen
# där V_0 är referensvolym = 0.01 m^3, och V är dragpåverkad volym
def N_t_90_Rd(f_t_90_d, A, Material, V_0=None, V=None):
    if Material == 'Konstruktionsvirke':
        val = f_t_90_d * A
    elif Material == 'Limträ':
        val = (V_0 / V)**0.2 * f_t_90_d * A
    return val



# Tryck

# Bärförmågan tryck parallellt fiberrikningen
def N_c_0_Rd(f_c_0_d, A, I, l_e, E_005, Material):
    if Material == 'Konstruktionsvirke':
        β_c = 0.2
    elif Material == 'Limträ':
        β_c = 0.1
    elif Material == 'LVL':
        β_c = 0.1

    i = math.sqrt(I / A)
    λ = l_e / i
    λ_rel = λ / math.pi * math.sqrt(f_c_0_d / E_005)
    k = 0.5*(1 + β_c * (λ_rel - 0.3) + λ_rel**2)
    if λ_rel <= 0.3:
        k_c = 1
    elif λ_rel > 0.3:
        k_c = 1 / (k + math.sqrt(k**2 - λ_rel**2))
    val =  f_c_0_d * A * k_c
    return val





# Tvärkraft 6.??


def V_Rd(f_v_d, A):
    val = A * f_v_d / 1.5

    display(Math(f"V_{{Rd}} = {val/1000:.2f} \\text{{kN}}"))
    return val