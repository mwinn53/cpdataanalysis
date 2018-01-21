import cpsbimports as cp
import pandas as pd
import time
from random import randint

def main():

    url = 'http://scoreboard.uscyberpatriot.org/index.php?division=Middle%20School'
    afile = 'lookups'
    ofile = 'output.csv'

    maintable= cp.getmaintable(url, afile)
    print('Retreived the main table. There are {} records.'.format(len(maintable.index)))

    newtable = pd.DataFrame()
    #  for each team in the table, navigate to the 'details' URL
    for index, row in maintable.iterrows():
        tnum = row['TeamNumber']
        print("\t[{} of {}] Fetching {}...".format(index, len(maintable.index), tnum))
        tmurl = "http://scoreboard.uscyberpatriot.org/team.php?team=" + row['TeamNumber']

        tmtbl = cp.getteamtable(tmurl)

        for i, r in tmtbl.iterrows():
            for c in range(len(r.index)):
                if r.index[c] == 'Image':
                    continue
                else:
                    row[r.Image + '-' + r.index[c]] = r.values[c]
        newtable = newtable.append(row)

        # [TODO] Grab all of the time series data from

        wait = randint(3, 7)
        time.sleep(wait)

        newtable.to_csv(ofile, sep=',')

    # [TODO] All new fields are 'char'; set fields to the appropriate data types (i.e., 'int')



if __name__ == "__main__":
    main()
