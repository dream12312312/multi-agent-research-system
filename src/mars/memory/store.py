import json, sqlite3, time
from pathlib import Path
from typing import Any
from mars.config.settings import get_settings

class SQLiteMemoryStore:
    def __init__(self, path: str | None = None):
        self.path = path or get_settings().memory_db_path_abs
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.execute("CREATE TABLE IF NOT EXISTS memories (id INTEGER PRIMARY KEY, session_id TEXT, kind TEXT, content TEXT, created_at REAL)")
            c.execute("CREATE INDEX IF NOT EXISTS idx_memories_kind ON memories(kind)")

    def _conn(self): return sqlite3.connect(self.path)

    def add(self, session_id: str, kind: str, content: dict[str, Any]) -> int:
        with self._conn() as c:
            cur = c.execute("INSERT INTO memories(session_id,kind,content,created_at) VALUES(?,?,?,?)", (session_id, kind, json.dumps(content), time.time()))
            return int(cur.lastrowid)

    def search(self, query: str, limit: int = 8) -> list[dict]:
        tokens = [t.lower() for t in query.split() if len(t) > 2][:8]
        with self._conn() as c:
            rows = c.execute("SELECT id,session_id,kind,content,created_at FROM memories ORDER BY created_at DESC LIMIT 250").fetchall()
        scored=[]
        for row in rows:
            text=row[3].lower(); score=sum(t in text for t in tokens)
            if score: scored.append((score,row))
        scored.sort(key=lambda x:(x[0],x[1][4]), reverse=True)
        return [{"id":r[0],"session_id":r[1],"kind":r[2],"content":json.loads(r[3]),"created_at":r[4]} for _,r in scored[:limit]]
