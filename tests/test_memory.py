from mars.memory.store import SQLiteMemoryStore

def test_memory_roundtrip(tmp_path):
    db=tmp_path/"m.sqlite3"; store=SQLiteMemoryStore(str(db))
    store.add("s1","preference",{"text":"prefers official docs"})
    results=store.search("official docs")
    assert results and results[0]["content"]["text"]=="prefers official docs"
