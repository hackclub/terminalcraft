import Foundation
#if canImport(GameplayKit)
	import GameplayKit
#else
	import Noise
#endif

actor MapGen {
	// TODO: chunks Chuck is [[Tile]]? gen new if it is nil
	// TODO: smooth from static to not static
	static let mapWidth = (500 * 2) / 2
	var mapWidth: Int { Self.mapWidth }
	static let mapHeight = 500 / 2
	var mapHeight: Int { Self.mapHeight }
	#if canImport(GameplayKit)
		var seed: Int32
		let temperatureMap: GKNoiseMap
		let elevationMap: GKNoiseMap
		let moistureMap: GKNoiseMap
	#else
		var seed: Int
		let temperatureMap: GradientNoise2D
		let elevationMap: GradientNoise2D
		let moistureMap: GradientNoise2D
	#endif

	init() {
		self.seed = .random(in: 2 ... 1_000_000_000)
		self.temperatureMap = Self.createNoiseGenerator(seed, frequency: 0.005)
		self.elevationMap = Self.createNoiseGenerator(seed + 1, frequency: 0.002)
		self.moistureMap = Self.createNoiseGenerator(seed + 2, frequency: 0.006)
	}

	#if canImport(GameplayKit)
		static func createNoiseGenerator(_ seed: Int32, frequency: Double) -> GKNoiseMap {
			let noiseSource = GKPerlinNoiseSource(
				frequency: frequency,
				octaveCount: 5, // Determines the detail level of the noise
				persistence: 0.4, // Controls amplitude reduction per octave
				lacunarity: 2.0, // Controls frequency increase per octave
				seed: seed // Ensure consistent generation
			)

			let noise = GKNoise(noiseSource)

			let noiseMap = GKNoiseMap(
				noise,
				size: vector_double2(Double(mapWidth), Double(mapHeight)),
				origin: vector_double2(0, 0),
				sampleCount: vector_int2(Int32(mapWidth), Int32(mapHeight)),
				seamless: true
			)

			// print(seed)
			return noiseMap
		}
	#else
		static func createNoiseGenerator(_ seed: Int, frequency: Double) -> GradientNoise2D {
			GradientNoise2D(amplitude: 0.4, frequency: frequency, seed: seed)
		}
	#endif

	func generateFullMap() async -> [[MapTile]] {
		var map: [[MapTile]] = createMap()

		addStaticArea(to: &map)

		for y in 0 ..< mapHeight {
			for x in 0 ..< mapWidth {
				if case let .biomeTOBEGENERATED(type) = map[y][x].type {
					switch type {
						case .desert:
							let rand = Int.random(in: 1 ... 10)
							if rand == 1 {
								map[y][x] = MapTile(type: .cactus, isWalkable: false, biome: type)
							} else {
								map[y][x] = MapTile(type: .sand, isWalkable: true, biome: type)
							}
						case .forest:
							map[y][x] = MapTile(type: .tree, isWalkable: true, event: .chopTree, biome: type)
						case .plains:
							let rand = Int.random(in: 1 ... 15)
							if rand == 2 || rand == 3 {
								map[y][x] = MapTile(type: .tree, isWalkable: true, event: .chopTree, biome: type)
							} else {
								map[y][x] = MapTile(type: .plain, isWalkable: true, biome: type)
							}
						case .snow, .tundra:
							let rand = Int.random(in: 1 ... 10)
							if rand == 2 || rand == 3 {
								map[y][x] = MapTile(type: .snow_tree, isWalkable: true, event: .chopTree, biome: type)
							} else if rand == 1 {
								map[y][x] = MapTile(type: .ice, isWalkable: true, biome: type)
							} else {
								map[y][x] = MapTile(type: .snow, isWalkable: true, biome: type)
							}
						case .volcano:
							let rand = Int.random(in: 1 ... 10)
							if rand == 1 || rand == 3 {
								map[y][x] = MapTile(type: .lava, isWalkable: false, biome: type)
							} else {
								map[y][x] = MapTile(type: .sand, isWalkable: true, biome: type)
							}
						case .ocean:
							map[y][x] = MapTile(type: .water, isWalkable: true, biome: type)
						case .coast:
							map[y][x] = MapTile(type: .sand, isWalkable: true, biome: type)
						case .mountain:
							map[y][x] = MapTile(type: .stone, isWalkable: false, biome: type)
						case .swamp:
							let rand = Int.random(in: 1 ... 10)
							if rand == 2 || rand == 3 {
								map[y][x] = MapTile(type: .tree, isWalkable: true, event: .chopTree, biome: type)
							} else if rand == 1 {
								map[y][x] = MapTile(type: .water, isWalkable: true, biome: type)
							} else {
								map[y][x] = MapTile(type: .plain, isWalkable: true, biome: type)
							}
					}
				}
			}
		}

		// #if DEBUG
		// 	await outputMap(map)
		// 	exit(0)
		// #endif

		return map
	}

	func addStaticArea(to map: inout [[MapTile]]) {
		let staticRegion = StaticMaps.MainMap
		let staticWidth = staticRegion[0].count
		let staticHeight = staticRegion.count
		let startX = (mapWidth - staticWidth) / 2
		let startY = (mapHeight - staticHeight) / 2

		for y in 0 ..< staticHeight {
			for x in 0 ..< staticWidth {
				let biome = map[startY + y][startX + x].biome

				var isInOkBiomes: Bool {
					biome == .snow || biome == .tundra || biome == .forest || biome == .plains || biome == .swamp
				}
				let oldTile = staticRegion[y][x]
				let newTile =
					if case let .biomeTOBEGENERATED(type: preBiome) = oldTile.type {
						if isInOkBiomes {
							MapTile(type: .biomeTOBEGENERATED(type: biome), isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
						} else {
							MapTile(type: .biomeTOBEGENERATED(type: preBiome), isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
						}
					} else if case .playerStart = oldTile.type {
						#if DEBUG
							MapTile(type: .playerStart, isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
						#else
							if case let .biomeTOBEGENERATED(type: preBiome) = oldTile.type {
								if isInOkBiomes {
									MapTile(type: .biomeTOBEGENERATED(type: biome), isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
								} else {
									MapTile(type: .biomeTOBEGENERATED(type: preBiome), isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
								}
							} else {
								MapTile(type: oldTile.type, isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
							}

						#endif
					} else {
						MapTile(type: oldTile.type, isWalkable: oldTile.isWalkable, event: oldTile.event, biome: biome)
					}
				map[startY + y][startX + x] = newTile
			}
		}
	}

	#if DEBUG
		func outputMap(_ map: [[MapTile]]) async {
			do {
				let filePath = FileManager.default.homeDirectoryForCurrentUser
				let directory = filePath.appendingPathComponent(".terminalkingdom")
				let file = directory.appendingPathComponent("map.txt")
				var mapString = ""
				for (index, row) in map.enumerated() {
					for rowTile in row {
						mapString += await rowTile.type.render()
					}
					if index != map.count - 1 {
						mapString += "\n"
					}
				}
				try mapString.write(to: file, atomically: true, encoding: .utf8)
			} catch {
				print(error)
			}
		}
	#endif

	private func createMap() -> [[MapTile]] {
		var biomeMap: [[BiomeType]] = []

		for y in 0 ..< mapHeight {
			var row: [BiomeType] = []
			for x in 0 ..< mapWidth {
				row.append(getBiome(x: x, y: y))
			}
			biomeMap.append(row)
		}

		// Apply biome smoothing here
		biomeMap = smoothBiomes(map: biomeMap)

		// Convert smoothed biome map to MapTile grid
		var tileMap: [[MapTile]] = []
		for y in 0 ..< mapHeight {
			var row: [MapTile] = []
			for x in 0 ..< mapWidth {
				let biome = biomeMap[y][x]
				row.append(MapTile(type: .biomeTOBEGENERATED(type: biome), biome: biome))
			}
			tileMap.append(row)
		}

		return tileMap
	}

	func getBiome(x: Int, y: Int) -> BiomeType {
		#if canImport(GameplayKit)
			let temperature = temperatureMap.value(at: vector_int2(Int32(x), Int32(y))) * 10 // Higher = hotter
			let elevation = elevationMap.value(at: vector_int2(Int32(x), Int32(y))) * 10 // Higher = higher
			let moisture = moistureMap.value(at: vector_int2(Int32(x), Int32(y))) * 10 // Higher = wetter
		#else
			let temperature = (temperatureMap.evaluate(Double(x), Double(y)) * 22).rounded() // Higher = hotter
			let elevation = (elevationMap.evaluate(Double(x), Double(y)) * 22).rounded() // Higher = higher
			let moisture = (moistureMap.evaluate(Double(x), Double(y)) * 22).rounded() // Higher = wetter
		#endif
		var biome: BiomeType = switch temperature {
			case -11 ..< -7: .volcano
			case -7 ..< -5: .desert
			case -5 ..< 5: .plains
			case 5 ..< 7: .snow
			case 7 ..< 11: .tundra
			default: .plains
		}

		if biome == .plains {
			biome = switch moisture {
				case -10 ..< -5: .desert
				case -5 ..< 2: .plains
				case 2 ..< 6: .forest
				case 6 ..< 10: .swamp
				default: .plains
			}
		}

		biome = switch elevation {
			case -10 ..< -6: .ocean
			case -6 ..< -5.5: .coast
			case 6 ..< 8: .mountain
			case 8 ... 10: .tundra
			default: biome
		}

		return biome
	}

	func smoothBiomes(map: [[BiomeType]]) -> [[BiomeType]] {
		var newMap = map
		for y in 1 ..< (map.count - 1) {
			for x in 1 ..< (map[0].count - 1) {
				let neighbors = [
					map[y - 1][x], map[y + 1][x], map[y][x - 1], map[y][x + 1],
				]
				let mostCommon = neighbors.mostCommonType()
				if Bool.random() {
					newMap[y][x] = mostCommon
				}
			}
		}
		return newMap
	}

	func getBiomeAtPlayerPosition() async -> BiomeType {
		let x = await MapBox.player.x
		let y = await MapBox.player.y
		return getBiome(x: x, y: y)
	}
}

extension Array where Element: Hashable {
	func mostCommonType() -> Element {
		let counts = reduce(into: [Element: Int]()) { $0[$1, default: 0] += 1 }
		return counts.max(by: { $0.value < $1.value })?.key ?? self[0]
	}
}
