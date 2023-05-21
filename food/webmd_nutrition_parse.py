import pickle

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re

from nutritions_typedef import nutritions

# official site
webmd_url = "https://www.webmd.com/diet/ingredients-guide"

# start of food-category page url
food_category_patt = r"https://www.webmd.com/diet/ingredients-guide/"

# start of food-health-benefit page url
food_patt = r"https://www.webmd.com/diet/health-benefits-"

# html element class name of food serving portion
serving_cls_name = "nutrition-col__serving-value"


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
  
  try:
    # WebDriverWait(driver=driver, timeout=5).until(
    #   Ec.presence_of_element_located(By.CLASS_NAME, )
    # )
    driver.get(url)
  except TimeoutException:
    driver.get(url)

  # nutrition column element
  nutrition_col = None
  try:
    nutrition_col = driver.find_element(By.CSS_SELECTOR, "div.nutrition-col")
  except NoSuchElementException:
    return None

  # portion size
  portion = nutrition_col.find_element(By.CSS_SELECTOR, "span.nutrition-col__serving-value").text
  nut.portion = portion

  # macro nutritions
  macro_table = nutrition_col.find_element(By.CSS_SELECTOR, "div.macro-table")
  for elt in macro_table.find_elements(By.CSS_SELECTOR, "div.macro-table__thead"):

    # a text containing nutrition label, value, and unit.
    lbl_val_unit = elt.find_element(By.CSS_SELECTOR, "div.macro-table__nutration").text

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
  micro_table = nutrition_col.find_element(By.CSS_SELECTOR, "div.micro-facts-vitamins")
  for elt in micro_table.find_elements(By.CSS_SELECTOR, "li.micro-facts-vitamins__li"):
    
    lbl = elt.find_element(By.CSS_SELECTOR, "span.micro-facts-vitamins__li-values").text
    percent = int(elt.find_element(By.CSS_SELECTOR, "span.micro-facts-vitamins__li-percent").text[:-1])
    
    match lbl:
      case "Vitamin A":
        nut.vitamin_a = percent
      case "Vitamin B6":
        nut.vitamin_b6 = percent
      case "Vitamin C":
        nut.vitamin_c = percent
      case "Vitamin D":
        nut.vitamin_d = percent
      case "Calcium":
        nut.calcium = percent
      case "Cobalamin":
        nut.cobalamin = percent
      case "Iron":
        nut.iron = percent
      case "Magnesium":
        nut.magnesium = percent
      case other:
        pass

  print(nut)
  return nut


options = Options()
# options.headless = True
# options.page_load_strategy = "none"
# options.add_argument("--window-size=960,1080")

driver = webdriver.Chrome(options=options)

# obtain links to each food category, i.e. fruits, vegetables, ...
food_category_links = scrape_href_list(driver, webmd_url, food_category_patt)

# obtain links to each individual food
food_links = []
for food_cat_link in food_category_links:
  food_links.extend(scrape_href_list(driver, food_cat_link, food_patt))

counter, n = 0, len(food_links)
result = {}

for link in food_links:
  counter += 1

  benefit_idx = link.find("benefits-")

  food_name = link[benefit_idx+9:]
  if food_name.startswith("of-"):
    food_name = food_name[3:]
  
  print(f"[{counter}/{n}] Analyzing {food_name}")
  result[food_name] = scrape_nutritional_facts(driver, link)

with open("food-nutritions.pkl", "wb") as f:
  pickle.dump(result, f)

driver.close()
