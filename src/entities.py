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
        self.sol_ingr1_amt = sol_ingr1_ratio
        self.sol_ingr2_name = sol_ingr2_name
        self.sol_ingr2_amt = sol_ingr2_ratio
        self.sol_ingr3_name = sol_ingr3_name
        self.sol_ingr3_amt = sol_ingr3_ratio
        self.sol_ingr_4_name = sol_ingr4_name
        self.sol_ingr4_amt = sol_ingr4_ratio
        self.flu_ingr1_name = flu_ingr1_name
        self.flu_ingr1_amt = flu_ingr1_ratio
        self.sol_waste_name = sol_waste_name
        self.sol_waste_amt = sol_waste_ratio
        self.flu_waste_name = flu_waste_name
        self.flu_waste_amt = flu_waste_ratio

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
            if self.sol_ingr4_name and self.sol_ingr4_ratio:
                total_ingredients[self.sol_ingr4_name] = self.sol_ingr4_ratio * desired_output_rate
            if self.flu_ingr1_name and self.flu_ingr1_ratio:
                total_ingredients[self.flu_ingr1_name] = self.flu_ingr1_ratio * desired_output_rate
            return total_ingredients












if __name__ == "__main__":