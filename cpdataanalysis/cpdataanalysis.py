import cpsbimports as cp
import pandas as pd
import time
from random import randint
import os.path

def main():

    # [TODO] Create command line args
    url = 'http://scoreboard.uscyberpatriot.org/index.php?division=Middle%20School'
    afile = 'lookups'
    ofile = 'output'

    maintable= cp.getmaintable(url, afile)
    print('Retreived the main table. There are {} records.'.format(len(maintable.index)))

    newtable = pd.DataFrame()

    #  for each team in the table, navigate to the 'details' URL
    for index, row in maintable.iterrows():
        tnum = row['TeamNumber']
        print("\t[{} of {}] Fetching {}...".format(index, len(maintable.index), tnum))
        tmurl = "http://scoreboard.uscyberpatriot.org/team.php?team=" + tnum

        # [TODO] Implement queued threading to reduce time to fetch the stats
        tmtbl, tmgraph = cp.getteamtable(tmurl)

        for i, r in tmtbl.iterrows():
            for c in range(len(r.index)):
                if r.index[c] == 'Image':
                    continue
                else:
                    row[r.Image + '-' + r.index[c]] = r.values[c]
        newtable = newtable.append(row)

        tmgraph['Team'] = tnum

        wait = randint(3, 7)
        time.sleep(wait)

        fname = ofile + '.csv'
        if os.path.exists(fname):
            newtable.to_csv(fname, sep=',', mode = 'a', header = False)
        else:
            newtable.to_csv(fname + '.csv', sep=',')

        fname = ofile + '_times.csv'
        if os.path.exists(fname):
            tmgraph.to_csv(fname, sep=',', mode = 'a', header = False)
        else:
            tmgraph.to_csv(fname, sep=',')

    # [TODO] All new fields are 'char'; set fields to the appropriate data types (i.e., 'int')


if __name__ == "__main__":
    main()
