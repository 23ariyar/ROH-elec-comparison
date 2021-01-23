import csv

filename = "csv.csv"

fields = []
democrats = {}
republicans = {}


with open(filename, 'r') as csvfile:
    csvreader = csv.reader(csvfile)

    fields = next(csvreader)
    
    rep_col = fields.index('REPUBLICANS')
    dem_col = fields.index('DEMOCRATS')
    
    for row in csvreader:
        republicans[row[rep_col]] = row[rep_col + 1]
        democrats[row[dem_col]] = row[dem_col + 1]
        