struct Recipe: Codable {
	let ingredients: [RecipeIngredient]
	let result: [RecipeResult]
	let station: StationType

	init(ingredients: [RecipeIngredient], result: [RecipeResult], station: StationType) {
		self.ingredients = ingredients
		self.result = result
		self.station = station
	}

	var name: String {
		"\(result.first!.item.inventoryName) (\(result.first!.count))"
	}

	struct RecipeIngredient: Codable {
		let item: ItemType
		let count: Int
	}

	struct RecipeResult: Codable {
		let item: ItemType
		let count: Int
	}
}

enum StationType: String, Codable {
	case furnace
	case anvil
	case workbench
}
