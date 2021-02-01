from webscraper import *

def get_images(url: str) -> set:
    """
    Returns all URLs that is found on `url` in which it belongs to the same website

    modified from https://matix.io/extract-text-from-webpage-using-beautifulsoup-and-python
    """
    # all URLs of `url`
    image_urls = set()

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

        if domain_name not in href:
            #still an internal link
            continue

        if href[-3:] == 'jpg' or href[-3:] == 'png' or href[-4:] == 'jpeg':
            #image link
            image_urls.add(href)
        
    return image_urls

link = 'https://www.votejohnny.us/'
urls = get_all_website_links(link)
'''
image_links = get_images(link)
for url in urls:
    image_links = set(list(image_links) + list(get_images(url))'''

print(urls)