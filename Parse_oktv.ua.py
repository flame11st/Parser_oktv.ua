from bs4 import BeautifulSoup
import urllib.request
from datetime import date
import csv

now = date.today()
month = now.month
month_now = ("0" + str(month)) if len(str(month)) == 1 else month

BASE_URL = 'http://oktv.ua/search'
kol = int(input("Введите Колличество месяцев(максимум 6): "))

def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()

#выводим колличество страниц
def page_count(html):
    soup = BeautifulSoup(html, "html.parser")
    pages = soup.find("ul", class_ = "pagination ok")
    count = pages.find_all("a")[-2].text
    return count

def parse(html):
    soup = BeautifulSoup(html,"html.parser")
    flats = soup.find_all("div", class_ = "col-xs-12 bl_1")

    perechen = []

    for flat in flats:

        id = flat.find_all("a")[2].get("href")
        adress = flat.find_all("a")[2].div.text
        price =  flat.find_all("a")[1].div.text
        href = "http://oktv.ua%s" % id

        perechen.append({
            "id" : id ,
            "adress" : adress,
            "price" : price,
            "href" : href
        })

    #перебирая все квартиры переходим по ссылкам внутрь страницы и достаем данные
    for i in perechen:

        for y in range(int(kol)):
            month_y = y+int(month_now)
            soup1 = BeautifulSoup(get_html(str(i["href"]+("?date=1.%i.2017" %month_y))),"html.parser")
            months = soup1.find("div", class_ = "col-sm-6 col-xs-12 cal-row calendar-first-xs")
            calendar = months.find("div", class_ = "calendar")
            data = calendar.find_all("div", class_ = ["day grey","day","day grey bron ","day bron "])

            cal = []

            for x in data:

                day = x.get("data-time-default")
                busy = x.get("data-busy")
                cal.append({
                    "Day" : day,
                    "busy" : busy
                })

            i["Calendar on month[%i]" %month_y] = cal

    return perechen

def save(projects, path):
    with open(path, 'w',newline="") as csvfile:
        writer = csv.writer(csvfile)

        for project in projects:
            writer.writerow(("ID Квартиры", "Адресс", "Цена", "Ссылка"))
            writer.writerow((project["id"],project["adress"], project["price"], project["href"]))
            writer.writerow((" "))
            writer.writerow(("Дата", "Статус"))

            for t in range(int(kol)):
                    writer.writerows((calendar["Day"], calendar["busy"]) for calendar in project["Calendar on month[%i]" % (t+int(month_now))])

            writer.writerow((" "))
            writer.writerow((" "))

def main():

    pages = page_count(get_html(BASE_URL))

    print("Найдено %s страниц..." % pages)

    flats = []
    kol_pages = int(input("Введите колличество страниц для парсинга: "))
    for page in range(0, kol_pages):

          flats.extend(parse(get_html(BASE_URL + "?start=%i" % (page*12))))
          print("Парсинг %d%% (%d/%d)" % (((page + 1) / kol_pages) * 100, page + 1, int(kol_pages)))


    print("Сохранение...")
    save(flats, input("Введите название файла: ")+".csv")

if __name__ == "__main__":
    main()