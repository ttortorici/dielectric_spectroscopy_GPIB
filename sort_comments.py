import csv
import sys
import os
import itertools
import yaml
#import datetime
sys.path.append('GPIB')
import get


def get_comment(f):
    """Retrieve data file's comment"""
    try:
        with open(f, 'r') as fff:
            comment_list = next(itertools.islice(csv.reader(fff), 1, None))[0].strip('# ').split('... ')
        comment = '%s; %s; %s' % tuple(comment_list)
    except:
        with open(f, 'r') as fff:
            comment = next(itertools.islice(csv.reader(fff), 1, None))[0].strip('# ')
    return comment

def sort_comments():
    path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy')

    year_folders = os.listdir(path)

    comments = {}

    year_folders = [y for y in year_folders if '.' not in y]
    for yy in year_folders:
        month_folders = os.listdir(os.path.join(path, yy))
        month_folders = [m for m in month_folders if '.' not in m]
        for mm in month_folders:
            day_folders = os.listdir(os.path.join(path, yy, mm))
            day_folders = [d for d in day_folders if '.' not in d]
            for dd in day_folders:
                comments['%s-%s-%s' % (yy, mm, dd)] = {}
                file_list = os.listdir(os.path.join(path, yy, mm, dd))
                file_list = [f for f in file_list if '.csv' in f]
                for ff in file_list:
                    comments['%s-%s-%s' % (yy, mm, dd)][ff] = get_comment(os.path.join(path, yy, mm, dd, ff))

    print comments
    with open(os.path.join(path, 'comments.yml'), 'w') as outfile:
        yaml.dump(comments, outfile, default_flow_style=False)


if __name__ == '__main__':
    sort_comments()


"""# for sorting unsorted files into folders, shouldn't ever need to use again
for f in files:
    if 'csv' in f:
        timestamp = f.replace('.csv', '')
        timestamp = timestamp.replace('_','.')
        skip = 0
        cont = True
        while cont:
            try:
                timestamp = float(timestamp[skip:])
                cont = False
            except ValueError:
                skip += 1

        date = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d')

        print "data file: %s was taken on %s" % (f, date)"""



"""def file_name(month=6, day=6, year=2016):
    year = str(year)
    if len(year) == 2:
        year = '20' + year

    month = str(month)
    if len(month) == 1:
        month = '0' + month

    day = str(day)
    if len(day) == 1:
        month = '0' + day
    print "Set date is: %s/%s/%s" % (month, day, year)
    date = os.path.join(year, month, day)
    try:
        path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', date)
        #print path
        filenames = os.listdir(path)
        filenames = [[string for string in filenames if '.csv' in string]]
    return filenames"""