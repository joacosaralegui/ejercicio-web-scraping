# BIGGEST TODO EVER: LIMPIAR ESTE MONSTRUO QUE ANDA
from app.api import services
from app.db import engine, database, metadata
import sys, getopt
import asyncio
import argparse

async def perform_crawling(url : str, verbose : bool = False):
    """
    Performs the actual crawling and prints the corresponding results to console.
    Supports verbose version with some reports but is disabled by default.
    """
    report = await services.handle_scraping_request(url)
    
    if verbose:
        print("Scraping terminado para \""+report.url+"\" ")
        print(report.info)
        print("Links encontrados (sin repetidos y en ningún orden en particular):")

    for link in report.links:
        print(link)

def main(url, verbose):    
    # The reason we need to use asyncio and handle this akwardly is
    # to be able to reuse all the async code that was written for the API.
    loop = asyncio.get_event_loop()

    # Connect to db
    loop.run_until_complete(database.connect())

    # Crawl
    loop.run_until_complete(perform_crawling(url, verbose))    

    # Disconnect from database on shutdown
    loop.run_until_complete(database.disconnect())

if __name__ == "__main__":
    # Parse arguments first, then call main function
    parser = argparse.ArgumentParser(description='Extraer todos los links contenidos en un sitio. \nPara almacenar en .csv o .txt puede utilizar el comando "python get_links.py URL > links.csv". \nPara un análisis sencillo utilize la opción -V.')
    parser.add_argument('-V', action='store_true',
                        help='Verbose. Si este parametro esta presente imprime un reporte.')
    parser.add_argument('url', help='URL del sitio a parsear.')
    args_parsed = parser.parse_args()
    
    main(args_parsed.url, args_parsed.V)



