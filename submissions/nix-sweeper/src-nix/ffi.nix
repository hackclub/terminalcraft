{
  lib,
  rand-nix,
  ...
} @ imports: let
  inherit (import ./board.nix imports) get_tile edit_tile generate_board regenerate_until_space_at_position get_win_state;
  inherit (import ./colors.nix imports) colors;
  inherit (import ./output.nix (imports // {inherit colors;})) board_to_ascii;
in {
  initial = {
    board_width,
    board_height,
    num_mines,
    random_seed ? 0,
  } @ config: let
    rng = rand-nix.rng.withSeed (toString random_seed);
    res = generate_board (config // {rng = rng;});
  in {
    inherit (config) board_width board_height num_mines;

    cursor_x = 0;
    cursor_y = 0;

    board = res.board;
    random_seed = res.rng.int;
    first_move = true;
  };

  update = action: {
    board,
    board_width,
    board_height,
    cursor_x,
    cursor_y,
    first_move,
    random_seed,
    ...
  } @ state: let
    move_cursor = x_offset: y_offset: let
      new_x = state.cursor_x + x_offset;
      new_y = state.cursor_y + y_offset;

      constrained_x = lib.max 0 (lib.min new_x (board_width - 1));
      constrained_y = lib.max 0 (lib.min new_y (board_height - 1));
    in {
      cursor_x = constrained_x;
      cursor_y = constrained_y;
    };

    edit_board_tile = edit_tile board;
    edit_board_tile_under_cursor = f: edit_board_tile f cursor_x cursor_y;

    flood_fill_reveal = let
      should_propagate = tile: !tile.flagged && !tile.revealed && tile.number == 0;
      reveal_if_not_flagged = tile:
        if !tile.flagged
        then tile // {revealed = true;}
        else tile;

      recusive_fill = prev_board: x: y: let
        is_valid_tile =
          true
          && x >= 0
          && x < board_width
          && y >= 0
          && y < board_height;

        board_self_revealed = edit_tile prev_board reveal_if_not_flagged x y;

        board_south_flooded = recusive_fill board_self_revealed x (y + 1);
        board_north_flooded = recusive_fill board_south_flooded x (y - 1);
        board_west_flooded = recusive_fill board_north_flooded (x - 1) y;
        board_east_flooded = recusive_fill board_west_flooded (x + 1) y;

        tile = get_tile prev_board x y;
      in
        if !is_valid_tile
        then lib.trace "invalid" prev_board
        else if !should_propagate tile
        then lib.trace "notzero" board_self_revealed
        else lib.trace "ok" board_east_flooded;
    in
      board: x: y: recusive_fill board x y;

    reveal_at_cursor = let
      config =
        state
        // {
          rng = rand-nix.rng.withSeed (toString random_seed);
        };
      first_move_space_res = regenerate_until_space_at_position cursor_x cursor_y config board;
      first_move_space_board = first_move_space_res.board;
      first_move_space_rng = first_move_space_res.rng;

      hit_mine = (get_tile board cursor_x cursor_y).mine;

      flood_fill = board: flood_fill_reveal board cursor_x cursor_y;
      hit_mine_board = edit_board_tile_under_cursor (tile: tile // {revealed = true;});
    in
      if first_move
      then {
        board = flood_fill first_move_space_board;
        random_seed = first_move_space_rng.int;
        first_move = false;
      }
      else if hit_mine
      then {
        board = hit_mine_board;
      }
      else {
        board = flood_fill board;
      };

    applied_action =
      if action == "up"
      then move_cursor 0 (-1)
      else if action == "down"
      then move_cursor 0 1
      else if action == "left"
      then move_cursor (-1) 0
      else if action == "right"
      then move_cursor 1 0
      else if action == "flag"
      then {
        board = edit_board_tile_under_cursor (tile:
          if !tile.revealed
          then tile // {flagged = !tile.flagged;}
          else tile);
      }
      else if action == "expose"
      then reveal_at_cursor
      else throw "Unsupported action `${action}`";

    inherit (get_win_state state) game_over game_won;
  in
    if !game_over
    then state // applied_action
    else state;

  output = state: let
    inherit (get_win_state state) game_over game_won;
    board_ascii = board_to_ascii state;

    end_text =
      if game_won
      then ["You Win!" "Press `r` to restart"]
      else ["Boom!" "Game over. Press `r` to restart"];
  in
    if game_over
    then board_ascii + "\n" + lib.concatStringsSep "\n" end_text
    else board_ascii;
}
