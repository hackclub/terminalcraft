enum PotterAreaDoorEvent {
	static func open(tile: DoorTile) async {
		let options: [MessageOption] = [
			.init(label: "Go Inside", action: { await goInside(tile: tile) }),
			.init(label: "Quit", action: {}),
		]
		let selectedOption = await MessageBox.messageWithOptions("What would you like to do?", speaker: .game, options: options)
		await selectedOption.action()
	}

	static func goInside(tile _: DoorTile) async {
		if await Game.shared.stages.farm.stageNumber >= 5 {
			await MapBox.setMapType(.potter)
		} else {
			await MessageBox.message("Its locked.", speaker: .game)
		}
	}
}
