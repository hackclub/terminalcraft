help="Commands:
W to swipe up
A to swipe left
S to swipe down
D to swipe right
Q to quit the game
H for help"

# Move Enum
# 0 -> Up
# 1 -> Down
# 2 -> Left
# 3 -> Right

move_rc_changes=(
  01 # Up
  21 # Down
  10 # Left
  12 # Right
)

move_rc=(
  00 # Up
  10 # Down
  00 # Left
  01 # Right
)
# 0 -> -1
# 1 -> 0
# 2 -> +1

cell_value_formatted=("    " "  1 " "  2 " "  4 " "  8 " " 16 " " 32 " " 64 " "128 " "256 " "512 " "1024" "2048")
cell_multiplier_formatted=("    " "\033[32;1m x2 \033[0m" "\033[31;1m /2 \033[0m")
spawns=(2 2 2 2 3)
win=0
score=0
movedLastMove=0
difficulty=0
cellValues=()
cellModified=()
cellMultiplier=()

get_index() {
  local row=$1
  local col=$2
  return $((row * size + col))
}

set_modified() {
  get_index $1 $2
  cellModified[$?]=$3
}

get_modified() {
  get_index $1 $2
  return ${cellModified[$?]}
}

set_multiplier() {
  get_index $1 $2
  cellMultiplier[$?]=$3
}

get_multiplier() {
  get_index $1 $2
  return ${cellMultiplier[$?]}
}

set_value() {
  if (( $3 == 12 )); then
    win=1
  fi
  get_index $1 $2
  cellValues[$?]=$3
}

get_value() {
  local row=$1
  local col=$2
  if (( row < 0 || row >= size || col < 0 || col >= size )); then
    return 255
  else
    get_index $row $col
    return ${cellValues[$?]}
  fi
}

get_row_delta() {
  local move=$1
  local moveRCDelta=${move_rc_changes[$move]}
  return $((moveRCDelta / 10))
}

get_col_delta() {
  local move=$1
  local moveRCDelta=${move_rc_changes[$move]}
  return $((moveRCDelta % 10))
}

end() {
  echo "Thanks for playing!"
  exit 0
}

help() {
  echo "$help"
}

menu() {
  read -r -p "Select an option: " choice
  case $choice in
    w|W) up ;;
    a|A) left ;;
    s|S) down ;;
    d|D) right ;;
    q|Q) end ;;
    h|H) help; menu ;;
    *) echo "Invalid option!"; menu ;;
  esac
}

spawn() {
  local value=${spawns[$((RANDOM % ${#spawns[@]}))]}
  local empty_cells=()
  for ((i = 0; i < size; i++)); do
    for ((j = 0; j < size; j++)); do
      get_value $i $j
      if (( $? == 0 )); then
        get_multiplier $i $j
        if (( $? == 0 )); then
          empty_cells+=("$i $j")
        fi
      fi
    done
  done
  if (( ${#empty_cells[@]} == 0 )); then
      return
  fi
  local random_index=$((RANDOM % ${#empty_cells[@]}))
  # shellcheck disable=SC2086
  set_value ${empty_cells[$random_index]} $value

  if (( difficulty == 2 )); then
    for ((i = 0; i < size; i++)); do
      for ((j = 0; j < size; j++)); do
        set_multiplier $i $j 0
      done
    done
  fi

  if (( difficulty > 1 )); then
    local multiplier=${multiplierSpawns[$((RANDOM % ${#multiplierSpawns[@]}))]}
    local random_index_2=$((RANDOM % ${#empty_cells[@]}))
    if (( random_index != random_index_2 )); then
      set_multiplier ${empty_cells[$random_index_2]} $multiplier
    fi
  fi
    set_multiplier ${empty_cells[$random_index]} 0
}

display_board() {
  local boundary="+"
  local fragment="------+"
  for ((i = 0; i < size; i++)); do
    boundary+="$fragment"
  done
  echo "$boundary"
  for ((i = 0; i < size; i++)); do
    echo -n "| "
    for ((j = 0; j < size; j++)); do
      get_value $i $j
      local value=$?
      if (( value == 0 )); then
        get_multiplier $i $j
        echo -n -e "${cell_multiplier_formatted[$?]} | "
      else
        echo -n -e "${cell_value_formatted[$value]} | "
      fi
    done
    echo -e ""
  done
  echo "$boundary"
}

up() {
  move 0
}
down() {
  move 1
}
left() {
  move 2
}
right() {
  move 3
}

move() {
  local move=$1
  local moveRC=${move_rc[$move]}

  local row=$(((moveRC / 10) * (size - 1)))
  local col=$(((moveRC % 10) * (size - 1)))

  local moveRCDelta="${move_rc_changes[$move]}"
  get_row_delta $move
  absolute $(($? - 1))
  local rowDel=$?
  get_col_delta $move
  absolute $(($? - 1))
  local colDel=$?

  for ((i = 0; i < size; i++)); do
    move_cell $row $col $move
    row=$((row + colDel))
    col=$((col + rowDel))
  done

  if ((movedLastMove == 1)); then
    spawn
  fi
  movedLastMove=0
  for ((i = 0; i < size; i++)); do
    for ((j = 0; j < size; j++)); do
      set_modified $i $j 0
    done
  done
  check_lose
  local lose=$?
  display_board
  echo "Score: $score"
  if (( win == 1 )); then
    echo "You win!"
    end
  fi
  if (( lose == 1 )); then
    echo "You lose!"
    end
  fi
  menu
}

absolute() {
  local value=$1
  if (( value < 0 )); then
    return $(( -value ))
  else
    return $value
  fi
}

move_cell() {
  local row=$1
  local col=$2
  local move=$3
  get_row_delta $move
  local rowDel=$(($? - 1))
  get_col_delta $move
  local colDel=$(($? - 1))
  get_value "$row" "$col"
  local cell=$?
  if (( cell == 255 )); then
    return
  fi
  local targetRow=$((row + rowDel))
  local targetCol=$((col + colDel))
  get_value $targetRow $targetCol
  local target=$?
  if (( target != 255 && cell != 0 )); then
    get_modified $targetRow $targetCol
    local targetModified=$?

    if (( "$target" == "0" )); then
      get_multiplier $targetRow $targetCol
      case $? in
        1) cell=$((cell + 1)); score=$((score + 2**cell)) ;;
        2) cell=$((cell - 1)); score=$((score + 2**cell)) ;;
      esac
      set_multiplier $targetRow $targetCol 0

      get_modified $row $col
      local thisModified=$?
      set_value $targetRow $targetCol $cell
      set_modified $targetRow $targetCol $thisModified
      set_value $row $col 0
      set_modified $row $col $targetModified
      movedLastMove=1
      move_cell $targetRow $targetCol $move
      return
    elif (( target == cell && targetModified == 0 )); then
        set_value $targetRow $targetCol $((target + 1))
        set_modified $targetRow $targetCol 1
        set_value $row $col 0
        movedLastMove=1
        score=$((score + 2**cell))
    fi
  fi
  move_cell $((row - rowDel)) $((col - colDel)) $move
}

check_move() {
  local row=$1
  local col=$2
  local value=$3
  get_value $row $col
  local target=$?
  if (( target == 0 || value == target )); then
    return 1
  else
    return 0
  fi
}

can_move() {
  local row=$1
  local col=$2
  get_value $row $col
  local cell=$?
  # assume cell exists i.e. cell != -1

  check_move $((row + 1)) $col $cell
  local up=$?
  check_move $((row - 1)) $col $cell
  local down=$?
  check_move $row $((col + 1)) $cell
  local left=$?
  check_move $row $((col - 1)) $cell
  local right=$?
  if (( up == 1 || down == 1 || left == 1 || right == 1 )); then
    return 1
  else
    return 0
  fi
}

check_lose() {
  for ((i = 0; i < size; i++)); do
    for ((j = 0; j < size; j++)); do
      can_move $i $j
      if (( $? == 1 )); then
        return 0
      fi
    done
  done
  return 1
}

echo -e "
\033[101;1m██████╗  ██████╗ ██╗  ██╗ █████╗ \033[0m
\033[101;1m╚════██╗██╔═████╗██║  ██║██╔══██╗\033[0m
\033[101;1m █████╔╝██║██╔██║███████║╚█████╔╝\033[0m
\033[101;1m██╔═══╝ ████╔╝██║╚════██║██╔══██╗\033[0m
\033[101;1m███████╗╚██████╔╝     ██║╚█████╔╝\033[0m
\033[101;1m╚══════╝ ╚═════╝      ╚═╝ ╚════╝ \033[0m

Welcome to 2048!
\033[1mChoose your difficulty\033[0m
  \033[32;1m1. Easy  \033[0m (Classic 2048 (6x6), nothing new)
  \033[33;1m2. Hard  \033[0m (Some multiplier gremlins sprinkled in)
  \033[31;1m3. Expert\033[0m (Nah you ain't beating this one)"
read -r -p "Enter difficulty (1, 2, or 3): " difficulty
if (( difficulty < 1 || difficulty > 3 )); then
  echo "Invalid difficulty! Defaulting to 1."
  difficulty=1
fi
case $difficulty in
  1) size=6; multiplierSpawns=(0 0 0 0 0);;
  2) size=4; multiplierSpawns=(0 0 0 1 2);;
  3) size=4; multiplierSpawns=(0 1 2 2 2);;
esac
for ((i = 0; i < size; i++)); do
  for ((j = 0; j < size; j++)); do
    set_value i j 0
    set_modified i j 0
    set_multiplier $i $j 0
done
done
spawn
spawn
help
display_board
menu
