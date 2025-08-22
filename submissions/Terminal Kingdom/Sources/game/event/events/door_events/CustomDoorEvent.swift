import Foundation

enum CustomDoorEvent {
	static func open(tile: DoorTile, mapID: UUID?, doorType _: DoorTileTypes) async {
		guard let mapID else {
			await MessageBox.message("This building doesn't have an inside. Try breaking and replacing the door.", speaker: .game)
			return
		}
		var options: [MessageOption] = [
			.init(label: "Go Inside", action: { await goInside(tile: tile, mapID: mapID) }),
		]

		let x = await Game.shared.player.position.x
		let y = await Game.shared.player.position.y
		let building = await Game.shared.hasKingdomBuilding(x: x, y: y)
		if let building {
			if await building.canBeUpgraded() {
				options.append(.init(label: "Upgrade", action: { await upgrade(building: building) }))
			}
		}
		options.append(.init(label: "Quit", action: {}))
		let selectedOption = await MessageBox.messageWithOptions("What would you like to do?", speaker: .game, options: options)
		await selectedOption.action()
	}

	static func goInside(tile _: DoorTile, mapID: UUID) async {
		await MapBox.setMapType(.custom(mapID: mapID))
	}

	static func upgrade(building: Building) async {
		var newBuilding = building
		await newBuilding.upgrade()
		guard let kingdom = await Game.shared.getKingdom(buildingID: building.id) else { return }
		await Game.shared.updateKingdomBuilding(kingdomID: kingdom.id, buildingID: building.id, newBuilding: newBuilding)
	}
}
