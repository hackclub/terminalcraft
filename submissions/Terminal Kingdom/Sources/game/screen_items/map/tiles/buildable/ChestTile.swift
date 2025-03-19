struct ChestTile: BuildableTile {
	let items: [Item]
	let isPlacedByPlayer: Bool

	init(items: [Item] = [], isPlacedByPlayer: Bool = false) {
		self.items = items
		self.isPlacedByPlayer = isPlacedByPlayer
	}
}
