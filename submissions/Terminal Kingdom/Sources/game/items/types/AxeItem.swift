import Foundation

struct AxeItem: Codable, Equatable, Hashable, HasDurability {
	private(set) var durability: Int

	init(durability: Int = 55) {
		self.durability = durability
	}

	mutating func removeDurability(count: Int = 1) {
		durability -= count
	}
}
