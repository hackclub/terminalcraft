// TODO: Give starting village NPCs names?
enum NPCJob: Codable, Hashable, Equatable {
	case blacksmith
	case blacksmith_helper
	case miner
	case mine_helper
	case carpenter
	case carpenter_helper
	case farmer
	case farmer_helper

	case king
	case salesman(type: SalesmanType)
	case builder
	case builder_helper
	case hunter
	case inventor
	case stable_master
	case doctor
	case chef
	case potter

	var render: String {
		switch self {
			case .king: "King Randolph"
			case .blacksmith: "Blacksmith"
			case .miner: "Miner"
			case .salesman(type: _): "Salesman"
			case .builder: "Builder"
			case .hunter: "Hunter"
			case .inventor: "Inventor"
			case .stable_master: "Stable Master"
			case .farmer: "Farmer"
			case .doctor: "Doctor"
			case .carpenter: "Carpenter"
			case .chef: "Chef"
			case .potter: "Potter"
			case .blacksmith_helper: "Blacksmith Helper"
			case .mine_helper: "Miner Helper"
			case .carpenter_helper: "Carpenter Helper"
			case .builder_helper: "Builder Helper"
			case .farmer_helper: "Farmer Helper"
		}
	}

	var isHelper: Bool {
		switch self {
			case .blacksmith_helper, .mine_helper, .carpenter_helper, .builder_helper, .farmer_helper: true
			default: false
		}
	}
}

enum MessageSpeakers {
	case player
	case game
	case dev
	case npc(name: String, job: NPCJob?)

	var render: String {
		get async {
			switch self {
				case .player: await Game.shared.player.name
				case .game: "This shouldn't be seen"
				case .dev: "Dev"
				case let .npc(name: name, job: job):
					if let job {
						"\(name) (\(job.render))"
					} else {
						"\(name)"
					}
			}
		}
	}
}

enum SalesmanType: Codable {
	case buy, sell, help
}
