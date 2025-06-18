import json

class Card:
    def __init__(self, title, description="", priority=1):
        self.title = title
        self.description = description
        self.priority = priority

class Column:
    def __init__(self, name):
        self.name = name
        self.cards = []

class KanbanBoard:
    def __init__(self):
        self.columns = []

    def add_column(self, name):
        self.columns.append(Column(name))

    def add_card(self, column_index, title, description="", priority=1):
        self.columns[column_index].cards.append(Card(title, description, priority))

    def move_card(self, from_col, to_col, card_index):
        card = self.columns[from_col].cards.pop(card_index)
        self.columns[to_col].cards.append(card)

    def save(self, filename):
        data = [
            {
                "name": col.name,
                "cards": [
                    {
                        "title": c.title,
                        "description": c.description,  # Fixed typo in key name (removed colon)
                        "priority": c.priority  # Added priority
                    } 
                    for c in col.cards
                ]
            }
            for col in self.columns
        ]
        with open(filename, "w") as f:
            json.dump(data, f)

    def load(self, filename):
        with open(filename, "r") as f:
            data = json.load(f)
        self.columns = []
        for col_data in data:
            col = Column(col_data["name"])
            for card_data in col_data["cards"]:
                col.cards.append(Card(
                    card_data["title"],
                    card_data.get("description", ""),
                    card_data.get("priority", 1)  # Added priority loading with default value 1
                ))
            self.columns.append(col)