struct BuildingTile: BuildableTile {
	// TODO: add type: wood or stone
	// wood will burn in hot biomes
	let isPlacedByPlayer: Bool

	init(isPlacedByPlayer: Bool = false) {
		self.isPlacedByPlayer = isPlacedByPlayer
	}
}
