use super::shapes;
use crate::{app::Area, app::Cell};
use ratatui::{style::Color, widgets::canvas::Shape};

/// the `Universe` in which game plays. Represented as a `Vec` of `Cell`s.
#[derive(Debug, Clone, PartialEq, Eq, Default)]
pub struct Universe {
    pub area: Area,
    pub cells: Vec<Cell>,
    pub name: String,
}
impl<U1: Into<usize>, U2: Into<usize>> std::ops::Index<(U1, U2)> for Universe {
    type Output = Cell;

    fn index(&self, idx: (U1, U2)) -> &Self::Output {
        // Convert (x;y) to index
        let idx = self.get_idx(idx);

        &self.cells[idx]
    }
}
impl<U1: Into<usize>, U2: Into<usize>> std::ops::IndexMut<(U1, U2)> for Universe {
    fn index_mut(&mut self, idx: (U1, U2)) -> &mut Self::Output {
        // Convert (x;y) to index
        let idx = self.get_idx(idx);

        &mut self.cells[idx]
    }
}

impl Universe {
    pub fn new(area: Area, cells: Vec<Cell>, name: impl ToString) -> Self {
        Self {
            area,
            cells,
            name: name.to_string(),
        }
    }
    pub fn with_name(self, name: impl ToString) -> Self {
        Self {
            name: name.to_string(),
            ..self
        }
    }
    pub fn name(&self) -> &str {
        &self.name
    }

    fn get_idx(&self, coord: (impl Into<usize>, impl Into<usize>)) -> usize {
        let row = coord.0.into();
        let col = coord.1.into();
        assert!(
            (0..self.area.height).contains(&(row as u16)),
            "index out of range: len is {}, but index is {row}",
            self.area.height,
        );
        assert!(
            (0..self.area.width).contains(&(col as u16)),
            "index out of range: len is {}, but index is {col}",
            self.area.width,
        );
        // Convert (x;y) to index
        let idx = (row * self.area.width as usize) + col;
        assert!(
            idx < self.cells.len(),
            "index out of range: len is {}, but index is {idx}",
            self.cells.len()
        );
        idx
    }

    pub fn live_neighbour_count(&self, row: u16, col: u16) -> u8 {
        let mut sum = 0;

        for delta_row in [self.area.height - 1, 0, 1] {
            for delta_col in [self.area.width - 1, 0, 1] {
                if delta_row == 0 && delta_col == 0 {
                    continue;
                }

                let neighbour_row = (row + delta_row) % self.area.height;
                let neighbour_col = (col + delta_col) % self.area.width;

                sum += self[(neighbour_row, neighbour_col)] as u8;
            }
        }
        sum
    }

    /// Convert properly formatted Vec of Strings to Universe
    fn from_vec_str(s: &[String]) -> Result<Self, String> {
        let (metadata, pattern): (Vec<_>, Vec<_>) = s.iter().partition(|l| l.starts_with('!'));

        let width = pattern
            .iter()
            .map(|ln| ln.chars().count())
            .max()
            .unwrap_or(0) as u16;
        let height = pattern.len() as u16;
        let area = Area::new(width, height);
        let mut univ = shapes::empty(area);

        if let Some(name) = metadata.first() {
            let name = name
                .replace(".cells", "")
                .replace('!', "")
                .replace("Name:", "");
            let name = name.trim();
            univ.name = name.to_string();
        };

        for (i, line) in pattern.iter().enumerate() {
            for (j, ch) in line.chars().enumerate() {
                univ[(i, j)] = ch.try_into()?;
            }
        }

        Ok(univ)
    }

    /// Create universe with width, height: inserting shape into the middle
    ///
    /// # Errors
    ///
    /// if shape can't fit universe
    pub fn from_figur(area: Area, figur: Universe) -> Result<Universe, ()> {
        let count_alive = |univ: &Universe| -> usize {
            univ.cells
                .iter()
                .filter(|cell| *cell == &Cell::Alive)
                .count()
        };

        let figur_alive = count_alive(&figur);

        if area < figur.area {
            return Err(());
        }

        let mut univ = shapes::empty(area).with_name(figur.name());

        let (start_row, start_col) = (
            (area.height - figur.height()) / 2,
            (area.width - figur.width()) / 2,
        );

        let mut j = 0;
        for row in start_row as usize..start_row as usize + figur.height() as usize {
            for i in 0..figur.width() as usize {
                univ[(row, start_col as usize + i)] = figur.cells[j];
                j += 1;
            }
        }

        assert_eq!(figur_alive, count_alive(&univ), "faulty algorithm");
        Ok(univ)
    }

    /// update life: `Universe`
    pub fn tick(&mut self) {
        let mut next = self.clone();

        for row in 0..self.height() {
            for col in 0..self.width() {
                let idx = (row, col);
                let cell = self[idx];
                let live_neighbours = self.live_neighbour_count(row, col);

                let next_cell = match (cell, live_neighbours) {
                    // Rule 1: Any live cell with fewer than two live neighbours
                    // dies, as if caused by underpopulation.
                    (Cell::Alive, n) if n < 2 => Cell::Dead,
                    // Rule 2: Any live cell with two or three live neighbours
                    // lives on to the next generation.
                    (Cell::Alive, 2 | 3) => Cell::Alive,
                    // Rule 3: Any live cell with more than three live
                    // neighbours dies, as if by overpopulation.
                    (Cell::Alive, n) if n > 3 => Cell::Dead,
                    // Rule 4: Any dead cell with exactly three live neighbours
                    // becomes a live cell, as if by reproduction.
                    (Cell::Dead, 3) => Cell::Alive,
                    // All other cells remain in the same state.
                    (otherwise, _) => otherwise,
                };

                next[idx] = next_cell;
            }
        }

        *self = next;
    }

    pub fn width(&self) -> u16 {
        self.area.width
    }

    pub fn height(&self) -> u16 {
        self.area.height
    }
}
impl std::str::FromStr for Universe {
    type Err = String;

    fn from_str(s: &str) -> Result<Self, Self::Err> {
        let v = s
            .trim()
            .lines()
            .map(str::trim)
            .map(std::convert::Into::into)
            .collect::<Vec<String>>();
        Self::from_vec_str(&v)
    }
}

impl Shape for Universe {
    fn draw(&self, painter: &mut ratatui::widgets::canvas::Painter) {
        for y in 0..self.height() {
            for x in 0..self.width() {
                match self[(y, x)] {
                    Cell::Alive => painter.paint(x.into(), y.into(), Color::White),
                    Cell::Dead => continue,
                }
            }
        }
    }
}

impl std::fmt::Display for Universe {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        writeln!(f, "╭{}╮\r", "─".repeat(self.width() as usize * 2))?;
        for line in self.cells.as_slice().chunks(self.width() as usize) {
            write!(f, "│")?;
            for &cell in line {
                let symbol = if cell == Cell::Dead { '◻' } else { '◼' }; // ◻
                write!(f, "{symbol} ")?;
            }
            writeln!(f, "│\r")?;
        }
        writeln!(f, "╰{}╯\r", "─".repeat(self.width() as usize * 2))
    }
}
