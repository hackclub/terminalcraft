import Foundation

struct Kingdom: Codable, Identifiable, Hashable, Equatable {
	let id: UUID
	var name: String
	var buildings: [Building]
	var npcsInKindom: [UUID]
	var hasCastle: Bool = false
	var data: [KingdomData] = []
	private(set) var radius: Int = 40
	var castleID: UUID? = nil

	init(id: UUID = UUID(), name: String, buildings: [Building], npcsInKindom: [UUID] = []) {
		self.id = id
		self.buildings = buildings
		self.npcsInKindom = npcsInKindom
		self.name = name
	}

	mutating func addData(_ data: KingdomData) {
		self.data.append(data)
	}

	mutating func removeData(_ data: KingdomData) {
		self.data.removeAll { $0 == data }
	}

	mutating func setHasCastle() {
		hasCastle = true
		let castleID = getCastle()?.id
		if let castleID {
			self.castleID = castleID
		}
	}

	mutating func removeCastle() {
		hasCastle = false
		castleID = nil
	}

	func getCastle() -> Building? {
		guard hasCastle else {
			return nil
		}
		// index 1 should be castle beucase it is the second building added
		if case .castle = buildings[1].type {
			return buildings[1]
		}

		// Otherwise, search for any castle
		return buildings.first { b in
			// if case let .custom(_, doorType: doorType) = b.type {
			if case .castle = b.type {
				// if case .castle = doorType {
				return true
				// }
			}
			return false
		}
	}

	func contains(x: Int, y: Int) -> Bool {
		let center = hasCastle ? getCastle() : buildings.first { $0.type == .builder }
		guard let building = center else { return false }
		let dx = x - building.x
		let dy = y - building.y
		return dx * dx + dy * dy <= radius * radius
	}
}

enum KingdomData: Codable, Hashable {
	case buildingCastle, gettingStuffToBuildCastle
}
