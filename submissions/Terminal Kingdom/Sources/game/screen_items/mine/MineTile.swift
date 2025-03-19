struct MineTile: Tile {
	let type: MineTileType
	var isWalkable: Bool
	var event: MineTileEvent?

	init(type: MineTileType, isWalkable: Bool = false, event: MineTileEvent? = nil) {
		self.type = type
		self.isWalkable = isWalkable
		self.event = event
	}

	var isInteractable: Bool {
		event != nil
	}

	static func isSeen(tile: MineTile, tileX: Int, tileY: Int, grid: [[MineTile]]) -> Bool {
		guard tile.type != .plain else { return true }

		let width = grid[0].count
		let height = grid.count

		if tileY + 1 < height, grid[tileY + 1][tileX].type == .plain {
			return true
		} else if tileY - 1 >= 0, grid[tileY - 1][tileX].type == .plain {
			return true
		} else if tileX + 1 < width, grid[tileY][tileX + 1].type == .plain {
			return true
		} else if tileX - 1 >= 0, grid[tileY][tileX - 1].type == .plain {
			return true
		}

		return false
	}

	static func == (lhs: MineTile, rhs: MineTile) -> Bool {
		lhs.type == rhs.type
	}

	static func findTilePosition(of type: MineTileType, in grid: [[MineTile]]) -> (Int, Int)? {
		for (y, row) in grid.enumerated() {
			if let x = row.firstIndex(where: { $0.type == type }) {
				return (x, y)
			}
		}
		return nil // Return nil if the tile is not found
	}
}

extension MineTile {
	func encode(to encoder: any Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(type, forKey: .tileType)
		try container.encode(isWalkable, forKey: .isWalkable)
		try container.encodeIfPresent(event, forKey: .event)
	}

	enum CodingKeys: CodingKey {
		case tileType
		case isWalkable
		case event
	}

	init(from decoder: any Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.type = try container.decode(MineTileType.self, forKey: .tileType)
		self.isWalkable = try container.decode(Bool.self, forKey: .isWalkable)
		self.event = try container.decodeIfPresent(MineTileEvent.self, forKey: .event)
	}
}
