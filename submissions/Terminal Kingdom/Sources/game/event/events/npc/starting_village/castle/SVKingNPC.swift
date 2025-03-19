enum SVKingNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo(after: firstDialogue)
		if await Game.shared.stages.builder.stage4Stages == .talkToKing {
			await MessageBox.message("Hello \(NPCJob.king.render), I am the builders apprentice, we were wondering if we could build a new house in the village?", speaker: .player)
			await MessageBox.message("Hello \(Game.shared.player.name)! Yes that is a good idea.", speaker: .king)
			await MessageBox.message("Ok! Thank you! I'll go let him know", speaker: .player)
			await Game.shared.stages.builder.setStage4Stages(.comeBack)
		} else {
			await help()
		}
	}

	static func help() async {
		await MessageBox.message("Input help here", speaker: .king)
	}

	static func firstDialogue() async {
		await MessageBox.message("Welcome to the village, \(Game.shared.player.name).", speaker: .king)
		await MessageBox.message("I am the king of this village. I have heard of your arrival and I am glad you are here.", speaker: .king)
		await MessageBox.message("I am here to help you navigate this village.", speaker: .king)
		await MessageBox.message("Seems like you figured out how to walk. Your goal is to learn how to create your own village and go make your own kingdom! You can learn different skills by talking to different people in the buildings.", speaker: .king)
		await MessageBox.message("Now you might be wondering what buttons to press. If you press the \(KeyboardKeys.space.render) or \(KeyboardKeys.enter.render) key, you can interact with the tile you are on.", speaker: .king)
		await MessageBox.message("For example, to open a door, you would press one of those keys while standing on the door.", speaker: .king)
		await MessageBox.message("You can also press the \("p".styled(with: .bold)) key to see your current location on the map.", speaker: .king)
		await MessageBox.message("If you have any questions, feel free to ask me.", speaker: .king)
		// await MessageBox.message("I suggest starting with the miner, blacksmith, or the builder.", speaker: .king)
		await MessageBox.message("Good luck!", speaker: .king)
	}
}
