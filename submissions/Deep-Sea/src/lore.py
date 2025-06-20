from rich.console import Console
from rich.panel import Panel
console = Console()
class LoreEntry:
    def __init__(self, entry_id, title, content, faction=None):
        self.id = entry_id
        self.title = title
        self.content = content
        self.faction = faction
ALL_LORE = {
    "log_anomaly_1": LoreEntry(
        "log_anomaly_1", 
        "Captain's Log - U.S.S. Wanderer",
        "Day 47. The anomaly... it's not just energy readings. It's a song. The crew hears it in their sleep. I hear it too. It promises... what does it promise? We're going deeper. Against regulations. Against reason. We have to know."
    )
}
class LoreManager:
    def __init__(self):
        self.unlocked_lore = set()
    def unlock_lore(self, lore_id):
        if lore_id in ALL_LORE and lore_id not in self.unlocked_lore:
            self.unlocked_lore.add(lore_id)
            entry = ALL_LORE[lore_id]
            return [f"\n[bold magenta]New Lore Unlocked: {entry.title}[/bold magenta]"]
        return []
    def get_lore_index_report(self):
        report = ["\n[bold]Lore Databank[/bold]"]
        if not self.unlocked_lore:
            report.append("No lore entries unlocked.")
            return report
        for i, lore_id in enumerate(self.unlocked_lore, 1):
            entry = ALL_LORE[lore_id]
            report.append(f" {i}. {entry.title}")
        report.append("\nType 'lore [number]' to read an entry.")
        return report
    def get_lore_entry_report(self, index):
        if not 1 <= index <= len(self.unlocked_lore):
            return ["[red]Invalid lore entry number.[/red]"]
        lore_id = list(self.unlocked_lore)[index - 1]
        entry = ALL_LORE[lore_id]
        return [f"[bold magenta]{entry.title}[/bold magenta]", entry.content]