import csv

filename = '/Users/rogerslab/Google_Drive/Dielectric_data/Teddy/2017/03/21/Cooling_1490123956_96.csv'
filename2= '/Users/rogerslab/Google_Drive/Dielectric_data/Teddy/2017/03/21/Cooling_1490123956_96_2.csv'

rows = []
with open(filename, 'r') as f:
    reader = csv.reader(f, delimiter='@')
    for row in reader:
        rows.append(row)
print repr(rows[:10])
with open(filename2, 'wb') as f:
    writer = csv.writer(f)
    for row in rows:
        writer.writerow([row[0].strip(',')])
