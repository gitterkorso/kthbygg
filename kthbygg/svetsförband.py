def β_w(material):
    # Korrelationsfaktor som beaktar att tillsatsmaterialet normalt har högre brotspänning än det grundmaterialet
    if 'S235' in material:
        return 0.8
    elif 'S275' in material:
        return 0.85
    elif 'S355' in material:
        return 0.9
    elif 'S420' in material:
        return 1.0
    elif 'S460' in material:
        return 1.0
    else:
        raise ValueError("Okänt material: {}".format(material))

