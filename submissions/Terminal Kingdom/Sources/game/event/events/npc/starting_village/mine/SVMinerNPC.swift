enum SVMinerNPC: StartingVillageNPC {
	static func talk() async {
		await NPC.setTalkedTo()
		if await Game.shared.stages.blacksmith.stage1Stages == .goToMine {
			await MessageBox.message("Ah, here you are. This is the iron the \("Blacksmith".styled(with: .bold)) needs.", speaker: .miner)
			await Game.shared.stages.blacksmith.setStage1Stages(.bringItBack)
			await Game.shared.stages.blacksmith.setStage1AIronUUIDsToRemove(Game.shared.player.collect(item: .init(type: .iron, canBeSold: false), count: 5))
		} else if await Game.shared.stages.blacksmith.stage4Stages == .collect {
			await MessageBox.message("Yes let me get that for you.", speaker: .miner)
			await Game.shared.stages.blacksmith.setStage4Stages(.bringItBack)
			await Game.shared.stages.blacksmith.setStage4CoalUUIDsToRemove(Game.shared.player.collect(item: .init(type: .coal, canBeSold: false), count: 5))
		} else if await Game.shared.stages.blacksmith.stage8Stages == .getMaterials {
			await MessageBox.message("Yes let me get that for you.", speaker: .miner)
			let uuids1 = await Game.shared.player.collect(item: .init(type: .iron, canBeSold: false), count: 3)
			let uuids2 = await Game.shared.player.collect(item: .init(type: .coal, canBeSold: false), count: 3)
			await Game.shared.stages.blacksmith.setStage8MaterialsToRemove(uuids1 + uuids2)
			await Game.shared.stages.blacksmith.setStage8Stages(.makeSteel)
		} else if await Game.shared.stages.builder.stage1Stages == .collect {
			await MessageBox.message("Yes let me get that for you.", speaker: .miner)
			let uuids1 = await Game.shared.player.collect(item: .init(type: .stone, canBeSold: false), count: 20)
			let uuids2 = await Game.shared.player.collect(item: .init(type: .iron, canBeSold: false), count: 10)
			await Game.shared.stages.builder.setStage1ItemsUUIDsToRemove(uuids1 + uuids2)
			await Game.shared.stages.builder.setStage1Stages(.bringBack)
		} else if await Game.shared.stages.farm.stage4Stages == .collect {
			if await Game.shared.stages.farm.stage4Stages.canGetClay {
				await MessageBox.message("You know how to do it, I'll let you practice this time. Take this pickaxe and go get it from the mine.", speaker: .miner)
				await Game.shared.stages.farm.setStage4PickaxeUUIDsToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 25)), canBeSold: false)))
			} else {
				await MessageBox.message("Yes let me get that for you", speaker: .miner)
				await Game.shared.stages.farm.setStage4ClayUUIDsToRemove(Game.shared.player.collect(item: .init(type: .clay, canBeSold: false), count: 10))
			}
			await Game.shared.stages.farm.setStage4Stages(.comeBack)
		} else {
			await getStage()
		}
	}

	static func getStage() async {
		if await Game.shared.stages.mine.isDone {
			await MessageBox.message("Thank you for helping me. You have completed all of the tasks I have for you.", speaker: .miner)
		} else {
			switch await Game.shared.stages.mine.stageNumber {
				case 0:
					if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .no {
						let options: [MessageOption] = [
							.init(label: "Yes", action: {}),
							.init(label: "No", action: {}),
						]
						let selectedOption = await MessageBox.messageWithOptions("Hello \(Game.shared.player.name)! Would you like to learn how to mine?", speaker: .miner, options: options)
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
				case 10:
					await stage10()
				default:
					break
			}
		}
	}

	static func stage0() async {
		if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber != .yes {
			if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .no {
				await MessageBox.message("Before I can teach you how to mine, you need to learn how to chop lumber.", speaker: .miner)
			}
			await RandomEventStuff.teachToChopLumber(by: .miner)
			if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .yes {
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await stage1()
				}
			}
		} else {
			await MessageBox.message("Hello \(Game.shared.player.name)! Looks like you already know how to chop lumber.", speaker: .miner)
			let options: [MessageOption] = [
				.init(label: "Yes", action: {}),
				.init(label: "No", action: {}),
			]
			let selectedOption = await MessageBox.messageWithOptions("Would you like to learn how to mine?", speaker: .miner, options: options)
			if selectedOption.label == "Yes" {
				await stage1()
			}
		}
	}

	static func stage1() async {
		switch await Game.shared.stages.mine.stage1Stages {
			case .notStarted:
				await MessageBox.message("To mine, you need a pickaxe. Go get one from the \("Blacksmith".styled(with: .bold)), he will have one for you.", speaker: .miner)
				await StatusBox.quest(.mine1)
				await Game.shared.stages.mine.setStage1Stages(.collect)
			case .collect:
				await MessageBox.message("It doesn't look like you got a pickaxe. from the \("Blacksmith".styled(with: .bold)). His building it marked with an \("!".styled(with: [.bold, .red]))", speaker: .miner)
			case .bringBack:
				await MessageBox.message("Thank you for getting the pickaxe!", speaker: .miner)
				await Game.shared.stages.mine.setStage1Stages(.done)
				if let id = await Game.shared.stages.mine.stage1PickaxeUUIDToRemove {
					await Game.shared.player.removeItem(id: id)
				}
				await StatusBox.removeQuest(quest: .mine1)
				fallthrough
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage2() async {
		switch await Game.shared.stages.mine.stage2Stages {
			case .notStarted:
				// TODO: make the Mine ! (red bold) (this is already the first time so no check needed)
				await MessageBox.message("I need you to mine 20 clay. You can do this by mining. The mine entrance the 'M' above and below me. is Here is a pickaxe. Be careful, it can only be used 50 times. ", speaker: .miner)
				await StatusBox.quest(.mine2)
				// TODO: make a door in the mine to come back
				await MessageBox.message("Oh also, press '\(KeyboardKeys.L.render)' to leave the mine.", speaker: .miner)
				await Game.shared.stages.mine.setStage2PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 20)), canBeSold: false)))
				await Game.shared.stages.mine.setStage2Stages(.mine)
			case .mine:
				if await Game.shared.player.has(item: .clay, count: 20) {
					await MessageBox.message("Yay thank you! You have collected enough clay.", speaker: .miner)
					await Game.shared.player.setMiningSkillLevel(.one)
					await Game.shared.player.removeItem(item: .clay, count: 20)
					await StatusBox.removeQuest(quest: .mine1)
					await Game.shared.stages.mine.setStage2Stages(.done)
					if let id = await Game.shared.stages.mine.stage2PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await StatusBox.removeQuest(quest: .mine2)
					fallthrough
				} else {
					if let stage2AxeUUIDToRemove = await Game.shared.stages.mine.stage2PickaxeUUIDToRemove, await !Game.shared.player.has(id: stage2AxeUUIDToRemove) {
						await MessageBox.message("Uh oh, looks like you lost your pickaxe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage2PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .clay) - 20)) clay.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage3() async {
		switch await Game.shared.stages.mine.stage3Stages {
			case .notStarted:
				await MessageBox.message("We need 50 lumber to upgrade the mine to be able to mine more stuff. Can you please go get 50 lumber and bring it back to me?", speaker: .miner)
				await Game.shared.stages.mine.setStage3AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 50)), canBeSold: false)))
				await StatusBox.quest(.mine3)
				await Game.shared.stages.mine.setStage3Stages(.collect)
			case .collect:
				if await Game.shared.player.has(item: .lumber, count: 50) {
					await MessageBox.message("Thank you for getting the lumber! Now we can upgrade the mine.", speaker: .miner)
					await Game.shared.player.removeItem(item: .lumber, count: 50)
					if let id = await Game.shared.stages.mine.stage3AxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.player.setMineLevel(.two)
					await Game.shared.stages.mine.setStage3Stages(.done)
					await StatusBox.removeQuest(quest: .mine3)
					fallthrough
				} else {
					if let id = await Game.shared.stages.mine.stage3AxeUUIDToRemove, await !Game.shared.player.has(id: id) {
						await MessageBox.message("Uh oh, looks like you lost your axe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage2PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .lumber) - 50)) lumber.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage4() async {
		switch await Game.shared.stages.mine.stage4Stages {
			case .notStarted:
				await MessageBox.message("Now that we have upgraded the mine, you can go to level 2! There you can find things like stone, coal, and iron.", speaker: .miner)
				await MessageBox.message("I need you to get a pickaxe from the \("Blacksmith".styled(with: .bold)). Then go get 30 stone for me.", speaker: .miner)
				await StatusBox.quest(.mine4)
				await Game.shared.stages.mine.setStage4Stages(.collectPickaxe)
			case .collectPickaxe:
				await MessageBox.message("It doesn't look like you got a pickaxe. from the \("Blacksmith".styled(with: .bold)). His building it marked with an \("!".styled(with: [.bold, .red]))", speaker: .miner)
			case .mine:
				if await Game.shared.player.has(item: .stone, count: 30) {
					await MessageBox.message("Thank you for getting the stone!", speaker: .miner)
					await Game.shared.player.removeItem(item: .stone, count: 30)
					if let id = await Game.shared.stages.mine.stage4PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.stages.mine.setStage4Stages(.done)
					await Game.shared.player.setMiningSkillLevel(.three)
					await StatusBox.removeQuest(quest: .mine4)
					fallthrough
				} else {
					if await !Game.shared.player.hasPickaxe() {
						await MessageBox.message("Uh oh, looks like you lost your pickaxe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage4PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .stone) - 30)) stone from level 2 of the mine.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage5() async {
		switch await Game.shared.stages.mine.stage5Stages {
			case .notStarted:
				await MessageBox.message("Here is another pickaxe. I need you to go get 20 iron for me.", speaker: .miner)
				await StatusBox.quest(.mine5)
				await Game.shared.stages.mine.setStage5Stages(.mine)
				await Game.shared.stages.mine.setStage5PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 20)), canBeSold: false)))
			case .mine:
				if await Game.shared.player.has(item: .iron, count: 20) {
					await MessageBox.message("Thank you for getting the iron!", speaker: .miner)
					await Game.shared.player.removeItem(item: .iron, count: 20)
					if let id = await Game.shared.stages.mine.stage5PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.stages.mine.setStage5Stages(.done)
					await Game.shared.player.setMiningSkillLevel(.four)
					await StatusBox.removeQuest(quest: .mine5)
					fallthrough
				} else {
					if await !Game.shared.player.hasPickaxe() {
						await MessageBox.message("Uh oh, looks like you lost your pickaxe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage5PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .iron) - 20)) iron.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage6() async {
		switch await Game.shared.stages.mine.stage6Stages {
			case .notStarted:
				await MessageBox.message("I haven't told you why you need to get all of this stuff yet. We are going to upgrade the mine again. Every time the items required to do so increase. So this time we need 100 lumber to upgrade. You are almost there to being a professional miner!", speaker: .miner)
				await MessageBox.message("Oh, also, I don't have an axe for you. The \("Blacksmith".styled(with: .bold)) can give you one.", speaker: .miner)
				await StatusBox.quest(.mine6)
				await Game.shared.stages.mine.setStage6Stages(.goGetAxe)
			case .goGetAxe:
				await MessageBox.message("I don't have an axe for you. The \("Blacksmith".styled(with: .bold)) can give you one.", speaker: .miner)
			case .collect:
				if await Game.shared.player.has(item: .lumber, count: 100) {
					await MessageBox.message("Thank you for getting the lumber!", speaker: .miner)
					await Game.shared.player.removeItem(item: .lumber, count: 100)
					if let id = await Game.shared.stages.mine.stage6AxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await Game.shared.stages.mine.setStage6Stages(.done)
					await Game.shared.player.setMiningSkillLevel(.five)
					await StatusBox.removeQuest(quest: .mine6)
					fallthrough
				} else {
					if await !Game.shared.player.hasPickaxe() {
						await MessageBox.message("Uh oh, looks like you lost your pickaxe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage6AxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .axe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .lumber) - 100)) lumber.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage7() async {
		switch await Game.shared.stages.mine.stage7Stages {
			case .notStarted:
				await MessageBox.message("Ok, now that we have the suppilies, we can upgrade the mine. This time I will let you do it! All you have to do is have the materials and go up to the door. There will be an option to upgrade, do that! Then come back to me.", speaker: .miner)
				await StatusBox.quest(.mine7)
				let uuids1 = await Game.shared.player.collect(item: Item(type: .stone, canBeSold: false), count: 30)
				let uuids2 = await Game.shared.player.collect(item: Item(type: .iron, canBeSold: false), count: 20)
				let uuids3 = await Game.shared.player.collect(item: Item(type: .lumber, canBeSold: false), count: 100)

				await Game.shared.stages.mine.setStage7ItemUUIDsToRemove(uuids1 + uuids2 + uuids3)
				await Game.shared.stages.mine.setStage7Stages(.upgrade)
			case .upgrade:
				await MessageBox.message("You haven't upgraded the mine yet. You need to walk up to the door and select upgrade.", speaker: .miner)
			case .upgraded:
				await MessageBox.message("Now that you have upgraded the mine, you can go to level 3! There you can find gold.", speaker: .miner)
				await Game.shared.stages.mine.setStage7Stages(.done)
				await Game.shared.player.setMiningSkillLevel(.seven)
				await Game.shared.player.setMineLevel(.three)
				await StatusBox.removeQuest(quest: .mine7)
				fallthrough
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage8() async {
		switch await Game.shared.stages.mine.stage8Stages {
			case .notStarted:
				await MessageBox.message("I asked the blacksmith to make a special gift for you. Go collect it from the blacksmith. Then come talk to me.", speaker: .miner)
				await StatusBox.quest(.mine8)
				await Game.shared.stages.mine.setStage8Stages(.getPickaxe)
			case .getPickaxe:
				if let id = await Game.shared.stages.mine.stage8PickaxeUUID {
					if await Game.shared.player.has(id: id) {
						await MessageBox.message("Thank you for getting the gift from the blacksmith! I hope you like it. It should help you in the future.", speaker: .miner)
						await Game.shared.stages.mine.setStage8Stages(.done)
						await StatusBox.removeQuest(quest: .mine8)
						fallthrough
					} else {
						await MessageBox.message("You haven't gotten the gift from the blacksmith yet.", speaker: .miner)
					}
				} else {
					await MessageBox.message("You haven't gotten the gift from the blacksmith yet.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage9() async {
		switch await Game.shared.stages.mine.stage9Stages {
			case .notStarted:
				await MessageBox.message("I want to teach you one more thing, but to do that I need to go get 5 gold from level 3 of the mine", speaker: .miner)
				await StatusBox.quest(.mine9)
				await Game.shared.stages.mine.setStage9Stages(.mine)
			case .mine:
				if await Game.shared.player.has(item: .gold, count: 5) {
					await MessageBox.message("Thank you for getting the gold!", speaker: .miner)
					await Game.shared.player.removeItem(item: .gold, count: 5)
					await Game.shared.stages.mine.setStage9Stages(.done)
					await Game.shared.player.setMiningSkillLevel(.nine)
					if let id = await Game.shared.stages.mine.stage9PickaxeUUIDToRemove {
						await Game.shared.player.removeItem(id: id)
					}
					await StatusBox.removeQuest(quest: .mine9)
					fallthrough
				} else {
					if await !Game.shared.player.hasPickaxe() {
						await MessageBox.message("Uh oh, looks like you lost your pickaxe, here is a new one.", speaker: .miner)
						await Game.shared.stages.mine.setStage9PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: .pickaxe(type: .init(durability: 5)), canBeSold: false)))
					}
					await MessageBox.message("You are almost there, you you still need to get \(abs(Game.shared.player.getCount(of: .gold) - 5)) gold.", speaker: .miner)
				}
			case .done:
				await Game.shared.stages.mine.next()
				if await RandomEventStuff.wantsToContinue(speaker: .miner) {
					await getStage()
				}
		}
	}

	static func stage10() async {
		switch await Game.shared.stages.mine.stage10Stages {
			case .notStarted:
				await MessageBox.message("I have one more thing for you to do. I need you to take this gold to the \("Salesman".styled(with: .bold)) and sell it for coins. Then come back to me.", speaker: .miner)
				await StatusBox.quest(.mine10)
				await Game.shared.stages.mine.setStage10Stages(.goToSalesman)
				await Game.shared.stages.mine.setStage10GoldUUIDsToRemove(Game.shared.player.collect(item: .init(type: .gold, canBeSold: false), count: 5))
			case .goToSalesman:
				await MessageBox.message("You haven't sold the gold to the \("Salesman".styled(with: .bold)) yet.", speaker: .miner)
			case .comeBack:
				await MessageBox.message("Thank you for selling the gold to the \("Salesman".styled(with: .bold)). I want you to keep the coins! Thank you for being a good junior miner!", speaker: .miner)
				await Game.shared.stages.mine.setStage10Stages(.done)
				await Game.shared.player.setMiningSkillLevel(.ten)
				await StatusBox.removeQuest(quest: .mine10)
				fallthrough
			case .done:
				await Game.shared.stages.mine.next()
		}
	}
}

enum MineStage1Stages: Codable {
	case notStarted, collect, bringBack, done
}

enum MineStage2Stages: Codable {
	case notStarted, mine, done
}

enum MineStage3Stages: Codable {
	case notStarted, collect, done
}

enum MineStage4Stages: Codable {
	case notStarted, collectPickaxe, mine, done
}

enum MineStage5Stages: Codable {
	case notStarted, mine, done
}

enum MineStage6Stages: Codable {
	case notStarted, goGetAxe, collect, done
}

enum MineStage7Stages: Codable {
	case notStarted, upgrade, upgraded, done
}

enum MineStage8Stages: Codable {
	case notStarted, getPickaxe, done
}

enum MineStage9Stages: Codable {
	case notStarted, mine, done
}

enum MineStage10Stages: Codable {
	case notStarted, goToSalesman, comeBack, done
}
