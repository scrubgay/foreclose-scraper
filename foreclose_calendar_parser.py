# foreclose_calendar_parser.py
# Parses predownloaded calendar pages from REAL FORECLOSE platform to generate a list of links to day summary sites.

from bs4 import BeautifulSoup
from foreclose_parser import parseMHTML, getMHTMLs
import os
import quopri

def scrapeLinks(soup) :
    dates = []
    entries = soup.select(".CALDAYBOX > .CALSELF")

    for entry in entries :
        dateString = entry.attrs["dayid"]
        dates.append(dateString)

    return dates
    
def main() :
    args_ = {
        "baseLink": "https://www.alachua.realforeclose.com/index.cfm?zaction=AUCTION&Zmethod=PREVIEW&AUCTIONDATE=",
        "inputDir": "./data/calendar",
        "outputDir": "./data",
    }

    fcPages = []

    files = getMHTMLs(args_["inputDir"])

    for file in files :
        filePath = os.path.join(args_["inputDir"], file)
        html = parseMHTML(filePath)

        soup = BeautifulSoup(html, "html.parser")

        dates = scrapeLinks(soup)

        dates = list(map(lambda x: args_["baseLink"] + x, dates))
        
        fcPages = fcPages + dates
    
    for page in fcPages :
        print(page)

main()