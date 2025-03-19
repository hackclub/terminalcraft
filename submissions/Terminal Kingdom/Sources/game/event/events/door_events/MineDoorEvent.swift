enum MineDoorEvent {
	static func open(tile: DoorTile) async {
		var options: [MessageOption] = [
			.init(label: "Go Inside", action: { await goInside(tile: tile) }),
		]
		if await Game.shared.player.has(item: .lumber, count: 100), await Game.shared.player.has(item: .iron, count: 20), await Game.shared.player.has(item: .stone, count: 30), await Game.shared.stages.mine.stage7Stages == .upgrade {
			options.append(.init(label: "Upgrade", action: { await upgrade(tile: tile) }))
		}
		options.append(.init(label: "Quit", action: {}))
		let selectedOption = await MessageBox.messageWithOptions("What would you like to do?", speaker: .game, options: options)
		await selectedOption.action()
	}

	static func goInside(tile _: DoorTile) async {
		await MapBox.setMapType(.mine)
	}

	static func upgrade(tile: DoorTile) async {
		if let ids = await Game.shared.stages.mine.stage7ItemUUIDsToRemove {
			await Game.shared.stages.mine.setStage7Stages(.upgraded)
			await Game.shared.player.removeItems(ids: ids)
			await goInside(tile: tile)
		}
	}
}
