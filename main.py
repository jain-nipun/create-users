import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import io, sys, argparse
import concurrent.futures
import urllib.request
# initialize the set of links (unique links)
internal_urls = set()

def is_valid(url):
    #Checks whether `url` is a valid URL.
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_website_links(url):
    #Returns all URLs that is found on `url` in which it belongs to the same website
    soup = BeautifulSoup(requests.get(url).content, "html.parser")

    #config = ConfigParser()
    #config.read(os.path.join(os.path.dirname(__file__), '../Config', 'config.ini'))
    #soup = requests.get(config['default']['root_url']).content

    #initialize dictionary to store urls as key and anchor_text and occurency as nested key value pair
    result = {}
    for a_tag in soup.find_all("a"):
        #to collrct all links whether they have text or not
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        #to break down the url string into components such as scheme, location, path etc.
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            continue
        anchor_text = a_tag.text
        #to increase the count of the occurence of anchor_texts, if we got the same anchor_text,
        # increase the occurence by 1, else occurence is 1
        if href in result.keys():
            if anchor_text in result[href].keys():
                result[href][anchor_text] += 1
            else:
                result[href][anchor_text] = 1
        else:
            result[href] = {}
            result[href][anchor_text] = 1

    return result

#URLS = ['http://www.foxnews.com/',
#   'http://www.cnn.com/',
#   'http://europe.wsj.com/',
#   'http://www.bbc.co.uk/',
#   'http://some-made-up-domain.com/']

#to write user-friendly command-line interfaces and parses the defined arguments from the sys
parser = argparse.ArgumentParser()
#to open the file  with type as read
parser.add_argument('file', type=argparse.FileType('r'))
#to get namespace object that contains property of each input
args = parser.parse_args()
#to read the lines from the file and store it in the variable URL as a list of urls
URLS = list(args.file.readlines())

#concurrent.futures module to execute calls asynchronously
with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
    result = {}
    #submit method executes the given command at some time in the future
    future_to_url = {executor.submit(get_all_website_links, url): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
            result.update(data)
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))

    with open(r'result.csv', 'w', newline='', encoding="utf-8") as file:
        file.write('href, anchor_text, total_occurence\n')
        for href in result:
            for anc_text in result[href]:
                count = str(result[href][anc_text])
                #to replace character ',' with a space and new line (\n) character
                #so that we get desired outputin csv file
                anc_text = anc_text.replace(',', ' ')
                anc_text = anc_text.replace('\n', '')
                # to write href, anchor_text and occurence in csv file (separated by ',')
                file.write(href + ',' + anc_text + ',' + count + '\n')
