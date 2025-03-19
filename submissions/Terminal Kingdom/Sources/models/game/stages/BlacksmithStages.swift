import Foundation

actor BlacksmithStages {
	private(set) var stageNumber = 0
	private(set) var stage1AIronUUIDsToRemove: [UUID]?
	private(set) var stage2AxeUUIDToRemove: UUID?
	private(set) var stage3LumberUUIDsToRemove: [UUID]?
	private(set) var stage4CoalUUIDsToRemove: [UUID]?
	private(set) var stage5ItemsToMakeSteelUUIDs: [UUID]?
	private(set) var stage5SteelUUIDsToRemove: [UUID] = []
	private(set) var stage6ItemsToMakePickaxeUUIDs: [UUID]?
	private(set) var stage6PickaxeUUIDToRemove: UUID?
	private(set) var stage7ItemsToMakeSwordUUIDs: [UUID]?
	private(set) var stage7SwordUUIDToRemove: UUID?
	private(set) var stage8MaterialsToRemove: [UUID]?
	private(set) var stage9SteelUUIDToRemove: [UUID]?

	private(set) var stage1Stages: BlacksmithStage1Stages = .notStarted
	private(set) var stage2Stages: BlacksmithStage2Stages = .notStarted
	private(set) var stage3Stages: BlacksmithStage3Stages = .notStarted
	private(set) var stage4Stages: BlacksmithStage4Stages = .notStarted
	private(set) var stage5Stages: BlacksmithStage5Stages = .notStarted
	private(set) var stage6Stages: BlacksmithStage6Stages = .notStarted
	private(set) var stage7Stages: BlacksmithStage7Stages = .notStarted
	private(set) var stage8Stages: BlacksmithStage8Stages = .notStarted
	var stage9Stages: BlacksmithStage9Stages = .notStarted

	func next() {
		stageNumber += 1
	}

	func setStage1AIronUUIDsToRemove(_ uuids: [UUID]) {
		stage1AIronUUIDsToRemove = uuids
	}

	func setStage2AxeUUIDToRemove(_ uuid: UUID) {
		stage2AxeUUIDToRemove = uuid
	}

	func setStage3LumberUUIDsToRemove(_ uuids: [UUID]) {
		stage3LumberUUIDsToRemove = uuids
	}

	func setStage4CoalUUIDsToRemove(_ uuids: [UUID]) {
		stage4CoalUUIDsToRemove = uuids
	}

	func setStage5ItemsToMakeSteelUUIDs(_ uuids: [UUID]) {
		stage5ItemsToMakeSteelUUIDs = uuids
	}

	func setStage5SteelUUIDsToRemove(_ uuids: [UUID]) {
		stage5SteelUUIDsToRemove = uuids
	}

	func setStage6PickaxeUUIDToRemove(_ uuid: UUID) {
		stage6PickaxeUUIDToRemove = uuid
	}

	func setStage6ItemsToMakePickaxeUUIDs(_ uuids: [UUID]) {
		stage6ItemsToMakePickaxeUUIDs = uuids
	}

	func setStage7ItemsToMakeSwordUUIDs(_ uuids: [UUID]) {
		stage7ItemsToMakeSwordUUIDs = uuids
	}

	func setStage7SwordUUIDToRemove(_ uuid: UUID) {
		stage7SwordUUIDToRemove = uuid
	}

	func setStage8MaterialsToRemove(_ uuids: [UUID]) {
		stage8MaterialsToRemove = uuids
	}

	func setStage9SteelUUIDToRemove(_ uuid: [UUID]) {
		stage9SteelUUIDToRemove = uuid
	}

	func setStage1Stages(_ stage: BlacksmithStage1Stages) {
		stage1Stages = stage
	}

	func setStage2Stages(_ stage: BlacksmithStage2Stages) {
		stage2Stages = stage
	}

	func setStage3Stages(_ stage: BlacksmithStage3Stages) {
		stage3Stages = stage
	}

	func setStage4Stages(_ stage: BlacksmithStage4Stages) {
		stage4Stages = stage
	}

	func setStage5Stages(_ stage: BlacksmithStage5Stages) {
		stage5Stages = stage
	}

	func setStage6Stages(_ stage: BlacksmithStage6Stages) {
		stage6Stages = stage
	}

	func setStage7Stages(_ stage: BlacksmithStage7Stages) {
		stage7Stages = stage
	}

	func setStage8Stages(_ stage: BlacksmithStage8Stages) {
		stage8Stages = stage
	}

	func setStage9Stages(_ stage: BlacksmithStage9Stages) {
		stage9Stages = stage
	}
}
