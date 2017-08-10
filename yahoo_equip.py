import sqlite3


all_equips = []
with sqlite3.connect('e:\\Python\\Crawler\\yahoo_new_car.sqlite3') as conn:
    cursor = conn.cursor()
    equips = cursor.execute('select equip from yahooNewCars')

    for item in equips:
        if len(item[0].strip()) > 0:
            equip = item[0].strip().split('|')
            all_equips += equip

all_equips = list(set(all_equips))
print(all_equips)
with open('yahoo_all_equip.csv', 'w', encoding='utf-8') as f:
    for eq in all_equips:
        f.write(eq + '\n')