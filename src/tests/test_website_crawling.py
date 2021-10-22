from datetime import datetime
import json

from bs4 import BeautifulSoup

from app.api import services

def test_crawl_url_one_link_success(test_app,monkeypatch):
    """
    Crawls a dummy site and has to find one link only.     
    """
    # URL to request crawling
    test_request_payload = {"url": "https://onelinksite.com" }
    # Response expected
    test_response_links = ['http://example.com/']
    # Dummy site
    test_site = """
        <html><head><title>The Dormouse's story</title></head>
        <body>
        <a href="http://example.com/" class="example" id="link1">Example</a>
        </body>
    """

    # We patch the function that retrieves the actual HTML of the site and parses it 
    # to give this placeholder site parsed version
    async def mock_get_site_soup(payload):
        return BeautifulSoup(test_site,'html.parser')
    monkeypatch.setattr(services, "get_site_soup", mock_get_site_soup)

    # Fetches the links in site
    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)
    response_dict = response.json()

    # Check if everything went right
    assert response.status_code == 200
    assert response_dict['links'] == test_response_links


def test_bad_url(test_app):
    """
    The api should be able to handle a bad URL error properly.
    """
    test_request_payload = {"url": "bad_url.//unexistingsite.com" }

    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)

    assert response.status_code == 404

def test_empty_url(test_app):
    """
    All empty urls should be issued a warning or error 
    """
    test_request_payload = {"url": "" }

    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)

    assert response.status_code == 404

def test_bad_site(test_app):
    """
    Broken or non-existing sites should through error
    """
    test_request_payload = {"url": "http://thissitedoesntexist.xyz.com" }

    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)
    assert response.status_code == 403

def test_change_reports(test_app,monkeypatch):
    """
    This tests goes through the process of requesting the same site twice and getting a report
    with the difference in the amount of DISTINCT links between the two crawls.
    It uses two placeholder versions of the same site and only one URL, as it's meant to be a site that changes.
    """
    test_request_payload = {"url": "https://onelinksite.com" }

    test_site_1 = """
        <html><head><title>The Dormouse's story</title></head>
        <body>
        <a href="http://example.com/" class="example" id="link1">Example</a>
        </body>
    """
    
    test_site_2 = """
        <html><head><title>The Dormouse's story</title></head>
        <body>
        <a href="http://example1.com/" class="example" id="link1">Example</a>
        <a href="http://example2.com/" class="example" id="link1">Example</a>
        </body>
    """

    # This mock function will return the one link site
    async def mock_get_site_soup_1(payload):
        return BeautifulSoup(test_site_1,'html.parser')
    
    # This one the one with two links
    async def mock_get_site_soup_2(payload):
        return BeautifulSoup(test_site_2,'html.parser')

    # We set the one link first
    monkeypatch.setattr(services, "get_site_soup", mock_get_site_soup_1)
    # Request the scraping to generate the corresponding log
    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)
    # Patch again the soup function to get more links this time in the website
    monkeypatch.setattr(services, "get_site_soup", mock_get_site_soup_2)
    # Request crawl
    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)
    # Parse response
    response_dict = response.json()

    # Check if everything went right and the analysis is correct
    assert response.status_code == 200
    # One link difference (the site has one more link than last time. If it was negative then it means it lost one)
    assert response_dict['amount_difference'] == 1
    # Check that the first request was done no longer than a second ago, cose it could be comparing against a differente request
    # which is wrong. We always want to compare with the last one done in this case. (This could change if we would like to make a more
    # complicated comparison function or some report of changes over time, eg.)
    assert response_dict['last_request_date'] != None
    last_request_date = datetime.strptime(response_dict['last_request_date'], "%Y-%m-%dT%H:%M:%S.%f")
    assert (last_request_date-datetime.now()).total_seconds() > -1


def test_no_reports(test_app,monkeypatch):
    """
    This tests goes through the process of requesting a website that hasn't been crawl before
    and verifies that the amount_difference and last_request_date are Null, which means there is no previous crawl stored.
    This works because the testing modules drops and recreates the database everytime. 
    For a production enviroment this should be changed and test should use a different database.
    """
    test_request_payload = {"url": "https://firstlinksite.com" }
    test_site = """
        <html><head><title>The Dormouse's story</title></head>
        <body>
        <a href="http://example.com/" class="example" id="link1">Example</a>
        </body>
    """
    
    # This mock function will return the one link site
    async def mock_get_site_soup(payload):
        return BeautifulSoup(test_site,'html.parser')

    # We set the one link first
    monkeypatch.setattr(services, "get_site_soup", mock_get_site_soup)
    # Request the scraping to generate the corresponding log
    response = test_app.post("/scraping/", data=json.dumps(test_request_payload),)
    response_dict = response.json()

    # Check if everything went right and the analysis is correct
    assert response.status_code == 200
    assert response_dict['amount_difference'] == None
    assert response_dict['last_request_date'] == None