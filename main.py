# CSVMaker. Class will make a CSV that can be used by mysql workbench
# to inject into the database manually
import csv
from decimal import *

def main():
    # Creating main connection
    # Capacitors
    getcontext().prec = 4
    vRatings = ['16V', '25V', '50V']
    pF = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6, 1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
          3.3, 3.6, 3.9, 4.3, 4.7, 5.1, 5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

    uF = [0.01, 0.015, 0.022, 0.033, 0.047, 0.068]
    multiples = [1, 10, 100, 1000]
    units = ['pf', 'uf']
    packages = ['CAP 0402/1005', 'CAP 0603/1608', 'CAP 0805/2012']
    symbol = 'Capacitors'
    dielectric = 'Ceramic'
    symbolsPath = 'Symbols/Passives.schlib'
    footprintPath = 'Footprints/Passives.Pcblib'
    date = '2018-10-20'
    creator = 'Nick Mah'
    # Figure out how to define name
    with open('Capacitors.csv', 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Writing Header
        csvWriter.writerow(['"Name"', '"Value"', '"Voltage_Rating"', '"Dielectric"', '"Package"', '"Comment"', '"Created_By"',
                            '"Created_Date"', '"Library Ref"', '"Library Path"', '"Footprint Ref"', '"Footprint Path"'])
        # csvWriter.writerow(['test', '10k', '1%', '1/4W', '0402', 'Tester', 'Nick Mah', '2018-10-20', 'Capacitors', 'Symbols', '0402/1005','Footprints'])
        for vRating in vRatings:
            for package in packages:
                if(package == '0402'):
                    lastUF = uF[0]  # 10uF is last value
                elif(package == '0603'):
                    lastUF = uF[0:2]  # 22uF is last value
                else:
                    lastUF = uF[0:4]  # 47uF is last value
                    for unit in units:
                        if(unit == 'pf'):
                            capacitors = pF
                        else:
                            capacitors = uF
                        for multiple in multiples:
                            if(unit == 'uF' and multiple == 1000):
                                capacitors = lastUF  # use truncated uF for last iteration
                            for capacitor in capacitors:
                                capacitor = Decimal(capacitor)
                                # capacitor *= 1000
                                # capacitor = round(capacitor)
                                # capacitor /= 1000
                                capacitor *= Decimal(multiple)
                                if capacitor >= 9.9:
                                    capacitor = int(capacitor)   
                                elif(capacitor >= .99):
                                    capacitor = round(capacitor,1)
                                elif(capacitor >= .099):
                                    capacitor = round(capacitor,2)
                                elif(capacitor >= .0099):
                                    capacitor = round(capacitor, 3)
                                elif(capacitor >= .00099):
                                    capacitor = round(capacitor, 4)
                                else:
                                    capacitor = round(capacitor, 5)                                
                                name = 'Cap_{value}{unit}_{vRating}_{package}'.format(
                                    value=capacitor, unit=unit, package=package, vRating=vRating)
                                comment = 'Capacitor MLCC {value}{unit} {vRating} {package}'.format(
                                    value=capacitor, unit=unit, package=package, vRating=vRating)
                                csvWriter.writerow([name, '{}{}'.format(
                                    capacitor, unit), vRating, dielectric, package, comment, creator, date, symbol, symbolsPath, package, footprintPath])


if __name__ == "__main__":
    main()
