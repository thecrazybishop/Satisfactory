from entities import Items

iron_ingot = Items(
    name="Iron Ingot",
    prod_in="Smelter",
    ipm=30,
    sol_ingr1_name="Iron Ore",
    sol_ingr1_ratio=1,
)
iron_plate = Items(
    name="Iron Plate",
    prod_in="Constructor",
    ipm=20,
    sol_ingr1_name="Iron Ingot",
    sol_ingr1_ratio=1.5,
)

iron_rod = Items(
    name="Iron Rod",
    prod_in="Constructor",
    ipm=15,
    sol_ingr1_name="Iron Ingot",
    sol_ingr1_ratio=1,
)

screw = Items(
    name="Screw",
    prod_in="Constructor",
    ipm=40,
    sol_ingr1_name="Iron Rod",
    sol_ingr1_ratio=0.25,
)
rein_iron_plate = Items(
    name="Reinforced Iron Plate",
    prod_in="Assembler",
    ipm=5,
    sol_ingr1_name="Iron Plate",
    sol_ingr1_ratio=6,
    sol_ingr2_name="Screw",
    sol_ingr2_ratio=12,
)
mod_frame = Items(
    name="Modular Frame",
    prod_in="Assembler",
    ipm=2,
    sol_ingr1_name="Reinforced Iron Plate",
    sol_ingr1_ratio=1.5,
    sol_ingr2_name="Iron Rod",
    sol_ingr2_ratio=6
)
copper_ingot = Items(
    name="Copper Ingot",
    prod_in="Smelter",
    ipm=30,
    sol_ingr1_name="Copper Ore",
    sol_ingr1_ratio=1,
)
copper_wire = Items(
    name="Copper Wire",
    prod_in="Constructor",
    ipm=30,
    sol_ingr1_name="Copper Ingot",
    sol_ingr1_ratio=.5,
)
cable = Items(
    name="Cable",
    prod_in="Constructor",
    ipm=30,
    sol_ingr1_name="Copper Wire",
    sol_ingr1_ratio=2,
)
copper_sheet = Items(
    name="Copper Sheet",
    prod_in="Constructor",
    ipm=20,
    sol_ingr1_name="Copper Ingot",
    sol_ingr1_ratio=1.5,
)


items_dict = {
    "Iron Ingot": iron_ingot,
    "Iron Plate": iron_plate,
    "Iron Rod": iron_rod,
    "Screw": screw,
    "Reinforced Iron Plate": rein_iron_plate,
    "Modular Frame": mod_frame,
    "Copper Ingot": copper_ingot,
    "Copper Wire": copper_wire,
    "Cable": cable,
    "Copper Sheet": copper_sheet,
}
