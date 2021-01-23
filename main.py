#code adapted from: https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/

from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from urllib.error import HTTPError
import requests
import time
import urllib.request
import csv
from database import PolDB
import os

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

def get_text(url: str) -> str:
    res = requests.get(url)
    html_page = res.content
    soup = BeautifulSoup(html_page, 'html.parser')
    text = soup.find_all(text=True)


    images = set()
    for img in soup.findAll('img'):
        images.add(img.get('src'))
    

    output = ''
    blacklist = [
    '[document]',
    'noscript',
    'header',
    'html',
    'meta',
    'head', 
    'input',
    'script',
    'style',
    'figcaption'
    # there may be more elements you don't want, such as "style", etc.
    ]

    for t in text:
        if t.parent.name not in blacklist:
            output += '{} '.format(t)

    return (output, images)

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()

    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc

    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
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

        if href in urls:
            # already in the set
            continue

        if domain_name not in href:
            continue

        urls.add(href)
        
    return urls

def get_all_text(main_url, name):
    urls = get_all_website_links(main_url)
    images = set()

    start_time = time.time()
    counter = 0

    f = open("practice.txt", "w+")
    f.truncate(0)
    try: (text, images) = get_text(main_url); f.write(text)
    except UnicodeEncodeError: print("Skipped " + main_url)


    try: os.mkdir('images/' + name)
    except FileExistsError: pass

    for url in urls:
        if url[-4:] == '.jpg':
            urllib.request.urlretrieve(url, ("images/{}/image_{}.jpg").format(name, counter))
            counter += 1
        else: 
            try: (text, images_temp) = get_text(main_url); f.write(text); images = images | images_temp
            except UnicodeEncodeError: print("Skipped " + url); continue
        elapsed_time = time.time() - start_time
        print("Elapsed Time: {}".format(hms_string(elapsed_time)))
        print("URL Completed: " + url)
    

    print ("Reading all images..")
    for image in images:
        print("Reading: " + image)
        ext = image[image.rfind('.'):]
        
        try: 
            urllib.request.urlretrieve(image, ("images/{}/image_{}" + ext).format(name, counter))
            
            counter += 1
            print("Read.")

        except (ValueError, HTTPError) as e:
            print("Skipped: " + url)
        


    
    print ("All images read.")
    return f

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
    db = PolDB('politician.db')
    (democrats, republicans) = read_csv('politicians.csv')
    
    democrats = {'Katherine Clark': 'https://www.katherineclark.org/'}
    for person, base_url in democrats.items():
        try: f = get_all_text(base_url, person)
        except ConnectionResetError: continue
        contents = f.read()
        db.insert(base_url, person, contents, 'D')
        f.close()
    
    raise Exception("No!")

    for person, base_url in republicans.items():
        try: f = get_all_text(base_url, person)
        except ConnectionResetError: continue
        contents = f.read()
        db.insert(base_url, person, contents, 'R')
        f.close()