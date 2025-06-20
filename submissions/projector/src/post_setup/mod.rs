use crate::database::{manage::setup_database, model::Project};

pub mod editor;

pub fn run_post_setup(project: &mut Project) -> color_eyre::Result<()> {
    editor::run_editor_setup(std::path::Path::new(&project.path))?;

    // Add project to database
    project.insert(&setup_database()?)?;
    Ok(())
}
