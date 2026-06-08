import { terminal, ScreenBufferHD } from "terminal-kit";
import { version } from "../../package.json";
import { EventEmitter } from "events";
import Vector2 from "@equinor/videx-vector2";
import GameSettings from "@config/index";
import Objects from "@config/objects";
import Pipe from "@modules/objects/pipe"; 
import Player from "@modules/objects/player";

export default class Game {
  readonly screen = new ScreenBufferHD({
    dst: terminal,
    noFill: false,
    width: GameSettings.windowSize.x,
    height: GameSettings.windowSize.y,
  });

  events: EventEmitter = new EventEmitter();
  private score = 0;
  
  private player = new Player(new Vector2(this.getScreenCenter.x / 2, this.getScreenCenter.y), this);
  private pipes = [new Pipe(this, new Vector2(this.screen.width, 0))];

  constructor() {
    terminal.grabInput(true);
    terminal.hideCursor();

    terminal.on("exit", () => {
      terminal.reset();
    });

    setInterval(() => {
      this.screen.clear();

      this.tick();
      this.events.emit("tick");

      this.screen.draw({ delta: true });
    }, 1000 / 60);
  }

  tick() {
    this.drawBorderLine(GameSettings.textGap);
    this.drawBorderLine(this.screen.height - 1);

    const titleCenter = this.getScreenCenter.x - Math.floor(GameSettings.title.length / 2);
    const versionCenter = this.getScreenCenter.x - Math.floor(version.length / 2);
    this.drawText(GameSettings.title, new Vector2(titleCenter, 0));
    this.drawText("v" + version, new Vector2(versionCenter, 1));
    this.drawText(`Score: ${this.score}`, new Vector2(0, 1));

    for (let i = 0; i < this.pipes.length; i++) {
      const pipe = this.pipes[i];

      if (pipe.getPosition.x < 0) {
        this.pipes.splice(i, 1);
        pipe.destroy();
      } else if (this.pipes[this.pipes.length - 1].getPosition.x < this.screen.width - Objects.pipes.pipeGaps) {
        this.pipes.push(new Pipe(this, new Vector2(this.screen.width, 0)));
      }

      if (this.player.colliding(pipe)) 
        this.terminate();
      else if (this.player.inGap(pipe))
        this.score++;
      
      if (this.player.getPosition.y > this.screen.height + Objects.player.deadzone) 
        this.terminate();
    }
  }
  
  terminate() {
    this.drawText("GAME OVER", new Vector2(this.getScreenCenter.x - 10, this.getScreenCenter.y - 1));
    
    terminal.grabInput(false);
    setTimeout(() => {
      process.exit();
    }, 100);
  }
  
  drawText(text: string, position: Vector2) {
    this.screen.put(
      {
        x: position.x,
        y: position.y,
        wrap: false,
        attr: { },
        dx: 1,
        dy: 0,
      },
      text
    );
  }
  
  private drawBorderLine(y: number) {
    this.screen.put(
      {
        x: 0,
        y: y,
        wrap: false,
        attr: { },
        dx: 1,
        dy: 0,
      },
      "-".repeat(this.screen.width)
    );
  }
  
  get getPipes(): Pipe[] {
    return this.pipes;
  }
  
  get getScore(): number {
    return this.score;
  }
  
  get getPlayer(): Player {
    return this.player;
  }
  
  get getScreenCenter(): Vector2 {
    return new Vector2(this.screen.width / 2, this.screen.height / 2);
  }
}
