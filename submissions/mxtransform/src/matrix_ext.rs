use ndarray::Array2;

pub(crate) trait MatrixExt {
    fn print(&self);
    fn invert(&mut self);
    fn det(&self) -> f32;
}

impl MatrixExt for Array2<f32> {
    fn print(&self) {
        for row in self.rows() {
            print!("| ");
            for value in row {
                print!("{:>5.2} ", value);
            }
            println!("|");
        }
    }

    fn invert(&mut self) {
        if self.dim() != (2, 2) {
            unimplemented!("Matrix inversion is only implemented for 2x2 matrices");
        }

        let det = self.det();
        let inv_det = 1.0 / det;

        self[[0, 0]] *= inv_det;
        self[[0, 1]] *= -inv_det;
        self[[1, 0]] *= -inv_det;
        self[[1, 1]] *= inv_det;
    }

    fn det(&self) -> f32 {
        if self.dim() != (2, 2) {
            unimplemented!("Matrix determinant is only implemented for 2x2 matrices");
        }

        let a = self[[1, 1]];
        let b = self[[1, 0]];
        let c = self[[0, 1]];
        let d = self[[0, 0]];

        a * d - b * c
    }
}
