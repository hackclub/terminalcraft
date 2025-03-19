enum RandomEventStuff {
	static func teachToChopLumber(by choppingLumberTeachingDoorTypes: ChoppingLumberTeachingDoorTypes) async {
		let speaker: NPCJob = switch choppingLumberTeachingDoorTypes {
			case .builder: .builder
			case .miner: .miner
		}
		switch await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber {
			case .no:
				await MessageBox.message("Here is what you need to do, take this axe and walk up to a tree and press the \(KeyboardKeys.space.render), or the \(KeyboardKeys.enter.render) key to chop it down. Please go get 10 lumber and bring it to me to show me you can do it.", speaker: speaker)
				await Game.shared.stages.random.setChopTreeAxeUUIDToRemove(Game.shared.player.collectIfNotPresent(item: .init(type: .axe(type: .init(durability: 10)), canBeSold: false)))
				await StatusBox.quest(.chopLumber(for: choppingLumberTeachingDoorTypes.name))
				await Game.shared.startingVillageChecks.setHasBeenTaughtToChopLumber(.inProgress(by: choppingLumberTeachingDoorTypes))
			case .inProgress(by: choppingLumberTeachingDoorTypes):
				if await Game.shared.player.has(item: .lumber, count: 10) {
					await MessageBox.message("Nice! 10 lumber! Now we can continue.", speaker: speaker)
					await Game.shared.player.removeItem(item: .lumber, count: 10)

					if let id = await Game.shared.stages.random.chopTreeAxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.startingVillageChecks.setHasBeenTaughtToChopLumber(.yes)
					await StatusBox.removeQuest(quest: .chopLumber(for: choppingLumberTeachingDoorTypes.name))
				} else {
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .lumber) - 10)) lumber.", speaker: speaker)
				}
			default:
				if case let .inProgress(otherDoorType) = await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber {
					await MessageBox.message("Please finish \(otherDoorType.name)'s quest first, then come back here.", speaker: speaker)
				}
		}
	}

	static func wantsToContinue(speaker: NPCJob) async -> Bool {
		let options: [MessageOption] = [
			.init(label: "Yes", action: {}),
			.init(label: "No", action: {}),
		]
		let selectedOption = await MessageBox.messageWithOptions("Would you like to continue and do your next task?", speaker: speaker, options: options)
		return selectedOption.label == "Yes"
	}
}
