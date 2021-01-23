#code adapted from: https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python/


from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
import requests
import time
import urllib.request 
from inscriptis import get_text 


MAIN_URL = "https://trentkelly.house.gov/"

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


urls = get_all_website_links(MAIN_URL)


def get_all_text(main_url):
    start_time = time.time()

    f = open("practice.txt", "w")
    html = urllib.request.urlopen(main_url).read().decode('utf-8') 
    f.write(get_text(html))

    for url in urls:
        html = urllib.request.urlopen(url).read().decode('utf-8') 
        f.write(get_text(html))

        elapsed_time = time.time() - start_time
        print("Elapsed Time: {}".format(hms_string(elapsed_time)))
        print("URL Completed: " + url)

    return None
        


print(get_all_text(MAIN_URL))