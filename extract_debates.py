from bs4 import BeautifulSoup
import random
import re
import requests
from datetime import datetime
import urllib.parse as urlparse
from sentiment import analyze_utterances
import affiliations

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
        self.soup = BeautifulSoup(response.content, 'html.parser')

        page_links = []
        try :
            for link in [h.get('href') for h in self.soup.find_all('a')]:
                # limit analysis to most recent debates for now
                if link.startswith(debate_prefix) and (int(link.split('=')[-1]) >= 110489):
                    page_links.append(link)

        except Exception: # Magnificent exception handling
            pass

        ### I copied this originally from a stackoverflow answer, ###
        ### and when I remove this, it screws it up. I don't know ###
        ### what it does though                                  ###
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
            - text: raw HTML of debate contents (string)
            - link: URL to the page of the debate (string)
        """
        # list where debate content stored
        debate_dct_list = []

        # Crawl 3 webpages (or stop if all url has been fetched)
        while len(self.visited_links) < 1 or (self.visited_links == self.debate_links):
            self.open()

        for link in self.debate_links:
            debate_response = requests.get(link)
            response_content = str(debate_response.content)

            # fix <p> issue
            # extract contents of "displaytext" span
            span_pattern = re.compile(r'<span class=\"displaytext\">(.*)</span>')
            debate_html = span_pattern.search(response_content).group(1)
            debate_html_original = debate_html

            # replace internal <p> with proper paragraph breaks
            debate_html = re.sub(r'><',r'> <', debate_html) # this is kludgy but whatever
            debate_html = re.sub(r'((?<!</[P|p]>).)(<[p|P]>)', r'\1</p>\n<p>', debate_html)

            # wrap the whole debate contents in <p> and </p>
            if not re.match(r'<[p|P]>', debate_html):
                debate_html = '<p>' + debate_html
            debate_html = debate_html + '</p>'

            debate_soup = BeautifulSoup(response_content, 'html.parser')
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

                    debate_dct_list.append({'name': debate_name,
                                            'date': debate_date,
                                            'location': debate_loc,
                                            'html': debate_html,
                                            'link': link})

            # break
        return debate_dct_list

class Debate(object):
    'Stores a debate as a structured object.'

    def __init__(self, debate_dict):
        self.name = debate_dict['name']
        self.date = debate_dict['date']
        self.location = debate_dict['location']
        self.html = debate_dict['html']
        self.link = debate_dict['link']

    def get_lines(self):
        """ Get all utterances in the debate.

        @return: a list of utterances in the debate, where each line is a dictionary with the following keys:
        - speaker: speaker's name
        - text: text of the utterance
        """
        soup = BeautifulSoup(self.html, 'html.parser')
        p_list = soup.find_all('p')
        line_list = []

        # set a 'pointer' to the current speaker and line, for multiline utterances.
        current_speaker = ""
        current_line = ""
        current_index = 0
        for p in p_list:
            # get speaker

            # change the speaker, if speaker tag present
            if p.find('b'):
                # find bold words
                bold_text = p.b.get_text()
                bold_text = re.sub(r'\\', r'', bold_text) # remove backslashes

                # extract speaker tag
                name_pattern = re.compile(r'(\w|\'-)+')
                if re.search(name_pattern, bold_text):
                    # first word in bold text, including symbols that can be inside names
                    speaker = re.search(name_pattern, bold_text).group(0).title()

                    # add a new line of dialogue to results list
                    if not re.search(r'^(Participants|Moderators?)', speaker):
                        # change speaker
                        current_speaker = speaker
                        current_line = p.get_text()
                        # remove speaker tag from line
                        current_line = ":".join(current_line.split(":")[1:])

                        # write utterance
                        line_list.append({
                            'speaker': current_speaker,
                            'text': current_line
                        })
                        current_index += 1

            # if same speaker from previous utterance (and that speaker is set), attach this line to previous, separated by a newline character
            elif current_speaker != "":
                line_list[current_index - 1]['text'] += '\n ' + p.get_text()

        return line_list

if __name__ == '__main__':
    C = Crawler()
    debate_dct_list = C.run()
    sorted_debate_dct_list = sorted(debate_dct_list, key=lambda k : k['date'])
    affil_dct = affiliations.get_affil_dct()

    for debate in sorted_debate_dct_list:
        print(debate['name'], debate['date'], debate['location'], len(debate['html']), debate['link'])

        analysis = Debate(debate)
        print(len(analysis.get_lines()), 'utterances in this debate')

        # sentiment analysis
        sentiment_list = ['neg', 'neu', 'pos', 'compound']
        debate_sentiment_dct = analyze_utterances(analysis.get_lines())
        # debate ID
        debate_namedate = "{}_{}".format(debate['name'].replace(" ","_"),debate['date'])

        # print sentiment scores to csv
        with open('sentiment_values.csv', 'a') as sentiment_csv:
            for speaker, speaker_sentiments in debate_sentiment_dct.items():
                for sentiment in sentiment_list:
                    # print("{},{},{},{}".format(debate_namedate,
                    #                            speaker,
                    #                            sentiment,
                    #                            speaker_sentiments[sentiment]))
                    sentiment_csv.write("{},{},{},{},{}\n".format(
                        debate_namedate,
                        speaker,
                        affil_dct[speaker],
                        sentiment,
                        speaker_sentiments[sentiment]))
        # # break
