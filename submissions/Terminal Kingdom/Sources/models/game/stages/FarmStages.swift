import Foundation

actor FarmStages {
	private(set) var stageNumber = 0
	private(set) var stage1AxeUUIDToRemove: UUID?
	private(set) var stage2SeedUUIDToRemove: UUID?
	private(set) var stage4ClayUUIDToRemove: [UUID]?
	private(set) var stage4PickaxeUUIDToRemove: UUID?
	private(set) var stage5ClayUUIDToRemove: [UUID]?

	private(set) var stage1Stages: FarmStage1Stages = .notStarted
	private(set) var stage2Stages: FarmStage2Stages = .notStarted
	private(set) var stage3Stages: FarmStage3Stages = .notStarted
	private(set) var stage4Stages: FarmStage4Stages = .notStarted
	private(set) var stage5Stages: FarmStage5Stages = .notStarted
	private(set) var stage6Stages: FarmStage6Stages = .notStarted

	func next() {
		stageNumber += 1
	}

	func setStage1AxeUUIDsToRemove(_ uuid: UUID) {
		stage1AxeUUIDToRemove = uuid
	}

	func setStage2SeedUUIDsToRemove(_ uuid: UUID) {
		stage2SeedUUIDToRemove = uuid
	}

	func setStage4ClayUUIDsToRemove(_ uuid: [UUID]) {
		stage4ClayUUIDToRemove = uuid
	}

	func setStage4PickaxeUUIDsToRemove(_ uuid: UUID) {
		stage4PickaxeUUIDToRemove = uuid
	}

	func setStage5ClayUUIDsToRemove(_ uuid: [UUID]) {
		stage5ClayUUIDToRemove = uuid
	}

	func setStage1Stages(_ stage: FarmStage1Stages) {
		stage1Stages = stage
	}

	func setStage2Stages(_ stage: FarmStage2Stages) {
		stage2Stages = stage
	}

	func setStage3Stages(_ stage: FarmStage3Stages) {
		stage3Stages = stage
	}

	func setStage4Stages(_ stage: FarmStage4Stages) {
		stage4Stages = stage
	}

	func setStage5Stages(_ stage: FarmStage5Stages) {
		stage5Stages = stage
	}

	func setStage6Stages(_ stage: FarmStage6Stages) {
		stage6Stages = stage
	}
}
