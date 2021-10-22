from fastapi import HTTPException

from app.api.models import CrawlRequest, CrawlResponse, CrawlLogSchema
from app.db import database, crawl_logs

from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from typing import List
from datetime import datetime

async def handle_scraping_request(url : str) -> CrawlResponse:
    # Fetch all links from site    
    links = await fetch_links(url) 
    amount_of_links = len(links)

    # Fetch las request before loggin this one
    log_before = await get_last_log(url)

    # Save log of crawl
    await store_scraping_log(url, amount_of_links)

    # TODO: Compare to previous log to see if anything has changed!
    if log_before:
        amount_difference = amount_of_links - log_before.amount_of_links
        last_request_date = log_before.date
        info = await generate_report(amount_difference, last_request_date, amount_of_links)
        return CrawlResponse(url=url, links=links, info=info, amount_difference=amount_difference, last_request_date=last_request_date)
    else:
        info = "Primera vez que se procesa este sitio."
        return CrawlResponse(url=url , links=links, info=info)

    

async def fetch_links(url: str) -> List[str]:
    """
    Given a certain URL, retrieves a list of all the links contained 
    in that site without repetition 

    :param url: URL of the site to search
    :return: Returns a list of strings representing all links found in the site
    """
    # Fetch BeatifulSoup object for this site
    soup = await get_site_soup(url)
    
    # Get all links for this parsed site
    links = await get_links(soup)
    
    return links

async def get_site_soup(url : str) -> BeautifulSoup:
    """
    Given a certain URL, generates the BeautifulSoup object to represent it by parsing the site's HTML.
    Can throw different HTTPExceptions if it founds invalid addresses or broken sites.

    :param url: URL of the site to parse
    :return: BeautifulSoup object representing the parsed website
    """
    try:
        req = Request(url)
    except ValueError:
        # In case that the URL is not valid or there is any error
        # while constructing the request, let the final user know
        raise HTTPException(status_code=404, detail="HTTP Error 404: Invalid URL detected.")

    try:
        # Fetch HTML site
        html_page = urlopen(req)
    except HTTPError:
        raise HTTPException(status_code=403, detail="HTTP Error 403: Forbidden. Check that the URL is valid and the site is accessible.")

    # Return BeautifulSoup object
    return BeautifulSoup(html_page, "lxml")


async def get_links(soup : BeautifulSoup) -> List[str]:
    """
    Given a parsed site in BeautifulSoup format, returns a List of links found inside 

    :param soup: Parsed site
    :return: List of strings represeting all distinct links in a website
    """
    # Use a set to ignore repetitions efficiently
    links = set()

    # Fetch all <a> objects in the site
    for link_item in soup.findAll('a'):
        # Get link
        link = link_item.get('href')        
        links.add(link)
    
    # Switch back to list to mantain consistency with the rest of the program
    links = list(links)
    
    return links

async def generate_report(amount_difference : int, last_request_date : datetime, total_amount : int) -> str:
    """
    This function generates an automatic comment in Spanish refering to the changes in the amount of links
    contained in the same website in two different snapshots. It does not report if the links in fact changed or are the same, 
    only the difference in the total amount of distinct links found in the website in two different times,

    :param ammount_difference: integer that represents the difference in total amount of links between the two crawls
    :return: String containing a report in spanish of the difference
    """
    # Simple way of creating a report according to difference in amount of links
    if amount_difference > 0:
        return "El sitio tiene " + str(amount_difference) + " links más en total que la última vez que se revisó ("+ str(total_amount) +"), el " + datetime.strftime(last_request_date, "%d/%m/%Y") + "."
    elif amount_difference < 0:
        return "El sitio tiene " + str(amount_difference) + " links menos en total que la última vez que se revisó ("+ str(total_amount) +"), el " + datetime.strftime(last_request_date, "%d/%m/%Y") + "."
    
    return "El sitio tiene la misma cantidad de links que la última vez que se revisó ("+ str(total_amount) +"), el " + datetime.strftime(last_request_date, "%d/%m/%Y") + "."
    
async def store_scraping_log(url : str, amount_of_links : int) -> int:
    """
    Stores a Log for the scraping of the website with the current datetime, the url crawled and the amount of links found
    This function could be extended to store the actual links if necessary and generate further comparisons and reports.
    Returns the id of the object stored, but it can be ignored.
    """
    query = crawl_logs.insert().values(url=url, amount_of_links=amount_of_links, date=datetime.now())
    return await database.execute(query=query)

async def get_last_log(url: str) -> CrawlLogSchema:
    """
    Fetches the last crawl log for the given url. If it doesn't exists returns None,
    else returns a  pydantic model object containing the relevant info
    """
    query = crawl_logs.select().where(crawl_logs.c.url == url).order_by(crawl_logs.c.date.desc())
    last = await database.fetch_one(query=query)
    if not last:
        return None
    else:
        return CrawlLogSchema(url=last['url'],date=last['date'],amount_of_links=last['amount_of_links'])
