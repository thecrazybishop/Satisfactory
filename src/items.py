"""
Stores all the items in Satisfactory
"""

class Items:
    def __int__(self, name, stack_size, recipe=None):
        if recipe is None:
            recipe = ['DEFAULT']
        self.name = name,
        self.stack_size = stack_size,
        self.recipe = recipe
    def __str__(self):
        return "Item: " + str(self.name) + "\n" + "Stack Size: " + str(self.stack_size)

    def __eq__(self, other_item):
        return True if other_item.name == self.name else False