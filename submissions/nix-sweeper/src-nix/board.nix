{
  lib,
  rand-nix,
  ...
}: let
  get_tile = board: x: y: (lib.elemAt (lib.elemAt board y) x);

  edit_tile = board: f: tile_x: tile_y:
    lib.imap0 (y: row:
      if y == tile_y
      then
        lib.imap0 (x: tile:
          if x == tile_x
          then f tile
          else tile)
        row
      else row)
    board;

  get_num_covered_tiles = board: let
    tiles = lib.flatten board;
  in
    lib.count (tile: !tile.revealed) tiles;

  is_mine_revealed = board: let
    tiles = lib.flatten board;
  in
    lib.any (tile: tile.mine && tile.revealed) tiles;

  get_win_state = {
    board,
    num_mines,
    ...
  } @ config: let
    mine_revealed = is_mine_revealed board;
    num_covered_tiles = get_num_covered_tiles board;
    revealed_all_other_tiles = num_covered_tiles == num_mines;
  in {
    game_over = mine_revealed || revealed_all_other_tiles;
    game_won = revealed_all_other_tiles && !mine_revealed;
  };

  generate_board = {
    board_width,
    board_height,
    num_mines,
    rng,
    ...
  } @ config: let
    place_mine = board: rng: let
      mine_x = rng.intBetween 1 board_width - 1;
      mine_y = rng.next.intBetween 1 board_height - 1;
    in {
      board = edit_tile board (tile: tile // {mine = true;}) mine_x mine_y;
      rng = rng.skip 2;
    };

    fill_board = n: board: rng: let
      res = place_mine board rng;
    in
      if n == 0
      then res
      else fill_board (n - 1) res.board res.rng;

    number_tile = board: y: x: let
      neighbor = x_offset: y_offset: {
        x = x + x_offset;
        y = y + y_offset;
      };

      neighbors = [
        (neighbor (-1) 1)
        (neighbor 0 1)
        (neighbor 1 1)
        (neighbor (-1) 0)
        (neighbor 1 0)
        (neighbor (-1) (-1))
        (neighbor 0 (-1))
        (neighbor 1 (-1))
      ];

      valid_neighbors = lib.filter (neighbor:
        true
        && neighbor.x >= 0
        && neighbor.x < board_width
        && neighbor.y >= 0
        && neighbor.y < board_height)
      neighbors;

      mine_neighbors = lib.filter (neighbor: (get_tile board neighbor.x neighbor.y).mine) valid_neighbors;
    in
      lib.length mine_neighbors;

    assign_numbers = board:
      lib.imap0 (y: row:
        lib.imap0 (x: tile:
          tile
          // {
            number =
              if !tile.mine
              then number_tile board y x
              else 9;
          })
        row)
      board;

    empty_board = lib.replicate board_height (lib.replicate board_width {
      revealed = false;
      flagged = false;
      mine = false;
      number = 0;
    });
    filled_board = fill_board num_mines empty_board rng;
    numbered_board = assign_numbers filled_board.board;
  in {
    board = numbered_board;
    rng = filled_board.rng;
  };

  regenerate_until_space_at_position = x: y: {rng, ...} @ config: board: let
    regen_recursive = config: {
      board,
      rng,
    } @ res: let
      new_config = config // {rng = rng.next;};
      new_board = regen_recursive new_config (generate_board new_config);
    in
      if (get_tile board x y).number == 0
      then res
      else new_board;
  in
    regen_recursive config {
      board = board;
      rng = rng;
    };
in {
  inherit get_tile edit_tile generate_board regenerate_until_space_at_position get_win_state;
}
