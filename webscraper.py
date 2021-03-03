from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import time
import html2text
import csv
import nltk
from database import PolDB_Text

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

    from https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/

    NOTES: The scheme identifies the protocol to be used to access the resource on the Internet. It can be HTTP (without SSL) or HTTPS (with SSL)
    NOTES: general structure of a URL: scheme://netloc/path;parameters?
    NOTES: netloc (which stands for network locality) is what the first level domain (FLD) represents
    """
    parsed = urlparse(url) #urlparse return characteristics of the url like netloc and scheme
    return bool(parsed.netloc) and bool(parsed.scheme) #if there is a scheme and netloc, it is a valid url

def get_all_website_links(url: str) -> list:
    """
    Returns all URLs that is found on `url` in which it belongs to the same website

    modified from https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python
    """
    # all URLs of `url`
    urls = set()
    image_urls = set()
    social_urls = set()


    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc

    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "html.parser") #r.content = binary, r.text = unicode

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
        
        if href[-3:] == 'jpg' or href[-3:] == 'png' or href[-4:] == 'jpeg':
            #image link
            image_urls.add(href)
            continue
        
        if 'twitter' in href or 'instagram' in href or 'facebook' in href or 'tiktok' in href:
            social_urls.add(href)


        if domain_name not in href:
            #still an internal link
            continue

        urls.add(href)


    return urls, social_urls

def get_text(url: str, min_wc_sentence: int = 5) -> str:
    """
    Returns the text of a given url by using HTML2Text

    :param url: a valid url as defined by is_valid
    :param min_wc_sentence: a minimum amount of words that line should have. defaults to 5
    :param images: determines wether to return image urls found
    :return: the text of the url
    """
    def text_cleaner(text):
        """
        Cleans text for images, filtered words, and non english words
        """
        #removes images and their captions
        while True:
            beg = text.find('![')
            end = text.find(']', beg)
            if beg != -1 and end != -1:
                text = text.replace(text[beg:end+1], '')
            else:
                break

        #if a line has like than 5 words, don't include it. this gets rid of things like donate now, etc.
        #text = ' '.join([line for line in text.split('\n') if len(line.split()) >= min_wc_sentence])

        #removes non english words, do this when most of the words are removed, length process
        text = " ".join(w for w in nltk.wordpunct_tokenize(text) if w.lower() in WORDS or not w.isalpha())

        #removes words in filter
        for word in FTR:
            text = text.replace(word, '')
         
        return text

    
    headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:55.0) Gecko/20100101 Firefox/55.0',
    }

    h = html2text.HTML2Text()
    h.ignore_links = True
    soup = BeautifulSoup(requests.get(url, headers = headers).content, "html.parser", from_encoding="iso-8859-1")
    return  text_cleaner(h.handle(soup.prettify()))

def complete_scraper(base: str) -> str:
    """
    Given a url, this function will scrape the website for all other urls
    and return the text of all found urls

    :param base: a valid url as defined by is_valid
    """
    urls = []
    
    try: urls, sm_urls = get_all_website_links(base)
    except: print ('Could not scrape for website links for: ' + base)
    
    my_str = ''
    
    try: my_str = get_text(base)
    except: print('Skipped: ' + base)
    
    for url in urls:
        #don't read .pdf and .mp3 links
        if url[-3: ] == 'pdf' or url[-3: ] == 'mp3': continue
        
        
        try: my_str = my_str + get_text(url)
        except: print('Skipped: ' + url) 
        
    return my_str, sm_urls

def read_csv(filename: str) -> tuple: 
    """
    :param filename: a valid .csv file that has columns mapping politicians to their campaign urls
    :return: returns a tuple of dictionaries mapping politicains to their campaign website

    """
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

def iterate_over(my_dict: dict, party: str, database: PolDB_Text) -> None:
    for num, (person, base_url) in enumerate(my_dict.items()):
        text, sm_urls = complete_scraper(base_url)
        print(str(num + 1) + ") Done with base_url: " + base_url + '  (' + party + ')')
        database.insert(base_url, person, party, text, sm_urls)

if __name__ == '__main__':

    '''
    #For Debugging
    nltk.download('words')
    WORDS = set(nltk.corpus.words.words())

    #words to exclude
    FTR = ['instagram', 'youtube', 'twitter', 'facebook', 'address', '_', '*', '#', '<', '>', ';', ':']
    get_all_website_links('https://ayannapressley.com/')

    '''
    #download all english words
    nltk.download('words')
    WORDS = set(nltk.corpus.words.words())

    #words to exclude
    FTR = ['instagram', 'youtube', 'twitter', 'facebook', 'address', '_', '*', '#', '<', '>', ';', ':', '[', ']', '|', '/']
    
    db = PolDB_Text('politicians.db')
    (democrats, republicans) = read_csv('politicians.csv')

    iterate_over(democrats, 'D', db)
    iterate_over(republicans, 'R', db)

    print('Done.')


