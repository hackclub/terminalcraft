struct Stats: Codable {
	private(set) var blacksmithSkillLevel: SkillLevels = .zero
	private(set) var miningSkillLevel: SkillLevels = .zero
	private(set) var builderSkillLevel: SkillLevels = .zero // architect?
	private(set) var huntingSkillLevel: SkillLevels = .zero
	private(set) var inventorSkillLevel: SkillLevels = .zero
	private(set) var stableSkillLevel: SkillLevels = .zero
	private(set) var farmingSkillLevel: SkillLevels = .zero
	private(set) var medicalSkillLevel: SkillLevels = .zero
	private(set) var cookingSkillLevel: SkillLevels = .zero
	private(set) var mineLevel: MineLevel = .one {
		didSet {
			if mineLevel.rawValue < oldValue.rawValue {
				mineLevel = oldValue
			}
		}
	}

	mutating func setBlacksmithSkillLevel(_ level: SkillLevels) {
		blacksmithSkillLevel = level
	}

	mutating func setMiningSkillLevel(_ level: SkillLevels) {
		miningSkillLevel = level
	}

	mutating func setBuilderSkillLevel(_ level: SkillLevels) {
		builderSkillLevel = level
	}

	mutating func setHuntingSkillLevel(_ level: SkillLevels) {
		huntingSkillLevel = level
	}

	mutating func setInventorSkillLevel(_ level: SkillLevels) {
		inventorSkillLevel = level
	}

	mutating func setStableSkillLevel(_ level: SkillLevels) {
		stableSkillLevel = level
	}

	mutating func setFarmingSkillLevel(_ level: SkillLevels) {
		farmingSkillLevel = level
	}

	mutating func setMedicalSkillLevel(_ level: SkillLevels) {
		medicalSkillLevel = level
	}

	mutating func setCookingSkillLevel(_ level: SkillLevels) {
		cookingSkillLevel = level
	}

	mutating func setMineLevel(_ level: MineLevel) {
		mineLevel = level
	}
}

extension PlayerCharacter {
	func setBlacksmithSkillLevel(_ level: SkillLevels) {
		stats.setBlacksmithSkillLevel(level)
	}

	func setMiningSkillLevel(_ level: SkillLevels) {
		stats.setMiningSkillLevel(level)
	}

	func setBuilderSkillLevel(_ level: SkillLevels) {
		stats.setBuilderSkillLevel(level)
	}

	func setHuntingSkillLevel(_ level: SkillLevels) {
		stats.setHuntingSkillLevel(level)
	}

	func setInventorSkillLevel(_ level: SkillLevels) {
		stats.setInventorSkillLevel(level)
	}

	func setStableSkillLevel(_ level: SkillLevels) {
		stats.setStableSkillLevel(level)
	}

	func setFarmingSkillLevel(_ level: SkillLevels) {
		stats.setFarmingSkillLevel(level)
	}

	func setMedicalSkillLevel(_ level: SkillLevels) {
		stats.setMedicalSkillLevel(level)
	}

	func setCookingSkillLevel(_ level: SkillLevels) {
		stats.setCookingSkillLevel(level)
	}

	func setMineLevel(_ level: MineLevel) {
		stats.setMineLevel(level)
	}
}

enum AllSkillLevels: CaseIterable {
	case blacksmithSkillLevel
	case miningSkillLevel
	case builderSkillLevel
	case huntingSkillLevel
	case inventorSkillLevel
	case stableSkillLevel
	case farmingSkillLevel
	case medicalSkillLevel

	var stat: SkillLevels {
		get async {
			switch self {
				case .blacksmithSkillLevel:
					await Game.shared.player.stats.blacksmithSkillLevel
				case .miningSkillLevel:
					await Game.shared.player.stats.miningSkillLevel
				case .builderSkillLevel:
					await Game.shared.player.stats.builderSkillLevel
				case .huntingSkillLevel:
					await Game.shared.player.stats.huntingSkillLevel
				case .inventorSkillLevel:
					await Game.shared.player.stats.inventorSkillLevel
				case .stableSkillLevel:
					await Game.shared.player.stats.stableSkillLevel
				case .farmingSkillLevel:
					await Game.shared.player.stats.farmingSkillLevel
				case .medicalSkillLevel:
					await Game.shared.player.stats.medicalSkillLevel
			}
		}
	}

	var name: String {
		switch self {
			case .blacksmithSkillLevel:
				"Blacksmith Skill Level"
			case .miningSkillLevel:
				"Mining Skill Level"
			case .builderSkillLevel:
				"Builder Skill Level"
			case .huntingSkillLevel:
				"Hunting Skill Level"
			case .inventorSkillLevel:
				"Inventor Skill Level"
			case .stableSkillLevel:
				"Stable Skill Level"
			case .farmingSkillLevel:
				"Farming Skill Level"
			case .medicalSkillLevel:
				"Medical Skill Level"
		}
	}
}

enum SkillLevels: Int, Codable {
	case zero = 0
	case one = 1
	case two = 2
	case three = 3
	case four = 4
	case five = 5
	case six = 6
	case seven = 7
	case eight = 8
	case nine = 9
	case ten = 10
}

enum MineLevel: Int, Codable, CaseIterable {
	case one = 1
	case two = 2
	case three = 3
}
