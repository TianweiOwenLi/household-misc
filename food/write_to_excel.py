import xlwt, pickle
from nutritions_typedef import nutritions

food_idx, portion_idx, \
  protein_idx, carb_idx, lipid_idx, cal_idx, \
  fiber_idx, \
  na_idx, k_idx, \
  vit_a_idx, vit_b6_idx, vit_b12_idx, vit_c_idx, vit_d_idx, \
  ca_idx, fe_idx, mg_idx \
  = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16

with open("food-nutritions.pkl", "rb") as f:
  data: dict = pickle.load(f)
  
  book = xlwt.Workbook(encoding="utf-8")
  sheet = book.add_sheet("Nutritional Facts Sheet")

  sheet.write(0, food_idx, "Food name")
  sheet.write(0, portion_idx, "Portion (g)")
  sheet.write(0, protein_idx, "Protein (g)")
  sheet.write(0, carb_idx, "Carb (g)")
  sheet.write(0, lipid_idx, "Lipids (g)")
  sheet.write(0, cal_idx, "Calories")
  sheet.write(0, fiber_idx, "Dietary fiber (g)")
  sheet.write(0, na_idx, "Na (mg)")
  sheet.write(0, k_idx, "K (mg)")
  sheet.write(0, vit_a_idx, "Vitamin A (% DV)")
  sheet.write(0, vit_b6_idx, "Vitamin B6 (% DV)")
  sheet.write(0, vit_b12_idx, "Vitamin B12 (% DV)")
  sheet.write(0, vit_c_idx, "Vitamin C (% DV)")
  sheet.write(0, vit_d_idx, "Vitamin D (% DV)")
  sheet.write(0, ca_idx, "Ca (% DV)")
  sheet.write(0, fe_idx, "Fe (% DV)")
  sheet.write(0, mg_idx, "Mg (% DV)")

  counter = 0
  for food_name in data.keys():

    nut: nutritions = data[food_name]
    if nut == None:
      continue

    counter += 1

    # parse portion in grams
    portion_str = nut.portion
    lparen_idx, rparen_idx = portion_str.find("("), portion_str.find(")")
    portion_str_num_with_gram = portion_str[lparen_idx+1:rparen_idx]
    portion_str_num = portion_str_num_with_gram[:-2]
    portion_num = float(portion_str_num)

    sheet.write(counter, food_idx, food_name)
    sheet.write(counter, portion_idx, portion_num)
    sheet.write(counter, protein_idx, nut.protein)
    sheet.write(counter, carb_idx, nut.carb)
    sheet.write(counter, lipid_idx, nut.lipid)
    sheet.write(counter, cal_idx, nut.calories())
    sheet.write(counter, fiber_idx, nut.dietary_fiber)
    sheet.write(counter, na_idx, nut.sodium)
    sheet.write(counter, k_idx, nut.potassium)
    sheet.write(counter, vit_a_idx, nut.vitamin_a)
    sheet.write(counter, vit_b6_idx, nut.vitamin_b6)
    sheet.write(counter, vit_b12_idx, nut.cobalamin)
    sheet.write(counter, vit_c_idx, nut.vitamin_c)
    sheet.write(counter, vit_d_idx, nut.vitamin_d)
    sheet.write(counter, ca_idx, nut.calcium)
    sheet.write(counter, fe_idx, nut.iron)
    sheet.write(counter, mg_idx, nut.magnesium)
    

  book.save("data.xlsx")
