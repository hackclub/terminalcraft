enum DoorPlaceError: Error {
	case noDoor
	case noSpace
	case notEnoughBuildingsNearby
	case invalidPosition
	case notARectangle

	var localizedDescription: String {
		switch self {
			case .noDoor: "You don't have a door to place."
			case .noSpace: "You can only place a door on a plain tile."
			case .notEnoughBuildingsNearby: "There must be at least 3 buildings that you placed nearby."
			case .invalidPosition: "You can't place a door at this position."
			// TODO: allow for non-rectangular buildings
			case .notARectangle: "The building must be a rectange"
		}
	}
}
