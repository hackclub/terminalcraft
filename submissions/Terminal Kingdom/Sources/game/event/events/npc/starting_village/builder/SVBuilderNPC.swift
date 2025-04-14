enum SVBuilderNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo()
		await getStage()
	}

	static func getStage() async {
		switch await Game.shared.stages.builder.stageNumber {
			case 0:
				if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .no {
					let options: [MessageOption] = [
						.init(label: "Yes", action: {}),
						.init(label: "No", action: {}),
					]
					let selectedOption = await MessageBox.messageWithOptions("Hello \(Game.shared.player.name)! Would you like to learn how to build?", speaker: .builder, options: options)
					if selectedOption.label == "Yes" {
						await stage0()
					} else {
						return
					}
				} else {
					await stage0()
				}
			case 1:
				await stage1()
			case 2:
				await stage2()
			case 3:
				await stage3()
			case 4:
				await stage4()
			case 5:
				await stage5()
			case 6:
				await stage6()
			case 7:
				await stage7()
			case 8:
				await stage8()
			case 9:
				await stage9()
			default:
				break
		}
	}

	static func stage0() async {
		if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber != .yes {
			if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .no {
				await MessageBox.message("Before I can teach you how to build, you need to learn how to chop lumber.", speaker: .builder)
			}
			await RandomEventStuff.teachToChopLumber(by: .builder)
			if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .yes {
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await stage1()
				}
			}
		} else {
			await MessageBox.message("Hello \(Game.shared.player.name)! Looks like you already know how to chop lumber.", speaker: .builder)
			let options: [MessageOption] = [
				.init(label: "Yes", action: {}),
				.init(label: "No", action: {}),
			]
			let selectedOption = await MessageBox.messageWithOptions("Would you like to learn how to build?", speaker: .builder, options: options)
			if selectedOption.label == "Yes" {
				await stage1()
			}
		}
	}

	static func stage1() async {
		switch await Game.shared.stages.builder.stage1Stages {
			case .notStarted:
				await MessageBox.message("Before we can start building, we need materials. Can you go collect 20 stone and 10 iron from the mine and bring it back to me?", speaker: .builder)
				await Game.shared.stages.builder.setStage1Stages(.collect)
				await StatusBox.quest(.builder1)
			case .collect:
				await MessageBox.message("You haven't gone to the mine yet. It will be marked with an \("!".styled(with: .bold)) on the map.", speaker: .builder)
			case .bringBack:
				if await Game.shared.player.has(item: .stone, count: 20), await Game.shared.player.has(item: .iron, count: 10) {
					await MessageBox.message("Great, You have collected the materials!", speaker: .builder)
					if let ids = await Game.shared.stages.builder.stage1ItemsUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ids)
					}
					await Game.shared.stages.builder.setStage1Stages(.done)
					await Game.shared.player.setBuilderSkillLevel(.one)
					await StatusBox.removeQuest(quest: .builder1)
					fallthrough
				} else {
					await MessageBox.message("You still need to collect the materials. It will be marked with an \("!".styled(with: .bold)) on the map.", speaker: .builder)
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage2() async {
		switch await Game.shared.stages.builder.stage2Stages {
			case .notStarted:
				await MessageBox.message("Now, we need some lumber. Can you get 20 of it? Here is an axe.", speaker: .builder)
				await Game.shared.stages.builder.setStage2Stages(.collect)
				await StatusBox.quest(.builder2)
				await Game.shared.stages.builder.setStage2AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 20)), canBeSold: false)))
			case .collect:
				if await Game.shared.player.has(item: .lumber, count: 20) {
					await MessageBox.message("Great, You have collected the lumber! Now we can start building.", speaker: .builder)
					if let id = await Game.shared.stages.builder.stage2AxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.player.removeItem(item: .lumber, count: 20)
					await Game.shared.player.setBuilderSkillLevel(.two)
					await Game.shared.stages.builder.setStage2Stages(.done)
					await StatusBox.removeQuest(quest: .builder2)
					fallthrough
				} else {
					if let id = await Game.shared.stages.builder.stage2AxeUUIDToRemove, await !Game.shared.player.has(id: id) {
						await MessageBox.message("Uh oh, looks like you lost your axe. Here is a new one.", speaker: .builder)
						await Game.shared.stages.builder.setStage2AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, but you still need to get \(abs(Game.shared.player.getCount(of: .lumber) - 20)) lumber.", speaker: .builder)
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage3() async {
		switch await Game.shared.stages.builder.stage3Stages {
			case .notStarted:
				await MessageBox.message("Now that we have the materials, we can start building. Can you make a door at the workstation. It is marked as a \(StationTileType.workbench.render). Here are the materials you will need.", speaker: .builder)
				await Game.shared.stages.builder.setStage3Stages(.makeDoor)
				await StatusBox.quest(.builder3)
				let uuid1 = await Game.shared.player.collect(item: .init(type: .lumber, canBeSold: false), count: 4)
				let uuid2 = await Game.shared.player.collect(item: .init(type: .iron, canBeSold: false), count: 1)
				await Game.shared.stages.builder.setStage3ItemsToMakeDoorUUIDsToRemove(uuid1 + uuid2)
			case .makeDoor:
				await MessageBox.message("You haven't made the door yet. It is marked with a \(StationTileType.workbench.render).", speaker: .builder)
			case .returnToBuilder:
				if await Game.shared.player.has(item: .door(tile: .init(type: .house)), count: 1) {
					await MessageBox.message("Great, You have made the door!", speaker: .builder)
					if let ids = await Game.shared.stages.builder.stage3ItemsToMakeDoorUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ids)
					}
					if let id = await Game.shared.stages.builder.stage3DoorUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.stages.builder.setStage3Stages(.done)
					await Game.shared.player.setBuilderSkillLevel(.three)
					await StatusBox.removeQuest(quest: .builder3)
					fallthrough
				} else {
					await MessageBox.message("You still need to make the door. It is marked with a \(StationTileType.workbench.render).", speaker: .builder)
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage4() async {
		switch await Game.shared.stages.builder.stage4Stages {
			case .notStarted:
				await MessageBox.message("Now that we have the door, we can start building. Can you go talk to the king and ask him for permission to build a house?", speaker: .builder)
				await Game.shared.stages.builder.setStage4Stages(.talkToKing)
				await StatusBox.quest(.builder4)
			case .talkToKing:
				await MessageBox.message("You haven't talked to the king yet.", speaker: .builder)
			case .comeBack:
				await MessageBox.message("I see that you've talked to the king. What did he say?", speaker: .builder)
				await MessageBox.message("He said we can build a new house!", speaker: .player)
				await MessageBox.message("Nice! Lets get started right away!", speaker: .builder)
				await Game.shared.stages.builder.setStage4Stages(.done)
				await Game.shared.player.setBuilderSkillLevel(.four)
				await StatusBox.removeQuest(quest: .builder4)
				fallthrough
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage5() async {
		switch await Game.shared.stages.builder.stage5Stages {
			case .notStarted:
				await MessageBox.message("Now that we have permission, we can start building immediately! Can you begin building the house?", speaker: .builder)
				await instructions()
				await Game.shared.stages.builder.setStage5Stages(.buildHouse)
				await Game.shared.player.setCanBuild(true)
				let uuid1 = await Game.shared.player.collect(item: .init(type: .lumber, canBeSold: false), count: 5 * 24)
				let uuid2 = await Game.shared.player.collect(item: .init(type: .door(tile: .init(type: .house)), canBeSold: false), count: 1)
				await Game.shared.stages.builder.setStage5ItemsToBuildHouseUUIDsToRemove(uuid1 + uuid2)
				await StatusBox.quest(.builder5)
			case .buildHouse:
				if await Game.shared.stages.builder.stage5HasBuiltHouse {
					await MessageBox.message("Nice, you have built the house!", speaker: .builder)
					await Game.shared.stages.builder.setStage5Stages(.done)
					await Game.shared.player.setBuilderSkillLevel(.five)
					await StatusBox.removeQuest(quest: .builder5)
					if let ids = await Game.shared.stages.builder.stage5ItemsToBuildHouseUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ids)
					}
					await Game.shared.player.setCanBuild(false)
					fallthrough
				} else {
					await MessageBox.message("You haven't built the house yet.", speaker: .builder)
					await MessageBox.messageWithOptions("Do you want to hear the instructions again?", speaker: .builder, options: [.init(label: "Yes", action: instructions), .init(label: "No", action: {})]).action()
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
		func instructions() async {
			await MessageBox.message("This is what you need to do: Go pick an area and press \(KeyboardKeys.b.render). This will put you in \("build mode".styled(with: .bold)). Then press \(KeyboardKeys.enter.render), as long as you have 5 lumber you will build a building tile. Place the buildings next to each other. Then place the door in a small area. If you are unsure, look at the other buildings in this village. If you want to see all the controls press \(KeyboardKeys.questionMark.render) in build mode.", speaker: .builder)
		}
	}

	static func stage6() async {
		switch await Game.shared.stages.builder.stage6Stages {
			case .notStarted:
				await MessageBox.message("Now that we have a house, we need to decorate the interior. Can you collect 30 lumber and bring it back to me?", speaker: .builder)
				await Game.shared.stages.builder.setStage6Stages(.collect)
				await StatusBox.quest(.builder6)
				await Game.shared.stages.builder.setStage6AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 30)), canBeSold: false)))
			case .collect:
				if await Game.shared.player.has(item: .lumber, count: 30) {
					await MessageBox.message("Great! You have collected the lumber! Now we can start decorating the inside.", speaker: .builder)
					if let id = await Game.shared.stages.builder.stage6AxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.player.removeItem(item: .lumber, count: 30)
					await Game.shared.player.setBuilderSkillLevel(.six)
					await Game.shared.stages.builder.setStage6Stages(.done)
					await StatusBox.removeQuest(quest: .builder6)
					fallthrough
				} else {
					if let id = await Game.shared.stages.builder.stage6AxeUUIDToRemove, await !Game.shared.player.has(id: id) {
						await MessageBox.message("Uh oh, looks like you lost your axe, here is a new one.", speaker: .builder)
						await Game.shared.stages.builder.setStage6AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .lumber) - 30)) lumber.", speaker: .builder)
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage7() async {
		switch await Game.shared.stages.builder.stage7Stages {
			case .notStarted:
				await MessageBox.message("Can you take these decorations and organize them inside of the house? You can decorate it however you want!", speaker: .builder)
				await Game.shared.stages.builder.setStage7Stages(.buildInside)
				await StatusBox.quest(.builder7)
				let uuid1 = await Game.shared.player.collect(item: .init(type: .bed, canBeSold: false), count: 1)
				let uuid2 = await Game.shared.player.collect(item: .init(type: .chest, canBeSold: false), count: 2)
				let uuid3 = await Game.shared.player.collect(item: .init(type: .desk, canBeSold: false), count: 1)
				await Game.shared.stages.builder.setStage7ItemsToBuildInsideUUIDsToRemove(uuid1 + uuid2 + uuid3)
				await Game.shared.player.setCanBuild(true)
			case .buildInside:
				if await Game.shared.stages.builder.stage7HasBuiltInside {
					await MessageBox.message("Looks like you are done!", speaker: .builder)
					await Game.shared.stages.builder.setStage7Stages(.done)
					await Game.shared.player.setBuilderSkillLevel(.seven)
					await StatusBox.removeQuest(quest: .builder7)
					if let ids = await Game.shared.stages.builder.stage7ItemsToBuildInsideUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ids)
					}
					await Game.shared.player.setCanBuild(false)
					fallthrough
				} else {
					await MessageBox.message("You haven't decorated the interior of your house yet.", speaker: .builder)
				}
			case .done:
				await Game.shared.stages.builder.next()
				if await RandomEventStuff.wantsToContinue(speaker: .builder) {
					await getStage()
				}
		}
	}

	static func stage8() async {
		await Game.shared.player.setCanBuild(true)
		await MessageBox.message("You can now build when ever you want! But remember that you can only break pieces that you place. Also we don't accually need that that house; since you built it, why don't you keep it!", speaker: .builder)
		await Game.shared.player.setBuilderSkillLevel(.nine)
		// TODO: check if the player has enough stats
		await MessageBox.message("I also think you are ready to make your own village! Come back to me when you are ready.", speaker: .builder)
		await Game.shared.stages.builder.next()
	}

	static func stage9() async {
		// TODO: check if the player has enough stats
		await MessageBox.message("So, you are ready to go create your own kingdom! You will need this.", speaker: .builder)
		_ = await Game.shared.player.collect(item: .init(type: .door(tile: .init(type: .builder))))
		await MessageBox.message("Go and have fun!!", speaker: .builder)
		await Game.shared.player.setBuilderSkillLevel(.nine)
		await Game.shared.stages.builder.next()
	}
}

enum BuilderStage1Stages: Codable {
	case notStarted, collect, bringBack, done
}

enum BuilderStage2Stages: Codable {
	case notStarted, collect, done
}

enum BuilderStage3Stages: Codable {
	case notStarted, makeDoor, returnToBuilder, done
}

enum BuilderStage4Stages: Codable {
	case notStarted, talkToKing, comeBack, done
}

enum BuilderStage5Stages: Codable {
	case notStarted, buildHouse, done
}

enum BuilderStage6Stages: Codable {
	case notStarted, collect, done
}

enum BuilderStage7Stages: Codable {
	// TODO: add more cases
	case notStarted, buildInside, done
}

enum BuilderStage8Stages: Codable {
	// TODO: add more cases
	case notStarted, done
}

enum BuilderStage9Stages: Codable {
	// TODO: add more cases
	case notStarted, done
}

enum BuilderStage10Stages: Codable {
	// TODO: add more cases
	case notStarted, done
}
