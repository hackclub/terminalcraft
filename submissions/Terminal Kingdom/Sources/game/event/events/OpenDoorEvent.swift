enum OpenDoorEvent {
	static func openDoor(doorTile: DoorTile) async {
		if await MapBox.mapType != .mainMap, await MapBox.mapType != .mining {
			await leaveBuildingMap()
		} else {
			switch doorTile.type {
				case .castle: await CastleDoorEvent.open(tile: doorTile)
				case .blacksmith: await BlacksmithDoorEvent.open(tile: doorTile)
				case .mine: await MineDoorEvent.open(tile: doorTile)
				case .shop: await ShopDoorEvent.open(tile: doorTile)
				case .builder: await BuilderDoorEvent.open(tile: doorTile)
				case .hunting_area: await HuntingAreaDoorEvent.open(tile: doorTile)
				case .inventor: await InventorDoorEvent.open(tile: doorTile)
				case .house: await HouseDoorEvent.open(tile: doorTile)
				case .stable: await StableDoorEvent.open(tile: doorTile)
				case .farm: await FarmDoorEvent.open(tile: doorTile)
				case .hospital: await HospitalDoorEvent.open(tile: doorTile)
				case .carpenter: await CarpenterDoorEvent.open(tile: doorTile)
				case .restaurant: await RestaurantDoorEvent.open(tile: doorTile)
				case .potter: await PotterAreaDoorEvent.open(tile: doorTile)
				case let .custom(mapID: mapID, doorType: doorType): await CustomDoorEvent.open(tile: doorTile, mapID: mapID, doorType: doorType)
			}
		}
	}

	private static func leaveBuildingMap() async {
		let currentTile = await MapBox.tilePlayerIsOn

		let newCoordinates: (x: Int, y: Int)? = switch await MapBox.mapType {
			case let .farm(type: farmType):
				if case let .door(playerDoorTile) = currentTile.type {
					// enter, out
					switch (farmType, playerDoorTile.type) {
						case (.main, .farm(type: .farm_area)):
							DoorTileTypes.farm(type: .farm_area).coordinatesForStartingVillageBuildings
						case (.farm_area, .farm(type: .main)):
							DoorTileTypes.farm(type: .main).coordinatesForStartingVillageBuildings
						default:
							// No change in doors has happened
							nil
					}
				} else {
					nil
				}
			case let .castle(side: castleSide):
				await exitCastle(castleSide: castleSide, currentTile: currentTile)
			case let .hospital(side: hospitalSide):
				if case let .door(playerDoorTile) = currentTile.type {
					// enter, out
					switch (hospitalSide, playerDoorTile.type) {
						case (.top, .hospital(side: .bottom)):
							DoorTileTypes.hospital(side: .bottom).coordinatesForStartingVillageBuildings
						case (.bottom, .hospital(side: .top)):
							DoorTileTypes.hospital(side: .top).coordinatesForStartingVillageBuildings
						default:
							// No change in doors has happened
							nil
					}
				} else {
					nil
				}
			default:
				nil
		}

		if let newCoordinates {
			await MapBox.setMainMapPlayerPosition(newCoordinates)
		}

		await Game.shared.maps.setMap(mapType: MapBox.mapType, map: MapBox.buildingMap.grid)

		// Return to the main map
		await MapBox.setMapType(.mainMap)
	}

	private static func exitCastle(castleSide: CastleSide, currentTile: MapTile) async -> (x: Int, y: Int)? {
		var topCoordinates: (x: Int, y: Int) {
			DoorTileTypes.castle(side: .top).coordinatesForStartingVillageBuildings
		}
		var rightCoordinates: (x: Int, y: Int) {
			DoorTileTypes.castle(side: .right).coordinatesForStartingVillageBuildings
		}
		var bottomCoordinates: (x: Int, y: Int) {
			DoorTileTypes.castle(side: .bottom).coordinatesForStartingVillageBuildings
		}
		var leftCoordinates: (x: Int, y: Int) {
			DoorTileTypes.castle(side: .left).coordinatesForStartingVillageBuildings
		}
		return if case let .door(playerDoorTile) = currentTile.type {
			// enter, out
			switch (castleSide, playerDoorTile.type) {
				case (.top, .castle(side: .right)):
					rightCoordinates
				case (.top, .castle(side: .bottom)):
					bottomCoordinates
				case (.top, .castle(side: .left)):
					leftCoordinates
				case (.right, .castle(side: .top)):
					topCoordinates
				case (.right, .castle(side: .bottom)):
					bottomCoordinates
				case (.right, .castle(side: .left)):
					leftCoordinates
				case (.bottom, .castle(side: .top)):
					topCoordinates
				case (.bottom, .castle(side: .right)):
					rightCoordinates
				case (.bottom, .castle(side: .left)):
					leftCoordinates
				case (.left, .castle(side: .top)):
					topCoordinates
				case (.left, .castle(side: .right)):
					rightCoordinates
				case (.left, .castle(side: .bottom)):
					bottomCoordinates
				case (.left, .castle(side: .left)):
					leftCoordinates
				default:
					// No change in doors has happened
					nil
			}
		} else {
			nil
		}
	}
}
