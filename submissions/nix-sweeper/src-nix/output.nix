{
  lib,
  colors,
  ...
}: let
  tile_to_ascii = selected: tile: let
    revealed_icon =
      if tile.mine
      then "*"
      else if tile.number == 0
      then " "
      else toString tile.number;

    tile_icon =
      if tile.revealed
      then revealed_icon
      else if tile.flagged
      then "◆"
      else "-";

    tile_color =
      if tile.flagged
      then colors.flag
      else if !tile.revealed
      then colors.normal
      else if tile.mine
      then colors.mine
      else colors."number_${toString tile.number}";

    n = colors.normal.foreground;
    t = tile_color.foreground;
  in
    if selected
    then "${n}<${t}${tile_icon}${n}>"
    else " ${t}${tile_icon} ";

  board_to_ascii = {
    board,
    board_width,
    board_height,
    cursor_x,
    cursor_y,
    ...
  } @ state: let
    is_selected = x: y: cursor_x == x && cursor_y == y;

    n = colors.normal.foreground;
    row_to_ascii = y: row: "${n}│${lib.concatStrings (lib.imap0 (x: tile_to_ascii (is_selected x y)) row)}${n}│";
    rows_ascii = lib.concatStringsSep "\n" (lib.imap0 row_to_ascii board);
    line_ascii = lib.concatStrings (lib.replicate (3 * board_width) "─");

    board_ascii = ''
      ┌${line_ascii}┐
      ${rows_ascii}
      └${line_ascii}┘
    '';
  in
    board_ascii;
in {
  inherit board_to_ascii;
}
