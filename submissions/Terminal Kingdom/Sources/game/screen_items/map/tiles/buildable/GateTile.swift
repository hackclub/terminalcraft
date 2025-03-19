struct GateTile: BuildableTile {
	let isPlacedByPlayer: Bool
	let isOpen: Bool

	init(isPlacedByPlayer: Bool = false, isOpen: Bool = false) {
		self.isPlacedByPlayer = isPlacedByPlayer
		self.isOpen = isOpen
	}
}
