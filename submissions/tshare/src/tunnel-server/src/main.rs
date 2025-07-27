use anyhow::Result;
use axum::extract::ws::{Message, WebSocket};
use axum::extract::{Path, Query, State, WebSocketUpgrade};
use axum::http::StatusCode;
use axum::response::{IntoResponse, Response};
use axum::routing::{get, post};
use axum::{Json, Router};
use clap::Parser;
use dashmap::DashMap;
use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use tokio::sync::{RwLock, broadcast, mpsc};
use tracing::{error, info, warn};
use uuid::Uuid;

type SessionMap = Arc<DashMap<String, SessionState>>;

#[derive(Clone)]
struct SessionState {
    session_id: String,
    owner_password_hash: Option<String>,
    guest_password_hash: Option<String>,
    is_guest_readonly: bool,
    // Broadcast channel for PTY data going to web clients
    pty_broadcast: broadcast::Sender<Vec<u8>>,
    // Sender for web data going to PTY client
    web_to_pty_tx: Arc<RwLock<Option<mpsc::Sender<Vec<u8>>>>>,
    // Terminal history buffer
    history: Arc<RwLock<Vec<u8>>>,
}

#[derive(Clone)]
struct AppState {
    sessions: SessionMap,
}

#[derive(Deserialize)]
struct CreateSessionRequest {
    owner_password: Option<String>,
    guest_password: Option<String>,
    is_guest_readonly: bool,
}

#[derive(Serialize)]
struct CreateSessionResponse {
    session_id: String,
}

#[derive(Serialize)]
struct SessionDetails {
    session_id: String,
    owner_password_hash: Option<String>,
    guest_password_hash: Option<String>,
    is_guest_readonly: bool,
}

#[derive(Deserialize)]
struct WebSocketQuery {
    user_type: Option<String>,
}

#[derive(Parser, Debug)]
#[command(
    author,
    version,
    about = "TShare tunnel server - handles PTY data streams"
)]
struct Args {
    /// Host to bind the server to
    #[arg(long, default_value = "127.0.0.1")]
    host: String,

    /// Port for the server
    #[arg(long, default_value_t = 8385)]
    port: u16,
}

#[tokio::main]
async fn main() -> Result<()> {
    // Create ~/.tshare directory if it doesn't exist
    let home_dir = std::env::var("HOME").unwrap_or_else(|_| ".".to_string());
    let tshare_dir = format!("{home_dir}/.tshare");
    std::fs::create_dir_all(&tshare_dir)?;

    // Clear previous log file
    let log_path = format!("{tshare_dir}/tunnel-server.log");
    let _ = std::fs::remove_file(&log_path);

    // Configure logging to both console and file
    let log_file = std::fs::OpenOptions::new()
        .create(true)
        .write(true)
        .truncate(true)
        .open(&log_path)?;

    use tracing_subscriber::fmt::writer::MakeWriterExt;
    let writer = std::io::stdout.and(log_file);

    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| tracing_subscriber::EnvFilter::new("info")),
        )
        .with_writer(writer)
        .init();

    let args = Args::parse();

    let sessions: SessionMap = Arc::new(DashMap::new());
    let app_state = AppState { sessions };

    // Combined server with both API and WebSocket routes
    let app = Router::new()
        .route("/api/session", post(create_session))
        .route("/api/session/{id}", get(get_session))
        .route("/ws/pty/{id}", get(handle_pty_ws))
        .route("/ws/web/{id}", get(handle_web_ws))
        .with_state(app_state);

    let addr = format!("{}:{}", args.host, args.port);
    let listener = tokio::net::TcpListener::bind(&addr).await?;

    info!("Tunnel server starting");
    info!("Server listening on {} (API and WebSocket)", addr);

    if let Err(e) = axum::serve(listener, app).await {
        error!("Server error: {:?}", e);
    }

    Ok(())
}

async fn create_session(
    State(state): State<AppState>,
    Json(request): Json<CreateSessionRequest>,
) -> Result<Json<CreateSessionResponse>, StatusCode> {
    let session_id = Uuid::new_v4().to_string();

    info!("Creating new session: {}", session_id);
    info!(
        "Session config - readonly: {}, has_owner_pass: {}, has_guest_pass: {}",
        request.is_guest_readonly,
        request.owner_password.is_some(),
        request.guest_password.is_some()
    );

    let owner_password_hash = match request.owner_password {
        Some(password) => {
            let hash = bcrypt::hash(password, bcrypt::DEFAULT_COST).map_err(|e| {
                error!(
                    "Failed to hash owner password for session {}: {}",
                    session_id, e
                );
                StatusCode::INTERNAL_SERVER_ERROR
            })?;
            Some(hash)
        }
        None => None,
    };

    let guest_password_hash = match request.guest_password {
        Some(password) => {
            let hash = bcrypt::hash(password, bcrypt::DEFAULT_COST).map_err(|e| {
                error!(
                    "Failed to hash guest password for session {}: {}",
                    session_id, e
                );
                StatusCode::INTERNAL_SERVER_ERROR
            })?;
            Some(hash)
        }
        None => None,
    };

    let (pty_broadcast, _) = broadcast::channel(1024);
    let web_to_pty_tx = Arc::new(RwLock::new(None));
    let history = Arc::new(RwLock::new(Vec::new()));

    let session = SessionState {
        session_id: session_id.clone(),
        owner_password_hash,
        guest_password_hash,
        is_guest_readonly: request.is_guest_readonly,
        pty_broadcast,
        web_to_pty_tx,
        history,
    };

    state.sessions.insert(session_id.clone(), session);

    info!(
        "Successfully created session: {} (total sessions: {})",
        session_id,
        state.sessions.len()
    );

    Ok(Json(CreateSessionResponse { session_id }))
}

async fn get_session(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
) -> Result<Json<SessionDetails>, StatusCode> {
    info!("Looking up session: {}", session_id);

    let session = state.sessions.get(&session_id).ok_or_else(|| {
        warn!("Session not found: {}", session_id);
        StatusCode::NOT_FOUND
    })?;

    let details = SessionDetails {
        session_id: session.session_id.clone(),
        owner_password_hash: session.owner_password_hash.clone(),
        guest_password_hash: session.guest_password_hash.clone(),
        is_guest_readonly: session.is_guest_readonly,
    };

    info!("Retrieved session details for: {}", session_id);
    Ok(Json(details))
}

async fn handle_pty_ws(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
    ws: WebSocketUpgrade,
) -> Response {
    let session = match state.sessions.get(&session_id) {
        Some(session_ref) => session_ref.clone(),
        None => return StatusCode::NOT_FOUND.into_response(),
    };

    ws.on_upgrade(move |socket| handle_pty_websocket(socket, session))
}

async fn handle_web_ws(
    State(state): State<AppState>,
    Path(session_id): Path<String>,
    Query(query): Query<WebSocketQuery>,
    ws: WebSocketUpgrade,
) -> Response {
    let session = match state.sessions.get(&session_id) {
        Some(session_ref) => session_ref.clone(),
        None => return StatusCode::NOT_FOUND.into_response(),
    };

    let user_type = query.user_type.unwrap_or_else(|| "guest".to_string());
    ws.on_upgrade(move |socket| handle_web_websocket(socket, session, user_type))
}

async fn handle_pty_websocket(socket: WebSocket, session: SessionState) {
    let (mut ws_sender, mut ws_receiver) = socket.split();
    let session_id = session.session_id.clone();

    info!("PTY WebSocket connected for session: {}", session_id);

    // Create channel for receiving web-to-pty data
    let (web_to_pty_tx, mut web_to_pty_rx) = mpsc::channel(1024);

    // Store the sender in the session
    {
        let mut tx_guard = session.web_to_pty_tx.write().await;
        *tx_guard = Some(web_to_pty_tx);
        info!("Stored web-to-pty channel for session: {}", session_id);
    }

    // Task to forward PTY data to web clients via broadcast
    let pty_broadcast = session.pty_broadcast.clone();
    let history = session.history.clone();
    let session_id_clone = session_id.clone();
    let forward_pty_to_web = tokio::spawn(async move {
        info!(
            "Starting PTY-to-web forwarding for session: {}",
            session_id_clone
        );
        let mut session_ended_sent = false;
        while let Some(msg) = ws_receiver.next().await {
            match msg {
                Ok(Message::Binary(data)) => {
                    // Store in history
                    {
                        let mut history_guard = history.write().await;
                        history_guard.extend_from_slice(&data);
                    }

                    let subscribers = pty_broadcast.receiver_count();
                    let result = pty_broadcast.send(data.to_vec());
                    if result.is_ok() && subscribers > 0 {
                        info!(
                            "Forwarded {} bytes to {} web clients for session: {}",
                            data.len(),
                            subscribers,
                            session_id_clone
                        );
                    }
                }
                Ok(Message::Close(_)) => {
                    info!(
                        "PTY WebSocket close message received for session: {}",
                        session_id_clone
                    );
                    if !session_ended_sent {
                        let _ = pty_broadcast.send(b"__TSHARE_SESSION_ENDED__".to_vec());
                        session_ended_sent = true;
                    }
                    break;
                }
                Err(e) => {
                    warn!(
                        "PTY WebSocket error for session {}: {}",
                        session_id_clone, e
                    );
                    if !session_ended_sent {
                        let _ = pty_broadcast.send(b"__TSHARE_SESSION_ENDED__".to_vec());
                        session_ended_sent = true;
                    }
                    break;
                }
                _ => {}
            }
        }
        info!(
            "PTY-to-web forwarding ended for session: {}",
            session_id_clone
        );
        // Send session end notification only if not already sent
        if !session_ended_sent {
            let _ = pty_broadcast.send(b"__TSHARE_SESSION_ENDED__".to_vec());
        }
    });

    // Task to forward web data to PTY
    let session_id_clone = session_id.clone();
    let forward_web_to_pty = tokio::spawn(async move {
        info!(
            "Starting web-to-PTY forwarding for session: {}",
            session_id_clone
        );
        while let Some(data) = web_to_pty_rx.recv().await {
            info!(
                "Forwarding {} bytes from web to PTY for session: {}",
                data.len(),
                session_id_clone
            );
            if ws_sender.send(Message::Binary(data.into())).await.is_err() {
                warn!(
                    "Failed to send data to PTY for session: {}",
                    session_id_clone
                );
                break;
            }
        }
        info!(
            "Web-to-PTY forwarding ended for session: {}",
            session_id_clone
        );
    });

    tokio::select! {
        _ = forward_pty_to_web => {},
        _ = forward_web_to_pty => {},
    }

    // Clear the sender when PTY disconnects
    {
        let mut tx_guard = session.web_to_pty_tx.write().await;
        *tx_guard = None;
        info!("Cleared web-to-pty channel for session: {}", session_id);
    }

    info!("PTY WebSocket disconnected for session: {}", session_id);
}

async fn handle_web_websocket(socket: WebSocket, session: SessionState, user_type: String) {
    let (mut ws_sender, mut ws_receiver) = socket.split();
    let session_id = session.session_id.clone();

    // Determine readonly status based on user type and session settings
    // Authentication logic:
    // - If no passwords set: auto-authenticate as owner (full access)
    // - If owner_pass provided and matches: authenticate as owner (full access)
    // - If guest_pass provided and matches: authenticate as guest (follows is_guest_readonly setting)
    // - Owners always have read/write access regardless of is_guest_readonly
    // - Guests have read/write access only if is_guest_readonly is false
    let is_readonly = match user_type.as_str() {
        "owner" => false,                     // Owners always have write access
        "guest" => session.is_guest_readonly, // Guests follow session readonly setting
        _ => true,                            // Default to readonly for unknown user types
    };

    info!(
        "Web WebSocket connected for session: {} (user_type: {}, readonly: {})",
        session_id, user_type, is_readonly
    );

    // Send history to new web client first
    let history_data = {
        let history_guard = session.history.read().await;
        history_guard.clone()
    };

    if !history_data.is_empty() {
        info!(
            "Sending {} bytes of history to new web client for session: {}",
            history_data.len(),
            session_id
        );
        if ws_sender
            .send(Message::Binary(history_data.into()))
            .await
            .is_err()
        {
            warn!(
                "Failed to send history to web client for session: {}",
                session_id
            );
            return;
        }
    }

    // Subscribe to PTY broadcast
    let mut pty_broadcast_rx = session.pty_broadcast.subscribe();
    let web_to_pty_tx_ref = session.web_to_pty_tx.clone();

    // Task to forward PTY data to web client
    let session_id_clone = session_id.clone();
    let forward_pty_to_web = tokio::spawn(async move {
        info!(
            "Starting PTY-to-web forwarding for web client of session: {}",
            session_id_clone
        );
        while let Ok(data) = pty_broadcast_rx.recv().await {
            info!(
                "Sending {} bytes to web client for session: {}",
                data.len(),
                session_id_clone
            );
            if ws_sender.send(Message::Binary(data.into())).await.is_err() {
                warn!(
                    "Failed to send data to web client for session: {}",
                    session_id_clone
                );
                break;
            }
        }
        info!(
            "PTY-to-web forwarding ended for web client of session: {}",
            session_id_clone
        );
    });

    // Task to forward web data to PTY (if not readonly)
    let session_id_clone = session_id.clone();
    let forward_web_to_pty = tokio::spawn(async move {
        info!(
            "Starting web-to-PTY forwarding for session: {} (readonly: {})",
            session_id_clone, is_readonly
        );
        while let Some(msg) = ws_receiver.next().await {
            match msg {
                Ok(Message::Binary(data)) => {
                    if !is_readonly {
                        info!(
                            "Received {} bytes from web client for session: {}",
                            data.len(),
                            session_id_clone
                        );
                        let tx_guard = web_to_pty_tx_ref.read().await;
                        if let Some(web_to_pty_tx) = tx_guard.as_ref() {
                            if web_to_pty_tx.send(data.to_vec()).await.is_err() {
                                warn!(
                                    "Failed to forward web data to PTY for session: {}",
                                    session_id_clone
                                );
                                break;
                            }
                        } else {
                            warn!(
                                "No PTY connection available for session: {}",
                                session_id_clone
                            );
                        }
                    } else {
                        info!(
                            "Ignoring input from web client (readonly mode) for session: {}",
                            session_id_clone
                        );
                    }
                }
                Ok(Message::Text(text)) => {
                    // Handle control messages like resize
                    if let Ok(msg) = serde_json::from_str::<serde_json::Value>(&text) {
                        if msg.get("type").and_then(|v| v.as_str()) == Some("resize") {
                            if let (Some(cols), Some(rows)) = (
                                msg.get("cols").and_then(|v| v.as_u64()),
                                msg.get("rows").and_then(|v| v.as_u64()),
                            ) {
                                info!(
                                    "Received resize request: {}x{} for session: {}",
                                    cols, rows, session_id_clone
                                );
                                // Forward resize message to PTY client
                                let tx_guard = web_to_pty_tx_ref.read().await;
                                if let Some(web_to_pty_tx) = tx_guard.as_ref() {
                                    let resize_msg = format!("RESIZE:{cols}:{rows}");
                                    if web_to_pty_tx.send(resize_msg.into_bytes()).await.is_err() {
                                        warn!(
                                            "Failed to send resize command to PTY for session: {}",
                                            session_id_clone
                                        );
                                    }
                                }
                            }
                        }
                    }
                }
                Ok(Message::Close(_)) => {
                    info!(
                        "Web WebSocket close message received for session: {}",
                        session_id_clone
                    );
                    break;
                }
                Err(e) => {
                    warn!(
                        "Web WebSocket error for session {}: {}",
                        session_id_clone, e
                    );
                    break;
                }
                _ => {}
            }
        }
        info!(
            "Web-to-PTY forwarding ended for session: {}",
            session_id_clone
        );
    });

    tokio::select! {
        _ = forward_pty_to_web => {},
        _ = forward_web_to_pty => {},
    }

    info!("Web WebSocket disconnected for session: {}", session_id);
}
