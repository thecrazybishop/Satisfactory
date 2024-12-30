"""
Stores all the items in Satisfactory
"""

class Items:
    def __init__(self, name, prod_in, ipm, sol_ingr1=None, sol_ingr2=None, sol_ingr3=None,
                 sol_ing4=None, flu_ingr1=None, sol_waste=None, flu_waste=None):
        self.name = name
        #  What machine it is produced in
        self.prod_in = prod_in
        #  how many items per min
        self.ipm = ipm
        #  first solid ingredient
        self.sol_ingr1 = sol_ingr1
        self.sol_ingr2 = sol_ingr2
        self.sol_ingr3 = sol_ingr3
        self.sol_ingr4 = sol_ing4
        self.flu_ingr1 = flu_ingr1
        self.sol_waste = sol_waste
        self.flu_waste = flu_waste

    def __str__(self):
        return "Item:" + self.name  + "\n" + "Produced in:" + self.prod_in + "\n" + "Rate:" + str(self.ipm)

    def calculate_total_ingredients(self, desired_output_rate):
        total_ingredients = {}

        def add_ingredient(ingredient, quantity):
            if ingredient in total_ingredients:
                total_ingredients[ingredient.name] += quantity
            else:
                total_ingredients[ingredient.name] = quantity

        def calculate(item, multiplier):
            if item.sol_ingr1:
                add_ingredient(item.sol_ingr1, item.sol_ingr1.ipm * multiplier)
                calculate(item.sol_ingr1, multiplier)
            if item.sol_ingr2:
                add_ingredient(item.sol_ingr2, item.sol_ingr2.ipm * multiplier)
                calculate(item.sol_ingr2, multiplier)
            if item.sol_ingr3:
                add_ingredient(item.sol_ingr3, item.sol_ingr3.ipm * multiplier)
                calculate(item.sol_ingr3, multiplier)
            if item.sol_ingr4:
                add_ingredient(item.sol_ingr4, item.sol_ingr4.ipm * multiplier)
                calculate(item.sol_ingr4, multiplier)
            if item.flu_ingr1:
                add_ingredient(item.flu_ingr1, item.flu_ingr1.ipm * multiplier)
                calculate(item.flu_ingr1, multiplier)

        multiplier = desired_output_rate / self.ipm
        calculate(self, multiplier)
        return total_ingredients

recipes = {
    "Iron Ore": Items("Iron Ore", "Miner Mk.1", 60),
}


if __name__ == "__main__":
