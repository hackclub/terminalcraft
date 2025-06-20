class Outpost:
    def __init__(self, name, faction):
        self.name = name
        self.faction = faction
        self.inventory = {
            "fuel": {"price": 10, "quantity": 100},
            "spare_parts": {"price": 20, "quantity": 50}
        }
    def trade(self, submarine, item, quantity, action):
        messages = []
        if action == "buy":
            if self.inventory[item]["quantity"] >= quantity:
                cost = self.inventory[item]["price"] * quantity
                self.inventory[item]["quantity"] -= quantity
                submarine.resources[item]['level'] += quantity
                messages.append(f"[bold green]Bought {quantity} {item}.[/bold green]")
            else:
                messages.append("[bold red]Not enough stock.[/bold red]")
        elif action == "sell":
            self.inventory[item]["quantity"] += quantity
            submarine.resources[item]['level'] -= quantity
            messages.append(f"[bold green]Sold {quantity} {item}.[/bold green]")
        return messages