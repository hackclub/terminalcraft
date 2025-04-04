enum MineTileEvent: TileEvent {
	case placeholder

	static func trigger(event: MineTileEvent) async {
		switch event {
			case .placeholder:
				break
		}
	}
}
