from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import json 

import pandas

def obtainHtml(url):
    """"
    From a url, this funtion will return the page content.
    """
    # Config chrome options. The window will open in full screen.
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')  

    #Chromedriver's path, if you dont have it, you can download it in chromedriver page.
    chrome_driver_path = 'C:/Users/mega_/OneDrive/Desktop/chromedriver.exe'
    chrome_service = ChromeService(executable_path=chrome_driver_path)
    # Initialize chrome
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    driver.get(url)

    # Wait until the page is complete load
    driver.implicitly_wait(100)
    time.sleep(5)

    # obtain page content
    page_content = driver.page_source

    soup = BeautifulSoup(page_content, 'html.parser')
    driver.quit()
    return soup

def dataFromPage(soup):
    """
    This is a generator that will yield the name and price of the products in a page.
    """
    # Search for the product data
    products_data= soup.find_all('div', "valtech-carrefourar-search-result-0-x-galleryItem valtech-carrefourar-search-result-0-x-galleryItem--normal pa4")

    # Iter over all the products in the page in order to hace its price and name.
    for product_data in products_data:
        price_element= product_data.find('span', "valtech-carrefourar-product-price-0-x-currencyContainer")
        products_name = product_data.find('span', class_="vtex-product-summary-2-x-productBrand vtex-product-summary-2-x-brandName t-body")
        if price_element:
           # yield products and name
           yield products_name.text.strip(), price_element.text.strip()[2:]

def dataToList(products_iterator, sub_category):
    """
    This function will append the product and it's price to the products list
    """
    for product, price_element  in products_iterator:

        products.append([product, sub_category ,price_element])

def carrefourMainPage():
    # Config chrome options. The window will open in full screen.
    chrome_options = Options()
    chrome_options.add_argument('--start-maximized')  # Esta línea abrirá el navegador en pantalla completa

    # Chromedriver's path, if you dont have it, you can download it in chromedriver page.
    chrome_driver_path = 'C:/Users/mega_/OneDrive/Desktop/chromedriver.exe'
    chrome_service = ChromeService(executable_path=chrome_driver_path)

    # Initialize chrome
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

    # Load  carrefour's main page and wait until is load,
    driver.get("https://www.carrefour.com.ar")
    driver.implicitly_wait(10)
    time.sleep(2)
    return driver

driver = carrefourMainPage()
# Search the hiding menu and then click it it order the dislpay it.
element_selector = '[role="presentation"][aria-hidden="true"]'
elements = driver.find_elements(By.CSS_SELECTOR, element_selector)
elements[1].click()
driver.implicitly_wait(10)
time.sleep(2)

# find all the category items that can ve display
elements_selector = 'li.vtex-menu-2-x-menuItem.vtex-menu-2-x-menuItem--MenuCategoryFirstItem.list.vtex-menu-2-x-menuItem.vtex-menu-2-x-menuItem--MenuCategoryFirstItem.vtex-menu-2-x-menuItem--isClosed.vtex-menu-2-x-menuItem--MenuCategoryFirstItem--isClosed'
elements = driver.find_elements(By.CSS_SELECTOR, elements_selector)

page_content = driver.page_source
soup = BeautifulSoup(page_content, 'html.parser')
# find all the categories names
categories  = soup.find_all('div', class_="vtex-menu-2-x-styledLinkContent vtex-menu-2-x-styledLinkContent--MenuCategoryFirstItem flex justify-between nowrap")

next_page = "?page="
url_page = "https://www.carrefour.com.ar/"
i = 3
products = []

# Iter over all openable elements
for element in elements[2:]:
    sub_category = []
    # Move the mouse on the category text in order to display the subcategories
    ActionChains(driver).move_to_element(element).perform()
    driver.implicitly_wait(10)
    time.sleep(1)

    # find all the sub categories names
    element_selector = '.vtex-menu-2-x-styledLinkContent--MenuCategorySecondItem-hasSubmenu'
    sub_categories_found = WebDriverWait(driver, 10).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, element_selector))
    )
    category = categories[i].text.strip()
    print(category)
    if category  in ["Destacados", "Limpieza", "Perfumería", "Mundo Bebé", "Mascotas"]:
        continue

    # Page format "https://www.carrefour.com.ar/category"
    url_page_category = url_page + category.replace(" ", "-")

    # iter over the sub categories found to save them.
    for sub_category_found in sub_categories_found:
        sub_category_found_text = sub_category_found.text.strip()

        # Page format "https://www.carrefour.com.ar/category/sub_category"
        url_page_category_subcategory = url_page_category+"/" + sub_category_found_text.replace(" ", "-")
        if "," in url_page_category_subcategory:
            url_page_category_subcategory = url_page_category_subcategory.replace(",","")
        
        # Obtain page conten, then generetor of the page'products and add the page visited to the text_data_log.
        soup = obtainHtml(url_page_category_subcategory)
        products_iterators = dataFromPage(soup)

        # Obtein the number of pages that the sub_category has.
        button_divs = soup.find_all('div', class_='valtech-carrefourar-search-result-0-x-paginationButtonPages')
        dataToList(products_iterators, sub_category_found_text.replace(" ", "-").replace(",", ""))

        try:
            range_pages = range(2,int( button_divs[-1].text ))

            #Iter over all subcategory's pages.
            for j in range_pages:
                # Page format "https://www.carrefour.com.ar/category/sub_category/?page=str(i)"
                url_page_category_subcategory_next_pages = url_page_category_subcategory + next_page + str(j)
                if "," in url_page_category_subcategory_next_pages:
                    url_page_category_subcategory_next_pages = url_page_category_subcategory_next_pages.replace(",","")

                # Obtain page conten, then generetor of the page'products and add the page visited to the text_data_log.
                soup = obtainHtml(url_page_category_subcategory_next_pages)
                products_iterators = dataFromPage(soup)
                #add the data to a list.
                dataToList(products_iterators,sub_category_found_text.replace(" ", "-").replace(",", ""))
        except:
            pass


    i += 1

driver.quit()

# Save the data in a .csv file.
import pandas as pd
from datetime import datetime


column_names = ["Product", "Category", "Price"]
df = pd.DataFrame(products)
df.columns = column_names

date_today = datetime.now()
date_today = date_today.strftime("%d-%m-%Y")
save_file_name = f"Carrefour_Prices-{date_today}.csv"

df.to_csv(save_file_name, index = False, sep = ";")

