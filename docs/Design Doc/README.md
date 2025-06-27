# Overview

- **Description**: nodetion is an app that will ingest my Notion notes, chunk & embed them, and them visualize them as an interactive graph based on semantic similarity.
- **Purpose**: nodetion will help users study and uncover connections between notes. This project will also serve as a way for me to learn about embedding and vector databases in a hands-on manner.

# Core Features (MVP)

The MVP for this application will

- Extract my notes from Notion on demand.
- Chunk the notes into meaningful pieces.
- Embed each chunk and store with metadata in a vector database.
- Build a similarity graph
- Visualize the graph using a web-based interface
- Filter by date range and search by keyword
- Click on nodes to view metadata

## Out-of-Scope

- No scheduled or event-based note extraction; extraction will be on demand.
- No RAG-based querying.
- No dragging nodes in visualizer.
- No auth.

# Tech Stack

| **Use Case** | **Technology** | **Reason** |
| --- | --- | --- |
| Note extraction | Notion API |  |
| Embedding model | MiniLM | Small and free |
| Vector DB | Chroma | Supports metadata. Can be hosted locally in a docker contianer (free!) Simple API. |
| Frontend | React |  |
| Visualization | React Flow | Looks pretty |
| API | FastAPI | Python (has many AI libraries), easy to use, fast, rising in popularity and I want to learn it. |

# Data Model

### Embedding in Vector DB

```json
{
	"chunk_id": "<notion_page_id>_<chunk_index>",
	"content": "This is some example content!",
	"embedding": [0.1, 0.5, ..., 0.7],
	"metadata": {
		"notion_page_id": 123,
		"notion_page_title": "Hyrax 101",
		"created_time": "date string",
		"chunk_index": 2,
		"child_ids": ["uuid123", "uuid124", ...]
	}
}
```