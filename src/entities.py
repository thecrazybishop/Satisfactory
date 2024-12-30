"""
Stores all the items in Satisfactory
"""

class Items:
    def __init__(self, name, prod_in, ipm, sol_ingr1_name=None, sol_ingr1_ratio=None, sol_ingr2_name=None, sol_ingr2_ratio=None,
                 sol_ingr3_name=None, sol_ingr3_ratio=None, sol_ingr4_name=None, sol_ingr4_ratio=None, flu_ingr1_name=None,
                 flu_ingr1_ratio=None, sol_waste_name=None, sol_waste_ratio=None, flu_waste_name=None, flu_waste_ratio=None):
        self.name = name
        #  What machine it is produced in
        self.prod_in = prod_in
        #  how many items per min
        self.ipm = ipm
        #  first solid ingredient
        self.sol_ingr1_name = sol_ingr1_name
        self.sol_ingr1_ratio = sol_ingr1_ratio
        self.sol_ingr2_name = sol_ingr2_name
        self.sol_ingr2_ratio = sol_ingr2_ratio
        self.sol_ingr3_name = sol_ingr3_name
        self.sol_ingr3_ratio = sol_ingr3_ratio
        self.sol_ingr_4_name = sol_ingr4_name
        self.sol_ingr4_ratio = sol_ingr4_ratio
        self.flu_ingr1_name = flu_ingr1_name
        self.flu_ingr1_ratio = flu_ingr1_ratio
        self.sol_waste_name = sol_waste_name
        self.sol_waste_ratio = sol_waste_ratio
        self.flu_waste_name = flu_waste_name
        self.flu_waste_ratio = flu_waste_ratio

    def calculate_total_ingredients(self, desired_output_rate):
        """
        Calculates the total ingredients needed to produce the desired output rate
        """
        total_ingredients = {}
        if self.sol_ingr1_name and self.sol_ingr1_ratio:
            total_ingredients[self.sol_ingr1_name] = self.sol_ingr1_ratio * desired_output_rate
        if self.sol_ingr2_name and self.sol_ingr2_ratio:
            total_ingredients[self.sol_ingr2_name] = self.sol_ingr2_ratio * desired_output_rate
        if self.sol_ingr3_name and self.sol_ingr3_ratio:
            total_ingredients[self.sol_ingr3_name] = self.sol_ingr3_ratio * desired_output_rate
        if self.sol_ingr_4_name and self.sol_ingr4_ratio:
            total_ingredients[self.sol_ingr_4_name] = self.sol_ingr4_ratio * desired_output_rate
        if self.flu_ingr1_name and self.flu_ingr1_ratio:
            total_ingredients[self.flu_ingr1_name] = self.flu_ingr1_ratio * desired_output_rate
        return total_ingredients
#  for testing
item1 = Items(
    name="Iron Plate",
    prod_in="Constructor",
    ipm=20,
    sol_ingr1_name="Iron Ingot",
    sol_ingr1_ratio=1.6667,
)
#  for testing
item2 = Items(
    name="Iron Rod",
    prod_in="Constructor",
    ipm=15,
    sol_ingr1_name="Iron Ingot",
    sol_ingr1_ratio=1,
)

items_list = [item1, item2]

desired_output_rate = 500
for item in items_list:
    total_ingredients = item.calculate_total_ingredients(desired_output_rate)
    print(f"Total ingredients needed to produce {desired_output_rate} {item.name} per minute:")
    for total_ingredients_name, total_ingredients_amt in total_ingredients.items():
        print(f"{total_ingredients_name}: {total_ingredients_amt}")
    print()

