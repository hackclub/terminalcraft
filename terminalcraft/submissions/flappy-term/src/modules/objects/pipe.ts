import Vector2 from "@equinor/videx-vector2";
import Game from "@modules/game";
import Object from "@modules/objects/object";
import Objects from "@config/objects";
import GameSettings from "@config/index";

export default class Pipe extends Object {
  readonly gap = Objects.pipes.holeSize;
  readonly width = Objects.pipes.width;
  private gapPosition = 0;
  playerInGap = false;

  constructor(game: Game, position: Vector2) {
    super("", position, game);

    // Gets the bottom of the gap position
    // Minimum is expected to be the text gap
    // Maximum is expected to be the height of the screen minus the gap
    // Subtracting or adding 1 to take account of the border line
    this.gapPosition = Math.floor(
      Math.random() * (game.screen.height - this.gap - GameSettings.textGap - 1)
    ) + GameSettings.textGap + 1;

    this.tick = () => {
      this.position.x -= Objects.pipes.speed;
      this.draw(game, this.position);
    };
    game.events.on("tick", this.tick);
  }

  override draw(game: Game, position: Vector2) {
    for (let y = GameSettings.textGap + 1; y < game.screen.height - 1; y++) {
      if (!(y >= this.gapPosition && y < this.gapPosition + this.gap)) {
        game.screen.put(
          {
            x: position.x,
            y: y,
            wrap: false,
            attr: { },
            dx: 1,
            dy: 0,
          },
          Objects.pipes.sprite.repeat(this.width)
        );
      }
    }
  }

  get getGapPosition(): number {
    return this.gapPosition;
  }
}
