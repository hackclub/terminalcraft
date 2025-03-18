enum UseFurnace {
	static func use(progress _: FurnaceProgress) async {
		var options: [MessageOption] = []
		for Allrecipe in AllRecipes.allCases {
			let recipe = Allrecipe.recipe
			if recipe.station != .furnace {
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
					for ingredient in recipe.ingredients {
						if await Game.shared.stages.blacksmith.stage5Stages == .makeSteel {
							if let ids = await Game.shared.stages.blacksmith.stage5ItemsToMakeSteelUUIDs {
								await Game.shared.player.removeItems(ids: ids)
							}
						} else if await Game.shared.stages.blacksmith.stage8Stages == .makeSteel {
							if let ids = await Game.shared.stages.blacksmith.stage8MaterialsToRemove {
								await Game.shared.player.removeItems(ids: ids)
							}
						} else {
							await Game.shared.player.removeItem(item: ingredient.item, count: ingredient.count)
						}
					}
					for result in recipe.result {
						if await Game.shared.stages.blacksmith.stage5Stages == .makeSteel {
							await Game.shared.stages.blacksmith.setStage5Stages(.done)
							await Game.shared.stages.blacksmith.setStage5SteelUUIDsToRemove(Game.shared.player.collect(item: .init(type: result.item, canBeSold: false), count: 5))
						} else if await Game.shared.stages.blacksmith.stage8Stages == .makeSteel {
							await Game.shared.stages.blacksmith.setStage8Stages(.comeBack)
							await Game.shared.stages.blacksmith.setStage8MaterialsToRemove(Game.shared.player.collect(item: .init(type: result.item, canBeSold: false), count: 3))
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
