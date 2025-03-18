enum SVMineHelperNPC: StartingVillageNPC {
	static func talk() async {
		await MessageBox.message("I'm busy here...", speaker: .mine_helper)
	}
}
