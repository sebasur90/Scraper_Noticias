import csv
import os
if not os.path.exists('./diarios.csv'): # valores por defecto
    with open('./diarios.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["diario", "seccion", "rss"])
        writer.writerow(["Telam", "Economia", "https://www.telam.com.ar/rss2/economia.xml"])
if not os.path.exists('./diarios/diarios_historicos.csv'): # valores por defecto
    with open('./diarios/diarios_historicos.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(["diario", "seccion", "titulo", "descripcion", "sentimiento", "pond_negativos", "pond_neutro", "pond_positivo"])

with open('./diarios.csv', 'r') as f:
    reader = csv.reader(f)
    diarios = {}
    n = 0
    for row in reader:
        if row[0] == 'diario':
            continue
        diarios[n] = {'diario': row[0], 'seccion': row[1], 'rss' : row[2]}
        n += 1
