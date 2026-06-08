import { terminal } from "terminal-kit";
import Game from "@modules/game";

const game = new Game();
terminal.on("key", (name: string) => {
  switch (name) {
    case "UP":
      game.getPlayer.jump();
      break;
    case " ":
      game.getPlayer.jump();
      break;
    case "CTRL_C":
      game.terminate();
  }
});
