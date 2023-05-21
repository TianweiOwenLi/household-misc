from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re

def scrape_href_list(driver, url, patt):
  """ Given some `selenium` driver, an url, and some regex pattern, 
  returns a list of hyperrefs in the url's content that matches the pattern.
  """
  driver.get(url)

  href_list = []

  for element_with_link in driver.find_elements(By.TAG_NAME, 'a'):
    link = element_with_link.get_attribute('href')
    if link and re.match(patt, link):
      href_list.append(link)
  
  return href_list



driver = webdriver.Firefox()
webmd_url = "https://www.webmd.com/diet/ingredients-guide"
result = {}

# obtain links to each food category, i.e. fruits, vegetables, ...
food_category_patt = r"https://www.webmd.com/diet/ingredients-guide/"
food_category_links = scrape_href_list(driver, webmd_url, food_category_patt)

# obtain links to each individual food
food_patt = r"https://www.webmd.com/diet/health-benefits-"
food_links = []
for food_cat_link in food_category_links:
  food_links.extend(scrape_href_list(driver, food_cat_link, food_patt))

for item in food_links:
  print(item)

driver.close()