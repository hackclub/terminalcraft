enum UseWorkstation {
	static func use() async {
		var options: [MessageOption] = []
		for Allrecipe in AllRecipes.allCases {
			let recipe = Allrecipe.recipe
			if recipe.station != .workbench {
				continue
			}
			if recipe.result[0].item == .door(tile: .init(type: .house)) {
				if await !(Game.shared.stages.builder.stage3Stages == .makeDoor) {
					continue
				}
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
						if await Game.shared.stages.builder.stage3Stages == .makeDoor {
							if let ids = await Game.shared.stages.builder.stage3ItemsToMakeDoorUUIDsToRemove {
								await Game.shared.player.removeItems(ids: ids)
							}
						} else {
							await Game.shared.player.removeItem(item: ingredient.item, count: ingredient.count)
						}
					}
					for result in recipe.result {
						if await Game.shared.stages.builder.stage3Stages == .makeDoor {
							await Game.shared.stages.builder.setStage3Stages(.returnToBuilder)
							await Game.shared.stages.builder.setStage3DoorUUIDToRemove(Game.shared.player.collect(item: .init(type: result.item, canBeSold: false)))
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
