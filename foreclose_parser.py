# foreclose_scraper.py
# Parses auction day summary sites for foreclosure entries and details. Currently works on pre-downloaded websites

from bs4 import BeautifulSoup
import os
import quopri
import csv

def parseMHTML(filePath) :
    parsed = open(filePath, "r").read()
    parsed = quopri.decodestring(parsed)

    return parsed

def getMHTMLs(inputDir) :
    files = os.listdir(inputDir)
    files = [f for f in files if ".mhtml" in f]

    return files

def scrapeForeclosures(soup) :
    outputs = []
    entries = soup.select("#Area_C > :not(.AUCTION_ITEM_SPACER)")

    aucDate = soup.select_one(".BLHeaderDateDisplay")

    for entry in entries :
        output = {}

        output["Auction Date"] = aucDate.string

        stats = entry.select(".AUCTION_STATS > .Astat_DATA")
        output["Auction status/sold"], output["Amount"], output["Buyer"] = [stat.string for stat in stats]

        details = entry.select(".AUCTION_DETAILS > table > tbody > tr")

        for d in details :
            label = d.select_one("th").string
            if label == None :
                label = "Property Address2:"
            label = label.replace(":", "")

            if label == "Parcel ID" or label == "Case #" :
                value = d.select_one("td > a").string
            else :
                value = d.select_one("td").string
            output[label] = value
        
        outputs.append(output)
    
    return outputs

def writeFCToFile(foreclosures, outputDir, outputName) :
    field_names = ["Auction Date", "Auction status/sold", "Amount", "Buyer", "Auction Type", "Case #", "Final Judgment Amount", "Parcel ID", "Property Address", "Property Address2", "Assessed Value", "Plaintiff Max Bid"]

    with open(os.path.join(outputDir, outputName), "w", newline="") as f :
        writer = csv.DictWriter(f, fieldnames = field_names)
        writer.writeheader()
        writer.writerows(foreclosures)

def main() :
    args_ = {
        "inputDir": "./data/pages",
        "outputDir": "./output",
        "outputName": "foreclosure-data.csv"
    }

    foreclosures = []

    files = getMHTMLs(args_["inputDir"])

    for file in files :
        filePath = os.path.join(args_["inputDir"], file)
        html = parseMHTML(filePath)

        soup = BeautifulSoup(html, "html.parser")

        foreclosures = foreclosures + scrapeForeclosures(soup)
    
    for fc in foreclosures :
        print(fc)
    
    writeFCToFile(foreclosures, args_["outputDir"], args_["outputName"])

main()