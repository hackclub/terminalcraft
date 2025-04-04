/// information about one `Cell`: either `Dead` or `Alive`
#[derive(Clone, Copy, Debug, PartialEq, Eq, Default)]
pub enum Cell {
    #[default]
    Dead = 0,
    Alive = 1,
}
impl From<bool> for Cell {
    fn from(alive: bool) -> Self {
        if alive {
            Self::Alive
        } else {
            Self::Dead
        }
    }
}
impl TryFrom<char> for Cell {
    type Error = String;

    fn try_from(ch: char) -> Result<Self, Self::Error> {
        match ch {
            'O' => Ok(Cell::Alive),
            '.' => Ok(Cell::Dead),
            _ => Err(format!(
                "parse error: {ch:?} is an invalid character, should be either '.' or 'O'"
            )),
        }
    }
}
