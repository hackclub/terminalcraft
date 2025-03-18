import Foundation

struct Item: Codable, Equatable, Hashable {
	let id: UUID
	let type: ItemType
	let canBeSold: Bool

	var price: Int? {
		type.price
	}

	var inventoryName: String {
		type.inventoryName
	}

	init(id: UUID = UUID(), type: ItemType, canBeSold: Bool = true) {
		self.id = id
		self.type = type
		if type == .coin {
			self.canBeSold = false
		} else {
			self.canBeSold = canBeSold
		}
	}
}

extension Item {
	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(id, forKey: .id)
		try container.encode(type, forKey: .tileType)
		try container.encode(canBeSold, forKey: .canBeSold)
	}

	enum CodingKeys: CodingKey {
		case id
		case tileType
		case canBeSold
	}

	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.id = try container.decode(UUID.self, forKey: .id)
		self.type = try container.decode(ItemType.self, forKey: .tileType)
		self.canBeSold = try container.decode(Bool.self, forKey: .canBeSold)
	}
}
