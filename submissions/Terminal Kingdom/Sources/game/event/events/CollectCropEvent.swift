enum CollectCropEvent {
	static func collectCrop() async {
		let tile = await MapBox.tilePlayerIsOn
		if case let .crop(crop: crop) = tile.type {
			await collect(cropTile: crop, isInPot: false)
		} else if case let .pot(tile: potTile) = tile.type {
			await collectInPot(potTile: potTile)
		}
	}

	static func collectInPot(potTile: PotTile) async {
		if potTile.cropTile.type != .none {
			switch potTile.cropTile.stage {
				case .seed, .sprout:
					await removeCrop()
				case .mature:
					await collect(cropTile: potTile.cropTile, isInPot: true)
			}
		} else {
			await addCrop()
		}
	}

	static func collect(cropTile: CropTile, isInPot: Bool) async {
		let tile = await MapBox.tilePlayerIsOn
		if isInPot {
			if cropTile.type != .none {
				await collectCropTile(cropTile.type)
				await MapBox.updateTile(newTile: .init(type: .pot(tile: .init(cropTile: .init(type: .none))), event: .collectCrop, biome: tile.biome))
			} else {
				await MessageBox.message("There is no crop here", speaker: .game)
			}
		} else {
			if case let .crop(crop: cropTile) = await MapBox.tilePlayerIsOn.type {
				await collectCropTile(cropTile.type, count: Int.random(in: 1 ... 3))
				await MapBox.updateTile(newTile: .init(type: .plain, biome: tile.biome))
			} else {
				await MessageBox.message("There is no crop here", speaker: .game)
			}
		}
	}

	private static func collectCropTile(_ cropTileType: CropTileType, count: Int = 1) async {
		switch cropTileType {
			case .carrot:
				_ = await Game.shared.player.collect(item: .init(type: .carrot), count: count)
			case .potato:
				_ = await Game.shared.player.collect(item: .init(type: .potato), count: count)
			case .wheat:
				_ = await Game.shared.player.collect(item: .init(type: .wheat), count: count)
			case .lettuce:
				_ = await Game.shared.player.collect(item: .init(type: .lettuce), count: count)
			case .tree_seed:
				await MessageBox.message("Timber!", speaker: .game)
				let lumberCount = Int.random(in: 1 ... 3)
				let seedCount = Int.random(in: 0 ... 2)
				_ = await Game.shared.player.collect(item: .init(type: .lumber), count: lumberCount)
				_ = await Game.shared.player.collect(item: .init(type: .tree_seed), count: seedCount)
				if await Game.shared.stages.farm.stage3Stages == .collect {
					await Game.shared.stages.farm.setStage3Stages(.comeBack)
				}
			case .none:
				break
		}
	}

	private static func addCrop() async {
		let tile = await MapBox.tilePlayerIsOn
		if await !Game.shared.player.has(item: .tree_seed) {
			await MessageBox.message("There is no crop here", speaker: .game)
			return
		}
		let options: [MessageOption] = [.init(label: "Quit", action: {}), .init(label: "Plant Seed", action: {
			if await Game.shared.stages.farm.stage2Stages == .plant {
				await Game.shared.stages.farm.setStage2Stages(.comeback)
			}
			await MapBox.updateTile(newTile: .init(type: .pot(tile: .init(cropTile: .init(type: .tree_seed))), event: .collectCrop, biome: tile.biome))
			await Game.shared.addCrop(TilePosition(x: MapBox.player.x, y: MapBox.player.y, mapType: MapBox.mapType))
		})]
		let selectedOption = await MessageBox.messageWithOptions("Plant Seed", speaker: .game, options: options)
		await selectedOption.action()
	}

	private static func removeCrop() async {
		let tile = await MapBox.tilePlayerIsOn
		let options: [MessageOption] = [.init(label: "Quit", action: {}), .init(label: "Remove Seed", action: {
			await Game.shared.removeCrop(TilePosition(x: MapBox.player.x, y: MapBox.player.y, mapType: MapBox.mapType))
			await MapBox.updateTile(newTile: .init(type: .pot(tile: .init()), event: .collectCrop, biome: tile.biome))
		})]
		let selectedOption = await MessageBox.messageWithOptions("Remove Seed", speaker: .game, options: options)
		await selectedOption.action()
	}
}
