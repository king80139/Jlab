from bs4 import BeautifulSoup
from selenium import webdriver
import time
import datetime as dt
import pandas as pd
import re
import pickle

try:
    Lib = pd.read_csv("ProjectLibrary2.csv")
except UnicodeDecodeError:
    Lib = pd.read_csv("ProjectLibrary2.csv", encoding="cp949")

options = webdriver.ChromeOptions()
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
options.add_argument(
    "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

path = "/Users/ssakoon/Downloads/chromedriver"
browser = webdriver.Chrome(path, chrome_options=options)

startdate = list(Lib.loc[Lib["*함수명/ parameter이름"] == "Starting_Date", "Input File/Information"])[0]
startdate = dt.date(year=int(startdate.split(".")[0]),
                    month=int(startdate.split(".")[1]),
                    day=int(startdate.split(".")[2]))
untildate = startdate + dt.timedelta(days=1)

enddate = list(Lib.loc[Lib["*함수명/ parameter이름"] == "Ending_Date", "Input File/Information"])[0]
enddate = dt.date(year=int(enddate.split(".")[0]),
                  month=int(enddate.split(".")[1]),
                  day=int(enddate.split(".")[2]))

subject = list(Lib.loc[Lib["*함수명/ parameter이름"] == "*Crawl_Twitter", "Input File/Information"])[0]
# subject = search_for.replace(",","%20OR%20").replace(" ","%20")
language = "ko"

Raw_Message = pd.DataFrame(columns=["date", "contents"])

dates = []
contents = []
while not enddate == startdate:
    url = 'https://twitter.com/search?l=' + language + '&q=' + subject + \
          '%20since%3A' + str(startdate) + '%20until%3A' + str(untildate)
    browser.get(url)
    time.sleep(1)
    html = browser.page_source
    soup = BeautifulSoup(html, 'html.parser')

    lastHeight = browser.execute_script("return document.body.scrollHeight")
    while True:
        cleaner = re.compile('<.*?>')
        unicode_list = re.compile("[^가-힣|^a-z|^A-Z|^0-9| ]+")
        enter_code = re.compile("[\n]+")
        space_code = re.compile("[\s]+")

        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

        newHeight = browser.execute_script("return document.body.scrollHeight")
        if newHeight != lastHeight:
            lastHeight = newHeight

        else:
            html = browser.page_source
            soup = BeautifulSoup(html, 'html.parser')
            contents = soup.find_all("div", {
                "class": "css-901oao r-1fmj7o5 r-1qd0xha r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0"})

            tw = []
            for t in contents:
                t = re.sub(cleaner, "", str(t))
                t = re.sub(space_code, " ", re.sub(enter_code, " ", t))
                t = re.sub(unicode_list, "", t)
                tw.append(t)

            dates = [startdate] * len(tw)

            startdate = untildate
            untildate += dt.timedelta(days=1)

            daily_Message = pd.DataFrame({"date": dates, "contents": tw})
            # display(daily_Message)

            Raw_Message = pd.concat([Raw_Message, daily_Message], axis=0, sort=True)
            break
        Raw_Message = Raw_Message.reset_index(drop=True)

with open(subject + "_text.pickle", "wb") as fw:
    pickle.dump(Raw_Message, fw)
Raw_Message.to_csv(list(Lib.loc[Lib["*함수명/ parameter이름"] == "*Crawl_Twitter", "Output file"])[0],
                   encoding="cp949", index=False)  # 인코딩의 경우 Window OS의 경우 default값인 utf-8을 사용하면 되지만
# MacOS의 경우 cp949로 인코딩해야 직접 파일을 열어서 볼때 안 깨진다.

Raw_Message.head(15)

