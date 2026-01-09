import math

def a_LT(I_t,I_y):
    val = 1 - (I_t / I_y)
    return val

def ε_y(N_Ed, M_y_Ed, W_y_el, A):
    val = (M_y_Ed * A)/ (W_y_el * N_Ed)
    return val

def ε_z(N_Ed, M_z_Ed, W_z_el, A):
    val = (M_z_Ed * A)/ (W_z_el * N_Ed)
    return val

def C_my(C_my0, a_LT, ε_y):
    val = C_my0 + (1 - C_my0) * ((math.sqrt(ε_y) * a_LT) / (1 + math.sqrt(ε_y) * a_LT))
    return val

def C_mz(C_mz0, a_LT, ε_z):
    val = C_mz0 + (1 - C_mz0) * ((math.sqrt(ε_z) * a_LT) / (1 + math.sqrt(ε_z) * a_LT))
    return val

def C_m_LT(C_my, a_LT, N_Ed, N_z_cr, N_t_cr):
    val = (C_my**2 * a_LT) / (math.sqrt((1 - (N_Ed / N_z_cr))*(1- (N_Ed / N_t_cr))))
    return val

def μ_y(N_Ed, N_y_cr, χ_y):
    val = ((1 - (N_Ed / N_y_cr)) / ((1 - χ_y*((N_Ed / N_y_cr)))))
    return val

def μ_z(N_Ed, N_z_cr, χ_z):
    val = ((1 - (N_Ed / N_z_cr)) / ((1 - χ_z*((N_Ed / N_z_cr)))))
    return val


# INTERAKTIONSFORMLER enligt EC3 6.3.3(4) tabell A1

def k_yy_LT(C_my, C_m_LT, μ_y, N_Ed, N_y_cr, tvk, C_yy=0):
    if tvk == 1 or tvk == 2:
         val = ((C_my * C_m_LT * μ_y) / (1 - (N_Ed / N_y_cr))) * (1/C_yy)
    if tvk == 3 or tvk == 4:
        val = (C_my * C_m_LT * μ_y) / (1 - (N_Ed / N_y_cr))
    return val

def k_yz_LT(C_mz, μ_y, N_Ed, N_z_cr, tvk, C_yz=0, w_z=0, w_y=0):
    if tvk == 1 or tvk == 2:
        val = ((C_mz * μ_y) / (1 - (N_Ed / N_z_cr))) * (1/C_yz) * 0.6 * (math.sqrt(w_z / w_y))
    if tvk == 3 or tvk == 4:   
        val = (C_mz * μ_y) / (1 - (N_Ed / N_z_cr))
    return val

def k_zy_LT(C_my, C_m_LT, μ_z, N_Ed, N_y_cr, tvk, C_zy=0, w_y=0, w_z=0):
    if tvk == 1 or tvk == 2:
        val = ((C_my * C_m_LT * μ_z) / (1 - (N_Ed / N_y_cr))) * (1/C_zy)* 0.6 * math.sqrt(w_y/w_z)
    if tvk == 3 or tvk == 4: 
        val = (C_my * C_m_LT * μ_z) / (1 - (N_Ed / N_y_cr))       
    return val

def k_zz_LT(C_mz, μ_z, N_Ed, N_z_cr, tvk, C_zz=0):
    if tvk == 1 or tvk == 2:
        val = ((C_mz * μ_z) / (1 - (N_Ed / N_z_cr))) * (1 / C_zz)
    if tvk == 3 or tvk == 4: 
        val = (C_mz * μ_z) / (1 - (N_Ed / N_z_cr))
    return val