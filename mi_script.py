import sys
from typing import List

import selenium.webdriver.remote.webelement
from selenium import webdriver
from selenium.webdriver.common.by import By
import sqlite3

args = sys.argv


def screenshot_product(link: str, item_id: str):
    driver = webdriver.Firefox()
    driver.get(link)
    driver.save_screenshot('data/' + 'item_' + item_id + '.png')
    driver.quit()


def get_data_of_items_in_page(items_per_page: List[selenium.webdriver.remote.webelement.WebElement],
                              stars_to_filter: int, cursor, sql_connection):
    for item in items_per_page:
        stars_of_item = int(
            item.find_element(By.CLASS_NAME, 'ratings').find_elements(By.TAG_NAME, 'p')[-1].get_attribute(
                'data-rating'))
        if stars_of_item >= stars_to_filter:
            link = item.find_element(By.CLASS_NAME, 'title').get_attribute('href')
            item_id = link.split('/')[-1]
            reviews = int(
                item.find_element(By.CLASS_NAME, 'ratings').find_elements(By.TAG_NAME, 'p')[0].text.split()[0])
            if reviews >= 10:
                screenshot_product(link, item_id)
            description = item.find_element(By.CLASS_NAME, 'description').text
            price = float(item.find_element(By.CLASS_NAME, 'caption').text.splitlines()[0][1:])
            sqlite3.connect('db.sqlite')
            cursor.execute("INSERT INTO items VALUES (?,?,?)", [item_id, description, price])
            sql_connection.commit()


def scrape(driver, sql_connection, cursor, main_link: str, amount_of_pages: int, stars_to_filter: int = 3):
    for page in range(1, amount_of_pages + 1):
        link_to_scrape = main_link + '?page=' + str(page)
        driver.get(link_to_scrape)
        items_per_page = driver.find_elements(By.CLASS_NAME, 'thumbnail')

        get_data_of_items_in_page(items_per_page, stars_to_filter, cursor, sql_connection)


def main(main_link='https://webscraper.io/test-sites/e-commerce/static/computers/laptops'):
    sql_connection = sqlite3.connect('db.db')
    cursor = sql_connection.cursor()
    sql = 'create table if not exists items (item_id integer, description text, price double)'
    cursor.execute(sql)

    driver = webdriver.Firefox()
    driver.get(main_link)
    ul_list_data = driver.find_element(By.CLASS_NAME, "pagination")
    amount_of_pages = int(ul_list_data.text.splitlines()[-2])

    if len(args) == 2:
        scrape(driver=driver, sql_connection=sql_connection, cursor=cursor, main_link=main_link,
               amount_of_pages=amount_of_pages)
    elif len(args) == 3:
        stars_to_filter_by = int(args[-1])
        scrape(driver=driver, sql_connection=sql_connection, cursor=cursor, main_link=main_link,
               amount_of_pages=amount_of_pages, stars_to_filter=stars_to_filter_by)
    else:
        print('Example usage:\nmi_script --stars 5')


if __name__ == '__main__':
    main()
