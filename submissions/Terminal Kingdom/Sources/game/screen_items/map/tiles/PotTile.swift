struct PotTile: Codable, Hashable, Equatable {
	var cropTile: CropTile

	init(cropTile: CropTile = .init(type: .none)) {
		self.cropTile = cropTile
	}

	static func renderCropInPot(tile: PotTile) async -> String {
		if tile.cropTile.type == .none {
			await Game.shared.config.useNerdFont ? "󰋥" : "p"
		} else {
			await CropTile.renderCrop(tile: tile.cropTile)
		}
	}

	mutating func grow() {
		cropTile.grow()
	}
}

extension PotTile {
	enum CodingKeys: CodingKey {
		case cropTile
	}

	func encode(to encoder: Encoder) throws {
		var container = encoder.container(keyedBy: CodingKeys.self)
		try container.encode(cropTile, forKey: .cropTile)
	}

	init(from decoder: Decoder) throws {
		let container = try decoder.container(keyedBy: CodingKeys.self)
		self.cropTile = try container.decode(CropTile.self, forKey: .cropTile)
	}
}
