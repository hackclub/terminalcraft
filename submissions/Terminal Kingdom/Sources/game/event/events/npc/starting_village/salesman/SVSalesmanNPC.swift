enum SVSalesmanNPC: StartingVillageNPC {
	static func talk() async {
		if await Game.shared.stages.mine.stage10Stages == .goToSalesman {
			await MessageBox.message("Oooh 5 gold! Can buy that for 10 coins!", speaker: .salesman(type: .buy))
			let options: [MessageOption] = [
				.init(label: "Yes", action: {
					if let ids = await Game.shared.stages.mine.stage10GoldUUIDsToRemove {
						await Game.shared.player.removeItems(ids: ids)
						_ = await Game.shared.player.collect(item: .init(type: .coin), count: 10)
						await MessageBox.message("Thank you!", speaker: .salesman(type: .buy))
						await Game.shared.stages.mine.setStage10Stages(.comeBack)
					}
				}),
				.init(label: "No", action: {
					await MessageBox.message("Oh ok", speaker: .salesman(type: .buy))
				}),
			]
			let selectedOption = await MessageBox.messageWithOptions("Would you like to sell the 5 gold?", speaker: .salesman(type: .buy), options: options)
			await selectedOption.action()
		} else if await Game.shared.stages.blacksmith.stage9Stages == .goToSalesman {
			let price = ItemType.steel.price! * 3
			await MessageBox.message("Oooh 3 steel! Can buy that for \(price) coins!", speaker: .salesman(type: .buy))
			let options: [MessageOption] = [
				.init(label: "Yes", action: {
					if let ids = await Game.shared.stages.blacksmith.stage9SteelUUIDToRemove {
						await Game.shared.player.removeItems(ids: ids)
						_ = await Game.shared.player.collect(item: .init(type: .coin), count: price)
						await MessageBox.message("Thank you!", speaker: .salesman(type: .buy))
						await Game.shared.stages.blacksmith.setStage9Stages(.comeBack)
					}
				}),
				.init(label: "No", action: {
					await MessageBox.message("Oh ok", speaker: .salesman(type: .buy))
				}),
			]
			let selectedOption = await MessageBox.messageWithOptions("Would you like to sell the 3 steel?", speaker: .salesman(type: .buy), options: options)
			await selectedOption.action()
		} else {
			let tile = await MapBox.tilePlayerIsOn
			if case let .shopStandingArea(type: type) = tile.type {
				switch type {
					case .buy:
						if await Game.shared.startingVillageChecks.firstTimes.hasTalkedToSalesmanBuy == false {
							await Game.shared.startingVillageChecks.setHasTalkedToSalesmanBuy()
						}
						await buy()
					case .sell:
						if await Game.shared.startingVillageChecks.firstTimes.hasTalkedToSalesmanSell == false {
							await Game.shared.startingVillageChecks.setHasTalkedToSalesmanSell()
						}
						await sell()
					case .help:
						if await Game.shared.startingVillageChecks.firstTimes.hasTalkedToSalesmanHelp == false {
							await Game.shared.startingVillageChecks.setHasTalkedToSalesmanHelp()
						}
						await help()
				}
			}
		}
	}

	private static func buy() async {
		var leaveShop = false
		var options: [MessageOption] = [
			.init(label: "Leave", action: { leaveShop = true }),
		]
		for skillLevel in AllSkillLevels.allCases {
			await addOptionsForSkill(options: &options, skillLevel: skillLevel)
		}
		if options.count <= 1 {
			await MessageBox.message("There are no items are available to buy right now. Come back when you have more skills.", speaker: .salesman(type: .buy))
			return
		}
		while !leaveShop {
			let selectedOption = await MessageBox.messageWithOptions("Would you like to buy?", speaker: .salesman(type: .buy), options: options, hideInventoryBox: false)
			if selectedOption.label != "Leave" {
				let amount = await MessageBox.messageWithTypingNumbers("How many?", speaker: .salesman(type: .buy))
				for _ in 1 ... amount {
					await selectedOption.action()
				}
			} else {
				leaveShop = true
			}
		}
	}

	private static func sell() async {
		var leaveShop = false
		var options: [MessageOption] = [
			.init(label: "Leave", action: { leaveShop = true }),
		]
		for item in await Array(Set(Game.shared.player.items)) {
			await sellOption(options: &options, item: item)
		}
		while !leaveShop {
			let selectedOption = await MessageBox.messageWithOptions("Would you like to sell?", speaker: .salesman(type: .sell), options: options, hideInventoryBox: false)
			if selectedOption.label != "Leave" {
				let amount = await MessageBox.messageWithTypingNumbers("How many?", speaker: .salesman(type: .sell))
				for _ in 1 ... amount {
					await selectedOption.action()
				}
				await InventoryBox.printInventory()
			} else {
				leaveShop = true
			}
		}
	}

	private static func help() async {
		await MessageBox.message("Welcome to the shop \(Game.shared.player.name)!", speaker: .salesman(type: .help))
		await MessageBox.message("If you want to buy, talk to the guy with the \("!".styled(with: [.green, .blue])). Or if you want to sell talk to the guy with the \("!".styled(with: [.bold, .blue])).", speaker: .salesman(type: .help))
		await Game.shared.startingVillageChecks.setHasTalkedToSalesmanBuy(false)
		await Game.shared.startingVillageChecks.setHasTalkedToSalesmanSell(false)
	}
}

extension SVSalesmanNPC {
	private static func buyItem(item: ItemType, count: Int, price: Int) async {
		if await Game.shared.player.has(item: .coin, count: price) {
			_ = await Game.shared.player.collect(item: .init(type: item), count: count)
			await Game.shared.player.removeItem(item: .coin, count: price * count)
		} else {
			await MessageBox.message("You don't have enough coins!", speaker: .salesman(type: .buy))
		}
	}

	private static func sellItem(item: Item, count: Int, price: Int) async {
		if await Game.shared.player.has(item: item, count: count) {
			await Game.shared.player.removeItem(item: item.type, count: count)
			_ = await Game.shared.player.collect(item: .init(type: .coin), count: price * count)
		} else {
			await MessageBox.message("You don't have that much!", speaker: .salesman(type: .sell))
		}
	}

	private static func addOptionsForSkill(options: inout [MessageOption], skillLevel: AllSkillLevels) async {
		if await Game.shared.startingVillageChecks.hasBeenTaughtToChopLumber == .yes {
			await buyOption(options: &options, item: .lumber)
		}
		switch await (skillLevel, skillLevel.stat) {
			case (.miningSkillLevel, .one):
				await buyOption(options: &options, item: .pickaxe(type: .init()))
				await buyOption(options: &options, item: .stone)
			// TODO: press on item, and see a buy 1, buy 2, buy 5, buy 10...
			// TODO: Add more stuff here
			default:
				break
		}
	}

	private static func buyOption(options: inout [MessageOption], item: ItemType) async {
		if let price = item.price {
			let newItem = MessageOption(label: "\(item.inventoryName); price: \(price) coin\(price > 1 ? "s" : "")", action: { await buyItem(item: item, count: 1, price: price) })
			if !options.contains(where: { $0 != newItem }) {
				options.append(newItem)
			}
		}
	}

	private static func sellOption(options: inout [MessageOption], item: Item) async {
		if let price = item.price, item.canBeSold {
			let newItem = MessageOption(label: "\(item.inventoryName); price: \(price) coins", action: { await sellItem(item: item, count: 1, price: price) })
			if options.contains(where: { $0 != newItem }) {
				options.append(newItem)
			}
		}
	}
}
