import time
from itertools import count

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import NoSuchElementException, TimeoutException, ElementNotInteractableException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.ie.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
import requests
import re


headers = {
    "ACCEPT-LANGUAGE" : "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7",
    "USER-AGENT" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36"
}

content = requests.get("https://appbrewery.github.io/Zillow-Clone/", headers=headers)
# print(content.text)

soup = BeautifulSoup(content.text, "html.parser")

property_anchor_tag = soup.find_all(name="a", class_="StyledPropertyCardDataArea-anchor")
# print(all_links)

all_property_links_list = [link.get('href') for link in property_anchor_tag]
#print(all_property_links)

all_property_address_list = [address.text.strip() for address in property_anchor_tag]

# print(all_property_address)

all_property_rent_tag = soup.find_all(name="span", attrs={"data-test": "property-card-price"})
all_property_rent_list = [re.sub('[a-zA-Z +/]+','', span.text) for span in all_property_rent_tag]
# print(all_property_rent_list)


# ---------------- selenium code ---------------------------------
GOOGLE_SHEET_URL = "https://docs.google.com/forms/d/1dMNXtaSofHfL8AfR5kxHSd77ALJXdVb7Z_0sIBwp4Bk/edit"

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=chrome_options)

wait = WebDriverWait(driver, timeout=10)

print(f"Data Size: {len(all_property_address_list)} records")
#time.sleep(10)

for counter in range(0, len(all_property_address_list)):
    try:
        driver.get(GOOGLE_SHEET_URL)
        address = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[1]/div/div/div[2]/div/div[1]/div/div[1]/input')))
        rent  = wait.until(ec.visibility_of_element_located(
            (By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[2]/div/div/div[2]/div/div[1]/div/div[1]/input')))
        link = wait.until(ec.visibility_of_element_located((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[2]/div[3]/div/div/div[2]/div/div[1]/div/div[1]/input')))
        submit = wait.until(ec.element_to_be_clickable((By.XPATH, '//*[@id="mG61Hd"]/div[2]/div/div[3]/div[1]/div[1]/div/span/span')))

        address.send_keys(all_property_address_list[counter])
        rent.send_keys(all_property_rent_list[counter])
        link.send_keys(all_property_links_list[counter])
        submit.click()
        print(f"record {counter}/{len(all_property_address_list)} added to the sheet.")
        # next_response = driver.find_element(by=By.XPATH, value='/html/body/div[1]/div[2]/div[1]/div/div[4]/a')
        # next_response.click()
    except NoSuchElementException:
        time.sleep(5)
    except TimeoutException:
        time.sleep(5)
    except ElementNotInteractableException:
        time.sleep(5)
    finally:
        if counter == len(all_property_address_list)-1:
            driver.quit()


