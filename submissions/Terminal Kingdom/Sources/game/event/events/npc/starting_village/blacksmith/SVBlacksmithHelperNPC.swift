enum SVBlacksmithHelperNPC: StartingVillageNPC {
	static func talk() async {
		await MessageBox.message("I'm busy here...", speaker: .blacksmith_helper)
	}
}
