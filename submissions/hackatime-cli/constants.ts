import type { Text } from "ink";

export const hackatimeApiUrl = "https://waka.hackclub.com/api/";

// 110
export const bigBanner = ` ___  ___  ________  ________  ___  __    ________  _________  ___  _____ ______   _______                  ________  ___       ___     
|\\  \\|\\  \\|\\   __  \\|\\   ____\\|\\  \\|\\  \\ |\\   __  \\|\\___   ___\\\\  \\|\\   _ \\  _   \\|\\  ___ \\                |\\   ____\\|\\  \\     |\\  \\    
\\ \\  \\\\\\  \\ \\  \\|\\  \\ \\  \\___|\\ \\  \\/  /|\\ \\  \\|\\  \\|___ \\  \\_\\ \\  \\ \\  \\\\\\__\\ \\  \\ \\   __/|   ____________\\ \\  \\___|\\ \\  \\    \\ \\  \\   
 \\ \\   __  \\ \\   __  \\ \\  \\    \\ \\   ___  \\ \\   __  \\   \\ \\  \\ \\ \\  \\ \\  \\\\|__| \\  \\ \\  \\_|/__|\\____________\\ \\  \\    \\ \\  \\    \\ \\  \\  
  \\ \\  \\ \\  \\ \\  \\ \\  \\ \\  \\____\\ \\  \\\\ \\  \\ \\  \\ \\  \\   \\ \\  \\ \\ \\  \\ \\  \\    \\ \\  \\ \\  \\_|\\ \\|____________|\\ \\  \\____\\ \\  \\____\\ \\  \\ 
   \\ \\__\\ \\__\\ \\__\\ \\__\\ \\_______\\ \\__\\\\ \\__\\ \\__\\ \\__\\   \\ \\__\\ \\ \\__\\ \\__\\    \\ \\__\\ \\_______\\              \\ \\_______\\ \\_______\\ \\__\\
    \\|__|\\|__|\\|__|\\|__|\\|_______|\\|__| \\|__|\\|__|\\|__|    \\|__|  \\|__|\\|__|     \\|__|\\|_______|               \\|_______|\\|_______|\\|__|`;

// 76
export const smallBanner = `
 _                 _                 _                        _  _ 
| |               | |            _  (_)                      | |(_)
| |__  _____  ____| |  _ _____ _| |_ _ ____  _____ _____ ____| | _ 
|  _ \\(____ |/ ___) |_/ |____ (_   _) |    \\| ___ (_____) ___) || |
| | | / ___ ( (___|  _ (/ ___ | | |_| | | | | ____|    ( (___| || |
|_| |_\\_____|\\____)_| \\_)_____|  \\__)_|_|_|_|_____)     \\____)\\_)_|`;

// 60
export const smallerBanner = `
_  _ ____ ____ _  _ ____ ___ _ _  _ ____    ____ _    _ 
|__| |__| |    |_/  |__|  |  | |\\/| |___ __ |    |    | 
|  | |  | |___ | \\_ |  |  |  | |  | |___    |___ |___ | `;

// 56
export const smallestBanner = `
  _            _        _   _                  _ _ 
 | |_  __ _ __| |____ _| |_(_)_ __  ___ ___ __| (_)
 | ' \\/ _\` / _| / / _\` |  _| | '  \\/ -_)___/ _| | |
 |_||_\\__,_\\__|_\\_\\__,_|\\__|_|_|_|_\\___|   \\__|_|_|`;

export class Thresholds {
  public static getColor(amount: number, colorMapping: ColorMapping): string | undefined {
    return colorMapping.find(([threshold]) => amount < threshold)?.[1];
  }

  static readonly today: ColorMapping = [
    [60 * 10, "redBright"],
    [60 * 30, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly week: ColorMapping = [
    [60 * 10 * 5, "redBright"],
    [60 * 30 * 5, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly month: ColorMapping = [
    [60 * 10 * 20, "redBright"],
    [60 * 30 * 20, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly todayProject: ColorMapping = [
    [60 * 5, "redBright"],
    [60 * 15, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly weekProject: ColorMapping = [
    [60 * 5 * 5, "redBright"],
    [60 * 15 * 5, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly monthProject: ColorMapping = [
    [60 * 5 * 15, "redBright"],
    [60 * 15 * 15, "yellowBright"],
    [Infinity, "greenBright"],
  ];

  static readonly lastHeartbeat: ColorMapping = [
    [1000 * 60 * 60, "green"],
    [1000 * 60 * 60 * 18, "yellow"],
    [Infinity, "red"],
  ];
}
export type ColorMapping = [number, Parameters<typeof Text>[0]["color"]][];

export type EntryColorMapping = Record<string, Parameters<typeof Text>[0]["color"]>;

export class EntryColors {
  public static getColor(category: string, mapping: EntryColorMapping): EntryColorMapping[keyof EntryColorMapping] {
    return mapping[category];
  }

  static readonly category: EntryColorMapping = {
    advising: "#ff45d4",
    browsing: "#e59215",
    building: "#e8ce3d",
    "code reviewing": "#34f5db",
    coding: "#1f9aef",
    communicating: "#6f2170",
    debugging: "#c49af9",
    designing: "#9061ca",
    indexing: "#fff09d",
    learning: "#38a2eb",
    "manual testing": "#34be61",
    meeting: "#fd1464",
    planning: "#ff4585",
    researching: "#4cbfc0",
    "running tests": "#ec5756",
    supporting: "#ed07a4",
    translating: "#5a42cf",
    "writing docs": "#36e3ff",
    "writing tests": "#3cec76",
  };

  static readonly editor: EntryColorMapping = {
    "visual studio code": "#007acc",
    vscode: "#007acc",
    "intellij idea": "#2876e1",
    pycharm: "#d2ee5c",
    webstorm: "#21d789",
    "android studio": "#99cd00",
    xcode: "#1575f9",
    "sublime text": "#ff9800",
    vim: "#019733",
    neovim: "#068304",
    emacs: "#8c76c3",
    brackets: "#067dc3",
    eclipse: "#443582",
    netbeans: "#aed43a",
    atom: "#49b77e",
    rider: "#f7a415",
    rubymine: "#ff6336",
    phpstorm: "#d93ac1",
    clion: "#14c9a5",
    goland: "#bd4ffc",
    datagrip: "#907cf2",
    dbeaver: "#897363",
    blender: "#fb8007",
    obsidian: "#4a38a0",
    postman: "#fc6b33",
    figma: "#c7b9ff",
    sketch: "#f7b500",
    "notepad++": "#9ecf54",
    "arduino ide": "#048184",
    kakoune: "#dd5f4a",
    kate: "#0b7aef",
    komodo: "#fcb414",
    terminal: "#000000",
  };

  static readonly os: EntryColorMapping = {
    windows: "#00a4ef",
    macos: "#555555",
    linux: "#fbc02d",
    bsd: "#cc0000",
    solaris: "#df7700",
    "unknown os": "#757575",
  };

  static readonly language: EntryColorMapping = {
    "1c enterprise": "#814ccc",
    abap: "#e8274b",
    actionscript: "#882b0f",
    ada: "#02f88c",
    agda: "#315665",
    alloy: "#64c800",
    ampl: "#e6efbb",
    angelscript: "#c7d7dc",
    apex: "#1797c0",
    apl: "#5a8164",
    assembly: "#6e4c13",
    astro: "#ff5a03",
    autohotkey: "#6594b9",
    awk: "#1c3552",
    bash: "#89e051",
    batchfile: "#c1f12e",
    beef: "#c80fa0",
    bibtex: "#778899",
    bicep: "#519aba",
    c: "#555555",
    clojure: "#db5855",
    cmake: "#da3434",
    cobol: "#fcd7de",
    coffeescript: "#244776",
    crystal: "#000100",
    css: "#563d7c",
    d: "#ba595e",
    dart: "#00b4ab",
    dockerfile: "#0db7ed",
    ejs: "#a91e50",
    elixir: "#6e4a7e",
    elm: "#60b5cc",
    "emacs lisp": "#c065db",
    erlang: "#b83998",
    "f#": "#b845fc",
    fortran: "#4d41b1",
    glsl: "#5686a5",
    go: "#00add8",
    graphql: "#e10098",
    groovy: "#4298b8",
    haskell: "#5e5086",
    hlsl: "#aace60",
    html: "#e34c26",
    java: "#b07219",
    javascript: "#f1e05a",
    julia: "#a270ba",
    json: "#292929",
    "json with comments": "#292929",
    json5: "#267cb9",
    jsoniq: "#40d47e",
    toml: "#9c4221",
    xml: "#0060ac",
    kotlin: "#f18e33",
    latex: "#008080",
    lisp: "#3fb68b",
    lua: "#000080",
    makefile: "#427819",
    markdown: "#083fa1",
    matlab: "#e16737",
    nim: "#ffe953",
    nix: "#7e7eff",
    "objective-c": "#438eff",
    ocaml: "#ef7a08",
    pascal: "#e3f171",
    perl: "#0298c3",
    php: "#4f5d95",
    powershell: "#012456",
    python: "#3572a5",
    r: "#198ce7",
    ruby: "#701516",
    rust: "#dea584",
    scala: "#dc322f",
    scss: "#c6538c",
    shell: "#89e051",
    solidity: "#aa6746",
    sql: "#e38c00",
    svelte: "#ff3e00",
    swift: "#ffac45",
    typescript: "#3178c6",
    vala: "#a56de2",
    vbscript: "#15c8da",
    verilog: "#b2b7f8",
    vhdl: "#adb2cb",
    vue: "#41b883",
    yaml: "#cb171e",
  };
}
