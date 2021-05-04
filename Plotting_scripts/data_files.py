"""Get data files based on date of run"""

import os
import sys
sys.path.append('../GPIB')
import get


def file_name_sorted(month=6, day=6, year=2016):
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
    print date
    path = os.path.join(get.googledrive(), 'Dielectric_data', 'Teddy', date)
    #print path
    filenames = os.listdir(path)
    filenames = [[string for string in filenames if '_sorted' in string]]
    #print filenames
    return filenames

def file_name(month=6, day=6, year=2016):
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
        #print filenames
    except:
        print 'failed'
        date = '%d/%d/%d' % (int(month), int(day), int(year))
        if date == '6/6/2016':
            filenames = [['Hystersis_Check_1465241637_08.csv',
                          # 'Cooling_1465249385_35.csv',
                          # 'Cooling_1465249536_82.csv',
                          # 'Cooling_1465249891_34.csv',
                          'Cooling_1465249997_01.csv',
                          # 'Cooling_1465253401_92.csv',
                          'Cooling_1465253519_52.csv',
                          'Cooling_1465254760_47.csv']]
        elif date == '6/7/2016':
            filenames = [['Hystersis_Check_1465318552_61.csv']]
        elif date == '6/8/2016':
            filenames = [['Bake_then_Cool_1465409960_31.csv',
                          'Cooling_1465419189_83.csv',
                          'Cooling_1465423486_76.csv',
                          'Cooling_1465424730_36.csv',
                          'Cooling_1465426315_04.csv',
                          'Cooling_1465426445_64.csv',
                          'Cooling_1465426500_31.csv',
                          'Cooling_1465427051_3.csv']]
        elif date == '6/9/2016':
            filenames = [['Bake_1465495585_84.csv',
                          'Bake_then_Cool_1465495585_84.csv']]
        elif date == '6/10/2016':
            # filenames = [['Bake_1465495585_84.csv',
            #              'Bake_then_Cool_1465495585_84.csv']]
            filenames = [['Bake_then_Cool_1465581362_09.csv',
                          'Bake_then_Cool_1465586145_01.csv']]
        elif date == '6/13/2016':
            filenames = [['Bake_then_Cool_1465836435_71.csv']]
        elif date == '6/14/2016':
            filenames = [['Bake_then_Cool_1465934539_76.csv']]
        elif date == '6/15/2016':
            filenames = [[#'Cool_1466007442_75.csv',
                          #'Cooling_1466018776_1.csv',
                          'Cooling_1466027990_95.csv',
                          'Cooling_1466030947_24.csv']]
        elif date == '6/16/2016':
            filenames = [['Cooling_1466096568_46.csv']]
        elif date == '6/17/2016':
            filenames = [['Cooling_1466202488_49.csv']]
        elif date == '6/20/2016':
            filenames = [['Cooling_1466465064_49.csv']]
        elif date == '6/21/2016':
            filenames = [['Cooling_1466634874_88.csv']]
        elif date == '6/22/2016':
            filenames = [['Cooling_1466612771_88.csv']]
        elif date == '6/24/2016':
            filenames = [['Cooling_1466792962_45.csv',
                          'Cooling_1466807602_43.csv',
                          'Cooling_1466814729_01.csv']]
        elif date == '6/25/2016':
            filenames = [['Cooling_1466814729_01.csv']]
        elif date == '6/27/2016':
            filenames = [['Cooling_1467046825_62.csv',
                          'Cooling_1467047885_55.csv',
                          'Cooling_1467087517_26.csv',
                          'Cooling_1467096780_85.csv',
                          'Cooling_1467135489_32.csv']]
        elif date == '6/29/2016':
            filenames = [[#'Cooling_1467229519_93.csv',          # testing light effects
                          #'Cooling_1467239746_39.csv',          # silver paint drying
                          'Cooling_1467242719_28.csv']]         # evacuating cryostat overnight
        elif date == '6/30/2016':
            filenames = [[#'Cooling_1467303130_77.csv',         # bare capacitor with silver paint
                          'Cooling_1467328927_66.csv',           # fixed after breaking
                          'Cooling_1467329599_73.csv'
                         ]]
        elif date == '7/1/2016':
            filenames = [['Cooling_1467411192_74.csv']]         # bare cap cooldown from 400K
        elif date == '7/5/2016':
            filenames = [['Cooling_1467736250_59.csv']]         # bare cap 2
        elif date == '7/6/2016':
            filenames = [['Cooling_1467823107_39.csv']]         # bare cap 3 quick
        elif date == '7/7/2016':
            filenames = [['Cooling_1467870309_81.csv']]
        elif date == '7/8/2016':
            filenames = [['Cooling_1467933473_96.csv']]         # over weekend and cool to 250K
        elif date == '7/11/2016':
            filenames = [[#'Cooling_1468266285_84.csv',
                          'Cooling_1468296326_83.csv']]
        elif date == '7/12/2016':
            filenames = [['Cooling_1468361439_48.csv']]         # tpp GBA140 cooldown
        elif date == '7/13/2016':
            filenames = [['Cooling_1468434924_25.csv']]         # GBA140 w/ helium
        elif date == '7/14/2016':
            filenames = [[
                          #'Cooling_1468535716_79.csv',           # curing silver epoxy
                          'Cooling_1468542662_31.csv'            # applying material GBA121
                        ]]
        elif date == '7/19/2016':
            filenames = [['Cooling_1468959484_96.csv']]         # GBA124
        elif date == '7/21/2016':
            filenames = [['Cooling_1469136462_36.csv']]         # Bake GBA141 overnight
        elif date == '7/22/2016':
            filenames = [['Cooling_1469206296_6.csv']]          # cool GBA141
        elif date == '8/17/2016':
            filenames = [['Cooling_1471469639_83.csv']]         # baking GBA139
        elif date == '8/18/2016':
            filenames = [['Cooling_1471542136_93.csv']]         # cooling GBA139
        elif date == '8/22/2016':
            filenames = [['Cooling_1471884642_89.csv']]         # cooling GBA140
        elif date == '8/24/2016':
            filenames = [['Cooling_1472062659_65.csv']]         # redoing GBA140
        elif date == '8/26/2016':
            filenames = [['Cooling_1472230025_75.csv']]         # cooling GBA 121
        elif date == '8/29/2016':
            filenames = [['Cooling_1472489387_2.csv']]
        else:
            filenames = [['']]
    return filenames