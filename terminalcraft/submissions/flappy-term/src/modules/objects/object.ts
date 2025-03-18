import Vector2 from "@equinor/videx-vector2";
import Game from "@modules/game";

export default abstract class GameObject {
  protected tick: () => void;
  protected position = new Vector2(0, 0);
  protected sprite: string;
  protected game: Game;

  constructor(sprite: string, position: Vector2, game: Game) {
    this.sprite = sprite;
    this.position = position;
    this.game = game;
  }

  draw(game: Game, position: Vector2) {
    game.screen.put(
      { x: position.x, y: position.y, wrap: false, attr: {}, dx: 1, dy: 0 },
      this.sprite
    );

    this.position = position;
  }

  destroy() {
    this.game.events.off("tick", this.tick);
  }

  get getPosition(): Vector2 {
    return this.position;
  }
}