import Foundation

struct DoorTile: BuildableTile, Hashable {
	let type: DoorTileTypes
	let isPartOfPlayerVillage: Bool
	let isPlacedByPlayer: Bool
	private(set) var level: Int
	var hasCustomMap: Bool { isPlacedByPlayer }

	init(type: DoorTileTypes, isPartOfPlayerVillage: Bool = false, isPlacedByPlayer: Bool = false) {
		self.type = type
		self.isPartOfPlayerVillage = isPartOfPlayerVillage
		self.level = 1
		self.isPlacedByPlayer = isPlacedByPlayer
	}

	static func renderDoor(tile: DoorTile) async -> String {
		let conditions: [(DoorTileTypes, Bool)] = await [
			(.mine, Game.shared.stages.blacksmith.stage1Stages == .goToMine),
			(.hunting_area, Game.shared.stages.blacksmith.stage7Stages == .bringToHunter),
			(.shop, Game.shared.stages.blacksmith.stage9Stages == .goToSalesman),
			(.blacksmith, Game.shared.stages.mine.stage1Stages == .collect),
			(.shop, Game.shared.stages.mine.stage10Stages == .goToSalesman),
			(.carpenter, Game.shared.stages.blacksmith.stage3Stages == .goToCarpenter),
			(.mine, Game.shared.stages.builder.stage1Stages == .collect),
			(.mine, Game.shared.stages.farm.stage4Stages == .collect),
			(.potter, Game.shared.stages.farm.stage5Stages == .collect),
		]
		if await MapBox.mapType == .mainMap {
			for (doorType, condition) in conditions {
				if tile.type == doorType, condition {
					return "!".styled(with: [.bold, .red])
				}
			}
		}
		return await (Game.shared.config.useNerdFont ? "󰠚" : "D").styled(with: [.bold, .brown])
	}
}

extension DoorTile {
	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.type = try container.decode(DoorTileTypes.self, forKey: .tileType)
		self.isPartOfPlayerVillage = try container.decode(Bool.self, forKey: .isPartOfPlayerVillage)
		self.isPlacedByPlayer = try container.decode(Bool.self, forKey: .isPlacedByPlayer)
		self.level = try container.decode(Int.self, forKey: .level)
	}

	enum CodingKeys: CodingKey {
		case tileType
		case isPartOfPlayerVillage
		case isPlacedByPlayer
		case level
	}

	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(type, forKey: .tileType)
		try container.encode(isPartOfPlayerVillage, forKey: .isPartOfPlayerVillage)
		try container.encode(isPlacedByPlayer, forKey: .isPlacedByPlayer)
		try container.encode(level, forKey: .level)
	}
}
