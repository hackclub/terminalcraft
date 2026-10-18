#!/usr/bin/env python3
import json, sqlite3, os, sys, time, datetime as dt, subprocess as sp, threading, signal, platform, argparse
from pathlib import Path
from collections import defaultdict, deque
from contextlib import contextmanager
import hashlib, re, glob, shutil, atexit
import psutil, requests

class Activity:
    def __init__(self, type_, content, timestamp=None, duration=0, meta=None, window_title=None, url=None):
        self.type = type_
        self.content = content
        self.timestamp = timestamp or dt.datetime.now().isoformat()
        self.duration = duration
        self.meta = meta or {}
        self.window_title = window_title  # Store full window title
        self.url = url  # Store extracted URL if available
        self.hash = hash(f"{type_}:{content}:{timestamp}:{window_title}")

class DatabaseManager:
    def __init__(self, db_path):
        self.db = sqlite3.connect(db_path, check_same_thread=False)
        self.init_schema()
    
    def init_schema(self):
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS activities (
                id INTEGER PRIMARY KEY,
                timestamp REAL,
                type TEXT,
                content TEXT,
                duration INTEGER DEFAULT 0,
                meta TEXT,
                date TEXT,
                hash INTEGER UNIQUE,
                app_version TEXT,
                session_id TEXT,
                window_title TEXT,
                url TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_date_type ON activities(date, type);
            CREATE INDEX IF NOT EXISTS idx_timestamp ON activities(timestamp);
            CREATE INDEX IF NOT EXISTS idx_session ON activities(session_id);
            CREATE INDEX IF NOT EXISTS idx_content ON activities(content);
            CREATE INDEX IF NOT EXISTS idx_window_title ON activities(window_title);
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time REAL,
                end_time REAL,
                total_activities INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS app_stats (
                name TEXT PRIMARY KEY,
                total_time INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                last_used REAL
            );
            CREATE TABLE IF NOT EXISTS app_details (
                id INTEGER PRIMARY KEY,
                app_name TEXT,
                window_title TEXT,
                url TEXT,
                timestamp REAL,
                duration INTEGER DEFAULT 0,
                session_id TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_app_details_app ON app_details(app_name);
            CREATE INDEX IF NOT EXISTS idx_app_details_timestamp ON app_details(timestamp);
        """)
        self.db.commit()
    
    def insert_activity(self, activity, session_id):
        try:
            self.db.execute("""
                INSERT OR IGNORE INTO activities 
                (timestamp, type, content, duration, meta, date, hash, session_id, window_title, url) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dt.datetime.fromisoformat(activity.timestamp).timestamp(),
                activity.type, activity.content, activity.duration,
                json.dumps(activity.meta), 
                dt.datetime.fromisoformat(activity.timestamp).date().isoformat(),
                activity.hash, session_id, activity.window_title, activity.url
            ))
            
            # Also insert into app_details for detailed tracking
            if activity.type == "app" and activity.window_title:
                self.db.execute("""
                    INSERT INTO app_details 
                    (app_name, window_title, url, timestamp, duration, session_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    activity.content, activity.window_title, activity.url,
                    dt.datetime.fromisoformat(activity.timestamp).timestamp(),
                    activity.duration, session_id
                ))
            
            if activity.type == "app":
                self.update_app_stats(activity.content, activity.duration)
            self.db.commit()
            return True
        except Exception as e:
            print(f"Database error: {e}")  # Debug
            return False
    
    def update_app_stats(self, app_name, duration):
        self.db.execute("""
            INSERT OR REPLACE INTO app_stats (name, total_time, usage_count, last_used)
            VALUES (?, 
                COALESCE((SELECT total_time FROM app_stats WHERE name = ?), 0) + ?,
                COALESCE((SELECT usage_count FROM app_stats WHERE name = ?), 0) + 1,
                ?)
        """, (app_name, app_name, duration, app_name, time.time()))
    
    def get_activities(self, date_range=None, activity_type=None):
        query = "SELECT timestamp, type, content, duration, meta, window_title, url FROM activities"
        params, conditions = [], []
        
        if date_range:
            if isinstance(date_range, str):
                conditions.append("date = ?")
                params.append(date_range)
            elif isinstance(date_range, tuple) and len(date_range) == 2:
                conditions.append("date >= ? AND date <= ?")
                params.extend(date_range)
        
        if activity_type:
            conditions.append("type = ?")
            params.append(activity_type)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC"
        
        if not date_range:
            query += " LIMIT 100"
        
        return self.db.execute(query, params).fetchall()
    
    def get_app_details(self, app_name, date_range=None, limit=50):
        """Get detailed information for a specific app"""
        query = """
            SELECT timestamp, window_title, url, duration 
            FROM app_details 
            WHERE app_name = ?
        """
        params = [app_name]
        
        if date_range:
            if isinstance(date_range, str):
                # Single date
                start_ts = dt.datetime.strptime(date_range, '%Y-%m-%d').timestamp()
                end_ts = start_ts + 86400  # Add 24 hours
                query += " AND timestamp >= ? AND timestamp < ?"
                params.extend([start_ts, end_ts])
            elif isinstance(date_range, tuple) and len(date_range) == 2:
                # Date range
                start_ts = dt.datetime.strptime(date_range[0], '%Y-%m-%d').timestamp()
                end_ts = dt.datetime.strptime(date_range[1], '%Y-%m-%d').timestamp() + 86400
                query += " AND timestamp >= ? AND timestamp < ?"
                params.extend([start_ts, end_ts])
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        return self.db.execute(query, params).fetchall()
    
    def get_app_stats(self, limit=10):
        return self.db.execute("""
            SELECT name, total_time, usage_count, last_used 
            FROM app_stats 
            ORDER BY total_time DESC 
            LIMIT ?
        """, (limit,)).fetchall()
    
    def cleanup_old_data(self, days=30):
        cutoff = (dt.datetime.now() - dt.timedelta(days=days)).isoformat()
        self.db.execute("DELETE FROM activities WHERE date < ?", (cutoff,))
        self.db.execute("DELETE FROM app_details WHERE timestamp < ?", 
                       (dt.datetime.fromisoformat(cutoff).timestamp(),))
        self.db.commit()
    
    def close(self):
        self.db.close()

class SystemTracker:
    def __init__(self, os_type):
        self.os_type = os_type
        self.process_cache = {}
        self.window_history = deque(maxlen=50)
    
    def get_active_window_details(self):
        """Get both app name and full window title with URL extraction"""
        window_title = None
        
        if self.os_type == "darwin":
            window_title = self._cmd(['osascript', '-e', 
                'tell app "System Events" to return name of first application process whose frontmost is true'])
            # Try to get window title for macOS
            full_title = self._cmd(['osascript', '-e', 
                'tell app "System Events" to return title of front window of first application process whose frontmost is true'])
            if full_title and full_title != window_title:
                window_title = full_title
                
        elif self.os_type == "linux":
            methods = [
                lambda: self._get_x11_window_details(),
                lambda: (self._cmd(['xdotool', 'getwindowfocus', 'getwindowname']), None),
                lambda: (os.environ.get('DESKTOP_SESSION', 'Unknown'), None)
            ]
            for method in methods:
                try:
                    result = method()
                    if result and result[0]: 
                        window_title = result[0]
                        break
                except: continue
                
        elif self.os_type == "windows":
            window_title = self._get_windows_window_details()
        
        if not window_title:
            return None, None, None
        
        # Extract app name and URL
        app_name = self.clean_app_name(window_title)
        url = self.extract_url(window_title, app_name)
        
        return app_name, window_title, url
    
    def _get_x11_window_details(self):
        """Get detailed window information for X11"""
        try:
            active_id = self._cmd(['xprop', '-root', '_NET_ACTIVE_WINDOW'])
            if active_id and 'window id' in active_id:
                window_id = active_id.split()[-1]
                name = self._cmd(['xprop', '-id', window_id, 'WM_NAME'])
                if name and '"' in name:
                    title = name.split('"')[1]
                    return title
        except: pass
        return None
    
    def _get_windows_window_details(self):
        """Get detailed window information for Windows"""
        try:
            import ctypes
            user32 = ctypes.windll.user32
            hwnd = user32.GetForegroundWindow()
            length = user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                user32.GetWindowTextW(hwnd, buf, length + 1)
                return buf.value
        except: pass
        return None
    
    def get_active_window(self):
        """Legacy method for compatibility"""
        app_name, window_title, url = self.get_active_window_details()
        return window_title or app_name
    
    def _cmd(self, cmd):
        try:
            return sp.run(cmd, capture_output=True, text=True, timeout=2).stdout.strip()
        except:
            return None
    
    def extract_url(self, window_title, app_name):
        """Extract URL from window title based on the application"""
        if not window_title or not app_name:
            return None
        
        app_lower = app_name.lower()
        title_lower = window_title.lower()
        
        # Browser URL extraction patterns
        browser_patterns = {
            'chrome': [
                r'https?://[^\s]+',
                r'(https?://[^/]+)',  # Just domain
                r'([^/]+\.[a-z]{2,})',  # Domain without protocol
            ],
            'firefox': [
                r'https?://[^\s]+',
                r'— Mozilla Firefox.*?(https?://[^\s]+)',
                r'([^/]+\.[a-z]{2,})',
            ],
            'edge': [
                r'https?://[^\s]+',
                r'Microsoft Edge.*?(https?://[^\s]+)',
                r'([^/]+\.[a-z]{2,})',
            ],
            'safari': [
                r'https?://[^\s]+',
                r'([^/]+\.[a-z]{2,})',
            ]
        }
        
        # Check if it's a browser
        for browser in browser_patterns:
            if browser in app_lower:
                for pattern in browser_patterns[browser]:
                    match = re.search(pattern, window_title, re.IGNORECASE)
                    if match:
                        url = match.group(1) if match.groups() else match.group(0)
                        # Clean up URL
                        if not url.startswith(('http://', 'https://')):
                            if '.' in url and not url.startswith('www.'):
                                url = 'https://' + url
                        return url
        
        # Extract file paths for editors/IDEs
        if any(keyword in app_lower for keyword in ['code', 'editor', 'notepad', 'vim', 'emacs']):
            # Look for file paths
            file_patterns = [
                r'([A-Z]:\\[^|<>:"*?\r\n]+)',  # Windows paths
                r'(/[^|<>:"*?\r\n]+\.[a-zA-Z0-9]+)',  # Unix paths with extension
                r'(~/[^|<>:"*?\r\n]+)',  # Home directory paths
            ]
            for pattern in file_patterns:
                match = re.search(pattern, window_title)
                if match:
                    return match.group(1)
        
        # Extract document names for Office apps
        if any(keyword in app_lower for keyword in ['word', 'excel', 'powerpoint', 'libreoffice']):
            # Look for document names (usually before app name)
            doc_patterns = [
                r'^([^-]+?)\s*[-–]\s*Microsoft',
                r'^([^-]+?)\s*[-–]\s*LibreOffice',
                r'([^\\/:*?"<>|]+\.[a-zA-Z0-9]+)',  # Filename with extension
            ]
            for pattern in doc_patterns:
                match = re.search(pattern, window_title)
                if match:
                    return match.group(1).strip()
        
        return None
    
    def clean_app_name(self, window_title):
        if not window_title:
            return None
            
        app_mappings = {
            'powershell': 'PowerShell',
            'cmd': 'Command Prompt',
            'notepad++': 'Notepad++',
            'chrome': 'Google Chrome',
            'firefox': 'Firefox',
            'edge': 'Microsoft Edge',
            'code': 'VS Code',
            'explorer': 'File Explorer',
            'discord': 'Discord',
            'spotify': 'Spotify',
            'vlc': 'VLC Media Player',
            'excel': 'Microsoft Excel',
            'word': 'Microsoft Word',
            'powerpoint': 'Microsoft PowerPoint',
            'teams': 'Microsoft Teams',
            'slack': 'Slack',
            'zoom': 'Zoom',
            'steam': 'Steam',
            'git': 'Git Bash'
        }
        
        title_lower = window_title.lower()
        
        for key, clean_name in app_mappings.items():
            if key in title_lower:
                return clean_name
        
        if 'windows powershell' in title_lower or 'powershell' in title_lower:
            return 'PowerShell'
            
        if 'administrator:' in title_lower:
            clean_title = window_title.split('Administrator: ', 1)[-1]
            return self.clean_app_name(clean_title)
        
        patterns = [
            r'^(.+?) - ',
            r' - (.+?)$',
            r'^(.+?) \(',
            r'^([^-]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, window_title)
            if match:
                app_name = match.group(1).strip()
                if len(app_name) > 2 and not any(char in app_name for char in ['\\', '/', ':', '|']):
                    return app_name
        
        cleaned = re.sub(r'[\\/:*?"<>|].*', '', window_title).strip()
        return cleaned if len(cleaned) > 2 else None

class AIAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1/chat/completions"
        
    def analyze_activities(self, activities, system_info=None):
        if not activities:
            return "No activities to analyze"
        
        summary = self._prepare_summary(activities, system_info)
        
        if not self.api_key:
            return self._local_analysis(summary)
        
        try:
            return self._openai_analysis(summary)
        except:
            return self._local_analysis(summary)
    
    def _prepare_summary(self, activities, system_info):
        apps, hourly = defaultdict(int), defaultdict(int)
        total_time = 0
        
        for row in activities:
            timestamp, type_, content, duration = row[:4]
            try:
                hour = dt.datetime.fromtimestamp(timestamp).hour
                hourly[hour] += 1
            except: pass
            
            if type_ == "app":
                apps[content] += duration
                total_time += duration
        
        return {
            'total_activities': len(activities),
            'total_time': total_time,
            'apps': dict(sorted(apps.items(), key=lambda x: x[1], reverse=True)[:5]),
            'peak_hours': dict(sorted(hourly.items(), key=lambda x: x[1], reverse=True)[:3]),
            'system_info': system_info or {}
        }
    
    def _openai_analysis(self, summary):
        prompt = f"""Analyze this productivity data:
        
Activities: {summary['total_activities']}
Active time: {summary['total_time']//3600}h {(summary['total_time']%3600)//60}m
Top apps: {summary['apps']}
Peak hours: {summary['peak_hours']}

Provide concise insights on productivity patterns, focus areas, and recommendations."""
        
        response = requests.post(self.base_url, 
            json={
                "model": "gpt-4o-mini",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 300,
                "temperature": 0.7
            },
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=15
        )
        
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            raise Exception(f"API error: {response.status_code}")
    
    def _local_analysis(self, summary):
        insights = []
        
        if summary['total_time'] > 0:
            avg_session = summary['total_time'] / len(summary['apps']) if summary['apps'] else 0
            insights.append(f"Average app session: {avg_session//60:.0f} minutes")
        
        if summary['peak_hours']:
            peak_hour = max(summary['peak_hours'].items(), key=lambda x: x[1])
            hour_12 = dt.datetime.strptime(f"{peak_hour[0]:02d}:00", "%H:%M").strftime("%I:%M %p")
            insights.append(f"Most active at {hour_12} ({peak_hour[1]} activities)")
        
        top_app = max(summary['apps'].items(), key=lambda x: x[1]) if summary['apps'] else None
        if top_app:
            insights.append(f"Primary focus: {top_app[0]} ({top_app[1]//60} minutes)")
        
        return "📊 Analysis:\n" + "\n".join(f"• {insight}" for insight in insights)

class DaemonManager:
    def __init__(self, pidfile):
        self.pidfile = pidfile
    
    def daemonize(self):
        """Fork the process to run as daemon"""
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit parent
        except OSError as e:
            sys.stderr.write(f"Fork #1 failed: {e}\n")
            sys.exit(1)
        
        os.chdir("/")
        os.setsid()
        os.umask(0)
        
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)  # Exit second parent
        except OSError as e:
            sys.stderr.write(f"Fork #2 failed: {e}\n")
            sys.exit(1)
        
        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())
        
        # Write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(f"{pid}\n")
    
    def delpid(self):
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)
    
    def start_daemon(self, target_func):
        """Start daemon"""
        if self.is_running():
            print("Daemon already running")
            return False
        
        if platform.system().lower() == "windows":
            # Windows doesn't support fork, run directly
            target_func()
        else:
            self.daemonize()
            target_func()
        return True
    
    def stop_daemon(self):
        """Stop daemon"""
        if not os.path.exists(self.pidfile):
            print("Daemon not running")
            return False
        
        with open(self.pidfile) as f:
            pid = int(f.read().strip())
        
        try:
            while True:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
        except OSError:
            self.delpid()
            print("Daemon stopped")
            return True
    
    def is_running(self):
        """Check if daemon is running"""
        if not os.path.exists(self.pidfile):
            return False
        
        with open(self.pidfile) as f:
            try:
                pid = int(f.read().strip())
                os.kill(pid, 0)  # Check if process exists
                return True
            except (ValueError, OSError):
                self.delpid()
                return False

class TraceShell:
    def __init__(self):
        self.home = Path.home() / ".traceshell"
        self.home.mkdir(exist_ok=True)
        
        self.pidfile = self.home / "daemon.pid"
        self.daemon = DaemonManager(str(self.pidfile))
        
        self.db_manager = DatabaseManager(self.home / "trace.db")
        self.system_tracker = SystemTracker(platform.system().lower())
        self.ai_analyzer = AIAnalyzer(os.getenv("OPENAI_API_KEY", ""))
        
        self.tracking = threading.Event()
        self.buffer = deque(maxlen=500)
        self.session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        
        self.cfg = self._load_config()
    
    def _load_config(self):
        cfg_file = self.home / "config.json"
        defaults = {
            "tracking": {"apps": True, "interval": 2, "min_duration": 5, "detailed": True},
            "ai": {"enabled": bool(os.getenv("OPENAI_API_KEY"))},
            "privacy": {"retention_days": 30},
            "performance": {"buffer_size": 500, "batch_size": 10}
        }
        
        if cfg_file.exists():
            try:
                with open(cfg_file) as f:
                    saved = json.load(f)
                    for key, value in saved.items():
                        if key in defaults:
                            if isinstance(value, dict) and isinstance(defaults[key], dict):
                                defaults[key].update(value)
                            else:
                                defaults[key] = value
            except: pass
        
        with open(cfg_file, 'w') as f:
            json.dump(defaults, f, indent=2)
        
        return defaults
    
    def _create_session(self):
        self.db_manager.db.execute("""
            INSERT OR REPLACE INTO sessions (id, start_time, total_activities)
            VALUES (?, ?, 0)
        """, (self.session_id, time.time()))
        self.db_manager.db.commit()
    
    def _get_date_range(self, period):
        today = dt.date.today()
        
        if period == "today":
            return today.isoformat()
        elif period == "yesterday":
            yesterday = today - dt.timedelta(days=1)
            return yesterday.isoformat()
        elif period == "week":
            week_ago = today - dt.timedelta(days=7)
            return (week_ago.isoformat(), today.isoformat())
        else:
            return None
    
    def log_activity(self, activity_type, content, duration=0, meta=None, window_title=None, url=None):
        activity = Activity(activity_type, content, None, duration, meta, window_title, url)
        self.buffer.append(activity)
        
        if len(self.buffer) >= self.cfg["performance"]["batch_size"]:
            self._flush_buffer()
    
    def _flush_buffer(self):
        if not self.buffer: return
        
        activities = list(self.buffer)
        self.buffer.clear()
        
        for activity in activities:
            self.db_manager.insert_activity(activity, self.session_id)
        
        self.db_manager.db.execute("""
            UPDATE sessions 
            SET total_activities = total_activities + ?, end_time = ?
            WHERE id = ?
        """, (len(activities), time.time(), self.session_id))
        self.db_manager.db.commit()
    
    def _tracking_loop(self):
        """Main tracking loop that runs in daemon"""
        state = {
            'current_app': None,
            'current_title': None,
            'current_url': None,
            'window_start': None
        }
        
        self._create_session()
        
        def cleanup_handler(signum, frame):
            if state['current_app'] and state['window_start']:
                duration = int(time.time() - state['window_start'])
                if duration >= self.cfg["tracking"]["min_duration"]:
                    self.log_activity("app", state['current_app'], duration, 
                                    window_title=state['current_title'], url=state['current_url'])
            self._flush_buffer()
            self.db_manager.close()
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, cleanup_handler)
        signal.signal(signal.SIGINT, cleanup_handler)
        
        while True:
            try:
                now = time.time()
                
                # Get detailed window information
                app_name, window_title, url = self.system_tracker.get_active_window_details()
                
                # Check if anything changed
                changed = (app_name != state['current_app'] or 
                          window_title != state['current_title'] or
                          url != state['current_url'])
                
                if app_name and changed:
                    # Log previous activity if it existed
                    if state['current_app'] and state['window_start']:
                        duration = int(now - state['window_start'])
                        if duration >= self.cfg["tracking"]["min_duration"]:
                            self.log_activity("app", state['current_app'], duration,
                                            window_title=state['current_title'], url=state['current_url'])
                    
                    # Start tracking new activity
                    state['current_app'] = app_name
                    state['current_title'] = window_title
                    state['current_url'] = url
                    state['window_start'] = now
                
                time.sleep(self.cfg["tracking"]["interval"])
                
            except Exception as e:
                time.sleep(5)
    
    def start_daemon(self):
        """Start daemon in background"""
        if self.daemon.is_running():
            print("🔄 TraceShell daemon already running")
            return
        
        print("🚀 Starting TraceShell daemon...")
        success = self.daemon.start_daemon(self._tracking_loop)
        if success:
            time.sleep(1)  # Give daemon time to start
            if self.daemon.is_running():
                print("✅ TraceShell daemon started successfully")
                print("📱 Tracking applications with detailed window information")
                print("💡 Use 'traceshell status' to check status")
            else:
                print("❌ Failed to start daemon")
    
    def stop_daemon(self):
        """Stop background daemon"""
        if not self.daemon.is_running():
            print("⏹️ TraceShell daemon not running")
            return
        
        print("🛑 Stopping TraceShell daemon...")
        if self.daemon.stop_daemon():
            print("✅ TraceShell daemon stopped")
        else:
            print("❌ Failed to stop daemon")
    
    def detail(self, app_name, date=None, period=None, limit=50):
        """Show detailed information for a specific application"""
        if period:
            date_range = self._get_date_range(period)
        elif date:
            date_range = date
        else:
            date_range = None
        
        # Get detailed app information
        details = self.db_manager.get_app_details(app_name, date_range, limit)
        
        if not details:
            period_str = f" for {period}" if period else (f" for {date}" if date else "")
            return print(f"📭 No detailed information found for '{app_name}'{period_str}")
        
        # Create title
        if period == "today":
            title = f"🔍 Today's Details for {app_name}"
        elif period == "yesterday":
            title = f"🔍 Yesterday's Details for {app_name}"
        elif period == "week":
            title = f"🔍 This Week's Details for {app_name}"
        elif date:
            title = f"🔍 Details for {app_name} on {date}"
        else:
            title = f"🔍 Recent Details for {app_name}"
        
        print(f"\n{title}")
        print("=" * len(title))
        
        # Group by URL/document for better organization
        grouped_details = defaultdict(list)
        total_time = 0
        
        for timestamp, window_title, url, duration in details:
            dt_obj = dt.datetime.fromtimestamp(timestamp)
            time_str = dt_obj.strftime("%H:%M:%S")
            date_str = dt_obj.strftime("%Y-%m-%d")
            
            # Use URL as key if available, otherwise use window title
            key = url if url else (window_title if window_title else "Unknown")
            
            grouped_details[key].append({
                'time': time_str,
                'date': date_str,
                'window_title': window_title,
                'url': url,
                'duration': duration
            })
            total_time += duration
        
        # Display results
        print(f"\n📊 Summary: {len(details)} sessions, {total_time//60}m {total_time%60}s total")
        print(f"📅 Showing {len(grouped_details)} unique items\n")
        
        # Sort by total time spent on each item
        sorted_items = sorted(grouped_details.items(), 
                            key=lambda x: sum(item['duration'] for item in x[1]), 
                            reverse=True)
        
        for i, (key, sessions) in enumerate(sorted_items, 1):
            item_total = sum(s['duration'] for s in sessions)
            session_count = len(sessions)
            
            # Display header for this item
            print(f"{i}. {key}")
            print(f"   ⏱️  {item_total//60}m {item_total%60}s across {session_count} session(s)")
            
            # Show recent sessions for this item
            recent_sessions = sorted(sessions, key=lambda x: x['time'], reverse=True)[:5]
            for session in recent_sessions:
                duration_str = f"{session['duration']//60}m {session['duration']%60}s" if session['duration'] > 0 else "Active"
                
                if session['url'] and session['url'] != key:
                    print(f"   📄 {session['time']} - {session['window_title']} ({duration_str})")
                    print(f"      🔗 {session['url']}")
                else:
                    print(f"   📄 {session['time']} - {session['window_title']} ({duration_str})")
            
            if len(sessions) > 5:
                print(f"   ... and {len(sessions) - 5} more sessions")
            print()
    
    def status(self):
        """Show current daemon status and recent activity"""
        if self.daemon.is_running():
            print("✅ TraceShell daemon is running")
            
            # Get recent activities
            recent = self.db_manager.get_activities(limit=10)
            if recent:
                print("\n📊 Recent Activity:")
                for row in recent[:5]:
                    timestamp, type_, content, duration, meta, window_title, url = row
                    dt_obj = dt.datetime.fromtimestamp(timestamp)
                    time_str = dt_obj.strftime("%H:%M")
                    
                    if type_ == "app":
                        if url:
                            print(f"  {time_str} - {content}: {url}")
                        elif window_title and window_title != content:
                            print(f"  {time_str} - {content}: {window_title}")
                        else:
                            print(f"  {time_str} - {content}")
        else:
            print("❌ TraceShell daemon is not running")
            print("💡 Start with: python traceshell.py start")
    
    def show(self, period="today", activity_type=None, ai=False):
        """Show activities for a time period"""
        date_range = self._get_date_range(period)
        activities = self.db_manager.get_activities(date_range, activity_type)
        
        if not activities:
            return print(f"📭 No activities found for {period}")
        
        # Create summary
        period_title = period.capitalize() if period != "week" else "This Week"
        print(f"\n📈 {period_title}'s Activity Report")
        print("=" * 40)
        
        # Group by app and calculate stats
        app_stats = defaultdict(lambda: {'time': 0, 'count': 0, 'details': []})
        total_time = 0
        
        for row in activities:
            timestamp, type_, content, duration, meta, window_title, url = row
            if type_ == "app":
                app_stats[content]['time'] += duration
                app_stats[content]['count'] += 1
                if window_title or url:
                    app_stats[content]['details'].append({
                        'title': window_title,
                        'url': url,
                        'duration': duration,
                        'timestamp': timestamp
                    })
                total_time += duration
        
        # Sort by time spent
        sorted_apps = sorted(app_stats.items(), key=lambda x: x[1]['time'], reverse=True)
        
        print(f"📊 Total tracked time: {total_time//3600}h {(total_time%3600)//60}m")
        print(f"📱 Applications used: {len(sorted_apps)}\n")
        
        # Show top applications with details
        for i, (app_name, stats) in enumerate(sorted_apps[:10], 1):
            hours = stats['time'] // 3600
            minutes = (stats['time'] % 3600) // 60
            time_str = f"{hours}h {minutes}m" if hours > 0 else f"{minutes}m"
            
            print(f"{i:2d}. {app_name} - {time_str} ({stats['count']} sessions)")
            
            # Show unique URLs/documents for this app
            if stats['details']:
                unique_items = {}
                for detail in stats['details']:
                    key = detail['url'] if detail['url'] else detail['title']
                    if key and key != app_name:
                        if key not in unique_items:
                            unique_items[key] = 0
                        unique_items[key] += detail['duration']
                
                # Show top 3 items for this app
                if unique_items:
                    sorted_items = sorted(unique_items.items(), key=lambda x: x[1], reverse=True)[:3]
                    for item, duration in sorted_items:
                        item_min = duration // 60
                        item_str = item if len(item) <= 60 else item[:57] + "..."
                        print(f"     📄 {item_str} ({item_min}m)")
        
        # AI Analysis if enabled
        if ai and self.ai_analyzer.api_key:
            print("\n🤖 AI Analysis:")
            print("-" * 20)
            analysis = self.ai_analyzer.analyze_activities(activities)
            print(analysis)
    
    def cleanup(self):
        """Clean up old data"""
        days = self.cfg["privacy"]["retention_days"]
        print(f"🧹 Cleaning up data older than {days} days...")
        self.db_manager.cleanup_old_data(days)
        print("✅ Cleanup completed")

def print_banner():
    """Print a cool banner for TraceShell"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                            🚀 TRACESHELL v2.0 🚀                            ║
║                     Advanced Activity Tracking & Analytics                   ║
║                                                                              ║
║  📊 Track applications, windows, and URLs with AI-powered insights          ║
║  🔍 Detailed analysis of your digital productivity patterns                 ║
║  🤖 Smart recommendations based on your usage data                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def print_enhanced_help():
    """Print an enhanced, beautiful help message"""
    print_banner()
    
    help_text = """
🎯 QUICK START
═══════════════════════════════════════════════════════════════════════════════
  traceshell start                    🚀 Start tracking your activities
  traceshell show                     📊 View today's activity report
  traceshell status                   ✅ Check if daemon is running
  traceshell stop                     🛑 Stop the tracking daemon

📋 COMMANDS
═══════════════════════════════════════════════════════════════════════════════
  start                              🚀 Launch the background tracking daemon
                                        • Monitors active applications
                                        • Tracks window titles and URLs
                                        • Stores data in local SQLite database
  
  stop                               🛑 Stop the background tracking daemon
                                        • Safely shuts down tracking
                                        • Saves all buffered data
  
  status                             ✅ Show daemon status and recent activity
                                        • Current tracking state
                                        • Last 5 activities
                                        • System information
  
  show                               📊 Display comprehensive activity reports
                                        • Time spent per application
                                        • Detailed breakdowns with URLs/docs
                                        • Productivity insights
  
  cleanup                            🧹 Remove old data based on retention policy
                                        • Configurable retention period
                                        • Frees up storage space

🔍 DETAILED ANALYSIS
═══════════════════════════════════════════════════════════════════════════════
  --detail APP_NAME                  🔬 Deep dive into specific application usage
                                        • Session history with timestamps
                                        • Documents/URLs accessed
                                        • Usage patterns and trends
  
📅 TIME PERIODS
═══════════════════════════════════════════════════════════════════════════════
  --period today                     📈 Today's activities (default)
  --period yesterday                 📊 Yesterday's complete report
  --period week                      📉 Past 7 days analysis
  --date YYYY-MM-DD                  📋 Specific date report

🎨 FILTERS & OPTIONS
═══════════════════════════════════════════════════════════════════════════════
  --type app                         📱 Filter by applications only
  --type file                        📄 Filter by file activities
  --type url                         🌐 Filter by URL activities
  --ai                              🤖 Include AI-powered insights (requires API key)
  --limit N                         📊 Limit results to N items (default: 50)

💡 EXAMPLES
═══════════════════════════════════════════════════════════════════════════════
  traceshell start                           🚀 Begin tracking
  traceshell show --period week --ai         📊 Weekly report with AI analysis
  traceshell --detail "Google Chrome"        🔍 Chrome usage details
  traceshell show --date 2024-12-25         📅 Christmas day activities
  traceshell --detail "VS Code" --period week   💻 Code editor weekly usage

🔧 CONFIGURATION
═══════════════════════════════════════════════════════════════════════════════
  Config file: ~/.traceshell/config.json
  Database:    ~/.traceshell/trace.db
  PID file:    ~/.traceshell/daemon.pid
  
  📝 Set OPENAI_API_KEY environment variable for AI features
  ⚙️  Customize tracking intervals and retention in config.json

🛡️  PRIVACY & SECURITY
═══════════════════════════════════════════════════════════════════════════════
  • All data stored locally on your machine
  • No data transmitted except for optional AI analysis
  • Configurable data retention policies
  • Window titles and URLs tracked for context

📞 NEED HELP?
═══════════════════════════════════════════════════════════════════════════════
  Having issues? Check these common solutions:
  
  🚫 Daemon won't start:     Check file permissions in ~/.traceshell/
  📊 No data showing:        Ensure you've run 'traceshell start' first
  🤖 AI not working:         Set OPENAI_API_KEY environment variable
  💾 Database errors:        Try 'traceshell cleanup' to fix corruption

═══════════════════════════════════════════════════════════════════════════════
"""
    print(help_text)

def main():
    # Check if no arguments provided or help requested
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help', 'help']):
        print_enhanced_help()
        return
    
    parser = argparse.ArgumentParser(
        description="TraceShell - Advanced Activity Tracker with AI Analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False  # We'll handle help ourselves
    )
    
    # Add custom help argument
    parser.add_argument('-h', '--help', action='store_true', help='Show this enhanced help message')
    
    parser.add_argument("command", nargs="?", 
                       choices=["start", "stop", "status", "show", "cleanup"], 
                       help="🎯 Main command to execute")
    
    parser.add_argument("--detail", metavar="APP_NAME", 
                       help="🔍 Show detailed breakdown for specific application")
    
    parser.add_argument("--period", choices=["today", "yesterday", "week"], default="today",
                       help="📅 Time period: today (default), yesterday, or week")
    
    parser.add_argument("--date", metavar="YYYY-MM-DD",
                       help="📋 Show activities for specific date")
    
    parser.add_argument("--type", choices=["app", "file", "url"], 
                       help="🎨 Filter by activity type")
    
    parser.add_argument("--ai", action="store_true", 
                       help="🤖 Include AI-powered insights and recommendations")
    
    parser.add_argument("--limit", type=int, default=50, metavar="N",
                       help="📊 Maximum number of results to display (default: 50)")
    
    args = parser.parse_args()
    
    # Handle help
    if args.help:
        print_enhanced_help()
        return
    
    trace = TraceShell()
    
    try:
        # Handle --detail flag
        if args.detail:
            trace.detail(args.detail, args.date, args.period, args.limit)
            return
        
        # Handle regular commands
        if args.command == "start":
            trace.start_daemon()
        elif args.command == "stop":
            trace.stop_daemon()
        elif args.command == "status":
            trace.status()
        elif args.command == "show":
            trace.show(args.period, args.type, args.ai)
        elif args.command == "cleanup":
            trace.cleanup()
        else:
            print_enhanced_help()
    
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        trace.db_manager.close()

if __name__ == "__main__":
    main()