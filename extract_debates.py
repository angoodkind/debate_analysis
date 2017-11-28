from bs4 import BeautifulSoup
import random
import requests
from datetime import datetime
import urllib.parse as urlparse

class Crawler(object):
    'Crawls an index of debates, stores each debate in a list. By default, this is the UCSB American Presidency Project database of presidential debates.'

    def __init__(self, index_page = "http://www.presidency.ucsb.edu/debates.php"):
        self.soup = None                       # Beautiful Soup object
        self.current_page = index_page         # Current page's address
        self.debate_links = set()              # Queue with every debate_links fetched
        self.visited_links = set()

        self.counter = 0 # Simple counter for debug purpose

    def open(self, debate_prefix = "http://www.presidency.ucsb.edu/ws/index.php?"):
        """ Open the index page, populate debate_links with links to each debate
        """

        # Open url
        # print(self.counter , ":", self.current_page)
        response = requests.get(self.current_page)
        self.visited_links.add(self.current_page)

        # Fetch every debate_links
        self.soup = BeautifulSoup(response.content, "html.parser")

        page_links = []
        try :
            for link in [h.get('href') for h in self.soup.find_all('a')]:
                # print("Found link: '" + link + "'")
                if link.startswith(debate_prefix):
                    page_links.append(link)

        except Exception: # Magnificent exception handling
            pass

        ### I copied this originally from a stackoverflow answer, ###
        ### and when I remove this, it screws it up. I don't know ###
        ### what it does thought                                  ###
        # Update debate_links
        self.debate_links = self.debate_links.union(set(page_links))
        # Choose a random url from non-visited set
        self.current_page = random.sample(self.debate_links.difference(self.visited_links), 1)[0]
        self.counter+=1

    def run(self):
        """ Get information about all the debates in the index.

        @return: list of debates, where each debate is a dictionary with keys:
            - name: title of the debate (string)
            - date
            - location: where debate was held, in format "City, State" (string)
            - text: raw HTML of debate
            - link: URL to the page of the debate
        """
        # list where debate content stored
        debate_dct_list = []

        # Crawl 3 webpages (or stop if all url has been fetched)
        while len(self.visited_links) < 1 or (self.visited_links == self.debate_links):
            self.open()

        for link in self.debate_links:
            # print(link)
            debate_response = requests.get(link)
            debate_soup = BeautifulSoup(debate_response.content, 'html.parser')
            ## this works, but returns a list with other info as well
            # debate_name = debate_soup.find_all('span', attrs={'class':'ver10'})
            debate_title = debate_soup.find('meta', attrs={'name':'title'})
            debate_full_title = debate_title['content']
            # only split on last '-' that separates name and date
            debate_name_date = debate_full_title.split(':')[1].rsplit("-", 1)
            # there are a few outliers. we can handle these later
            if len(debate_name_date) == 2:
                debate_name_loc = debate_name_date[0].strip().split(' in ')
                if len(debate_name_loc) == 2:
                    debate_name = debate_name_loc[0].strip()
                    debate_loc = debate_name_loc[1].strip()
                    debate_date_str = debate_name_date[1].strip()
                    debate_date = datetime.strptime(debate_date_str, '%B %d, %Y').date()
                    debate_text = debate_soup.find('span', {'class': 'displaytext'}).get_text()
                    # print(debate_text)

                    debate_dct_list.append({'name': debate_name,
                                            'date': debate_date,
                                            'location': debate_loc,
                                            'text': debate_text,
                                            'link': link})

            return debate_dct_list
            # break

    def debates

if __name__ == '__main__':
    C = Crawler()
    debate_dct_list = C.run()
    for debate in debate_dct_list:
        print(debate['name'], debate['date'], debate['location'], len(debate['text']), debate['link'])
