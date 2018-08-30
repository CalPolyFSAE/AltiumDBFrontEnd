# CSVMaker. Class will make a CSV that can be used by mysql workbench
# to inject into the database manually
import csv


def main():
    # Creating main connection
    # Resistors
    tolerances = [1, 5, 10]
    E12 = [1.0, 1.2, 1.5,
           1.8, 2.2, 2.7,
           3.3, 3.9, 4.7,
           5.6, 6.8, 8.2]

    E24 = [1.0,	1.1, 1.2,
           1.3,	1.5, 1.6,
           1.8,	2.0, 2.2,
           2.4,	2.7, 3.0,
           3.3,	3.6, 3.9,
           4.3,	4.7, 5.1,
           5.6,	6.2, 6.8,
           7.5,	8.2, 9.1]
    multiples = [1, 10, 100]
    units = ['', 'k', 'M']
    packages = ['0402', '0603', '0805']
    powers = ['1/10W', '1/4W', '1/2W']
    symbol = 'Resistor'
    symbolsPath = 'Symbols/Passives.schlib'
    footprintPath = 'Footprints/Passibes.Pcblib'
    date = '2018-10-20'
    creator = 'Nick Mah'
    # Figure out how to define name
    with open('Resistors.csv', 'w', newline='') as csvfile:
        csvWriter = csv.writer(csvfile, delimiter=',',
                               quotechar='|', quoting=csv.QUOTE_MINIMAL)
        # Writing Header
        csvWriter.writerow(['Name', 'Value', 'Tolerance', 'Power', 'Package', 'Comment', 'Created_By',
                            'Created_Date', 'Library Ref', 'Library Path', 'Footprint Ref', 'Footprint Path'])
        # csvWriter.writerow(['test', '10k', '1%', '1/4W', '0402', 'Tester', 'Nick Mah', '2018-10-20', 'Resistor', 'Symbols', '0402/1005','Footprints'])
        for tolerance in tolerances:
            if(tolerance == 1 or tolerance == 5):
                resistances = E24
            else:
                resistances = E12
            for package in packages:
                if(package == '0402'):
                    newPowers = ['1/10W']
                elif(package == '0603'):
                    newPowers = powers[0:1]
                else:
                    newPowers = powers
                for power in newPowers:
                    for unit in units:
                        for multiple in multiples:
                            for resistance in resistances:
                                resistance = round(resistance * multiple, 1)
                                if multiple != 1:
                                    resistance = int(resistance)
                                name = 'Res_{value}{unit}_{package}_{power}_{tolerance}%'.format(
                                    value=resistance, unit=unit, package=package, power=power, tolerance=tolerance)
                                comment = 'Resistor {value}{unit} {package} {power} {tolerance}%'.format(
                                    value=resistance, unit=unit, package=package, power=power, tolerance=tolerance)
                                csvWriter.writerow([name, '{}{}'.format(resistance, unit), '{}%'.format(
                                    tolerance), power, package, comment, creator, date, symbol, symbolsPath, package, footprintPath])


if __name__ == "__main__":
    main()
