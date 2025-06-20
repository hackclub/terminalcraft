import Foundation

struct NPC: Codable, Hashable, Equatable {
	let id: UUID
	let name: String
	let isStartingVillageNPC: Bool
	var hasTalkedToBefore: Bool
	var job: NPCJob?
	// skill level
	// let age: Int
	let gender: Gender
	private(set) var positionToWalkTo: TilePosition?
	private(set) var attributes: [NPCAttribute] = []

	init(id: UUID = UUID(), name: String? = nil, gender: Gender? = nil, job: NPCJob? = nil, isStartingVillageNPC: Bool = false, positionToWalkTo: TilePosition? = nil, tilePosition: NPCPosition? = nil, kingdomID: UUID) {
		self.id = id
		self.gender = gender ?? Gender.allCases.randomElement()!
		self.name = name ?? Self.generateRandomName(for: self.gender)
		self.job = job
		self.isStartingVillageNPC = isStartingVillageNPC
		self.hasTalkedToBefore = false
		if let tilePosition {
			self.positionToWalkTo = positionToWalkTo
			Task {
				await Game.shared.addNPC(tilePosition)
			}
		}
		Task {
			await Game.shared.addKingdomNPC(id, kingdomID: kingdomID)
		}
	}

	mutating func removePostion() {
		positionToWalkTo = nil
	}

	mutating func addAttribute(_ attribute: NPCAttribute) {
		attributes.append(attribute)
	}

	mutating func removeAttribute(_ attribute: NPCAttribute) {
		attributes.removeAll { $0 == attribute }
	}

	static func generateRandomName(for gender: Gender) -> String {
		let maleNames = [
			"Adam", "Ben", "Caleb", "Daniel", "Eric",
			"Felix", "Greg", "Craig", "Isaac", "Jack",
			"Kyle", "Leo", "Matt", "Nate", "Owen",
			"Paul", "Quinn", "Ryan", "Sam", "Tom",
			"Victor", "Theo", "Jim", "Eli", "Mark",
		]

		let femaleNames = [
			"Anna", "Beth", "Chloe", "Daisy", "Emma",
			"Faith", "Grace", "Hannah", "Ivy", "Julia",
			"Kate", "Lily", "Mia", "Nora", "Olivia",
			"Paige", "Jordan", "Rachel", "Sarah", "Tessa",
			"Violet", "Wendy", "Zoey", "Ellie", "Claire",
		]

		return (gender == .male ? maleNames : femaleNames).randomElement()!
	}

	mutating func updateTalkedTo() {
		hasTalkedToBefore = true
	}

	static func setTalkedTo(after: @escaping () async -> Void) async {
		let mapTile = await MapBox.tilePlayerIsOn
		guard case let .npc(tile: tile) = mapTile.type else {
			return
		}
		if tile.npc.hasTalkedToBefore == false {
			var newTile = tile
			newTile.npc.updateTalkedTo()
			let newMapTile = MapTile(type: .npc(tile: newTile), isWalkable: mapTile.isWalkable, event: mapTile.event, biome: mapTile.biome)
			await MapBox.updateTile(newTile: newMapTile)
			await after()
		}
	}

	static func setTalkedTo() async {
		await setTalkedTo(after: {})
	}

	static func == (lhs: NPC, rhs: NPC) -> Bool {
		lhs.id == rhs.id
	}

	func hash(into hasher: inout Hasher) {
		hasher.combine(id)
	}

	func talk() async {
		if let job {
			if isStartingVillageNPC {
				switch job {
					case .blacksmith:
						await SVBlacksmithNPC.talk()
					case .blacksmith_helper:
						await SVBlacksmithHelperNPC.talk()
					case .miner:
						await SVMinerNPC.talk()
					case .mine_helper:
						await SVMineHelperNPC.talk()
					case .carpenter:
						await SVCarpenterNPC.talk()
					case .carpenter_helper:
						await SVCarpenterHelperNPC.talk()
					case .king:
						await SVKingNPC.talk()
					case .salesman:
						await SVSalesmanNPC.talk()
					case .builder:
						await SVBuilderNPC.talk()
					case .builder_helper:
						await SVBuilderHelperNPC.talk()
					case .hunter:
						await SVHunterNPC.talk()
					case .inventor:
						break
					case .stable_master:
						break
					case .farmer:
						await SVFarmerNPC.talk()
					case .doctor:
						break
					case .chef:
						break
					case .potter:
						await SVPotterNPC.talk()
					case .farmer_helper:
						await SVFarmerHelperNPC.talk()
				}
			} else {
				switch job {
					case .builder:
						await BuilderNPC.talk(npc: self)
					default:
						break
				}
			}
		}
	}
}

enum Gender: String, Codable, CaseIterable {
	case male, female
}

enum NPCAttribute: Codable, CaseIterable {
	case needsAttention
}
