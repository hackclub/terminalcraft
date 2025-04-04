struct MapTile: Tile {
	let type: MapTileType
	let isWalkable: Bool
	let event: MapTileEvent?
	let biome: BiomeType

	init(type: MapTileType, isWalkable: Bool = true, event: MapTileEvent? = nil, biome: BiomeType) {
		self.type = type
		self.isWalkable = isWalkable
		if case .door = type {
			self.event = .openDoor
		} else {
			self.event = event
		}
		self.biome = biome
	}

	var isInteractable: Bool {
		event != nil
	}

	static func == (lhs: MapTile, rhs: MapTile) -> Bool {
		lhs.type == rhs.type
	}

	static func findTilePosition(of type: MapTileType, in grid: [[MapTile]]) -> (Int, Int)? {
		for (y, row) in grid.enumerated() {
			if let x = row.firstIndex(where: { $0.type == type }) {
				return (x, y)
			}
		}
		return nil // Return nil if the tile is not found
	}
}

extension MapTile {
	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(type, forKey: .tileType)
		try container.encode(isWalkable, forKey: .isWalkable)
		try container.encodeIfPresent(event, forKey: .event)
		try container.encode(biome, forKey: .biome)
	}

	enum CodingKeys: CodingKey {
		case tileType
		case isWalkable
		case event
		case biome
	}

	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.type = try container.decode(MapTileType.self, forKey: .tileType)
		self.isWalkable = try container.decode(Bool.self, forKey: .isWalkable)
		self.event = try container.decodeIfPresent(MapTileEvent.self, forKey: .event)
		self.biome = try container.decodeIfPresent(BiomeType.self, forKey: .biome) ?? .plains
	}
}
