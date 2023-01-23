# Postup inštalácie a spustenia skriptu

1. Začnite inštáláciou požadovaných knižíc uvedených v súbore requirements.txt.
2. Inštaláciu spustite príkazom `pip install -r requirements.txt`.
3. Uistite sa, že máte nainštalovanú najnovšiu verziu RFEM 6.
4. V súbore `tensegrity.py` nastavte počet iterácií v riadku č.99.
5. Po spustení skriptu sa začnú vstupy a výsledky zapisovať do súboru `data.csv`.
6. Priebeh výpočtu môžete sledovať v konzole.

## Súbor data.csv

1. riadok čísla prútov
2. riadok typy prútov
3. riadok vygenerované sily - vstupy
4. riadok výsledky výpočtu - výstupy

Prvý člen v každom riadku je číslo iterácie.
Ak spustíte výpočet viac ako raz, číslo iterácie sa vyresetuje na 0 a znova sa zapíšu čísla a typy prútov.
Pre lepšie pochopenie som zanechal testovacie dáta v súbore `data.csv`.
Pred spustením skriptu, môžete tieto dáta vymazať.
