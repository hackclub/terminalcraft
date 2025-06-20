use std::path::PathBuf;

use color_eyre::{eyre::ContextCompat, Result};
use image::{ImageReader, RgbaImage};
use ndarray::Array3;

pub(crate) type ImageArray = ndarray::ArrayBase<ndarray::OwnedRepr<u8>, ndarray::Dim<[usize; 3]>>;

pub(crate) fn load_image(path: &PathBuf) -> Result<(ImageArray, (usize, usize))> {
    let img = ImageReader::open(path)?.decode()?.into_rgba8();

    let (width, height) = (img.width() as usize, img.height() as usize);

    let array = Array3::<u8>::from_shape_vec((height, width, 4), img.as_raw().to_vec())?;

    Ok((array, (width, height)))
}

pub(crate) fn save_image(array: ImageArray, path: &PathBuf) -> Result<()> {
    let array = array.as_standard_layout().into_owned();

    let (height, width, _) = array.dim();

    let (flattened, _) = array.into_raw_vec_and_offset();

    let output_img = RgbaImage::from_raw(width as u32, height as u32, flattened)
        .wrap_err("Failed to create image from array")?;

    output_img.save(path)?;

    std::thread::sleep(std::time::Duration::from_secs(1));

    Ok(())
}
