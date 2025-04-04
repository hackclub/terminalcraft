use crate::AppResult;
use crossterm::event::{self, Event as CrosstermEvent, KeyEvent, KeyEventKind, MouseEvent};
use std::time::{Duration, Instant};
use std::collections::HashMap;
use std::env;

#[derive(Debug, Clone, Copy)]
pub enum Event {
    Tick,
    Key(KeyEvent),
    Mouse(MouseEvent),
    Resize(u16, u16),
}

#[derive(Debug, Clone, Copy)]
struct KeyState {
    last_press: Option<Instant>,
    last_release: Option<Instant>,
    is_held: bool,
}

impl Default for KeyState {
    fn default() -> Self {
        Self {
            last_press: None,
            last_release: None,
            is_held: false,
        }
    }
}

impl KeyState {
    // Temp function to determine if a key event should be processed
    fn should_process_key(&mut self, now: Instant, kind: KeyEventKind) -> bool {
        match kind {
            KeyEventKind::Press => {
                if let Some(last_press) = self.last_press {
                    // If last release is after last press -> new press
                    if let Some(last_release) = self.last_release {
                        if last_release > last_press {
                            self.is_held = false;
                            self.last_press = Some(now);
                            return true;
                        }
                    }

                    let elapsed = now.duration_since(last_press).as_millis();
                    
                    // stricter debounce
                    #[cfg(target_os = "windows")]
                    {
                        let shell = env::var("SHELL").unwrap_or_default();
                        if shell.contains("bash") || shell.contains("zsh") || shell.contains("fish") {
                            if elapsed < 60 && self.is_held {
                                return false;
                            }
                        } else if elapsed < 200 && self.is_held {
                            return false;
                        }
                    }

                    #[cfg(not(target_os = "windows"))]
                    if elapsed < 60 && self.is_held {
                        return false;
                    }
                }

                self.last_press = Some(now);
                self.is_held = true;
                true
            }
            KeyEventKind::Release => {
                self.last_release = Some(now);
                self.is_held = false;
                false
            }
            _ => false,
        }
    }
}

pub struct InputHandler {
    tick_rate: Duration,
    last_tick: Instant,
    key_states: HashMap<crossterm::event::KeyCode, KeyState>,
}

impl InputHandler {
    pub fn new(tick_rate: Duration) -> Self {
        Self {
            tick_rate,
            last_tick: Instant::now(),
            key_states: HashMap::new(),
        }
    }

    pub fn poll_event(&mut self) -> AppResult<Option<Event>> {
        let now = Instant::now();
        if now.duration_since(self.last_tick) >= self.tick_rate {
            self.last_tick = now;
            return Ok(Some(Event::Tick));
        }

        if event::poll(Duration::from_millis(1))? {
            match event::read()? {
                CrosstermEvent::Key(key) => {
                    let state = self.key_states.entry(key.code).or_default();
                    let should_process = state.should_process_key(now, key.kind);
                    
                    if should_process {
                        return Ok(Some(Event::Key(key)));
                    }
                    Ok(None)
                }
                CrosstermEvent::Mouse(e) => Ok(Some(Event::Mouse(e))),
                CrosstermEvent::Resize(w, h) => Ok(Some(Event::Resize(w, h))),
                _ => Ok(None),
            }
        } else {
            Ok(None)
        }
    }
}

#[cfg(target_arch = "wasm32")]
pub mod wasm {
    use super::*;
    use wasm_bindgen::{prelude::*, JsCast};
    use web_sys::{KeyboardEvent, MouseEvent as WebMouseEvent};

    pub struct WasmInputHandler {
        _keydown_listener: js_sys::Function,
        last_event: Option<Event>,
    }

    impl WasmInputHandler {
        pub fn new() -> Self {
            let document = web_sys::window().unwrap().document().unwrap();

            let keydown_callback = Closure::wrap(Box::new(move |event: KeyboardEvent| {
                let key_code = event.key();
            }) as Box<dyn FnMut(KeyboardEvent)>);

            document
                .add_event_listener_with_callback(
                    "keydown",
                    keydown_callback.as_ref().unchecked_ref(),
                )
                .unwrap();

            Self {
                _keydown_listener: keydown_callback.into_js_value().into(),
                last_event: None,
            }
        }

        pub fn poll_event(&mut self) -> Option<Event> {
            let event = self.last_event.take();
            self.last_event = None;
            event
        }
    }
}
