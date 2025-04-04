import Foundation

enum EditKingdomEvent {
	static func editKingdom(kingdomID: UUID) async {
		// TODO: make this into a pop up
		var exit = false
		while !exit {
			guard let kingdom = await Game.shared.getKingdom(id: kingdomID) else {
				await MessageBox.message("An error has occurred", speaker: .game)
				return
			}
			let options: [MessageOption] = [
				.init(label: "Quit", action: { exit = true }),
				.init(label: "Rename Kingdom", action: { await renameKingdom(kingdom: kingdom) }),
			]
			await MessageBox.message("Editing \(kingdom.name):", speaker: .game)
			await MessageBox.messageWithOptions("What do you want to do?", speaker: .game, options: options).action()
		}
	}

	static func renameKingdom(kingdom: Kingdom) async {
		let name = await MessageBox.messageWithTyping("New Name:", speaker: .game)
		if !name.isEmpty {
			await Game.shared.renameKingdom(id: kingdom.id, name: name)
		}
	}
}
