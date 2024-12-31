class Items:
    def __init__(self, name, prod_in, ipm, sol_ingr1_name=None, sol_ingr1_ratio=None, sol_ingr2_name=None, sol_ingr2_ratio=None,
                 sol_ingr3_name=None, sol_ingr3_ratio=None, sol_ingr4_name=None, sol_ingr4_ratio=None, flu_ingr1_name=None,
                 flu_ingr1_ratio=None, sol_waste_name=None, sol_waste_ratio=None, flu_waste_name=None, flu_waste_ratio=None):
        self.name = name
        self.prod_in = prod_in
        self.ipm = ipm
        self.sol_ingr1_name = sol_ingr1_name
        self.sol_ingr1_ratio = sol_ingr1_ratio
        self.sol_ingr2_name = sol_ingr2_name
        self.sol_ingr2_ratio = sol_ingr2_ratio
        self.sol_ingr3_name = sol_ingr3_name
        self.sol_ingr3_ratio = sol_ingr3_ratio
        self.sol_ingr4_name = sol_ingr4_name
        self.sol_ingr4_ratio = sol_ingr4_ratio
        self.flu_ingr1_name = flu_ingr1_name
        self.flu_ingr1_ratio = flu_ingr1_ratio
        self.sol_waste_name = sol_waste_name
        self.sol_waste_ratio = sol_waste_ratio
        self.flu_waste_name = flu_waste_name
        self.flu_waste_ratio = flu_waste_ratio

    def calculate_total_ingredients(self, desired_output_rate, items_dict):
        total_ingredients = {}
        breakdown = {}
        self.add_ingredients(total_ingredients, breakdown, self.sol_ingr1_name, self.sol_ingr1_ratio, desired_output_rate, items_dict)
        self.add_ingredients(total_ingredients, breakdown, self.sol_ingr2_name, self.sol_ingr2_ratio, desired_output_rate, items_dict)
        self.add_ingredients(total_ingredients, breakdown, self.sol_ingr3_name, self.sol_ingr3_ratio, desired_output_rate, items_dict)
        self.add_ingredients(total_ingredients, breakdown, self.sol_ingr4_name, self.sol_ingr4_ratio, desired_output_rate, items_dict)
        return total_ingredients, breakdown

    def add_ingredients(self, total_ingredients, breakdown, ingr_name, ingr_ratio, desired_output_rate, items_dict):
        if ingr_name and ingr_ratio:
            if ingr_name in items_dict:
                sub_ingredients, sub_breakdown = items_dict[ingr_name].calculate_total_ingredients(ingr_ratio * desired_output_rate, items_dict)
                for sub_ingr_name, sub_ingr_amnt in sub_ingredients.items():
                    if sub_ingr_name in total_ingredients:
                        total_ingredients[sub_ingr_name] += sub_ingr_amnt
                    else:
                        total_ingredients[sub_ingr_name] = sub_ingr_amnt
                if ingr_name in breakdown:
                    for sub_ingr_name, sub_ingr_amnt in sub_breakdown.items():
                        if sub_ingr_name in breakdown[ingr_name]:
                            breakdown[ingr_name][sub_ingr_name] += sub_ingr_amnt
                        else:
                            breakdown[ingr_name][sub_ingr_name] = sub_ingr_amnt
                else:
                    breakdown[ingr_name] = sub_breakdown
            else:
                if ingr_name in total_ingredients:
                    total_ingredients[ingr_name] += ingr_ratio * desired_output_rate
                else:
                    total_ingredients[ingr_name] = ingr_ratio * desired_output_rate
                breakdown[ingr_name] = ingr_ratio * desired_output_rate

