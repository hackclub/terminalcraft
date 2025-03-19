import Foundation

struct Stages {
	var random: RandomStages = .init()
	var blacksmith: BlacksmithStages = .init()
	var mine: MineStages = .init()
	var farm: FarmStages = .init()
	var builder: BuilderStages = .init()

	init() {}
}

actor RandomStages {
	var chopTreeAxeUUIDToRemove: UUID?

	func setChopTreeAxeUUIDToRemove(_ uuid: UUID) {
		chopTreeAxeUUIDToRemove = uuid
	}
}
