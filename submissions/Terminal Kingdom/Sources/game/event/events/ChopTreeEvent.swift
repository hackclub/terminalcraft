enum ChopTreeEvent {
	static func chopTree() async {
		await MessageBox.message("Timber!", speaker: .game)
		let x = await MapBox.player.x
		let y = await MapBox.player.y
		let tile = await MapBox.mainMap.grid[y][x]
		if tile.type == .tree || tile.type == .snow_tree {
			await MapBox.setMainMapGridTile(x: x, y: y, tile: MapTile(type: .plain, biome: tile.biome))

			let lumberCount = Int.random(in: 1 ... 3)
			let seedCount = Int.random(in: 1 ... 3)
			_ = await Game.shared.player.collect(item: .init(type: .lumber), count: lumberCount)
			_ = await Game.shared.player.collect(item: .init(type: .tree_seed), count: seedCount)
			await Game.shared.player.removeDurability(of: .axe)
		}
	}
}
