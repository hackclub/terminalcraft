use rusqlite::{
    types::{FromSql, FromSqlError, ToSqlOutput, ValueRef},
    ToSql,
};

#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash)]
pub enum ProgrammingLanguage {
    Rust,
    Python,
    JavaScript,
    Java,
    C,
    CSharp,
    CPlusPlus,
    Go,
    Swift,
    Kotlin,
}

impl ProgrammingLanguage {
    pub fn all_langs() -> Vec<ProgrammingLanguage> {
        vec![
            ProgrammingLanguage::Rust,
            ProgrammingLanguage::Python,
            ProgrammingLanguage::JavaScript,
            ProgrammingLanguage::Java,
            ProgrammingLanguage::C,
            ProgrammingLanguage::CSharp,
            ProgrammingLanguage::CPlusPlus,
            ProgrammingLanguage::Go,
            ProgrammingLanguage::Swift,
            ProgrammingLanguage::Kotlin,
        ]
    }
}

impl ToSql for ProgrammingLanguage {
    fn to_sql(&self) -> rusqlite::Result<ToSqlOutput> {
        Ok(ToSqlOutput::from(match self {
            ProgrammingLanguage::Rust => "Rust",
            ProgrammingLanguage::Python => "Python",
            ProgrammingLanguage::JavaScript => "JavaScript",
            ProgrammingLanguage::Java => "Java",
            ProgrammingLanguage::C => "C",
            ProgrammingLanguage::CSharp => "CSharp",
            ProgrammingLanguage::CPlusPlus => "CPlusPlus",
            ProgrammingLanguage::Go => "Go",
            ProgrammingLanguage::Swift => "Swift",
            ProgrammingLanguage::Kotlin => "Kotlin",
        }))
    }
}

impl FromSql for ProgrammingLanguage {
    fn column_result(value: ValueRef) -> Result<Self, FromSqlError> {
        match value.as_str()? {
            "Rust" => Ok(ProgrammingLanguage::Rust),
            "Python" => Ok(ProgrammingLanguage::Python),
            "JavaScript" => Ok(ProgrammingLanguage::JavaScript),
            "Java" => Ok(ProgrammingLanguage::Java),
            "C" => Ok(ProgrammingLanguage::C),
            "CSharp" => Ok(ProgrammingLanguage::CSharp),
            "CPlusPlus" => Ok(ProgrammingLanguage::CPlusPlus),
            "Go" => Ok(ProgrammingLanguage::Go),
            "Swift" => Ok(ProgrammingLanguage::Swift),
            "Kotlin" => Ok(ProgrammingLanguage::Kotlin),
            other => Err(FromSqlError::Other(Box::<
                dyn std::error::Error + Send + Sync,
            >::from(format!(
                "Unknown language: {}",
                other
            )))),
        }
    }
}
