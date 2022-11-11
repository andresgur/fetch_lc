__all__ = ["convert_ra_dec"]


def convert_ra_dec(ra, dec):
    """Convert strings of Right Ascension and Declination into decimal format"""
    if ":" in ra:
        split_ra = ra.split(":")
    elif " " in ra:
        split_ra = ra.split(" ")
        ra = (float(split_ra[0]) + float(split_ra[1]) / 60 + float(split_ra[2]) / 3600) / 24 * 360
    else:
        ra = float(ra)

    if ":" in dec:
        split_dec = dec.split(":")
        dec = float(split_dec[0])
    elif " " in dec:
        split_dec = dec.split(" ")
        dec = float(split_dec[0])
        if dec<0:
            dec = float(split_dec[0]) - float(split_dec[1]) / 60 - float(split_dec[2]) / 3600
        else:
            dec =  float(split_dec[0]) + float(split_dec[1]) / 60  + float(split_dec[2]) / 3600
    else:
        dec = float(dec)
    return ra, dec
