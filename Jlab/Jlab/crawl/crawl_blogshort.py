import datetime as dt
from bs4 import BeautifulSoup
import requests
import pandas as pd

'''
크롤링 example
keyword = "keyword"
term = 1    (# 1 -> daily, 7 -> weekly, 30 -> monthly, 90 -> quarter, 365 -> annual)
startdate, enddate = dt.date(year=2018, month=1, day=1),  dt.date(year=2018, month=1, day=4)

urlinstance = UrlPattern(keyword, startdate, enddate, term)
table = urlinstance.crawl()
'''


class UrlPattern:
    def __init__(self, keyword, startdate, enddate, term):
        self.keyword = keyword
        self.startdate = startdate
        self.enddate = enddate
        self.term = term
        self.untildate = self.startdate + dt.timedelta(days=self.term - 1)
        self.page = 1
        self.table = pd.DataFrame(columns=["date", "contents"])
        self.prior_boxes = []

    def generate(self):
        sd = str(self.startdate).replace("-", "")
        ud = str(self.untildate).replace("-", "")
        return f"https://search.daum.net/search?w=blog&m=board&collName=blog_total&q={self.keyword}&spacing=0&DA=STC&sd={sd}000000&ed={ud}235959&period=u&page={self.page}"

    def page_up(self):
        self.page += 1
        return self.generate()

    def date_up(self):
        self.page = 1
        self.startdate = self.startdate + dt.timedelta(days=self.term)
        self.untildate = self.startdate + dt.timedelta(days=self.term - 1)
        return self.generate()

    def crawl(self):
        url = self.generate()
        while self.untildate <= self.enddate:
            html = requests.get(url).text
            soup = BeautifulSoup(html, 'html.parser')
            boxes = soup.find_all("p", {"class": "f_eb desc"})
            boxes = [ctnt.get_text() for ctnt in boxes]
            if boxes != []:
                # 박스가 빈리스트가 아니면 1. 새로운 내용이 있거나, 2. 그 전게 반복되던가
                if (boxes != self.prior_boxes) & (self.page < 100):  # 그 전 페이지에서 boxes와 이번 페이지에서 boxes가 다르고 페이지가 100미만이면
                    self.prior_boxes = boxes
                    self.table = pd.concat([
                        self.table,
                        pd.DataFrame({"date": [str(self.startdate)] * len(boxes), "contents": boxes})
                    ]
                    ).reset_index(drop=True)

                    url = self.page_up()  # 페이지업
                else:  # 그 전 페이지에서 boxes와 이번 페이지에서 boxes가 같거나 페이지가 100이상이면
                    url = self.date_up()
            else:  # 빈리스트면 내용 없다는 거니까 날짜 올려라.
                url = self.date_up()
        return self.table.reset_index(drop=True)
