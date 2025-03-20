use std::time::Duration;

pub fn format_duration(duration: Duration) -> String {
    let total_seconds = duration.as_secs();
    let minutes = total_seconds / 60;
    let seconds = total_seconds % 60;

    format!("{:02}:{:02}", minutes, seconds)
}

pub fn format_elapsed(start_time: std::time::Instant) -> String {
    format_duration(start_time.elapsed())
}

pub fn format_wpm(wpm: f64) -> String {
    format!("{:.1}", wpm)
}

pub fn calculate_percentage(part: usize, total: usize) -> f64 {
    if total == 0 {
        0.0
    } else {
        (part as f64 / total as f64) * 100.0
    }
}

pub fn truncate_text(text: &str, max_length: usize) -> String {
    if text.len() <= max_length {
        text.to_string()
    } else {
        let mut result = text.chars().take(max_length - 3).collect::<String>();
        result.push_str("...");
        result
    }
}

#[cfg(target_arch = "wasm32")]
pub mod wasm {
    use wasm_bindgen::prelude::*;

    #[wasm_bindgen]
    pub fn log(message: &str) {
        web_sys::console::log_1(&JsValue::from_str(message));
    }

    #[wasm_bindgen]
    pub fn get_timestamp() -> f64 {
        js_sys::Date::now()
    }
}
