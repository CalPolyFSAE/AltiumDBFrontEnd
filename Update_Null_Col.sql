UPDATE Altium.Resistor
SET `ComponentLink1Description` = 'Datasheet'
WHERE `ComponentLink1Description` IS NULL;
UPDATE Altium.Resistor
SET `Supplier1` = 'Digi-Key'
WHERE `Supplier1` IS NULL;