def determine_year(license_plate):
    license_plate = license_plate.upper()
    
    if len(list(license_plate)) > 7:
        if license_plate[:3] >= "AF":
            return 2023
        elif "AF" <= license_plate[:2] < "AE":
            return 2022
        elif "AE" <= license_plate[:2] < "AD":
            if int(license_plate[3:6]) >= 600:
                return 2021
            else:
                return 2020
        elif "AD" <= license_plate[:2] < "AC":
            return 2019
        elif "AC" <= license_plate[:2] < "AA":
            return 2018
        elif license_plate[:3] >= "AA":
            return 2017
    else:
        if license_plate[:2] == "PM":
            return 2016
        elif "ON" <= license_plate[:2] < "PM":
            return 2015
        elif "NM" <= license_plate[:2] < "ON":
            return 2014
        elif "MB" <= license_plate[:2] < "NM":
            return 2013
        elif "KU" <= license_plate[:2] < "MB":
            return 2012
        elif "JN" <= license_plate[:2] < "KU":
            return 2011
        elif "IM" <= license_plate[:2] < "JN":
            return 2010
        elif "HT" <= license_plate[:2] < "IM":
            return 2009
        elif "GV" <= license_plate[:2] < "HT":
            return 2008
        elif "GB" <= license_plate[:2] < "GV":
            return 2007
        elif "FI" <= license_plate[:2] < "GB":
            return 2006
        elif "ET" <= license_plate[:2] < "FI":
            return 2005
        elif "EI" <= license_plate[:2] < "ET":
            return 2004
        elif "ED" <= license_plate[:2] < "EI":
            return 2003
        elif "DX" <= license_plate[:2] < "ED":
            return 2002
        elif "DO" <= license_plate[:2] < "DX":
            return 2001
        elif "DC" <= license_plate[:2] < "DO":
            return 2000
        elif "CM" <= license_plate[:2] < "DC":
            return 1999
        elif "BU" <= license_plate[:2] < "CM":
            return 1998
        elif "BD" <= license_plate[:2] < "BU":
            return 1997
        elif "AP" <= license_plate[:2] < "BD":
            return 1996
        else:
            return "<1995"

print(determine_year("KIA 976"))