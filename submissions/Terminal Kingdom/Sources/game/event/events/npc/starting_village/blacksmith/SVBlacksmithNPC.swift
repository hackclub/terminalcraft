enum SVBlacksmithNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo()
		if await Game.shared.stages.mine.stage1Stages == .collect {
			await MessageBox.message("Ah, here you are. Here is your pickaxe.", speaker: .blacksmith)
			await Game.shared.stages.mine.setStage1PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 20)), canBeSold: false)))
			await Game.shared.stages.mine.setStage1Stages(.bringBack)
		} else if await Game.shared.stages.mine.stage4Stages == .collectPickaxe {
			await MessageBox.message("Here you are. Here is your pickaxe.", speaker: .blacksmith)
			await Game.shared.stages.mine.setStage4PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 30)), canBeSold: false)))
			await Game.shared.stages.mine.setStage4Stages(.mine)
		} else if await Game.shared.stages.mine.stage6Stages == .goGetAxe {
			await MessageBox.message("Here you are. Here is your axe.", speaker: .blacksmith)
			await Game.shared.stages.mine.setStage6AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 100)), canBeSold: false)))
			await Game.shared.stages.mine.setStage6Stages(.collect)
		} else if await Game.shared.stages.mine.stage8Stages == .getPickaxe {
			await MessageBox.message("Here you are. Here is your gift.", speaker: .blacksmith)
			await Game.shared.stages.mine.setStage8PickaxeUUID(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 1000)), canBeSold: true)))
		} else {
			await getStage()
		}
	}

	static func getStage() async {
		switch await Game.shared.stages.blacksmith.stageNumber {
			case 0:
				let options: [MessageOption] = [
					.init(label: "Yes", action: {}),
					.init(label: "No", action: {}),
				]
				let selectedOption = await MessageBox.messageWithOptions("Hello \(Game.shared.player.name)! Would you like to learn how to be a blacksmith?", speaker: .blacksmith, options: options)
				if selectedOption.label == "Yes" {
					await Game.shared.stages.blacksmith.next()
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

	static func stage1() async {
		switch await Game.shared.stages.blacksmith.stage1Stages {
			case .notStarted, .goToMine:
				await Game.shared.stages.blacksmith.setStage1Stages(.goToMine)
				await MessageBox.message("I need you to go get some iron from the mine. Then bring it back to me. The door to the mine will be a \"\("!".styled(with: [.red, .bold]))\" to help you find your way.", speaker: .blacksmith)
				await StatusBox.quest(.blacksmith1)
			case .bringItBack:
				if await Game.shared.player.has(item: .iron, count: 5) {
					await MessageBox.message("Thank you!", speaker: .blacksmith)
					if let ironUUID = await Game.shared.stages.blacksmith.stage1AIronUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ironUUID)
					}
					await StatusBox.removeQuest(quest: .blacksmith1)
					await Game.shared.stages.blacksmith.setStage1Stages(.done)
					await Game.shared.player.setBlacksmithSkillLevel(.one)
					fallthrough
				} else {
					await MessageBox.message("Somehow do don't have iron.", speaker: .blacksmith)
				}
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage2() async {
		switch await Game.shared.stages.blacksmith.stage2Stages {
			case .notStarted:
				await Game.shared.stages.blacksmith.setStage2Stages(.getLumber)
				await MessageBox.message("Now I need you to get 20 lumber. Here is an axe.", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage2AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 20)), canBeSold: false)))
				await StatusBox.quest(.blacksmith2)
			case .getLumber:
				if await Game.shared.player.has(item: .lumber, count: 20) {
					await MessageBox.message("Thank you!", speaker: .blacksmith)
					if let id = await Game.shared.stages.blacksmith.stage2AxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.player.removeItem(item: .lumber, count: 20)
					await StatusBox.removeQuest(quest: .blacksmith2)
					await Game.shared.player.setBlacksmithSkillLevel(.two)
					await Game.shared.stages.blacksmith.setStage2Stages(.done)
					fallthrough
				} else {
					if let stage2AxeUUIDToRemove = await Game.shared.stages.blacksmith.stage2AxeUUIDToRemove, await !Game.shared.player.has(id: stage2AxeUUIDToRemove) {
						await MessageBox.message("Uh oh, looks like you lost your axe, here is a new one.", speaker: .blacksmith)
						await Game.shared.stages.blacksmith.setStage2AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .clay) - 20)) clay.", speaker: .blacksmith)
				}
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage3() async {
		switch await Game.shared.stages.blacksmith.stage3Stages {
			case .notStarted:
				await MessageBox.message("Now I need you to give this lumber to the carpenter to get sticks.", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage3LumberUUIDsToRemove(Game.shared.player.collect(item: .init(type: .lumber, canBeSold: false), count: 20))
				await Game.shared.stages.blacksmith.setStage3Stages(.goToCarpenter)
				await StatusBox.quest(.blacksmith3)
			case .goToCarpenter:
				await MessageBox.message("You haven't gone to the carpenter yet.", speaker: .blacksmith)
			case .comeBack:
				if await Game.shared.player.has(item: .stick, count: 20) {
					await MessageBox.message("Thank you!", speaker: .blacksmith)
					await StatusBox.removeQuest(quest: .blacksmith3)
					if let sticksUUIDs = await Game.shared.stages.blacksmith.stage3LumberUUIDsToRemove {
						await Game.shared.player.removeItems(ids: sticksUUIDs)
					}
					await Game.shared.player.setBlacksmithSkillLevel(.three)
					await Game.shared.stages.blacksmith.setStage3Stages(.done)
					fallthrough
				}
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage4() async {
		switch await Game.shared.stages.blacksmith.stage4Stages {
			case .notStarted:
				await MessageBox.message("I need you to get 5 coal from the miner. We need the iron, lumber and this coal, because I want to show you how to make a pickaxe.", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage4Stages(.collect)
				await StatusBox.quest(.blacksmith4)
			case .collect:
				await MessageBox.message("You haven't gotten the coal yet.", speaker: .blacksmith)
			case .bringItBack:
				if await Game.shared.player.has(item: .coal, count: 5) {
					await MessageBox.message("Thank you!", speaker: .blacksmith)
					await StatusBox.removeQuest(quest: .blacksmith4)
					if let coalUUIDs = await Game.shared.stages.blacksmith.stage4CoalUUIDsToRemove {
						await Game.shared.player.removeItems(ids: coalUUIDs)
					}
					await Game.shared.player.setBlacksmithSkillLevel(.four)
					await Game.shared.stages.blacksmith.setStage4Stages(.done)
					fallthrough
				}
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage5() async {
		switch await Game.shared.stages.blacksmith.stage5Stages {
			case .notStarted:
				await MessageBox.message("Now you get to do the fun stuff. I need to you make some steel. Go over to the furnace (\(StationTileType.furnace(progress: .empty).render))", speaker: .blacksmith)
				let uuids1 = await Game.shared.player.collect(item: .init(type: .coal, canBeSold: false), count: 5)
				let uuids2 = await Game.shared.player.collect(item: .init(type: .iron, canBeSold: false), count: 5)
				await Game.shared.stages.blacksmith.setStage5ItemsToMakeSteelUUIDs(uuids1 + uuids2)
				await StatusBox.quest(.blacksmith5)
				await Game.shared.stages.blacksmith.setStage5Stages(.makeSteel)
			case .makeSteel:
				await MessageBox.message("You haven't gone to the furnace yet. It is labeled with an \"\(StationTileType.furnace(progress: .empty).render)\"", speaker: .blacksmith)
			case .returnToBlacksmith:
				if await Game.shared.player.hasPickaxe() {
					await MessageBox.message("Yay! You made your first Pickaxe!", speaker: .blacksmith)
					await StatusBox.removeQuest(quest: .blacksmith5)
					await Game.shared.player.removeItems(ids: Game.shared.stages.blacksmith.stage5SteelUUIDsToRemove)
					await Game.shared.player.setBlacksmithSkillLevel(.five)
					await Game.shared.stages.blacksmith.setStage5Stages(.done)
					fallthrough
				}
			case .done:
				await Game.shared.stages.blacksmith.next()

				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage6() async {
		switch await Game.shared.stages.blacksmith.stage6Stages {
			case .notStarted:
				await MessageBox.message("I need you to make a pickaxe. Go over to the anvil (\(StationTileType.anvil.render)) and make a pickaxe. Here is all of the things you will need.", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage6Stages(.makePickaxe)
				await StatusBox.quest(.blacksmith6)
				let uuid1 = await Game.shared.player.collect(item: .init(type: .stick, canBeSold: false), count: 2)
				let uuid2 = await Game.shared.player.collect(item: .init(type: .steel, canBeSold: false), count: 3)
				await Game.shared.stages.blacksmith.setStage6ItemsToMakePickaxeUUIDs(uuid1 + uuid2)
			case .makePickaxe:
				await MessageBox.message("You haven't gone to the anvil yet. It is labeled with an \"\(StationTileType.anvil.render)\"", speaker: .blacksmith)
			case .returnToBlacksmith:
				if await Game.shared.player.hasPickaxe() {
					await MessageBox.message("Yay! You made your first Pickaxe!", speaker: .blacksmith)
					await StatusBox.removeQuest(quest: .blacksmith6)
					if let ids = await Game.shared.stages.blacksmith.stage6ItemsToMakePickaxeUUIDs {
						await Game.shared.player.removeItems(ids: ids)
					}
					if let id = await Game.shared.stages.blacksmith.stage6PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.player.setBlacksmithSkillLevel(.six)
					await Game.shared.stages.blacksmith.setStage6Stages(.done)
					fallthrough
				} else {
					await MessageBox.message("Somehow, you haven't made the pickaxe yet.", speaker: .blacksmith)
				}
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage7() async {
		switch await Game.shared.stages.blacksmith.stage7Stages {
			case .notStarted:
				await MessageBox.message("The hunter asked me to make him a sword. Why don't you do that? Here is the stuff you need. Make a sword on the anvil and then bring it to the Hunter in the \(DoorTileTypes.hunting_area.name.styled(with: .bold)).", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage7Stages(.makeSword)
				await StatusBox.quest(.blacksmith7)
				let uuid1 = await Game.shared.player.collect(item: .init(type: .stick, canBeSold: false), count: 2)
				let uuid2 = await Game.shared.player.collect(item: .init(type: .steel, canBeSold: false), count: 2)
				await Game.shared.stages.blacksmith.setStage7ItemsToMakeSwordUUIDs(uuid1 + uuid2)
			case .makeSword:
				await MessageBox.message("You haven't gone to the anvil yet. It is labeled with an \"\(StationTileType.anvil.render)\"", speaker: .blacksmith)
			case .bringToHunter:
				await MessageBox.message("You haven't brought the sword to the hunter yet. The \(DoorTileTypes.hunting_area.name.styled(with: .bold)) is marked with an \("!".styled(with: [.bold, .red])).", speaker: .blacksmith)
			case .comeBack:
				await MessageBox.message("Yay! You made your first sword!", speaker: .blacksmith)
				await StatusBox.removeQuest(quest: .blacksmith7)
				await Game.shared.player.setBlacksmithSkillLevel(.seven)
				await Game.shared.stages.blacksmith.setStage7Stages(.done)
				fallthrough
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage8() async {
		switch await Game.shared.stages.blacksmith.stage8Stages {
			case .notStarted:
				await MessageBox.message("You are almost there to becoming a blacksmith! I need you to get some materials from the mine. Then I need you to make some steel. Then come back to me", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage8Stages(.getMaterials)
				await StatusBox.quest(.blacksmith8)
			case .getMaterials:
				await MessageBox.message("You haven't gotten the materials yet.", speaker: .blacksmith)
			case .makeSteel:
				await MessageBox.message("You haven't made the steel at the furnace yet.", speaker: .blacksmith)
			case .comeBack:
				await MessageBox.message("Yay!", speaker: .blacksmith)
				await StatusBox.removeQuest(quest: .blacksmith8)
				await Game.shared.player.setBlacksmithSkillLevel(.eight)
				if let ids = await Game.shared.stages.blacksmith.stage8MaterialsToRemove {
					await Game.shared.player.removeItems(ids: ids)
				}
				await Game.shared.stages.blacksmith.setStage8Stages(.done)
				fallthrough
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}

	static func stage9() async {
		switch await Game.shared.stages.blacksmith.stage9Stages {
			case .notStarted:
				await MessageBox.message("Now I want you to sell this steel in the shop. The shop will be marked with an \"\("!".styled(with: [.bold, .red]))\"", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage9Stages(.goToSalesman)
				await StatusBox.quest(.blacksmith9)
				await Game.shared.stages.blacksmith.setStage9SteelUUIDToRemove(Game.shared.player.collect(item: .init(type: .steel, canBeSold: false), count: 3))
			case .goToSalesman:
				await MessageBox.message("You haven't gone to the salesman yet.", speaker: .blacksmith)
			case .comeBack:
				await MessageBox.message("I want you to keep these coins. I have one more thing I want to give you.", speaker: .blacksmith)
				await Game.shared.stages.blacksmith.setStage9Stages(.done)
				await StatusBox.removeQuest(quest: .blacksmith9)
				await Game.shared.player.setBlacksmithSkillLevel(.nine)
				fallthrough
			case .done:
				await Game.shared.stages.blacksmith.next()
				if await RandomEventStuff.wantsToContinue(speaker: .blacksmith) {
					await getStage()
				}
		}
	}
}

enum BlacksmithStage1Stages: Codable {
	case notStarted, goToMine, bringItBack, done
}

enum BlacksmithStage2Stages: Codable {
	case notStarted, getLumber, done
}

enum BlacksmithStage3Stages: Codable {
	case notStarted, goToCarpenter, comeBack, done
}

enum BlacksmithStage4Stages: Codable {
	case notStarted, collect, bringItBack, done
}

enum BlacksmithStage5Stages: Codable {
	case notStarted, makeSteel, returnToBlacksmith, done
}

enum BlacksmithStage6Stages: Codable {
	case notStarted, makePickaxe, returnToBlacksmith, done
}

enum BlacksmithStage7Stages: Codable {
	case notStarted, makeSword, bringToHunter, comeBack, done
}

enum BlacksmithStage8Stages: Codable {
	case notStarted, getMaterials, makeSteel, comeBack, done
}

enum BlacksmithStage9Stages: Codable {
	case notStarted, goToSalesman, comeBack, done
}
