#SS-EN 1993-1-1

# 6.6 
# För tvärnistt med hål anhålls dragbärförmågan från
def N_t_Rd_hål(A, f_y, gamma_M0, A_net, f_u, gamma_M2):
    N_pl_Rd = A * f_y / gamma_M0
    N_u_Rd = 0.9 * A_net * f_u / gamma_M2
    N_t_Rd = min(N_pl_Rd, N_u_Rd)
    return N_t_Rd




# Tryckkraft 6.2.4

def N_c_Rd(A, f_y, gamma_M0, tvk, A_eff=None):
    if tvk == 1 or tvk == 2 or tvk == 3:
        N_c_Rd = A * f_y / gamma_M0
    elif tvk == 4:
        N_c_Rd = A_eff * f_y / gamma_M0
    return N_c_Rd


# Böjmoment 6.2.5

def M_c_Rd(W_pl, f_y, gamma_M0, tvk, W_el_min=None, W_eff_min=None):
    if tvk == 1 or tvk == 2:
        M_c_Rd = W_pl * f_y / gamma_M0
    elif tvk == 3:
        M_c_Rd = W_el_min * f_y / gamma_M0
    elif tvk == 4:
        M_c_Rd = W_eff_min * f_y / gamma_M0

    return M_c_Rd

