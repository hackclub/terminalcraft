import Foundation

struct CitizenNPC: TalkableNPC {
	static func talk(npc: NPC) async {
		await MessageBox.message("Hello \(Game.shared.player.name)", speaker: npc)
	}
}
