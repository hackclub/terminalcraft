from flask import Flask, request, jsonify
from flask_socketio import SocketIO, join_room, emit
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

storage = {}
counters = {}
logs = {}
active_devices = {}
active_devices_by_session = {}

def purge_expired(passkey):
    now = time.time()
    if passkey in storage:
        storage[passkey] = [e for e in storage[passkey] if not e.get('expire_at') or e.get('expire_at') > now]

def add_log(passkey, event, device=None):
    logs.setdefault(passkey, [])
    logs[passkey].append({'event': event, 'timestamp': time.time(), 'device': device})

@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({'status': 'ok', 'timestamp': time.time(), 'version': 'bussy'}), 200

@app.route('/clipboard', methods=['POST'])
def add_clipboard():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Missing JSON payload'}), 400
    # Uncomment the next line for debugging:
    # print("DEBUG: Received POST /clipboard data:", data)
    passkey = data.get('passkey')
    text = data.get('text')
    if not passkey or not text:
        return jsonify({'error': 'Missing passkey or text'}), 400
    device = data.get('device', 'unknown')
    expire_in = data.get('expire_in')
    expire_at = time.time() + float(expire_in) if expire_in is not None else None
    counters[passkey] = counters.get(passkey, 0) + 1
    entry = {'id': counters[passkey], 'text': text, 'timestamp': time.time(), 'device': device}
    if expire_at:
        entry['expire_at'] = expire_at
    storage.setdefault(passkey, []).append(entry)
    add_log(passkey, 'add', device)
    socketio.emit('clipboard_update', entry, room=passkey)
    return jsonify({'success': True, 'entry': entry}), 200

@app.route('/clipboard', methods=['GET'])
def get_clipboard():
    passkey = request.args.get('passkey')
    limit = int(request.args.get('limit', 10))
    if not passkey:
        return jsonify({'error': 'Missing passkey'}), 400
    purge_expired(passkey)
    entries = storage.get(passkey, [])
    return jsonify({'entries': entries[-limit:]}), 200

@app.route('/clipboard/entry/<int:entry_id>', methods=['GET'])
def get_entry(entry_id):
    passkey = request.args.get('passkey')
    if not passkey:
        return jsonify({'error': 'Missing passkey'}), 400
    purge_expired(passkey)
    entries = storage.get(passkey, [])
    for entry in entries:
        if entry.get('id') == entry_id:
            return jsonify({'entry': entry}), 200
    return jsonify({'error': 'Entry not found'}), 404

@app.route('/clipboard/entry/<int:entry_id>', methods=['PUT'])
def update_entry(entry_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Missing JSON payload'}), 400
    passkey = data.get('passkey')
    new_text = data.get('text')
    if not passkey or not new_text:
        return jsonify({'error': 'Missing passkey or text'}), 400
    purge_expired(passkey)
    entries = storage.get(passkey, [])
    for entry in entries:
        if entry.get('id') == entry_id:
            entry['text'] = new_text
            entry['timestamp'] = time.time()
            if 'expire_at' in entry:
                expire_in = data.get('expire_in')
                if expire_in is not None:
                    entry['expire_at'] = time.time() + float(expire_in)
            add_log(passkey, 'update', data.get('device', 'unknown'))
            socketio.emit('clipboard_update', entry, room=passkey)
            return jsonify({'success': True, 'entry': entry}), 200
    return jsonify({'error': 'Entry not found'}), 404

@app.route('/clipboard', methods=['DELETE'])
def clear_clipboard():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'error': 'Missing JSON payload'}), 400
    passkey = data.get('passkey')
    if not passkey:
        return jsonify({'error': 'Missing passkey'}), 400
    storage[passkey] = []
    add_log(passkey, 'clear', data.get('device', 'unknown'))
    socketio.emit('clipboard_cleared', {}, room=passkey)
    return jsonify({'success': True}), 200

@app.route('/clipboard/device', methods=['GET'])
def get_device_entries():
    passkey = request.args.get('passkey')
    device = request.args.get('device')
    if not passkey or not device:
        return jsonify({'error': 'Missing passkey or device'}), 400
    purge_expired(passkey)
    entries = [entry for entry in storage.get(passkey, []) if entry.get('device') == device]
    return jsonify({'entries': entries}), 200

@app.route('/clipboard/stats', methods=['GET'])
def get_stats():
    passkey = request.args.get('passkey')
    if not passkey:
        return jsonify({'error': 'Missing passkey'}), 400
    purge_expired(passkey)
    entries = storage.get(passkey, [])
    stats = {
        'total_entries': len(entries),
        'active_devices': list(active_devices.get(passkey, []))
    }
    return jsonify({'stats': stats}), 200

@app.route('/clipboard/logs', methods=['GET'])
def get_logs():
    passkey = request.args.get('passkey')
    if not passkey:
        return jsonify({'error': 'Missing passkey'}), 400
    return jsonify({'logs': logs.get(passkey, [])}), 200

@socketio.on('join')
def on_join(data):
    try:
        passkey = data.get('passkey')
        device = data.get('device', 'unknown')
        if passkey:
            join_room(passkey)
            purge_expired(passkey)
            emit('clipboard_sync', storage.get(passkey, []))
            active_devices.setdefault(passkey, set()).add(device)
            active_devices_by_session[request.sid] = (passkey, device)
            add_log(passkey, 'join', device)
    except Exception as e:
        emit('error', {'error': str(e)})

@socketio.on('disconnect')
def on_disconnect():
    try:
        sid = request.sid
        if sid in active_devices_by_session:
            passkey, device = active_devices_by_session.pop(sid)
            if passkey in active_devices and device in active_devices[passkey]:
                active_devices[passkey].remove(device)
            add_log(passkey, 'disconnect', device)
    except Exception as e:
        pass

if __name__ == '__main__':
    socketio.run(app)
