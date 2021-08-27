import os
from selenium.webdriver import Chrome, ChromeOptions
import pandas as pd
import datetime
import math
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
from time import sleep

EXP_CSV_PATH = "./exp_list_{datetime}.csv"
MYNAVI_SEARCH_URL = "https://tenshoku.mynavi.jp/list/{place}/{job}/kw{keyword}/"

### Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    driver_path = ChromeDriverManager().install()
    return Chrome(driver_path,options=options)

def find_table_target_word(th_elms, td_elms, target:str): #td_elmsをtd内の<div class='text'>内の内容にする
    for th,td in zip(th_elms, td_elms):
        if th.text == target:
            return td.text

def run(place,job,keyword):
    if os.name == 'nt': #Windows
        driver = set_driver("chromedriver.exe", False)
    elif os.name == 'posix': #Mac
        driver = set_driver("chromedriver", False)
    driver.get(MYNAVI_SEARCH_URL.format(place=place,job=job,keyword=keyword))
    sleep(1)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    sleep(1)
    # ポップアップを閉じる
    driver.execute_script('document.querySelector(".karte-close").click()')
    df = pd.DataFrame()
    while True:
        companys = driver.find_elements_by_class_name('recruit')
        for company in companys:
            print(driver.current_url)
            company.find_element_by_css_selector(".txt>a").click() #企業名をクリック
            sleep(5)
            print(driver.current_url)
            company.find_element_by_css_selector("li:nth-child(odd)").click() #求人詳細ボタンをクリック
            sleep(5)
            print(driver.current_url)
            job_content = company.find_element_by_class_name('jobPointArea__wrap-jobDescription') #仕事内容
            print(driver.current_url)
            worker = company.find_element_by_class_name('jobPointArea__body--large') #対象となる方
            offer_table = company.find_element_by_class_name('jobOfferTable') #募集要項の表を取り出す
            company_table = company.find_element_by_css_selector('.jobOfferTable.thL') #会社情報の表を取り出す
            
            koyou = find_table_target_word(offer_table.find_elements_by_class_name('jobOfferTable__head'),offer_table.find_elements_by_class_name('text'),'雇用形態')
            time = find_table_target_word(offer_table.find_elements_by_class_name('jobOfferTable__head'),offer_table.find_elements_by_class_name('text'),'勤務時間')
            pay = find_table_target_word(offer_table.find_elements_by_class_name('jobOfferTable__head'),offer_table.find_elements_by_class_name('text'),'給与')
            rest = find_table_target_word(offer_table.find_elements_by_class_name('jobOfferTable__head'),offer_table.find_elements_by_class_name('text'),'休日・休暇')
            support = find_table_target_word(offer_table.find_elements_by_class_name('jobOfferTable__head'),offer_table.find_elements_by_class_name('text'),'福利厚生')
            money = find_table_target_word(company_table.find_elements_by_class_name('jobOfferTable__head'),company_table.find_elements_by_class_name('text'),'資本金')
            profit = find_table_target_word(company_table.find_elements_by_class_name('jobOfferTable__head'),company_table.find_elements_by_class_name('text'),'売上高')
            try:
                df = df.append({
                    '仕事内容':job_content.text,
                    '対象の方':worker.text,
                    '雇用形態':koyou,
                    '勤務時間':time,
                    '給与':pay,
                    '休日・休暇':rest,
                    '福利厚生':support,
                    '資本金':money,
                    '売上高':profit
                },ignore_index=True)
            except Exception as e:
                print('dataframe化失敗')
        print(df)
        link_page = driver.find_elements_by_css_selector(".pager_item.pager_next")
        print(len(link_page))
        if len(link_page) >= 1:
            link_url = link_page[0].get_attribute("href")
            driver.get(link_url)
        else:
            break

    df.to_csv(EXP_CSV_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')),encoding='utf-8')

if __name__ == "__main__":
    run('p02+','o11+','高収入')
