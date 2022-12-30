# foreclose_scraper.py
# Parses auction day summary sites for foreclosure entries and details. Currently works on pre-downloaded websites

from bs4 import BeautifulSoup
import os
import quopri
import csv
import re

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

        aucDateStr = aucDate.string
        aucDateStr = re.sub(r".*day ", "", aucDateStr)
        output["Auction Date"] = aucDateStr

        aucTab = entry.select_one(".adc-tab > a")
        if aucTab != None :
            aucLink = aucTab.attrs["href"]
            output["Auction.com Link"] = aucLink

        stats = entry.select(".AUCTION_STATS > .Astat_DATA")
        output["Auction status/sold"], output["Amount"], output["Buyer"] = [stat.string for stat in stats]

        details = entry.select(".AUCTION_DETAILS > table > tbody > tr")

        for d in details :
            label = d.select_one("th").string
            if label == None :
                label = "Property Address2:"
            label = label.replace(":", "")

            if label == "Parcel ID" or label == "Case #" :
                link = d.select_one("td > a")
                value = link.string
                if label == "Parcel ID" :
                    output["Parcel Link"] = link.attrs["href"]
                if label == "Case #" :
                    output["Case Link"] = link.attrs["href"]
            else :
                value = d.select_one("td").string
            output[label] = value
        
        outputs.append(output)
    
    return outputs

def writeFCToFile(foreclosures, outputDir, outputName) :
    field_names = ["Auction Date", "Auction status/sold", "Amount", "Buyer", "Auction Type", "Case #", "Case Link", "Final Judgment Amount", "Parcel ID", "Parcel Link", "Property Address", "Property Address2", "Assessed Value", "Plaintiff Max Bid", "Auction.com Link"]

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
        try :
            filePath = os.path.join(args_["inputDir"], file)
            html = parseMHTML(filePath)
            soup = BeautifulSoup(html, "html.parser")

            foreclosures = foreclosures + scrapeForeclosures(soup)

        except Exception as e :
            print("Error in file", file)
            print(e)
            continue
    
    writeFCToFile(foreclosures, args_["outputDir"], args_["outputName"])

main()