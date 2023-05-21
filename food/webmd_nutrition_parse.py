from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import re

# start of food-category page url
food_category_patt = r"https://www.webmd.com/diet/ingredients-guide/"

# start of food-health-benefit page url
food_patt = r"https://www.webmd.com/diet/health-benefits-"

# html element class name of food serving portion
serving_cls_name = "nutrition-col__serving-value"


@dataclass
class nutritions:
  """nutritional facts"""

  # proteins, carbs, lipids, and dietary fiber are in grams.
  protein: int = 0
  carb: int = 0
  lipid: int = 0
  dietary_fiber: int = 0

  # macro minerals are in mg
  sodium: int = 0
  potassium: int = 0

  # vitamins and micro minerals are in percent.
  vitamin_a: int = 0
  vitamin_b3: int = 0
  vitamin_b6: int = 0
  vitamin_b12: int = 0
  vitamin_c: int = 0
  vitamin_d: int = 0
  vitamin_e: int = 0

  calcium: int = 0
  magnesium: int = 0


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


def scrape_nutritional_facts(driver, url):
  """ Given some `selenium` driver and an url to WebMD food benefit page, 
  returns TODO
  """
  nut = nutritions()
  driver.get(url)

  # nutrition column element
  nutrition_col = driver.find_element(By.CLASS_NAME, "nutrition-col")

  # portion size
  portion = nutrition_col.find_element(By.CLASS_NAME, serving_cls_name).text

  # macro nutritions
  macro_table = nutrition_col.find_element(By.CLASS_NAME, "macro-table")
  for elt in macro_table.find_elements(By.CLASS_NAME, "macro-table__thead"):

    # a text containing nutrition label, value, and unit.
    lbl_val_unit = elt.find_element(By.CLASS_NAME, "macro-table__nutration").text

    # strip away unit: we already know it
    last_space_idx = lbl_val_unit.rfind(" ")
    lbl_val = lbl_val_unit[:last_space_idx]

    # strip away numerical
    last_space_idx = lbl_val.rfind(" ")
    lbl, val = lbl_val[:last_space_idx], int(lbl_val[last_space_idx+1:])

    # assign to suitable field
    match lbl:
      case "Total Fat":
        nut.lipid = val
      case "Total Carbohydrate":
        nut.carb = val
      case "Protein":
        nut.protein = val
      case "Sodium":
        nut.sodium = val
      case "Potassium":
        nut.potassium = val
      case "Dietary Fiber":
        nut.dietary_fiber = val
      case other:
        pass


  # micro nutritions
  micro_table = nutrition_col.find_element(By.CLASS_NAME, "micro-facts-vitamins")
  for elt in micro_table.find_elements(By.CLASS_NAME, "micro-facts-vitamins__li"):
    tag = elt.find_element(By.CLASS_NAME, "micro-facts-vitamins__li-values").text
    percent = int(elt.find_element(By.CLASS_NAME, "micro-facts-vitamins__li-percent").text[:-1])

  print(nut)



driver = webdriver.Firefox()
webmd_url = "https://www.webmd.com/diet/ingredients-guide"
result = {}

# obtain links to each food category, i.e. fruits, vegetables, ...
food_category_links = scrape_href_list(driver, webmd_url, food_category_patt)

# obtain links to each individual food
food_links = []
# for food_cat_link in food_category_links:
#   food_links.extend(scrape_href_list(driver, food_cat_link, food_patt))

# for item in food_links:
#   print(item)

scrape_nutritional_facts(driver, "https://www.webmd.com/diet/health-benefits-apples")

driver.close()
