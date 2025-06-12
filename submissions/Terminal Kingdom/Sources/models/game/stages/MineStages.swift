import Foundation

actor MineStages {
	private(set) var stageNumber = 0
	var isDone: Bool { stageNumber > 10 }
	private(set) var stage1PickaxeUUIDToRemove: UUID?
	private(set) var stage2PickaxeUUIDToRemove: UUID?
	private(set) var stage3AxeUUIDToRemove: UUID?
	private(set) var stage4PickaxeUUIDToRemove: UUID?
	private(set) var stage5PickaxeUUIDToRemove: UUID?
	private(set) var stage6AxeUUIDToRemove: UUID?
	private(set) var stage7ItemUUIDsToRemove: [UUID]?
	private(set) var stage8PickaxeUUID: UUID?
	private(set) var stage9PickaxeUUIDToRemove: UUID?
	private(set) var stage10GoldUUIDsToRemove: [UUID]?

	private(set) var stage1Stages: MineStage1Stages = .notStarted
	private(set) var stage2Stages: MineStage2Stages = .notStarted
	private(set) var stage3Stages: MineStage3Stages = .notStarted
	private(set) var stage4Stages: MineStage4Stages = .notStarted {
		didSet {
			StatusBox.questBoxUpdate()
		}
	}

	private(set) var stage5Stages: MineStage5Stages = .notStarted
	private(set) var stage6Stages: MineStage6Stages = .notStarted {
		didSet {
			StatusBox.questBoxUpdate()
		}
	}

	private(set) var stage7Stages: MineStage7Stages = .notStarted
	private(set) var stage8Stages: MineStage8Stages = .notStarted
	private(set) var stage9Stages: MineStage9Stages = .notStarted
	private(set) var stage10Stages: MineStage10Stages = .notStarted {
		didSet {
			StatusBox.questBoxUpdate()
		}
	}

	func next() {
		stageNumber += 1
	}

	func setStage1PickaxeUUIDToRemove(_ uuid: UUID) {
		stage1PickaxeUUIDToRemove = uuid
	}

	func setStage2PickaxeUUIDToRemove(_ uuid: UUID) {
		stage2PickaxeUUIDToRemove = uuid
	}

	func setStage3AxeUUIDToRemove(_ uuid: UUID) {
		stage3AxeUUIDToRemove = uuid
	}

	func setStage4PickaxeUUIDToRemove(_ uuid: UUID) {
		stage4PickaxeUUIDToRemove = uuid
	}

	func setStage5PickaxeUUIDToRemove(_ uuid: UUID) {
		stage5PickaxeUUIDToRemove = uuid
	}

	func setStage6AxeUUIDToRemove(_ uuid: UUID) {
		stage6AxeUUIDToRemove = uuid
	}

	func setStage7ItemUUIDsToRemove(_ uuids: [UUID]) {
		stage7ItemUUIDsToRemove = uuids
	}

	func setStage8PickaxeUUID(_ uuid: UUID) {
		stage8PickaxeUUID = uuid
	}

	func setStage9PickaxeUUIDToRemove(_ uuid: UUID) {
		stage9PickaxeUUIDToRemove = uuid
	}

	func setStage10GoldUUIDsToRemove(_ uuids: [UUID]) {
		stage10GoldUUIDsToRemove = uuids
	}

	func setStage1Stages(_ stage: MineStage1Stages) {
		stage1Stages = stage
	}

	func setStage2Stages(_ stage: MineStage2Stages) {
		stage2Stages = stage
	}

	func setStage3Stages(_ stage: MineStage3Stages) {
		stage3Stages = stage
	}

	func setStage4Stages(_ stage: MineStage4Stages) {
		stage4Stages = stage
	}

	func setStage5Stages(_ stage: MineStage5Stages) {
		stage5Stages = stage
	}

	func setStage6Stages(_ stage: MineStage6Stages) {
		stage6Stages = stage
	}

	func setStage7Stages(_ stage: MineStage7Stages) {
		stage7Stages = stage
	}

	func setStage8Stages(_ stage: MineStage8Stages) {
		stage8Stages = stage
	}

	func setStage9Stages(_ stage: MineStage9Stages) {
		stage9Stages = stage
	}

	func setStage10Stages(_ stage: MineStage10Stages) {
		stage10Stages = stage
	}
}
