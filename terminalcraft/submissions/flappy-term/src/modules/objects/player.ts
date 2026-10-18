import Vector2 from "@equinor/videx-vector2";
import GameSettings from "@config/index";
import Objects from "@config/objects";
import Object from "@modules/objects/object";
import Game from "@modules/game";
import Pipe from "@modules/objects/pipe";
 
export default class Player extends Object {
  private jumping = false;
  private velocity = 0;

  constructor(position: Vector2 = new Vector2(0, 0), game: Game) {
    super(Objects.player.sprite, position, game);
    
    this.tick = () => {
      if (!this.jumping) {
        this.velocity += GameSettings.gravity * Objects.player.mass;
        this.velocity = Math.min(this.velocity, Objects.player.maxVelocity);
        this.position.y += this.velocity;
      }

      if (this.position.y <= GameSettings.textGap)
        this.sprite = "";
      else
        this.sprite = Objects.player.sprite;

      this.draw(game, this.position);
    };
    game.events.on("tick", this.tick);
  }

  jump() {
    if (!this.jumping) {
      this.jumping = true;
      this.position.y -= Objects.player.jumpHeight;
 
      setTimeout(() => {
        this.jumping = false;
      }, 100); 
    }
  }

  colliding(pipe: Pipe): boolean {
    if (this.position.x >= pipe.getPosition.x - 2 && this.position.x < pipe.getPosition.x + pipe.width) 
      // Checks if the player is within the gap
      if (this.position.y < pipe.getGapPosition || this.position.y >= pipe.getGapPosition + pipe.gap)
        return true;
  
    return false;
  }

  inGap(pipe: Pipe): boolean {
    if (this.position.x >= pipe.getPosition.x + pipe.width && !pipe.playerInGap)
      if (!(this.position.y < pipe.getGapPosition || this.position.y >= pipe.getGapPosition + pipe.gap)) {
        pipe.playerInGap = true;
        return true;
      }

    return false;
  }
}
