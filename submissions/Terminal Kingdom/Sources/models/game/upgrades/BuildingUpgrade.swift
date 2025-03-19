import Foundation

struct BuildingUpgrade: Codable, Hashable, Equatable {
	let cost: [ItemAmount]
	// var timeToBuild: Int

	init(cost: [ItemAmount]) {
		self.cost = cost
	}
}

struct ItemAmount: Codable, Equatable, Hashable {
	let item: ItemType
	let count: Int
}
