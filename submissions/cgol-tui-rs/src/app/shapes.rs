use super::*;

/// Number of special shapes supported
pub const N: usize = 4;

#[cfg(test)]
mod tests;

pub fn all() -> Vec<Universe> {
    vec![
        Universe::from_str(GLIDER).unwrap(),
        Universe::from_str(GOSPER_GLIDER_GUN).unwrap(),
        Universe::from_str(COPPERHEAD).unwrap(),
        Universe::from_str(RABBITS).unwrap(),
        Universe::from_str(BONK_TIE).unwrap(),
        Universe::from_str(ACORN).unwrap(),
    ]
}

pub fn get_special(i: usize, area: Area) -> Universe {
    match i {
        0 => full(area),
        1 => frame(area),
        2 => rand(area),
        3 => stripes(area),
        i => unreachable!("index out of bounds: len is {N} but index is {i}"),
    }
}

pub fn rand(area: Area) -> Universe {
    let cells = (0..area.len()).map(|_i| fastrand::bool().into()).collect();
    Universe::new(area, cells, "random")
}

pub fn stripes(area: Area) -> Universe {
    let cells = (0..area.len())
        .map(|i| {
            if i % 2 == 0 || i % 7 == 0 {
                Cell::Alive
            } else {
                Cell::Dead
            }
        })
        .collect();
    Universe::new(area, cells, "stripes")
}

pub fn empty(area: Area) -> Universe {
    let cells = vec![Cell::Dead; area.len()];
    Universe::new(area, cells, "empty")
}

pub fn full(area: Area) -> Universe {
    let cells = vec![Cell::Alive; area.len()];
    Universe::new(area, cells, "full")
}

/// height: 5
/// width: 5
///  01234
/// 0.....0
/// 1.---.1
/// 2.|.|.2
/// 3.---.3
/// 4.....4
///  01234
pub fn frame(area: Area) -> Universe {
    let mut univ = empty(area).with_name("frame");
    if area.height < 3 || area.width < 3 {
        return univ;
    }
    // horizontal
    for i in [1, area.height - 2] {
        for j in 1..area.width - 1 {
            univ[(i, j)] = Cell::Alive;
        }
    }

    // vertical
    for j in [1, area.width - 2] {
        for i in 2..area.height - 2 {
            univ[(i, j)] = Cell::Alive;
        }
    }
    univ
}

pub const COPPERHEAD: &str = "\
!Name: Copperhead
.....O.OO...
....O......O
...OO...O..O
OO.O.....OO.
OO.O.....OO.
...OO...O..O
....O......O
.....O.OO...";

pub const GOSPER_GLIDER_GUN: &str = "\
!Name: Gosper glider gun
!Author: Bill Gosper
!The first known gun and the first known finite pattern with unbounded growth.
!www.conwaylife.com/wiki/index.php?title=Gosper_glider_gun
........................O
......................O.O
............OO......OO............OO
...........O...O....OO............OO
OO........O.....O...OO
OO........O...O.OO....O.O
..........O.....O.......O
...........O...O
............OO
";

/// 3x3
pub const GLIDER: &str = "\
!Name: Glider
..O
O.O
.OO";

/// 8x4
pub const RABBITS: &str = "\
!Name: Rabbits
O.....O.
..O...O.
..O..O.O
.O.O....";

/// 3×5
pub const BONK_TIE: &str = "\
!Name: Bonk tie
OO
OO
..O
..O
..O";

/// 7×3
pub const ACORN: &str = "\
!Name: Acorn
.O
...O
OO..OOO";
