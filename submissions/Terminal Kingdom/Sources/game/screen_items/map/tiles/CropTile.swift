import Foundation

struct CropTile: Codable, Hashable, Equatable {
	let id: UUID
	let type: CropTileType

	// 180 seconds max
	static let maxGrowthStage = 180
	private(set) var growthStage: Int {
		didSet {
			growthStage = max(0, min(growthStage, Self.maxGrowthStage))
		}
	}

	var stage: CropStage {
		if growthStage < (Self.maxGrowthStage / 3) {
			.seed
		} else if growthStage < (Self.maxGrowthStage) {
			.sprout
		} else {
			.mature
		}
	}

	init(id: UUID = UUID(), type: CropTileType, growthStage: Int = 0) {
		self.id = id
		self.type = type
		self.growthStage = growthStage
	}

	mutating func grow() {
		growthStage += 1
	}

	static func renderCrop(tile: CropTile) async -> String {
		switch tile.type {
			case .none:
				"."
			case .tree_seed:
				switch tile.stage {
					case .seed:
						await Game.shared.config.useNerdFont ? "" : "s"
					case .sprout:
						await (Game.shared.config.useNerdFont ? "" : "t").styled(with: .green)
					case .mature:
						await MapTileType.tree.render()
				}
			case .carrot:
				switch tile.stage {
					case .seed:
						"s"
					case .sprout:
						"p"
					case .mature:
						await Game.shared.config.useNerdFont ? "" : "c"
				}
			case .potato:
				"p"
			case .wheat:
				"w"
			case .lettuce:
				"l"
		}
	}
}

enum CropStage: Codable, Equatable {
	case seed
	case sprout
	case mature
}

extension CropTile {
	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(type, forKey: .tileType)
		try container.encode(growthStage, forKey: .growthStage)
	}

	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.id = try container.decode(UUID.self, forKey: .id)
		self.type = try container.decode(CropTileType.self, forKey: .tileType)
		self.growthStage = try container.decode(Int.self, forKey: .growthStage)
	}

	enum CodingKeys: CodingKey {
		case id
		case tileType
		case growthStage
	}
}
