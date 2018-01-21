
class CPTableParser:
    ''' Retrieves the HTML scoreboard provided by the website and
    storees it as a pandas dataframe'''

    def parse_url(self, url):

        try:
            response = requests.get(url)

        except requests.exceptions.RequestException as e:
            logging.warning('No response from {} ({}).'.format(url, e))
            logging.debug(e)
            return []

        # Accumulate the responses (e.g., for simulation and debugging)
        # if (logging.getLogger().getEffectiveLevel() == 10):
        if (logging.getLogger().getEffectiveLevel() > 0):
            if not os.path.exists('./pages'):
                os.makedirs('./pages')

            fname = './pages/cpscore_' + time.strftime('%Y-%b-%d_%H%M', time.localtime()) + '.php'
            page = open(fname, 'w')
            page.write(response.text)
            page.close()

        soup = BeautifulSoup(response.text, 'lxml')

        return [(0, self.parse_html_table(table)) for table in
                soup.find_all('table')]

    def parse_html_table(self, table):
        n_columns = 0
        n_rows = 0
        column_names = []

        # Find number of rows, columns, and column titles
        for row in table.find_all('tr'):

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows += 1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 \
            else range(0, n_columns)

        df = pd.DataFrame(columns=columns,
                          index=range(0, n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker, column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        # Convert numberical columns to integers if possible
        for col in df:
            try:
                df[col] = df[col].astype(int)
            except ValueError:
                pass

        return df




def addplaces(tbl):
    # add the overall place as a column so that each row can be tracked
    # without depending on the context of the table index
    tbl['OverallPlace'] = [i for i in tbl.index]

    d = {}
    row = 1     # rows are 1-indexed because tbl[0] is the header row

    tbl['StatePlace'] = pd.Series([], dtype=object)
    for i in tbl['State']:   # add a column for place within states
        if i in d:
            d[i] += 1
        else:
            d[i] = 1
        tbl.loc[row, 'StatePlace'] = d[i]
        row += 1

    return (d, tbl)

def addalias(fname, tbl):
    ''' Reads and parses the lookup file and returns the contents as a dictionary.'''
    f = open(fname, 'r')
    dict = {}

    for line in f:
        if line[0] == '#':
            continue

        s = line.strip().split(',')

        if s[0] in dict:
            logging.error("Duplicate alias for team {} ({}). The existing alias {} is in use.".format(s[0], s[1], dict[s[0]]))
        try:
            dict[s[0]] = s[1]
        except IndexError:
            logging.error('Error in alias file. There is no alias provided for {}'.format(s[0]))

    f.close()

    tbl['TeamName'] = tbl['TeamNumber'].map(dict).fillna('')

    return tbl

def readteam(fname):
    ''' Reads and parses the team file, and returns the contents as a list.'''

    t = []
    with open(fname) as f:
        for line in f:
            s = line.strip()
            if s[0] != '#':
                t.append(s)
    return t