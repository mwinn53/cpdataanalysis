import cpsbimports as cp
import pandas as pd
import time
from random import randint
import os.path
import argparse

pd.options.mode.chained_assignment = None

def main():

    # [TODO] Create command line args
    # Prep: Parse arguments for input
    parser = argparse.ArgumentParser(description='CyberPatriot Data Analysis Bot')

    parser.add_argument("url", help='URL to the Scoreboard', default="http://scoreboard.uscyberpatriot.org/index.php?division=Middle%20School")
    parser.add_argument('-t', "--team", help="Text file of team numbers to track (one per line).", default="lookups")
    parser.add_argument('-r', "--refresh", help="Refresh Interval (default: 5 seconds)")
    parser.add_argument('-o', "--output",
                        help="File name for output journal (default: 'output' in current directory)")
    args = parser.parse_args()

    # Positional arguments (mandatory)
    url = args.url
    afile = args.team

    if args.output:
        ofile = args.output
    else:
        ofile = 'output'

    if args.refresh:
        minwait = 1
        maxwait = int(args.refresh)

    maintable = cp.getmaintable(url, afile)
    maintable = maintable.sort_values(by='ScoredImages', ascending=False)
    starttime = time.time()
    print(
        'Start time {}'.format(time.ctime()))
    print('Retrieved the main table. There are {} records. Wait time will be randomized between 1 and {} seconds.'.format(len(maintable.index), maxwait))

    j = 0

    #  for each team in the table, navigate to the 'details' URL
    newtable = pd.DataFrame()
    newgraph = pd.DataFrame()

    for index, row in maintable.iterrows():
        tnum = row['TeamNumber']
        j += 1
        wait = randint(minwait, maxwait)

        for i in range(wait, 0, -1):
            print("\t[{} of {}] Fetching {}. Waiting for {} seconds... ({} picked from between 1 and {})".format(j, len(maintable.index), tnum, i, wait, maxwait), end='\r')
            time.sleep(1)

        tmurl = "http://scoreboard.uscyberpatriot.org/team.php?team=" + tnum

        # [TODO] Implement queued threading to reduce time to fetch the stats
        tmtbl, tmgraph = cp.getteamtable(tmurl)
        # print(tmtbl)

        for i, r in tmtbl.iterrows():
            # print("Showing index {} and row {}".format(i,r))  # troubleshooting
            for c in range(len(r.index)):
                # print("\tShowing {} in range {}".format(c,len(r.index)))  # troubleshooting
                if r.index[c] == 'Image':
                    # print("\t\t r.index is {}".format(r.index[c]))  # troubleshooting
                    continue
                else:
                    # print("\t\t row[{}-{}] is {}".format(r.Image,r.index[c], r.values[c]))  # troubleshooting
                    row[r.Image + '-' + r.index[c]] = r.values[c]
        newtable = newtable.append(row)
        # print(newtable) # troubleshooting

        tmgraph['Team'] = tnum
        newgraph = newgraph.append(tmgraph)

    print()
    fname = ofile + '.csv'
    newtable.sort_values(newtable.columns[0],axis=0, ascending=True, inplace=True)
    if os.path.exists(fname):
        newtable.to_csv(fname, sep=',', mode = 'a', header = False)
    else:
        newtable.to_csv(fname, sep=',', mode = 'w', header = True)

    fname = ofile + '_times.csv'
    if os.path.exists(fname):
        newgraph.to_csv(fname, sep=',', mode = 'a', header = False)
    else:
        newgraph.to_csv(fname, sep=',', mode = 'w', header = True)

    endtime = time.time()
    print("Finish Time {} ({})".format(time.ctime(),time.strftime("%H:%M %S", time.gmtime(endtime-starttime))))


if __name__ == "__main__":
    main()
