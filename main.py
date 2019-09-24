from telnetlib import EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import time

from geo_util import GeoUtil
from get_lat_lng import getLatLng
from spread import Generator

SHEET_NAME = input('시트 이름을 입력해주세요: ')

latitude = 37.566552
longitude = 126.9688839
zoom = '10'
range = 1.5

url = "https://new.land.naver.com/complexes?ms=" + str(latitude) + ',' \
      + str(longitude) + "," + zoom + "&a=APT&b=A1&e=RETAIL&f=70000"

wd = webdriver.Chrome('C:\\Users\cjg\Downloads\chromedriver_win32\chromedriver.exe')
wd.get(url)
action = webdriver.ActionChains(wd)
apartList = []
atagList = []
atagList = wd.find_elements_by_class_name('marker_complex--apart')

for atag in atagList:
    atag_id = atag.get_attribute("id")
    wd.execute_script(
        "(function() { " +
        "window.open('https://new.land.naver.com/complexes/" +
        atag_id + "?ms=" + str(latitude) + ',' + str(longitude) + ","
        + zoom + "&a=APT&b=A1&e=RETAIL&f=70000');" +
        "})();"
    )
    time.sleep(0.5)

    wd.switch_to.window(wd.window_handles[-1])
    time.sleep(0.5)
    try:
        rec_div = WebDriverWait(wd, 10).until(EC.presence_of_element_located((By.XPATH, '//script[@async="async"]')))
    except:
        print("time out error")
    atagList2 = []
    while len(atagList2) <= 0:
        atagList2 = wd.find_elements_by_class_name('marker_complex--apart')
    temp = None
    for atag2 in atagList2:
        if atag_id == atag2.get_attribute("id"):
            temp = atag2
            break
    button = temp.find_element_by_css_selector(
        'button.complex_data_button')
    wd.execute_script("arguments[0].click();", button)

    time.sleep(0.5)

    try:
        price = wd.find_element_by_xpath('//*[@id="summaryInfo"]/div[2]/div[1]/div/dl[1]/dd').text
        apart_name = wd.find_element_by_xpath('//*[@id="complexTitle"]').text
        generation = wd.find_element_by_xpath('//*[@id="detailContents1"]/div[1]/table/tbody/tr[1]/td[1]').text
        build_fin_year = wd.find_element_by_xpath('//*[@id="detailContents1"]/div[1]/table/tbody/tr[2]/td[1]').text
        manage_place = wd.find_element_by_xpath('//*[@id="detailContents1"]/div[1]/table/tbody/tr[6]/td').text
        address = wd.find_element_by_xpath('//*[@id="detailContents1"]/div[1]/table/tbody/tr[7]/td/p[1]').text

        lat, long, location = getLatLng(address)
        if range >= GeoUtil().get_harversion_distance(long, lat, longitude, latitude):
            print(" 통과")
            url = "https://new.land.naver.com/complexes/" + atag2.get_attribute("id").split('C')[0] + "?ms=" + str(
                lat) + ',' + str(
                long) + ",10&a=APT&b=A1&e=RETAIL&f=70000');"
            price = price.replace(" ", "")
            price = price.replace(",", "")
            price = price.split('~')

            if len(price) > 0:
                min_price = price[0].split('억')
                min_price = (int(min_price[0]) * 10000 + int(0 if min_price[1] == "" else min_price[1])) / 100
                max_price = min_price
            if len(price) > 1:
                max_price = price[1].split('억')
                max_price = (int(max_price[0]) * 10000 + int(0 if max_price[1] == "" else max_price[1])) / 100
            generation = generation.split('세')[0]
            if manage_place == '-':
                manage_place = ''
            apartList.append(
                [location, apart_name, manage_place, generation, build_fin_year, min_price, max_price, url, address])
    except Exception as e:
        print(e)
    wd.close()
    wd.switch_to.window(wd.window_handles[0])

generator = Generator()
generator.generate(SHEET_NAME)
generator.addRow(SHEET_NAME, apartList)
