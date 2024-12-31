import tkinter as tk
import tkinter.messagebox as msg
from entities import Items
import dictionary

def calculate_ingredients():
    try:
        selected_item = item_var.get()
        desired_output_rate = int(entry.get())
        total_ingredients, breakdown = dictionary.items_dict[selected_item].calculate_total_ingredients(desired_output_rate, dictionary.items_dict)
        result = f"Total ingredients needed to produce {desired_output_rate} {selected_item}(s) per minute:\n"
        for ingredient, amount in total_ingredients.items():
            result += f"{ingredient}: {amount}\n"
        result += "\nBreakdown of each sub-ingredient:\n"
        for ingredient, details in breakdown.items():
            result += f"{ingredient}: {details}\n"
            for sub_ingredient, sub_amount in details.items():
                result += f"  {sub_ingredient}: {sub_amount}\n"
        msg.showinfo("Calculation Result", result)
    except ValueError:
        msg.showerror("Input Error", "Please enter a valid number")

def create_window():
    # Create the main window
    root = tk.Tk()
    root.title("Satisfactory Calculator")

    # Set the window size
    root.geometry("400x300")

    # Add a label for the dropdown
    label_item = tk.Label(root, text="Select Item:")
    label_item.pack(pady=10)

    # Add a dropdown for item selection
    global item_var
    item_var = tk.StringVar(root)
    item_var.set(list(dictionary.items_dict.keys())[0])  # Set default value
    dropdown = tk.OptionMenu(root, item_var, *dictionary.items_dict.keys())
    dropdown.config(bg="black", fg="white")
    dropdown.pack(pady=10)

    # Add a label for the entry
    label_rate = tk.Label(root, text="Desired Output Rate (items per minute):", bg="black", fg="white")
    label_rate.pack(pady=10)

    # Add an entry widget
    global entry
    entry = tk.Entry(root)
    entry.pack(pady=10)

    # Add a button to trigger the calculation
    button = tk.Button(root, text="Calculate", command=calculate_ingredients)
    button.pack(pady=10)

    # Start the Tkinter event loop
    root.mainloop()

if __name__ == "__main__":
    create_window()