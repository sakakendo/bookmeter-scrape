import datetime
import time
import re
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup

def get_read_books(uid):
    page = 1
    while True:
        books = []

        url = f"https://bookmeter.com/users/{uid}/books/read?page={page}"
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        if res.status_code != 200:
            raise Exception("request failed with " + str(res.status_code) + " " + soup.find("title").string)

        book_details = soup.find_all("div", "book__detail")
        if len(book_details) == 0:
            break
        for detail in book_details:
            title = detail.find_all("div", "detail__title")[0].string
            date = detail.find_all("div", "detail__date")[0].string 
            page_count = detail.find_all("div", "detail__page")[0].string
            yield {
                'title': title,
                'date': datetime.datetime.strptime(date, '%Y/%m/%d') if date != '日付不明' else '',
                'page': int(page_count)
            }
        page += 1
        time.sleep(10)
        
def main():
    uid = input("Enter your user id: ")

    books = pd.DataFrame()
    for book in get_read_books(uid):
        books = books.append(pd.Series(book), ignore_index=True) 
    books.to_csv("./out/books.csv")

    books = books[books["date"] != '']
    minyear, maxyear = books["date"].min().to_pydatetime().year, \
        books["date"].max().to_pydatetime().year + 1

    for year in range(minyear, maxyear):
        df = books[(datetime.datetime(year, 1, 1) < books["date"]) & (books["date"] < datetime.datetime(year, 12, 31))]
        print(f"year: {year}, page: {df['page'].sum()}, count: {len(df)}")
        fig, ax = plt.subplots(figsize=(8, 4))
        plt.bar(df["date"], df["page"])
        plt.savefig("out/books"+ str(year) + ".png")
    print('successfully exported reports to ./out')

main()
