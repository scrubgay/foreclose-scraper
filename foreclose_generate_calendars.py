# foreclose_generate_calendars.py

def generateCalendarLinks(startDateObj, months, urlPref, urlPost) :
    dates = []
    for i in range(0, months) :
        dateStr = str(startDateObj["year"]) + "%2D" + str(startDateObj["month"]).zfill(2) + "%2D01"
        url = urlPref + dateStr + urlPost
        dates.append(url)

        startDateObj["month"] -= 1
        if startDateObj["month"] == 0 :
            startDateObj["month"] = 12
            startDateObj["year"] -= 1
    
    return dates

links = generateCalendarLinks({"year": 2015, "month": 12}, 24, "https://www.alachua.realforeclose.com/index.cfm?zaction=user&zmethod=calendar&selCalDate=%7Bts%20%27", "%2000%3A00%3A00%27%7D")

[print(link) for link in links]