enum SVHunterNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo()
		if await Game.shared.stages.blacksmith.stage7Stages == .bringToHunter {
			await Game.shared.stages.blacksmith.setStage7Stages(.comeBack)
			await MessageBox.message("Hello \(Game.shared.player.name)! Thank you for this sword!!", speaker: .hunter)
			if let id = await Game.shared.stages.blacksmith.stage7SwordUUIDToRemove {
				await Game.shared.player.removeItem(id: id)
			}
		} else {
			await getStage()
		}
	}

	static func getStage() async {
		let options: [MessageOption] = [
			.init(label: "Yes", action: {}),
			.init(label: "No", action: {}),
		]
		let selectedOption = await MessageBox.messageWithOptions("Hello \(Game.shared.player.name)! Would you like to learn how to be a hunter?", speaker: .hunter, options: options)
		if selectedOption.label == "Yes" {
			await stage1()
		} else {
			return
		}
	}

	static func stage1() async {}
}
