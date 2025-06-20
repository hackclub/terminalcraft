{lib, ...}: let
  terminal_colors = let
    color = value: let
      # nix does not do unicode escapes but json does
      escape = value: builtins.fromJSON ''"\u001B[${toString value}m"'';

      foreground_value = value + 30;
      foreground_bright_value = value + 90;
      background_value = value + 40;
    in {
      inherit value foreground_value foreground_bright_value background_value;
      foreground = escape foreground_value;
      foreground_bright = escape foreground_bright_value;
      background = escape background_value;
    };
  in {
    black = color 0;
    red = color 1;
    green = color 2;
    yellow = color 3;
    blue = color 4;
    magenta = color 5;
    cyan = color 6;
    white = color 7;
  };

  colors = {
    number_0 = terminal_colors.black;
    number_1 = terminal_colors.blue;
    number_2 = terminal_colors.cyan;
    number_3 = terminal_colors.green;
    number_4 = terminal_colors.magenta;
    number_5 = terminal_colors.red;
    number_6 = terminal_colors.red;
    number_7 = terminal_colors.red;
    number_8 = terminal_colors.magenta;

    normal = terminal_colors.white;
    mine = terminal_colors.yellow;
    flag = terminal_colors.yellow;
  };
in {
  inherit terminal_colors colors;
}
