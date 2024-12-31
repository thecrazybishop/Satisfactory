from entities import Items
import dictionary
def main():
    desired_output_rate = 19
    total_ingredients, breakdown = dictionary.rein_iron_plate.calculate_total_ingredients(desired_output_rate, dictionary.items_dict)
    print(f"Total ingredients needed to produce {desired_output_rate} Reinforced Iron Plates per minute:")
    for ingredient, amount in total_ingredients.items():
        print(f"{ingredient}: {amount}")

    print("\nBreakdown of each sub-ingredient:")
    for ingredient, details in breakdown.items():
        print(f"{ingredient}: {details}")
        for sub_ingredient, sub_amount in details.items():
            print(f"  {sub_ingredient}: {sub_amount}")

if __name__ == "__main__":
    main()