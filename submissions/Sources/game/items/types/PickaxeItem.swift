import Foundation

struct PickaxeItem: Codable, Equatable, Hashable, HasDurability {
	private(set) var durability: Int

	init(durability: Int = 50) {
		self.durability = durability
	}

	mutating func removeDurability(count: Int = 1) {
		durability -= count
	}
}
