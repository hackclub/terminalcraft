enum CastleDoorEvent {
	static func open(tile: DoorTile) async {
		var options: [MessageOption] = [
			.init(label: "Go Inside", action: { await goInside(tile: tile) }),
		]
		if tile.isPartOfPlayerVillage {
			options.append(.init(label: "Upgrade", action: { upgrade(tile: tile) }))
		}
		options.append(.init(label: "Quit", action: {}))
		let selectedOption = await MessageBox.messageWithOptions("What would you like to do?", speaker: .game, options: options)
		await selectedOption.action()
	}

	static func goInside(tile: DoorTile) async {
		if case let .castle(side: side) = tile.type {
			await MapBox.setMapType(.castle(side: side))
		}
	}

	static func upgrade(tile _: DoorTile) {
		// TODO: upgrade building
	}
}
