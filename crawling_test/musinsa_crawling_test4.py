from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
import time
import pandas as pd

def get_href_links(driver, wait, actions, num_items_to_fetch=100):
    href_links = set()
    while len(href_links) < num_items_to_fetch:
        actions.send_keys(Keys.END)
        time.sleep(2)
        
        for x in range(1, 46):
            try:
                xpath = f'//*[@id="root"]/main/div/section[3]/div[1]/div/div[{x}]/div/div[2]/a[2]'
                element = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
                href = element.get_attribute('href')
                href_links.add(href)
            except (NoSuchElementException, TimeoutException):
                continue

        print(f"Current number of unique href links: {len(href_links)}")
        if len(href_links) >= num_items_to_fetch:
            break

    return list(href_links)

def get_product_info(driver, wait, href_links):
    products = []
    for index, link in enumerate(href_links):
        driver.get(link)
        time.sleep(2)  # 페이지 로드 대기

        try:
            product_id = f"top{index + 1}"
            
            try:
                product_name = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[3]/h2'))).text
            except (NoSuchElementException, TimeoutException):
                product_name = "N/A"
                print(f"Product name not found for link: {link}")
                
            try:
                category = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[2]/a[1]'))).text
            except (NoSuchElementException, TimeoutException):
                category = "N/A"
                print(f"Category not found for link: {link}")

            try:
                price = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="root"]/div[5]/div/div/span'))).text.strip()
            except (NoSuchElementException, TimeoutException):
                price = "N/A"
                print(f"Price not found for link: {link}")

            try:
                image_element = wait.until(EC.presence_of_element_located((By.XPATH, '//img[@class="sc-1jl6n79-4 AqRjD"]')))
                image_url = image_element.get_attribute('src')
            except (NoSuchElementException, TimeoutException):
                image_url = "N/A"
                print(f"Image URL not found for link: {link}")

            description = link

            # 사이즈 정보 가져오기
            sizes = []
            try:
                ul_element = wait.until(EC.presence_of_element_located((By.XPATH, '//ul[contains(@class, "sc-1sxlp32-1") or contains(@class, "sc-8wsa6t-1 Qtsoe")]')))
                li_elements = ul_element.find_elements(By.TAG_NAME, 'li')
                for li in li_elements:
                    size_text = li.text.strip()
                    if size_text not in ["cm", "MY"]:
                        sizes.append(size_text)
            except (NoSuchElementException, TimeoutException):
                print(f"Size information not found for link: {link}")

            product = {
                "product_id": product_id,
                "product_name": product_name,
                "category": category,
                "price": price,
                "image_url": image_url,
                "description": description,
                "size": sizes
            }
            products.append(product)
            
            # 데이터 출력
            print(product)

        except Exception as e:
            print(f"Failed to extract data for link: {link} due to {e}")
            continue
    
    return products

def save_to_csv(products, filename="products.csv"):
    df = pd.DataFrame(products)
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"Data saved to {filename}")

def main():
    URL = "https://www.musinsa.com/categories/item/001?device=mw&sortCode=emt_high"
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ["enable-logging"])
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=option)
    driver.get(URL)
    time.sleep(3)

    driver.find_element(By.XPATH, '//*[@id="root"]/main/div/div[3]/div/button').click()
    time.sleep(1)

    wait = WebDriverWait(driver, 10)
    actions = driver.find_element(By.CSS_SELECTOR, 'body')

    href_links = get_href_links(driver, wait, actions, num_items_to_fetch=100)
    print(f"Number of unique href links: {len(href_links)}")

    products = get_product_info(driver, wait, href_links)
    print("Products extracted:")
    for product in products:
        print(product)

    save_to_csv(products)

    # driver.quit()

if __name__ == '__main__':
    main()
