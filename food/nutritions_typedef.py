from dataclasses import dataclass

@dataclass
class nutritions:
  """nutritional facts"""

  portion: str = ""

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
  vitamin_b6: int = 0
  vitamin_c: int = 0
  vitamin_d: int = 0

  calcium: int = 0
  cobalamin: int = 0
  iron: int = 0
  magnesium: int = 0

  def calories(self):
    return (self.protein + self.carb) * 4 + self.lipid * 9