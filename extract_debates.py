from bs4 import BeautifulSoup
import random
import requests
import urllib.parse as urlparse

debate_page = "http://www.presidency.ucsb.edu/debates.php"
# Each debate transcript starts http://www.presidency.ucsb.edu/ws/index.php?
debate_prefix = "http://www.presidency.ucsb.edu/ws/index.php?"

class Crawler(object):

    def __init__(self):
        self.soup = None                       # Beautiful Soup object
        self.current_page = debate_page        # Current page's address
        self.debate_links = set()              # Queue with every debate_links fetched
        self.visited_links = set()

        self.counter = 0 # Simple counter for debug purpose

    def open(self):

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
                    # print("Adding link" + link + "\n")
                # elif link.startswith('/'):
                #     parts = urlparse.urlparse(self.current_page)
                #     page_links.append(parts.scheme + '://' + parts.netloc + link)
                #     print("Adding link " + parts.scheme + '://' + parts.netloc + link + "\n")
                # else:
                #     page_links.append(self.current_page+link)
                #     print("Adding link " + self.current_page+link + "\n")

        except Exception: # Magnificent exception handling
            pass

        # Update debate_links
        self.debate_links = self.debate_links.union(set(page_links))

        # Choose a random url from non-visited set
        self.current_page = random.sample(self.debate_links.difference(self.visited_links), 1)[0]
        self.counter+=1

    def run(self):

        # Crawl 3 webpages (or stop if all url has been fetched)
        while len(self.visited_links) < 1 or (self.visited_links == self.debate_links):
            self.open()

        for link in self.debate_links:
            print(link)

if __name__ == '__main__':
    C = Crawler()
    C.run()