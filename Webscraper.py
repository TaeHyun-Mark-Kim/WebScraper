import pandas as pd
import urllib.request
from bs4 import BeautifulSoup
import re


#Need to install bs4 using the command 'pip install beatifulsoup4'

class Webscraper:

    def __init__(self):

        #Collects urls from a user-provided txt file
        txt_file = input('Please provide the name of txt file with request urls\n')
        with open(txt_file) as f:
            self.url_list = f.readlines()

        #List of initial urls
        self.url_list = [u.strip() for u in self.url_list]
        #Urls containing text files to process
        self.txt_list = []
        #regex templates to parse the data
        self.templates = self.generate_templates()
        #Pandas dataframe generated by each text file
        self.data_tables = []

    #For each txt url, create a pandas dataframe
    def txt_to_df(self):
        for url in self.txt_list:
            try:
                self.fn_txt(url)
            except:
                print("Failed to extract table from " + str(url))

    def url_to_csv(self, depth):
        self.scrap_txt_url(depth)
        print('URLs to Process: \n')
        self.print_txt_url()
        sample.txt_to_df()
        sample.print_tables()
        sample.df_to_csv()

    #Searchs web for txt files with the given depth
    def scrap_txt_url(self, depth):
        self.scrap_txt_urls_helper(self.url_list, 0, depth)

    #Recursive helper function for scrap_txt_url
    def scrap_txt_urls_helper(self, urls, count, limit):
        if count >= limit:
            for url in urls:
                if '.txt' in url or '.TXT' in url:
                    self.txt_list.append(url)
            return
        else:
            new_urls = []
            for url in urls:
                #If the url points to a text file, put it in a list to analyze later
                if '.txt' in url or '.TXT' in url:
                    self.txt_list.append(url)
                #If not, add the links contained within the page for further search
                else:
                    try:
                        URL_eg = urllib.request.urlopen(url)
                        soup = BeautifulSoup(URL_eg)
                        for link in soup.findAll('a', attrs={'href': re.compile("^http://")}):
                            #add links as new urls to process
                            new_url = link.get('href')
                            new_urls.append(new_url)
                    except:
                        print("Couldn't connect to a link " + str(url))
                self.scrap_txt_urls_helper(new_urls, count+1, limit)

    def generate_templates(self):
        template_list = []
        """
        To parse the data into separate columns, regex templates need to be
        hard-coded and added to the list
        """
        #regex based on http://www.ksbc.kerala.gov.in/circular/prmtrlisthigh1218.txt
        template1 = '.*\s(?P<SERIAL_NO>[0-9]+)\s(?P<ITEM_CODE>[0-9][0-9][0-9][0-9][0-9][0-9]).*\s(?P<DESCRIPTION>[A-Z].*[A-Z]).*\s(?P<MAX_AMOUNT>[0-9]+[.][0-9][0-9]).*'
        template_list.append(template1)

        #User's custom templates...

        return template_list

    #Determines whether given textfile's contents matches template
    def match_template(self, txt_content, tmp):
        limit = max(len(txt_content), 50)
        found = False
        i = 0
        #Check first 50 lines to see if there's a match
        while found is False and i < limit:
            match = re.match(tmp, str(txt_content[i]))
            if match:
                found = True
            i +=1
        return found

    def fn_txt(self, url):
        print('Reading ' + url + '...')
        #First, add dataframe with no column separation
        URL_eg = urllib.request.urlopen(url)
        df = pd.read_csv(URL_eg, sep='\t')
        self.data_tables.append(df)

        #If text file's contents match any of the templates,
        #add the column-separated data table
        myfile = urllib.request.urlopen(url)
        data = myfile.readlines()
        for t in self.templates:
            if self.match_template(data, t):
                print('match!')
                dict_list = []
                for line in data:
                    match = re.match(t, str(line))
                    if match:
                        dict_list.append(match.groupdict())
                new_df = pd.DataFrame(dict_list)
                self.data_tables.append(new_df)
                break

    def print_txt_url(self):
        print(self.txt_list)

    def print_tables(self):
        for t in self.data_tables:
            print(t)

    #Merge tables gathered from different txt files into a single dataframe
    def merge_tables(self):
        result = pd.concat(self.data_tables)
        return result

    #Converts all datatables into csvfiles
    def df_to_csv(self):
        #Uncomment below block if the user wants to merge all tables from different txt files
        """"
        final_table = self.merge_tables()
        self.data_tables.append(final_table)
        """
        count = 1
        for t in self.data_tables:
            try:
                if len(t.columns.values) is 0:
                    t.to_csv('data' + str(count) + '.csv', sep='\t', encoding='utf-8', index=True)
                else:
                    t.to_csv('data' + str(count) + '.csv', columns=t.columns.values, index=True)
            except:
                print('Failed to convert a dataframe into csv')
            finally:
                count+=1


sample = Webscraper()
sample.url_to_csv(depth=1)
"""
sample.scrap_txt_url(2)
sample.print_txt_url()
sample.txt_to_df()
sample.print_tables()
sample.df_to_csv()
"""
