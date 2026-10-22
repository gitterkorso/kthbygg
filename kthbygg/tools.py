import math

# Tvärsnittsberäknare 

def tvärsnitt():
     # Fråga användaren om antalet delareor
    num_areas = int(input("Ange antalet delareor: "))

    # Initialisera listor
    widths = []
    heights = []
    distances_y = []
    distances_z = []

    # Hämta data från användaren
    for i in range(num_areas):
        print("Delarea", i + 1, "(i mm)")
        widths.append(float(input("  Bredd b: ")))
        heights.append(float(input("  Hojd h: ")))
        distances_y.append(float(input("  y-koord tp: ")))
        distances_z.append(float(input("  z-koord tp: ")))

    # Material och normalkraft
    f_yd = float(input("Ange f_yd [MPa]: "))
    N_Ed = float(input("Ange N_Ed [kN], tryck + : "))

    # Beräkna area
    areas = []
    for i in range(num_areas):
        areas.append(widths[i] * heights[i])

    # Lokala tröghetsmoment
    local_iyy = []
    local_izz = []
    for i in range(num_areas):
        local_iyy.append((1 / 12) * widths[i] * heights[i] ** 3)
        local_izz.append((1 / 12) * heights[i] * widths[i] ** 3)

    # Total area
    total_area = sum(areas)

    # Gemensam tyngdpunkt
    centroid_y = 0
    centroid_z = 0

    for i in range(num_areas):
        centroid_y += areas[i] * distances_y[i]
        centroid_z += areas[i] * distances_z[i]

    centroid_y = centroid_y / total_area
    centroid_z = centroid_z / total_area

    # Tröghetsmoment
    iyy = 0
    izz = 0

    for i in range(num_areas):
        dy = distances_y[i] - centroid_y
        dz = distances_z[i] - centroid_z

        iyy += local_iyy[i] + areas[i] * dz ** 2
        izz += local_izz[i] + areas[i] * dy ** 2

    # Bestäm ytterkanter
    y_min = distances_y[0] - widths[0] / 2
    y_max = distances_y[0] + widths[0] / 2
    z_min = distances_z[0] - heights[0] / 2
    z_max = distances_z[0] + heights[0] / 2

    for i in range(num_areas):
        y_left = distances_y[i] - widths[i] / 2
        y_right = distances_y[i] + widths[i] / 2
        z_top = distances_z[i] - heights[i] / 2
        z_bot = distances_z[i] + heights[i] / 2

        if y_left < y_min:
            y_min = y_left
        if y_right > y_max:
            y_max = y_right
        if z_top < z_min:
            z_min = z_top
        if z_bot > z_max:
            z_max = z_bot

    # Elastiska böjmotstånd, båda sidor
    c_top = centroid_z - z_min
    c_bot = z_max - centroid_z
    c_left = centroid_y - y_min
    c_right = y_max - centroid_y

    W_el_y_top = iyy / c_top
    W_el_y_bot = iyy / c_bot
    W_el_z_left = izz / c_left
    W_el_z_right = izz / c_right

    # Konservativa elastiska böjmotstånd
    if W_el_y_top < W_el_y_bot:
        W_el_y = W_el_y_top
    else:
        W_el_y = W_el_y_bot

    if W_el_z_left < W_el_z_right:
        W_el_z = W_el_z_left
    else:
        W_el_z = W_el_z_right

    # Omvandla N_Ed från kN till N
    N_Ed_N = N_Ed * 1000

    # Kontroll av rimlighet för plastisk analys
    delta_A = N_Ed_N / f_yd

    # Skriv ut grunddata
    print("Area A: {:.2f} mm^2".format(total_area))
    print("Tyngdpunkt: ({:.2f}, {:.2f}) mm".format(centroid_y, centroid_z))
    print("Iy: {:.2f} mm^4".format(iyy))
    print("Iz: {:.2f} mm^4".format(izz))
    print("W_el_y: {:.2f} mm^3".format(W_el_y))
    print("W_el_z: {:.2f} mm^3".format(W_el_z))

    if abs(delta_A) > total_area:
        print("Fel: |N_Ed/f_yd| > A")
        print("PNL kan inte bestammas")
        return None

    # Funktion: area ovanför en nivå z_line
    def area_above(z_line):
        a = 0
        for i in range(num_areas):
            z_top = distances_z[i] - heights[i] / 2
            z_bot = distances_z[i] + heights[i] / 2
            b = widths[i]
            h = heights[i]

            if z_line <= z_top:
                part = 0
            elif z_line >= z_bot:
                part = b * h
            else:
                part = b * (z_line - z_top)

            a += part
        return a

    # Funktion: area till vänster om en nivå y_line
    def area_left(y_line):
        a = 0
        for i in range(num_areas):
            y_left = distances_y[i] - widths[i] / 2
            y_right = distances_y[i] + widths[i] / 2
            b = widths[i]
            h = heights[i]

            if y_line <= y_left:
                part = 0
            elif y_line >= y_right:
                part = b * h
            else:
                part = h * (y_line - y_left)

            a += part
        return a

    # Målyta på trycksidan
    target_area = (total_area + delta_A) / 2

    # Bisektion för z_PNL
    low = z_min
    high = z_max

    for _ in range(50):
        mid = (low + high) / 2
        a_mid = area_above(mid)

        if a_mid < target_area:
            low = mid
        else:
            high = mid

    z_pnl = (low + high) / 2

    # Bisektion för y_PNL
    low = y_min
    high = y_max

    for _ in range(50):
        mid = (low + high) / 2
        a_mid = area_left(mid)

        if a_mid < target_area:
            low = mid
        else:
            high = mid

    y_pnl = (low + high) / 2

    print("z_PNL: {:.2f} mm".format(z_pnl))
    print("y_PNL: {:.2f} mm".format(y_pnl))

    # Plastiskt moment kring z_PNL, dvs M_pl_y
    M_pnl_y = 0

    for i in range(num_areas):
        b = widths[i]
        h = heights[i]
        zc = distances_z[i]

        z_top = zc - h / 2
        z_bot = zc + h / 2

        # Hela delarean ovanför PNL
        if z_bot <= z_pnl:
            force = f_yd * b * h
            lever = z_pnl - zc
            M_pnl_y += force * lever

        # Hela delarean under PNL
        elif z_top >= z_pnl:
            force = f_yd * b * h
            lever = zc - z_pnl
            M_pnl_y += force * lever

        # Delarean skärs av PNL
        else:
            h_top = z_pnl - z_top
            h_bot = z_bot - z_pnl

            force_top = f_yd * b * h_top
            lever_top = h_top / 2
            M_pnl_y += force_top * lever_top

            force_bot = f_yd * b * h_bot
            lever_bot = h_bot / 2
            M_pnl_y += force_bot * lever_bot

    # Plastiskt moment kring y_PNL, dvs M_pl_z
    M_pnl_z = 0

    for i in range(num_areas):
        b = widths[i]
        h = heights[i]
        yc = distances_y[i]

        y_left = yc - b / 2
        y_right = yc + b / 2

        # Hela delarean till vänster om PNL
        if y_right <= y_pnl:
            force = f_yd * b * h
            lever = y_pnl - yc
            M_pnl_z += force * lever

        # Hela delarean till höger om PNL
        elif y_left >= y_pnl:
            force = f_yd * b * h
            lever = yc - y_pnl
            M_pnl_z += force * lever

        # Delarean skärs av PNL
        else:
            b_left = y_pnl - y_left
            b_right = y_right - y_pnl

            force_left = f_yd * b_left * h
            lever_left = b_left / 2
            M_pnl_z += force_left * lever_left

            force_right = f_yd * b_right * h
            lever_right = b_right / 2
            M_pnl_z += force_right * lever_right

    # Flytta momenten från PNL till tyngdpunkten
    M_pl_y_N_Rd_Nmm = M_pnl_y - N_Ed_N * (z_pnl - centroid_z)
    M_pl_z_N_Rd_Nmm = M_pnl_z - N_Ed_N * (y_pnl - centroid_y)

    # Ta absolutbelopp för utskrift som motstånd
    if M_pl_y_N_Rd_Nmm < 0:
        M_pl_y_N_Rd_Nmm = -M_pl_y_N_Rd_Nmm

    if M_pl_z_N_Rd_Nmm < 0:
        M_pl_z_N_Rd_Nmm = -M_pl_z_N_Rd_Nmm

    # Plastiska böjmotstånd
    W_pl_y_N = M_pl_y_N_Rd_Nmm / f_yd
    W_pl_z_N = M_pl_z_N_Rd_Nmm / f_yd

    # Omvandla till kNm
    M_pl_y_N_Rd_kNm = M_pl_y_N_Rd_Nmm / 1000000
    M_pl_z_N_Rd_kNm = M_pl_z_N_Rd_Nmm / 1000000

    print("W_pl_y_N: {:.2f} mm^3".format(W_pl_y_N))
    print("W_pl_z_N: {:.2f} mm^3".format(W_pl_z_N))
    print("M_pl_y_N_Rd: {:.2f} kNm".format(M_pl_y_N_Rd_kNm))
    print("M_pl_z_N_Rd: {:.2f} kNm".format(M_pl_z_N_Rd_kNm))

    return {
        "A": total_area,
        "y_tp": centroid_y,
        "z_tp": centroid_z,
        "Iy": iyy,
        "Iz": izz,
        "W_el_y": W_el_y,
        "W_el_z": W_el_z,
        "y_PNL": y_pnl,
        "z_PNL": z_pnl,
        "W_pl_y_N": W_pl_y_N,
        "W_pl_z_N": W_pl_z_N,
        "M_pl_y_N_Rd_kNm": M_pl_y_N_Rd_kNm,
        "M_pl_z_N_Rd_kNm": M_pl_z_N_Rd_kNm
    }