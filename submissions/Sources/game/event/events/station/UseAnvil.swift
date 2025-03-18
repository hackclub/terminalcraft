enum UseAnvil {
	static func use() async {
		var options: [MessageOption] = []
		for Allrecipe in AllRecipes.allCases {
			let recipe = Allrecipe.recipe
			if recipe.station != .anvil {
				continue
			}
			var canMake = true
			for ingredient in recipe.ingredients {
				if await Game.shared.player.has(item: ingredient.item, count: ingredient.count) {
					continue
				} else {
					canMake = false
					break
				}
			}
			if canMake {
				options.append(.init(label: recipe.name, action: {
					// TODO: only allow the player to make what they need for a quest
					for ingredient in recipe.ingredients {
						if await Game.shared.stages.blacksmith.stage6Stages == .makePickaxe {
							if let ids = await Game.shared.stages.blacksmith.stage6ItemsToMakePickaxeUUIDs {
								await Game.shared.player.removeItems(ids: ids)
							}
						} else if await Game.shared.stages.blacksmith.stage7Stages == .makeSword {
							if let ids = await Game.shared.stages.blacksmith.stage7ItemsToMakeSwordUUIDs {
								await Game.shared.player.removeItems(ids: ids)
							}
						} else {
							await Game.shared.player.removeItem(item: ingredient.item, count: ingredient.count)
						}
						await Game.shared.player.removeItem(item: ingredient.item, count: ingredient.count)
					}
					for result in recipe.result {
						if await Game.shared.stages.blacksmith.stage6Stages == .makePickaxe {
							await Game.shared.stages.blacksmith.setStage6Stages(.done)
							await Game.shared.stages.blacksmith.setStage6PickaxeUUIDToRemove(Game.shared.player.collect(item: .init(type: result.item, canBeSold: false)))
						} else if await Game.shared.stages.blacksmith.stage7Stages == .makeSword {
							await Game.shared.stages.blacksmith.setStage7Stages(.bringToHunter)
							await Game.shared.stages.blacksmith.setStage7SwordUUIDToRemove(Game.shared.player.collect(item: .init(type: result.item, canBeSold: false)))
						} else {
							_ = await Game.shared.player.collect(item: .init(type: result.item, canBeSold: true))
						}
					}
				}))
			}
		}
		options.append(.init(label: "Quit", action: {}))
		let selectedOption = await MessageBox.messageWithOptions("What would you like to make?", speaker: .game, options: options)
		await selectedOption.action()
	}
}
