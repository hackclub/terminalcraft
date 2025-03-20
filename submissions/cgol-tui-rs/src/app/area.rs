#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Default)]
pub struct Area {
    pub width: u16,
    pub height: u16,
}
impl Area {
    pub fn new(width: u16, height: u16) -> Self {
        Area { width, height }
    }
    pub const fn len(&self) -> usize {
        self.width as usize * self.height as usize
    }
    #[must_use]
    pub const fn is_empty(&self) -> bool {
        self.len() == 0
    }
}
impl<U1: Into<u16>, U2: Into<u16>> From<(U1, U2)> for Area {
    fn from(val: (U1, U2)) -> Self {
        Self {
            width: val.0.into(),
            height: val.1.into(),
        }
    }
}
