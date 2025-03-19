enum SVFarmerNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo()
		await getStage()
	}

	static func getStage() async {
		switch await Game.shared.stages.farm.stageNumber {
			case 0:
				let options: [MessageOption] = [
					.init(label: "Yes", action: {}),
					.init(label: "No", action: {}),
				]
				let selectedOption = await MessageBox.messageWithOptions("Hello \(Game.shared.player.name)! Would you like to learn how to be a farmer?", speaker: .farmer, options: options)
				if selectedOption.label == "Yes" {
					await Game.shared.stages.farm.next()
					await getStage()
				} else {
					return
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
			default:
				break
		}
	}

	static func stage1() async {
		switch await Game.shared.stages.farm.stage1Stages {
			case .notStarted:
				await MessageBox.message("We need some seeds to plant. Can you go chop down a tree and get a tree seed?", speaker: .farmer)
				await Game.shared.stages.farm.setStage1AxeUUIDsToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 1)), canBeSold: false)))
				await Game.shared.stages.farm.setStage1Stages(.collect)
				await StatusBox.quest(.farm1)
			case .collect:
				if await Game.shared.player.has(item: .tree_seed) {
					await MessageBox.message("Great job!", speaker: .farmer)
					await Game.shared.player.removeItem(item: .tree_seed)
					await Game.shared.stages.farm.setStage1Stages(.done)
					await StatusBox.removeQuest(quest: .farm1)
					await Game.shared.player.setFarmingSkillLevel(.one)
					fallthrough
				} else {
					if let id = await Game.shared.stages.farm.stage1AxeUUIDToRemove, await !Game.shared.player.has(id: id) {
						await MessageBox.message("Uh oh, looks like you lost your axe. Here is a new one.", speaker: .farmer)
						await Game.shared.stages.farm.setStage1AxeUUIDsToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 1)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, but you still need to get a tree seed.", speaker: .farmer)
				}
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}

	static func stage2() async {
		switch await Game.shared.stages.farm.stage2Stages {
			case .notStarted:
				await MessageBox.message("Now that we have seeds, we need to plant them. There is a pot in the room under me, go plant it in there.", speaker: .farmer)
				await Game.shared.stages.farm.setStage2Stages(.plant)
				await Game.shared.stages.farm.setStage2SeedUUIDsToRemove(Game.shared.player.collect(item: .init(type: .tree_seed, canBeSold: false)))
				await StatusBox.quest(.farm2)
			case .plant:
				await MessageBox.message("You haven't planted the seed yet.", speaker: .farmer)
			case .comeback:
				await MessageBox.message("Great job! Now it can start growing!", speaker: .farmer)
				await Game.shared.stages.farm.setStage2Stages(.done)
				await StatusBox.removeQuest(quest: .farm2)
				await Game.shared.player.setFarmingSkillLevel(.two)
				fallthrough
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}

	static func stage3() async {
		switch await Game.shared.stages.farm.stage3Stages {
			case .notStarted:
				await MessageBox.message("Now we need to wait for the tree to grow. After it has grown, collect it and bring it to me.", speaker: .farmer)
				await Game.shared.stages.farm.setStage3Stages(.collect)
				await StatusBox.quest(.farm3)
			case .collect:
				await MessageBox.message("You haven't collected the tree yet.", speaker: .farmer)
			case .comeBack:
				await MessageBox.message("Great job!", speaker: .farmer)
				await Game.shared.stages.farm.setStage3Stages(.done)
				await StatusBox.removeQuest(quest: .farm3)
				await Game.shared.player.setFarmingSkillLevel(.three)
				fallthrough
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}

	static func stage4() async {
		switch await Game.shared.stages.farm.stage4Stages {
			case .notStarted:
				await MessageBox.message("Now I want to teach you how to get a pot to plant your own stuff. Can you go get 10 clay from the mine?", speaker: .farmer)
				await Game.shared.stages.farm.setStage4Stages(.collect)
				await StatusBox.quest(.farm4)
			case .collect:
				if await Game.shared.stages.farm.stage4Stages.canGetClay {
					await MessageBox.message("You haven't collected the clay from the mine yet.", speaker: .farmer)
				} else {
					await MessageBox.message("You haven't collected the clay from the miner yet.", speaker: .farmer)
				}
			case .comeBack:
				if await Game.shared.player.has(item: .clay, count: 10) {
					// TODO: Test this, it might be better to just remove 10 clay and delete the stage4ClayUUIDToRemove
					if let ids = await Game.shared.stages.farm.stage4ClayUUIDToRemove {
						await Game.shared.player.removeItems(ids: ids)
					} else {
						await Game.shared.player.removeItem(item: .clay, count: 10)
					}
					if let id = await Game.shared.stages.farm.stage4PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}

					await Game.shared.stages.farm.setStage4Stages(.done)
					await StatusBox.removeQuest(quest: .farm4)
					await Game.shared.player.setFarmingSkillLevel(.four)
					fallthrough
				} else {
					if await Game.shared.stages.farm.stage4Stages.canGetClay {
						await MessageBox.message("You don't have the clay from the mine.", speaker: .farmer)
					} else {
						await MessageBox.message("You don't have the clay from the miner.", speaker: .farmer)
					}
				}
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}

	static func stage5() async {
		switch await Game.shared.stages.farm.stage5Stages {
			case .notStarted:
				await MessageBox.message("Now that you have the clay, you can take it to the potter and get 5 pots.", speaker: .farmer)
				await Game.shared.stages.farm.setStage5ClayUUIDsToRemove(Game.shared.player.collect(item: .init(type: .clay, canBeSold: false), count: 10))
				await Game.shared.stages.farm.setStage5Stages(.collect)
				await StatusBox.quest(.farm5)
			case .collect:
				await MessageBox.message("You haven't gotten the pot yet.", speaker: .farmer)
			case .comeBack:
				if await Game.shared.player.has(item: .pot, count: 5) {
					await MessageBox.message("Great job!", speaker: .farmer)
					await Game.shared.player.removeItem(item: .pot)
					await Game.shared.stages.farm.setStage5Stages(.done)
					await StatusBox.removeQuest(quest: .farm5)
					await Game.shared.player.setFarmingSkillLevel(.five)
					fallthrough
				} else {
					await MessageBox.message("You haven't gotten all the pots yet.", speaker: .farmer)
				}
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}

	static func stage6() async {
		switch await Game.shared.stages.farm.stage6Stages {
			case .notStarted:
				await MessageBox.message("I wanted to tell you that you can use the backyard part of my farm to plant your own stuff!", speaker: .farmer)
				await Game.shared.player.setFarmingSkillLevel(.six)
				await Game.shared.stages.farm.setStage6Stages(.done)
				fallthrough
			case .done:
				await Game.shared.stages.farm.next()
				if await RandomEventStuff.wantsToContinue(speaker: .farmer) {
					await getStage()
				}
		}
	}
}

enum FarmStage1Stages: Codable {
	case notStarted, collect, done
}

enum FarmStage2Stages: Codable {
	case notStarted, plant, comeback, done
}

enum FarmStage3Stages: Codable {
	case notStarted, collect, comeBack, done
}

enum FarmStage4Stages: Codable {
	case notStarted, collect, comeBack, done

	var canGetClay: Bool {
		get async {
			await Game.shared.stages.mine.stageNumber >= 3
		}
	}
}

enum FarmStage5Stages: Codable {
	case notStarted, collect, comeBack, done
}

enum FarmStage6Stages: Codable {
	case notStarted, done
}
