enum SVCarpenterNPC: StartingVillageNPC {
	static func talk() async {
		if await Game.shared.stages.blacksmith.stage3Stages == .goToCarpenter {
			await MessageBox.message("Here are your sticks.", speaker: .carpenter)
			if let lumberUUIDs = await Game.shared.stages.blacksmith.stage3LumberUUIDsToRemove {
				await Game.shared.player.removeItems(ids: lumberUUIDs)
			}
			await Game.shared.stages.blacksmith.setStage3LumberUUIDsToRemove(Game.shared.player.collect(item: .init(type: .stick, canBeSold: false), count: 20))
			await Game.shared.stages.blacksmith.setStage3Stages(.comeBack)
		} else {
			await MessageBox.message("I'm busy here...", speaker: .carpenter)
		}
	}
}
