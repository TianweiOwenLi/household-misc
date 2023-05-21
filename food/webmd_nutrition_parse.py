import pickle

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.support import expected_conditions as Ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
import re

from multiprocessing import Pool

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
  returns the parsed nutritional facts
  """
  nut = nutritions()
  
  nutrition_col = None
  try:
    driver.get(url)
    nutrition_col = WebDriverWait(driver=driver, timeout=5, poll_frequency=1).until(
      Ec.presence_of_element_located((By.CSS_SELECTOR, "div.nutrition-col"))
    )
  except TimeoutException:
    print(f"Timeout triggered on {url}")
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

  return nut

def scrape_nutfact_process(url):
  """ Similar to `scrape_nutritional_facts`, except can be used for 
  a standalone process
  """
  opt = Options()
  opt.add_argument('--headless')
  opt.add_argument("--window-size=960,1080")
  opt.page_load_strategy = "none"

  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument("--headless")
  chrome_options.add_experimental_option(
    # skip images
    "prefs", {"profile.managed_default_content_settings.images": 2}
  )

  driver = webdriver.Chrome(options=opt, chrome_options=chrome_options)

  benefit_idx = url.find("benefits-")

  food_name = url[benefit_idx+9:]
  if food_name.startswith("of-"):
    food_name = food_name[3:]
  
  print(f"Analyzing {food_name}")
  nut = scrape_nutritional_facts(driver, url)

  driver.close()
  return (food_name, nut)

opt = Options()
opt.add_argument('--headless')
opt.add_argument("--window-size=960,1080")

full_driver = webdriver.Chrome(options=opt)

# obtain links to each food category, i.e. fruits, vegetables, ...
food_category_links = scrape_href_list(full_driver, webmd_url, food_category_patt)

# obtain links to each individual food
food_links = []
for food_cat_link in food_category_links:
  guide_idx = food_cat_link.find("guide/")
  cat_name = food_cat_link[guide_idx+6:]
  print(f"Fetching category `{cat_name}`")
  food_links.extend(scrape_href_list(full_driver, food_cat_link, food_patt))

full_driver.close()


d, res = {}, []
with Pool() as pool:
  # parallel processing for better performance
  res = pool.map(scrape_nutfact_process, food_links)
  for (name, nut) in res:
    d[name] = nut

with open("food-nutritions.pkl", "wb") as f:
  pickle.dump(d, f)
