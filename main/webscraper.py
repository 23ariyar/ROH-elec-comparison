from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError
import requests
import time
import html2text
import csv
from database import PolDB

def hms_string(sec_elapsed: int) -> str:
    """
    Gets time in Hour:Minutes:Seconds
    :param sec_elapsed: seconds elapsed
    :return: Hour:Minutes:Seconds
    """
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)

def is_valid(url: str) -> bool:
    """
    Checks whether `url` is a valid URL.
    
    NOTES: The scheme identifies the protocol to be used to access the resource on the Internet. It can be HTTP (without SSL) or HTTPS (with SSL)
    NOTES: general structure of a URL: scheme://netloc/path;parameters?
    NOTES: netloc (which stands for network locality) is what the first level domain (FLD) represents
    """
    parsed = urlparse(url) #urlparse return characteristics of the url like netloc and scheme
    return bool(parsed.netloc) and bool(parsed.scheme) #if there is a scheme and netloc, it is a valid url

def get_all_website_links(url: str) -> list:
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()

    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc

    soup = BeautifulSoup(requests.get(url).content, "html.parser") #r.content = binary, r.text = unicode

    for a_tag in soup.findAll("a"): #finds all the <a> tags in this soup
        href = a_tag.attrs.get("href") #href is an attribute
        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)

        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        
        if not is_valid(href):
            # not a valid URL
            continue

        if domain_name not in href:
            #still an internal link
            continue

        urls.add(href)
        
    return urls

def get_text(url: str) -> str:
    def text_cleaner(text):
        while True:
            beg = text.find('![')
            end = text.find(')', beg)
            if beg != -1 and end != -1:
                text = text.replace(text[beg:end+1], '')
            else:
                return text

    h = html2text.HTML2Text()
    h.ignore_links = True
    soup = BeautifulSoup(requests.get(url).content, "html.parser")
    return  text_cleaner(h.handle(soup.prettify()))

def spider_scraper(base: str) -> str:
    urls = get_all_website_links(base)

    my_str = ''
    try: my_str = get_text(base)
    except: print('Skipped: ' + base)

    for url in urls:
        try: my_str = my_str + get_text(url)
        except: print('Skipped: ' + url) 
        
    return my_str

def read_csv(filename: str): 
    fields = []
    democrats = {}
    republicans = {}

    with open(filename, 'r') as csvfile:
        csvreader = csv.reader(csvfile)

        fields = next(csvreader)
        
        rep_col = fields.index('REPUBLICANS')
        dem_col = fields.index('DEMOCRATS')
        
        for row in csvreader:
            republicans[row[rep_col]] = row[rep_col + 1]
            democrats[row[dem_col]] = row[dem_col + 1]
    
    return (democrats, republicans)

if __name__ == '__main__':

    f = open("text.txt", "w")
    f.write(spider_scraper("https://www.zachfornorthdakota.com/"))
    f.close()
    """
    db = PolDB('politician.db')
    (democrats, republicans) = read_csv('politicians.csv')

    for person, base_url in democrats.items():
        text = spider_scraper(base_url)
        db.insert(base_url, person, text, 'D')

    print('Done.')
    """