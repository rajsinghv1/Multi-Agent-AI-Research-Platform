import sqlite3

from app.memory.database import get_connection


def init_knowledge_graph():
    """Create the knowledge graph tables."""

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS kg_entities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL COLLATE NOCASE UNIQUE,
                entity_type TEXT NOT NULL DEFAULT 'OTHER'
            );

            CREATE TABLE IF NOT EXISTS kg_relationships (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_id INTEGER NOT NULL,
                relation TEXT NOT NULL,
                target_id INTEGER NOT NULL,
                research_id INTEGER,
                FOREIGN KEY (source_id) REFERENCES kg_entities(id),
                FOREIGN KEY (target_id) REFERENCES kg_entities(id),
                FOREIGN KEY (research_id)
                    REFERENCES research_history(id) ON DELETE SET NULL,
                UNIQUE(source_id, relation, target_id, research_id)
            );

            CREATE INDEX IF NOT EXISTS idx_kg_source
            ON kg_relationships(source_id);

            CREATE INDEX IF NOT EXISTS idx_kg_target
            ON kg_relationships(target_id);
        """)


def add_entity(name, entity_type="OTHER"):
    """Add or reuse an entity."""

    name = name.strip()
    entity_type = entity_type.strip().upper()

    if not name:
        raise ValueError("Entity name cannot be empty")

    init_knowledge_graph()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO kg_entities (name, entity_type)
            VALUES (?, ?)
            """,
            (name, entity_type),
        )

        row = conn.execute(
            """
            SELECT id FROM kg_entities
            WHERE name = ? COLLATE NOCASE
            """,
            (name,),
        ).fetchone()

    return row["id"]


def add_relationship(source, relation, target, research_id=None):
    """Store a directed relationship."""

    if not relation or not relation.strip():
        raise ValueError("Relationship type cannot be empty")

    source_id = add_entity(source)
    target_id = add_entity(target)
    relation = relation.strip().upper()

    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO kg_relationships
                (source_id, relation, target_id, research_id)
            VALUES (?, ?, ?, ?)
            """,
            (source_id, relation, target_id, research_id),
        )


def save_extraction(extraction, research_id=None):
    """Save Gemini-extracted entities and relationships."""

    init_knowledge_graph()

    for entity in extraction.get("entities", []):
        add_entity(
            entity["name"],
            entity.get("type", "OTHER"),
        )

    for relationship in extraction.get("relationships", []):
        add_relationship(
            relationship["source"],
            relationship["relation"],
            relationship["target"],
            research_id=research_id,
        )


def get_entities(limit=100):
    """List stored entities."""

    init_knowledge_graph()

    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, name, entity_type
            FROM kg_entities
            ORDER BY name
            LIMIT ?
            """,
            (max(1, int(limit)),),
        ).fetchall()

    return [dict(row) for row in rows]


def get_relationships(entity_name=None, limit=100):
    """Retrieve knowledge graph edges."""

    init_knowledge_graph()

    query = """
        SELECT
            s.name AS source,
            r.relation,
            t.name AS target,
            r.research_id
        FROM kg_relationships r
        JOIN kg_entities s ON s.id = r.source_id
        JOIN kg_entities t ON t.id = r.target_id
    """

    parameters = []

    if entity_name:
        query += """
            WHERE s.name = ? COLLATE NOCASE
               OR t.name = ? COLLATE NOCASE
        """
        parameters.extend([entity_name, entity_name])

    query += " ORDER BY r.id DESC LIMIT ?"
    parameters.append(max(1, int(limit)))

    with get_connection() as conn:
        rows = conn.execute(query, parameters).fetchall()

    return [dict(row) for row in rows]


def get_graph_stats():
    """Return knowledge graph statistics."""

    init_knowledge_graph()

    with get_connection() as conn:
        entities = conn.execute(
            "SELECT COUNT(*) FROM kg_entities"
        ).fetchone()[0]

        relationships = conn.execute(
            "SELECT COUNT(*) FROM kg_relationships"
        ).fetchone()[0]

    return {
        "entities": entities,
        "relationships": relationships,
    }