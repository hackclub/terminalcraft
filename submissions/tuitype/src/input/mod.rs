use crate::AppResult;
use crossterm::event::{self, Event as CrosstermEvent, KeyEvent, MouseEvent};
use std::time::{Duration, Instant};

#[derive(Debug, Clone, Copy)]
pub enum Event {
    Tick,

    Key(KeyEvent),

    Mouse(MouseEvent),

    Resize(u16, u16),
}

pub struct InputHandler {
    tick_rate: Duration,

    last_tick: Instant,
}

impl InputHandler {
    pub fn new(tick_rate: Duration) -> Self {
        Self {
            tick_rate,
            last_tick: Instant::now(),
        }
    }

    pub fn poll_event(&mut self) -> AppResult<Option<Event>> {
        let now = Instant::now();
        if now.duration_since(self.last_tick) >= self.tick_rate {
            self.last_tick = now;
            return Ok(Some(Event::Tick));
        }

        if event::poll(Duration::from_millis(0))? {
            match event::read()? {
                CrosstermEvent::Key(key) => {
                    return Ok(Some(Event::Key(key)));
                }
                CrosstermEvent::Mouse(e) => Ok(Some(Event::Mouse(e))),
                CrosstermEvent::Resize(w, h) => Ok(Some(Event::Resize(w, h))),
                _ => Ok(None),
            }
        } else {
            if event::poll(Duration::from_millis(5))? {
                match event::read()? {
                    CrosstermEvent::Key(key) => Ok(Some(Event::Key(key))),
                    CrosstermEvent::Mouse(e) => Ok(Some(Event::Mouse(e))),
                    CrosstermEvent::Resize(w, h) => Ok(Some(Event::Resize(w, h))),
                    _ => Ok(None),
                }
            } else {
                Ok(None)
            }
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
