# Archive engine

Subsystem `archive` of Creative-Headquarters. Part of the [inventory](../INVENTORY.md).

Verifier confidence: 0.93 · 27 entries · 19 corrections made to the first reading.

## Summary

archive/ holds the "Living Archive Engine", a self-organizing knowledge system brought in unchanged from the external crispy-engine repo (DECISIONS.md D3; README.md line 213 maps archive/ to crispy-engine). Ingest is the one real pipeline. A React SPA sends raw text to POST /api/ingest (Bearer JWT required). FastAPI then (1) sends the text to Groq through the synchronous OpenAI Python client (primary model llama-3.3-70b-versatile, fallback llama3-8b-8192), which returns a 2-4 level taxonomy path, a confidence score, suggested links, alternative paths, entities, a one-sentence summary and key phrases. (2) It builds a 1536-dimension embedding: OpenAI text-embedding-3-small when OPENAI_API_KEY is set, otherwise a flat md5-derived pseudo-vector. Steps 1 and 2 go through asyncio.gather, but both coroutines make blocking sync calls with no await points, so in practice they run one after the other. (3) If Pinecone is configured, it queries Pinecone for the top 5 similar nodes. (4) It writes a row to PostgreSQL. (5) As FastAPI BackgroundTasks, it upserts the vector to Pinecone and writes Concept nodes with PARENT_OF and RELATES_TO edges to Neo4j. Read paths: GET /api/nodes (all nodes, Bearer token required), GET /api/nodes/{node_id} (no auth) and GET /api/search (ILIKE text search, no auth, no vector search). GET /health returns a static JSON body. Auth is JWT (HS256) with register and token endpoints. main.py mounts the auth router at /api/auth and auth.py also declares APIRouter(prefix='/auth'), so the routes as written are /api/auth/auth/register and /api/auth/auth/token, while ENGINE-README and the frontend use /api/auth/*. The Neo4j graph is write-only: no route reads it, and the frontend Graph tab is a d3 force layout of the node list with links=[] (no edges). The Pinecone store is off by default because the package is commented out of requirements.txt. The Celery reorganization tasks are stubs that return literals; celery beat schedules one of them every 86400 s. There is no WebSocket server: the frontend WebSocketManager exists, but its instantiation (ws://localhost:8000/ws) is commented out, and the backend has no /ws route. Deployment config: docker-compose.yml defines 7 services (postgres 5432, neo4j 7474/7687, redis 6379, backend 8000, celery_worker, celery_beat, frontend 3000->80). render.yaml defines 6 services (3 pserv, 2 web, 1 worker, no beat). There are also setup.sh and two Dockerfiles. No .env and no package-lock.json exist anywhere under archive/. The repo's own statements on run status: README.md lines 107-111 say "this has not been installed, built, or started", and that backend/requirements.txt and backend/Dockerfile "were newly written from the import graph in this pass and have never been exercised. Treat first boot as debugging, not as a smoke test." DECISIONS.md D4 says of those two files "Neither has been installed or run". requirements.txt line 2 reads "NOT yet exercised: no install or run has been performed against this file." DECISIONS.md D1 rejects this seven-service cloud stack in favour of a local-first design (an Ollama model plus an on-disk vector index) that has not been built. D6 says the planned "cosmos view" is GraphVisualization.jsx and NodeDetail.jsx rendering vault notes, which is also not implemented.

## Tools

### Living Archive backend (FastAPI app)

`service` · status `never-exercised`

Paths: `archive/backend/app/main.py`, `archive/backend/app/config.py`, `archive/backend/app/database.py`, `archive/backend/app/__init__.py`, `archive/backend/app/api/__init__.py`, `archive/backend/app/services/__init__.py`

FastAPI application titled from settings.PROJECT_NAME (default 'Living Archive Engine'). It mounts the auth router at API_V1_STR+'/auth' and the ingest, nodes and search routers at API_V1_STR (default '/api'), serves GET /health, creates all SQLAlchemy tables at startup and closes the Neo4j driver at shutdown.

**Entry points**

- `uvicorn app.main:app --host 0.0.0.0 --port 8000`
  - does: Container CMD in archive/backend/Dockerfile. Starts the API on port 8000.
  - changes: At startup, the lifespan runs Base.metadata.create_all against Postgres (creates the users and nodes tables if missing)
- `cd backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt && uvicorn app.main:app --reload`
  - does: Local dev server, from the ENGINE-README.md 'Backend Development' section (written there as separate lines)
  - changes: Creates venv/ and installs packages. Creates tables at startup.
- `GET /health`
  - does: Returns {"status":"ok","version":"1.0.0"}. Does not check Postgres, Neo4j or Redis.
  - changes: nothing
- `GET /docs`
  - does: FastAPI's auto-generated API docs (the docs_url default is not overridden). Referenced as http://localhost:8000/docs in DEPLOY.md, ENGINE-README.md and setup.sh.
  - changes: nothing

**Inputs**

- Settings from environment variables or a .env file (pydantic-settings, class Config env_file='.env')
- HTTP requests

**Outputs**

- JSON HTTP responses

**Reads**

- .env (relative to the process working directory, via pydantic-settings; none exists under archive/)
- process environment

**Writes**

- PostgreSQL tables users and nodes (create_all at startup)

**Depends on**

- python:3.11-slim image
- fastapi>=0.110
- uvicorn[standard]>=0.27
- pydantic>=2.6
- pydantic-settings>=2.2
- sqlalchemy[asyncio]>=2.0
- asyncpg>=0.29
- PostgreSQL 15
- Neo4j 5 (driver created at import by graph_store)
- Groq API (OpenAI client created at import by ai_engine)

**Environment and secret names (names only)**

- API_V1_STR
- PROJECT_NAME
- SECRET_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES
- POSTGRES_SERVER
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- SQLALCHEMY_DATABASE_URI
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD
- PINECONE_API_KEY
- PINECONE_ENVIRONMENT
- PINECONE_INDEX_NAME
- GROQ_API_KEY
- OPENAI_API_KEY
- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND

**Gates and checkpoints**

- CORS allow_origins is limited to http://localhost:3000 and http://localhost:5173, with allow_credentials=True and all methods and headers allowed
- docker-compose: backend depends_on postgres (service_healthy), neo4j (service_healthy), redis (service_started)

**Invoked by**

- docker-compose service 'backend'
- render.yaml web service 'living-archive-backend'
- Frontend API client (api.js)
- nginx /api proxy in the frontend container (used only if the bundle's API base is relative)
- Vite dev proxy /api (used only if the API base is relative)
- setup.sh health probe (curl -s http://localhost:8000/health)

**Invokes**

- Auth API
- Ingest API
- Nodes API
- Search API
- Relational store (PostgreSQL)
- Graph store (Neo4j) close() on shutdown

**Notes**

Import-time singletons: ai_engine (OpenAI client pointed at Groq), graph_store (Neo4j AsyncGraphDatabase driver), vector_store (Pinecone init when a key is set). Settings builds SQLALCHEMY_DATABASE_URI as postgresql+asyncpg://USER:PASSWORD@SERVER/DB (no port) unless the variable is set explicitly. All config defaults are non-empty placeholders except PINECONE_API_KEY, GROQ_API_KEY and OPENAI_API_KEY, which default to empty. The auth routes resolve to /api/auth/auth/* because the prefix is applied twice. There are no migrations: the schema comes only from create_all. All four __init__.py files are 0 bytes. Directory layout was reconstructed from the import graph, render.yaml and docker-compose.yml (DECISIONS.md D4). README.md says archive/ has not been installed, built or started.

### Auth API (/api/auth)

`service` · status `never-exercised`

Paths: `archive/backend/app/api/auth.py`, `archive/backend/app/schemas.py`, `archive/backend/app/models.py`

Account registration and OAuth2 password-flow login that issues HS256 JWTs. It also provides the get_current_user dependency that protects POST /api/ingest and GET /api/nodes.

**Entry points**

- `POST /api/auth/auth/register (effective path as written; ENGINE-README.md documents it and the frontend calls it as POST /api/auth/register) body JSON {"email":str,"password":str,"full_name":str|null}`
  - does: Rejects a duplicate email with 400 'Email already registered'. Otherwise stores the user with a bcrypt-hashed password, commits and returns User {id,email,full_name,is_active,created_at}.
  - changes: Inserts a row into Postgres table users
- `POST /api/auth/auth/token (effective path; documented and called as POST /api/auth/token) body application/x-www-form-urlencoded username=<email>&password=<password>`
  - does: Verifies credentials (400 'Incorrect email or password' on failure) and returns {access_token, token_type:'bearer'}. The JWT carries sub=user.id and exp=utcnow+ACCESS_TOKEN_EXPIRE_MINUTES (default 60*24*8 minutes = 8 days).
  - changes: nothing
- `get_current_user (FastAPI dependency; Authorization: Bearer <jwt>)`
  - does: Decodes the JWT with SECRET_KEY (HS256), loads UserModel by sub and returns {id,email}. Otherwise raises 401 'Could not validate credentials' with WWW-Authenticate: Bearer.
  - changes: nothing

**Inputs**

- email, password, full_name (register)
- form username/password (token)
- Bearer token (dependency)

**Outputs**

- User JSON
- Token JSON {access_token, token_type}

**Reads**

- Postgres users table

**Writes**

- Postgres users table

**Depends on**

- python-jose[cryptography]>=3.3
- passlib[bcrypt]>=1.7.4
- python-multipart>=0.0.9 (OAuth2PasswordRequestForm)

**Environment and secret names (names only)**

- SECRET_KEY
- ACCESS_TOKEN_EXPIRE_MINUTES

**Gates and checkpoints**

- OAuth2PasswordBearer(tokenUrl='api/auth/token') is the auth gate for POST /api/ingest and GET /api/nodes
- JWT signature and expiry check; the user must exist in the users table
- Duplicate-email check on register

**Invoked by**

- AuthModal tab via the Frontend API client
- Ingest API and Nodes API (dependency)

**Invokes**

- Relational store (PostgreSQL)

**Notes**

Path mismatch: because the prefix is applied twice, the routes the frontend calls (/api/auth/register, /api/auth/token) do not match the routes as written. The OAuth2PasswordBearer tokenUrl 'api/auth/token' is relative and also does not match the effective /api/auth/auth/token path. No logout, refresh or password-reset endpoints exist. UserModel.is_active is a Float column with default True, while the User schema declares a bool. create_access_token defaults to a 15-minute expiry when no delta is passed, but login always passes ACCESS_TOKEN_EXPIRE_MINUTES.

### Ingest API (POST /api/ingest)

`service` · status `never-exercised`

Paths: `archive/backend/app/api/ingest.py`, `archive/backend/app/schemas.py`

The core pipeline. It classifies and embeds submitted text, merges link suggestions from the LLM and from vector neighbours, saves the node to Postgres, and schedules background writes to the vector store and the Neo4j graph.

**Entry points**

- `POST /api/ingest Authorization: Bearer <jwt> body JSON {"type":"knowledge_ingestion" (optional, Literal, defaults to that value),"content":{"raw_text":str(1..50000),"timestamp":ISO datetime (required),"source":"manual_input"|"api"|"import" (default manual_input),"metadata":{} (optional)},"context":{"session_id":str (required),"user_id":str|null,"user_preferences":{"auto_link":bool=true,"language":str='en',"confidence_threshold":float=0.6}}}`
  - does: 1) Calls ai_engine.generate_embedding and ai_engine.classify through asyncio.gather. Both make blocking sync calls, so they run one after the other. 2) If vector_store.index exists, queries the top 5 neighbours. 3) Takes the last path element of each neighbour scoring above 0.8 as a suggestion, merges these with the LLM suggested_links, deduplicates with set() and keeps at most 5. 4) Inserts a NodeModel row (title=raw_text[:200], content, path, confidence, entities, summary, session_id, user_id from the token, metadata={key_phrases, source}) and commits. 5) Adds BackgroundTasks: vector upsert (id, embedding, {path, summary, user_id}) and graph create_node(id, path, {suggested_links}). 6) Returns IngestResponse {ok, data:{node_id, classification{path,confidence,suggested_links,alternative_paths}, extracted_entities[{text,label,start,end}], embedding_vector[1536], summary, key_phrases}, meta:{processing_time_ms, model_version:'groq-llama-3.3-70b', store_size (COUNT of nodes), vector_search_hits}}.
  - changes: Postgres nodes row (synchronous). Pinecone vector upsert (background, only if configured). Neo4j Concept nodes and edges (background).

**Inputs**

- IngestRequest JSON
- Bearer JWT

**Outputs**

- IngestResponse JSON
- HTTP 401 from get_current_user
- HTTP 422 on Pydantic validation failure
- HTTP 500 {detail: str(exception)} on any error inside the handler (after rollback)

**Reads**

- Pinecone index (query, if configured)
- Postgres nodes (count for store_size)

**Writes**

- Postgres nodes table
- Neo4j (via Graph store)
- Pinecone (via Vector store)

**Depends on**

- AI engine
- Vector store
- Graph store
- Relational store
- Groq API
- OpenAI embeddings API (optional)
- Pinecone (optional)

**Environment and secret names (names only)**

- GROQ_API_KEY
- OPENAI_API_KEY
- PINECONE_API_KEY
- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD

**Gates and checkpoints**

- get_current_user dependency: a Bearer token is required (typed Optional in the signature, but the dependency raises 401)
- Pydantic validation: raw_text length 1-50000, type literal 'knowledge_ingestion', timestamp required, source enum, context.session_id required
- Vector neighbour score threshold > 0.8 for merged suggestions
- ClassificationResult requires confidence in 0.0-1.0 and ExtractedEntity(**e) requires text/label/start/end. An LLM response that violates either becomes a 500.

**Invoked by**

- Ingest Knowledge panel (App.jsx) via api.ingest
- DEPLOY.md verification curl (sends no Authorization header, so it would be rejected with 401)

**Invokes**

- AI engine.classify
- AI engine.generate_embedding
- Vector store.query / upsert
- Graph store.create_node
- Relational store

**Notes**

The handler never reads content.timestamp, content.metadata, context.user_id, user_preferences.auto_link, language or confidence_threshold. model_version in the response is hardcoded. NodeModel.embedding_id is never set. Because the graph write runs in the background, any Neo4j failure happens after the 200 response. The response embedding_vector is the full 1536-float list. The order of suggested links is not deterministic because of set().

### Nodes API (GET /api/nodes, GET /api/nodes/{node_id})

`service` · status `never-exercised`

Paths: `archive/backend/app/api/nodes.py`

Lists all archived nodes and fetches a single node by id from Postgres.

**Entry points**

- `GET /api/nodes Authorization: Bearer <jwt>`
  - does: Returns every node (not filtered by user, no pagination) ordered by created_at desc, with fields id, title, content, path, confidence, summary, created_at (ISO).
  - changes: nothing
- `GET /api/nodes/{node_id}`
  - does: Returns the NodeModel ORM object (no response_model), or 404 'Node not found'. No auth dependency.
  - changes: nothing

**Inputs**

- node_id path parameter
- Bearer JWT (list only)

**Outputs**

- JSON list of node summaries
- single node object

**Reads**

- Postgres nodes table

**Depends on**

- Relational store

**Gates and checkpoints**

- GET /api/nodes requires a valid JWT (get_current_user); GET /api/nodes/{node_id} has no auth

**Invoked by**

- Frontend SPA loadNodes() on authentication, on the refresh button, and on an empty search
- api.getNode (defined, but no component calls it)

**Invokes**

- Relational store

**Notes**

The list omits entities, metadata, user_id, session_id, embedding_id and updated_at. As a result, the 'Recent Entities' panel only shows entities from nodes ingested in the current browser session.

### Search API (GET /api/search)

`service` · status `never-exercised`

Paths: `archive/backend/app/api/search.py`

Case-insensitive substring search over node content, summary and title.

**Entry points**

- `GET /api/search?q=<text>`
  - does: Runs SELECT on nodes WHERE content ILIKE %q% OR summary ILIKE %q% OR title ILIKE %q%, LIMIT 20, and returns the ORM objects. q is required with min_length=1. No auth.
  - changes: nothing

**Inputs**

- q query string

**Outputs**

- JSON list of up to 20 nodes

**Reads**

- Postgres nodes table

**Depends on**

- Relational store

**Gates and checkpoints**

- q min_length=1

**Invoked by**

- SearchBar via api.search

**Invokes**

- Relational store

**Notes**

The source comment says it 'would use vector search in production'. This route does not use the Vector store, even though ENGINE-README Features claims 'Vector Search: Semantic similarity search (with Pinecone or fallback)'.

### AI engine (Groq classification + embeddings)

`library` · status `never-exercised`

Paths: `archive/backend/app/services/ai_engine.py`

Uses an LLM to classify text into a 2-4 level path with confidence, suggested links and alternative paths. It also extracts entities (labels CONCEPT, PERSON, ORG, TECH, THEORY, FIELD), writes a one-sentence summary and key phrases, and generates 1536-dimension embeddings.

**Entry points**

- `await ai_engine.classify(text)`
  - does: Calls client.responses.create(model='llama-3.3-70b-versatile', input=[system SYSTEM_PROMPT, user text[:4000]], temperature=0.1, max_tokens=1000) on an OpenAI client whose base_url is https://api.groq.com/openai/v1. Strips ```json and ``` fences from response.output_text, runs json.loads and returns {classification{path,confidence(float),suggested_links,alternative_paths}, entities, summary (fallback text[:100]+'...'), key_phrases}. On any exception it prints the error and retries once with 'llama3-8b-8192'. A failure of the fallback propagates.
  - changes: nothing (network call to Groq)
- `await ai_engine.generate_embedding(text)`
  - does: If OPENAI_API_KEY is set, creates a new OpenAI client and calls embeddings.create(model='text-embedding-3-small', input=text[:8000]). If the key is missing or the call fails, returns a deterministic pseudo-embedding: 1536 copies of (int(md5(text),16) % 1000)/1000.
  - changes: nothing (network call to OpenAI if a key is set)

**Inputs**

- raw text

**Outputs**

- classification dict
- list[float] of length 1536

**Depends on**

- openai>=1.12 Python client
- Groq API (OpenAI-compatible endpoint https://api.groq.com/openai/v1)
- OpenAI embeddings API (optional)

**Environment and secret names (names only)**

- GROQ_API_KEY
- OPENAI_API_KEY

**Gates and checkpoints**

- Primary-to-fallback model retry on exception
- The system prompt demands STRICT JSON; the only validation is key access plus float(confidence)

**Invoked by**

- Ingest API

**Invokes**

- Groq responses endpoint (via the OpenAI client)
- OpenAI embeddings endpoint

**Notes**

Uses the synchronous OpenAI client inside async functions with no await points, so asyncio.gather in ingest gives no real concurrency. The Groq client is instantiated at import with GROQ_API_KEY. DECISIONS.md D1 says the classification prompt and JSON contract are the valuable part and should survive, but the transport should move to the local Ollama endpoint specified in skills/local_rag_orchestration.skill.md. When the md5 fallback is used, every vector is constant across all 1536 dimensions, so cosine similarity between vectors carries no meaning. ENGINE-README.md's Groq key check is curl -H "Authorization: Bearer $GROQ_API_KEY" https://api.groq.com/openai/v1/models.

### Relational store (PostgreSQL via SQLAlchemy async)

`data` · status `never-exercised`

Paths: `archive/backend/app/database.py`, `archive/backend/app/models.py`

System of record for users and knowledge nodes.

**Entry points**

- `get_db() FastAPI dependency (AsyncSessionLocal, expire_on_commit=False)`
  - does: Yields an AsyncSession, commits after the request, rolls back and re-raises on exception, then closes
  - changes: Postgres
- `docker-compose exec postgres pg_isready -U postgres`
  - does: Readiness check from ENGINE-README.md troubleshooting. setup.sh uses the same command with -T, and the compose healthcheck runs 'pg_isready -U postgres' via CMD-SHELL.
  - changes: nothing

**Inputs**

- ORM operations from the API routes

**Outputs**

- rows

**Reads**

- tables users, nodes

**Writes**

- table users (id String PK uuid4, email unique+index not null, hashed_password not null, full_name, is_active Float default True, created_at)
- table nodes (id String PK uuid4, title String(500), content Text, path ARRAY(String), confidence Float, embedding_id String, entities JSON, summary Text, metadata JSON, created_at, updated_at with onupdate, user_id FK users.id nullable, session_id indexed)

**Depends on**

- postgres:15-alpine container (db living_archive, named volume postgres_data, port 5432)
- sqlalchemy[asyncio]>=2.0
- asyncpg>=0.29

**Environment and secret names (names only)**

- POSTGRES_SERVER
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- SQLALCHEMY_DATABASE_URI

**Gates and checkpoints**

- compose healthcheck: pg_isready -U postgres, interval 5s, timeout 5s, 5 retries

**Invoked by**

- Auth API
- Ingest API
- Nodes API
- Search API
- Backend app lifespan (create_all)

**Notes**

No migrations exist. embedding_id is never populated. NodeModel declares a column attribute named 'metadata' (models.py line 31; see open_questions). UserModel.nodes and NodeModel.owner form a bidirectional relationship.

### Graph store (Neo4j)

`library` · status `never-exercised`

Paths: `archive/backend/app/services/graph_store.py`

Writes each node's classification path into Neo4j as a chain of :Concept nodes joined by PARENT_OF edges, plus RELATES_TO edges to suggested concepts.

**Entry points**

- `await graph_store.create_node(node_id, path, metadata)`
  - does: For each path segment i it runs: MERGE (p:Concept {name: path[i-1] or 'Root', level: i-1}); MERGE (c:Concept {name: segment, level: i, node_id: node_id if leaf else '<node_id>_<i>', created_at: datetime()}); MERGE (p)-[:PARENT_OF {weight:1.0}]->(c). Then, for each metadata.suggested_links target: MATCH (a:Concept {node_id}), MATCH (b:Concept {name: target}); MERGE (a)-[:RELATES_TO {type:'suggested', weight:0.5, created_at: datetime()}]->(b).
  - changes: Neo4j Concept nodes and PARENT_OF/RELATES_TO relationships
- `await graph_store.close()`
  - does: Closes the driver (called at FastAPI shutdown)
  - changes: nothing
- `http://localhost:7474 (Neo4j Browser)`
  - does: The only documented way to view the graph (DEPLOY.md, ENGINE-README.md, setup.sh)
  - changes: nothing

**Inputs**

- node_id
- path list
- suggested_links

**Outputs**

- none returned

**Reads**

- Neo4j (MATCH for link targets)

**Writes**

- Neo4j graph

**Depends on**

- neo4j>=5.17 (AsyncGraphDatabase)
- neo4j:5-community container. In compose it has NEO4J_PLUGINS ["apoc"], ports 7474 (HTTP) and 7687 (bolt), and named volume neo4j_data. On Render it has no plugins and a 10GB disk at /data.

**Environment and secret names (names only)**

- NEO4J_URI
- NEO4J_USER
- NEO4J_PASSWORD
- NEO4J_AUTH (container)
- NEO4J_PLUGINS (compose container only)

**Gates and checkpoints**

- compose healthcheck: wget --no-verbose --tries=1 --spider http://localhost:7474, interval 10s, timeout 10s, 5 retries

**Invoked by**

- Ingest API (FastAPI BackgroundTask)
- Backend app lifespan (close)

**Notes**

Write-only from the application's side: no API route queries Neo4j, and the frontend Graph tab does not read it. The child Concept MERGE pattern includes created_at: datetime() among the matched properties. The RELATES_TO MATCH on name alone can match several Concept nodes. The driver is created at module import. The APOC plugin is enabled in compose, but no code uses it.

### Vector store (Pinecone, optional)

`library` · status `never-exercised`

Paths: `archive/backend/app/services/vector_store.py`

Optional semantic-similarity index used to suggest links during ingest.

**Entry points**

- `await vector_store.upsert(node_id, embedding, metadata)`
  - does: Upserts {id, values, metadata{node_id, path, summary[:500], created_at}}. Does nothing when the index is None.
  - changes: Pinecone index
- `await vector_store.query(embedding, top_k=5, filter=None)`
  - does: Returns [{node_id, score, metadata}] with include_metadata=True, or [] when the index is None
  - changes: nothing
- `await vector_store.delete(node_id)`
  - does: Deletes the vector by id. Nothing calls it.
  - changes: Pinecone index

**Inputs**

- 1536-dimension embedding
- metadata

**Outputs**

- similar-node matches

**Reads**

- Pinecone index

**Writes**

- Pinecone index. _ensure_index creates a serverless index (dimension 1536, metric cosine, aws us-west-2) if it is missing.

**Depends on**

- pinecone>=3.0 (commented out in requirements.txt)
- Pinecone cloud service

**Environment and secret names (names only)**

- PINECONE_API_KEY
- PINECONE_INDEX_NAME
- PINECONE_ENVIRONMENT (defined in config, never read)

**Gates and checkpoints**

- Enabled only when PINECONE_API_KEY is non-empty AND 'from pinecone import Pinecone' succeeds. Init errors are printed and swallowed.

**Invoked by**

- Ingest API

**Invokes**

- Pinecone API

**Notes**

Disabled by default because the pinecone package is left out of requirements.txt per the local-first decision (DECISIONS.md D1). Ingest passes user_id, but upsert drops it. created_at is read from metadata, but ingest never supplies it. The Pinecone calls are synchronous inside async methods. ENGINE-README.md mentions an 'OR pgvector' fallback, which is not implemented.

### Reorganization tasks (Celery worker + beat)

`service` · status `stub`

Paths: `archive/backend/app/tasks/reorganization.py`, `archive/backend/app/tasks/__init__.py`

Intended background maintenance: daily tree-health analysis and batch re-embedding.

**Entry points**

- `celery -A app.tasks.reorganization worker --loglevel=info`
  - does: Runs the Celery worker (compose service celery_worker; render worker living-archive-celery)
  - changes: Redis broker and result keys
- `celery -A app.tasks.reorganization beat --loglevel=info`
  - does: Runs the scheduler (compose service celery_beat only). beat_schedule 'daily-reorg' sends app.tasks.reorganization.daily_reorganization every 86400.0 seconds.
  - changes: Redis broker
- `app.tasks.reorganization.daily_reorganization`
  - does: Returns the literal {"status":"completed","recommendations":[]}. Its docstring says 'Analyze tree health and generate recommendations'.
  - changes: nothing
- `app.tasks.reorganization.update_embeddings_batch`
  - does: Returns the literal {"processed":0}. It is not scheduled and nothing calls it.
  - changes: nothing

**Outputs**

- literal result dicts stored in the Redis result backend

**Writes**

- Redis (CELERY_BROKER_URL / CELERY_RESULT_BACKEND, default redis://redis:6379/0)

**Depends on**

- celery>=5.3
- redis>=5.0
- redis:7-alpine container (port 6379, named volume redis_data)

**Environment and secret names (names only)**

- CELERY_BROKER_URL
- CELERY_RESULT_BACKEND (config default only; not set by compose or render)
- GROQ_API_KEY (passed to the worker container, unused by the stubs)
- POSTGRES_SERVER, POSTGRES_PASSWORD, NEO4J_URI, NEO4J_PASSWORD (passed to the compose worker, unused by the stubs)

**Invoked by**

- celery beat schedule
- docker-compose celery_worker / celery_beat
- render.yaml living-archive-celery

**Notes**

The Celery app name is 'living_archive'. Nothing in the API enqueues these tasks (no .delay, apply_async or send_task anywhere). DECISIONS.md D1 calls them 'two stub Celery tasks that return literals' and says local-first probably means no Redis and no Celery. render.yaml defines no beat process.

### WebSocket protocol (WebSocketManager)

`protocol` · status `specified-not-implemented`

Paths: `archive/frontend/src/services/websocket.js`, `archive/frontend/src/App.jsx`

Client-side real-time event channel, intended for live updates from the backend.

**Entry points**

- `new WebSocketManager('ws://localhost:8000/ws').connect()`
  - does: Commented out at App.jsx lines 27-28. If enabled, it opens a socket, parses each message as JSON {type, payload} and calls the listeners registered for data.type.
  - changes: nothing
- `ws.on(event, cb) / ws.send(type, payload) / ws.disconnect()`
  - does: on registers a listener. send writes JSON {type,payload} only when the socket is OPEN. disconnect closes the socket.
  - changes: nothing

**Inputs**

- server messages {type, payload}

**Outputs**

- local events 'connected' (on open) and 'error'; any server-sent type

**Depends on**

- browser WebSocket API

**Gates and checkpoints**

- Reconnects on close up to maxReconnectAttempts=5, with a delay of 1000*2^attempts ms

**Invoked by**

- Frontend SPA (instantiation commented out)

**Notes**

The backend has no /ws route and no websocket endpoint of any kind. No event type names are defined anywhere. App.jsx imports the class and creates a ws useRef, but never uses either. The nginx /api location forwards Upgrade headers, but the intended URL is /ws, not /api/*.

### Living Archive frontend SPA (React + Vite)

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/App.jsx`, `archive/frontend/src/main.jsx`, `archive/frontend/src/index.css`, `archive/frontend/index.html`, `archive/frontend/package.json`, `archive/frontend/vite.config.js`, `archive/frontend/tailwind.config.js`, `archive/frontend/postcss.config.js`

Browser UI for signing in, ingesting text and browsing archived knowledge as a tree, graph or list, with search and a node detail modal.

**Entry points**

- `cd frontend && npm install && npm run dev`
  - does: Vite dev server on port 5173 with proxy '/api' -> http://localhost:8000 (ENGINE-README 'Frontend Development')
  - changes: node_modules/
- `npm run build`
  - does: vite build -> dist/ (build.outDir 'dist')
  - changes: archive/frontend/dist/
- `npm run preview`
  - does: vite preview of the build (package.json script; not mentioned in the docs)
  - changes: nothing
- `http://localhost:3000`
  - does: Served by the nginx container in the compose stack
  - changes: nothing

**Inputs**

- user text input
- JWT in localStorage

**Outputs**

- rendered views
- toasts (sonner Toaster, position top-right, theme dark)

**Reads**

- localStorage 'token'
- backend API

**Writes**

- localStorage 'token'

**Depends on**

- react ^18.2.0
- react-dom ^18.2.0
- d3 ^7.8.5
- sonner ^1.4.0
- lucide-react ^0.344.0
- vite ^5.1.0
- @vitejs/plugin-react ^4.2.1
- tailwindcss ^3.4.1
- postcss ^8.4.35
- autoprefixer ^10.4.17
- @types/react ^18.2.55
- @types/react-dom ^18.2.19
- Google Fonts CDN (Inter, JetBrains Mono)

**Environment and secret names (names only)**

- VITE_API_URL

**Gates and checkpoints**

- If localStorage has no token, only AuthModal renders
- The header shows metrics '{total} nodes • {avg}% avg'

**Invoked by**

- User browser

**Invokes**

- Frontend API client (api.js)
- AuthModal
- Ingest Knowledge panel
- Tree view tab
- Graph view tab
- List view tab
- SearchBar
- NodeDetail modal

**Notes**

Layout: a header (brand, SearchBar, Tree/Graph/List toggle, refresh button, metrics), a left column (the Ingest Knowledge form plus a 'Recent Entities' panel showing up to 8 entities from the first 10 nodes, or 'No entities yet...'), the main view area, and the NodeDetail overlay. There is no client router. package.json has no test script, although ENGINE-README.md says 'npm test'. index.html links /vite.svg as the favicon, but no such file exists (there is no public/ dir). index.css defines .node-card, .animate-slide-in and .animate-pulse-glow, which nothing uses. handleSearch does not update the header metrics.

### Frontend API client (api.js)

`library` · status `never-exercised`

Paths: `archive/frontend/src/services/api.js`

fetch wrapper that attaches the Bearer token and talks to the backend.

**Entry points**

- `api.login(email, password)`
  - does: POST ${API_BASE_URL}/auth/token with a form-urlencoded username/password body. Stores access_token in localStorage 'token'. Throws 'Login failed' on any non-ok response.
  - changes: localStorage 'token'
- `api.register(email, password, fullName)`
  - does: POST ${API_BASE_URL}/auth/register with JSON {email,password,full_name}
  - changes: backend users table
- `api.ingest(payload)`
  - does: POST ${API_BASE_URL}/ingest (JSON)
  - changes: backend stores
- `api.getNodes()`
  - does: GET ${API_BASE_URL}/nodes
  - changes: nothing
- `api.getNode(nodeId)`
  - does: GET ${API_BASE_URL}/nodes/{id} (no component uses it)
  - changes: nothing
- `api.search(query)`
  - does: GET ${API_BASE_URL}/search?q=<encodeURIComponent(query)>
  - changes: nothing

**Inputs**

- VITE_API_URL (build time)

**Outputs**

- parsed JSON

**Reads**

- localStorage 'token'

**Writes**

- localStorage 'token' (set on login, removed on 401)

**Depends on**

- browser fetch

**Environment and secret names (names only)**

- VITE_API_URL

**Gates and checkpoints**

- On HTTP 401 (request() only): clears the token, sets window.location.href='/login' and throws 'Unauthorized'
- On other non-ok responses: throws error.detail, or 'Unknown error' if the body is not JSON, or 'HTTP <status>'

**Invoked by**

- AuthModal
- Frontend SPA (loadNodes, handleSubmit, handleSearch)

**Invokes**

- Auth API
- Ingest API
- Nodes API
- Search API

**Notes**

API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'. The default is absolute, so the browser calls port 8000 directly rather than going through the nginx or Vite /api proxy. The backend CORS list allows :3000 and :5173 for this reason. /login is not a real route; the SPA fallback re-renders AuthModal because the token is gone.

### AuthModal tab (Sign In / Create Account)

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/components/AuthModal.jsx`

Login and registration screen shown when there is no stored token.

**Entry points**

- `Sign In form (Email, Password) -> api.login`
  - does: Logs in, then calls onAuth(true)
  - changes: localStorage 'token'
- `Create Account form (Full Name, Email, Password) -> api.register then api.login`
  - does: Registers, then logs in automatically. The 'Sign up' / 'Sign in' link toggles between the two modes.
  - changes: backend users table, localStorage 'token'

**Inputs**

- email
- password
- full name

**Outputs**

- authenticated state or inline error message

**Writes**

- localStorage 'token'

**Depends on**

- lucide-react

**Gates and checkpoints**

- HTML required fields (Full Name is required only in Create Account mode)

**Invoked by**

- Frontend SPA when not authenticated

**Invokes**

- Frontend API client

**Notes**

Because the backend applies the /auth prefix twice, both calls target paths that do not match the routes as written.

### Ingest Knowledge panel

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/App.jsx`

Text area plus a 'Process & Archive' button that submits text for classification.

**Entry points**

- `Process & Archive button -> handleSubmit -> api.ingest(payload)`
  - does: Sends {type:'knowledge_ingestion', content:{raw_text, timestamp: new Date().toISOString(), source:'manual_input'}, context:{session_id:'sess_'+9 random base-36 chars, user_preferences:{auto_link:true, language:'en'}}}. On ok it prepends {id, node_id, ...response.data} to local state, clears the input, shows the toast 'Classified: A > B > C' and updates the metrics. Otherwise it shows a toast with response.error or 'Processing failed' or err.message.
  - changes: backend stores; local node list

**Inputs**

- free text

**Outputs**

- new node in local state
- toast

**Depends on**

- sonner

**Gates and checkpoints**

- The button is disabled while processing or when the input is blank; the textarea is disabled while processing

**Invoked by**

- User

**Invokes**

- Ingest API

**Notes**

A new random session_id is generated on every submit. The locally kept node is the IngestResponse data, which has no created_at or title, so NodeDetail shows an invalid date for it.

### Tree view tab

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/components/TreeView.jsx`

Hierarchical browser. It builds a folder tree under 'Knowledge Root' from each node's classification path.

**Entry points**

- `View toggle 'Tree' (default view)`
  - does: Groups nodes by path (classification.path, else path, else ['Uncategorized']). Folders at render level <2 start expanded. Leaves show title (else the first 30 chars of summary, else 'Untitled') and a confidence %.
  - changes: nothing

**Inputs**

- nodes list

**Outputs**

- tree UI; onSelect(leaf)

**Depends on**

- lucide-react

**Invoked by**

- Frontend SPA

**Invokes**

- NodeDetail modal (via onSelect)

**Notes**

Clicking a leaf passes the wrapper object {id,name,confidence,leaf,data} to NodeDetail, not the node itself, so path, summary and entities show empty there and the date is invalid. The tree is built client-side and does not come from Neo4j.

### Graph view tab

`web-app` · status `partial`

Paths: `archive/frontend/src/components/GraphVisualization.jsx`

d3 force-directed view of nodes.

**Entry points**

- `View toggle 'Graph'`
  - does: Runs d3.forceSimulation (link distance 100 with id d=>d.id, charge -300, center, collision radius 40) in a 600px-high SVG. Circle radius is 15+(d.confidence||0.5)*15. Fill is one of 4 colours chosen by path depth. Labels are the first 20 chars of title, else summary, else 'Untitled'. Nodes are draggable, and clicking a circle calls onNodeClick(d).
  - changes: nothing

**Inputs**

- nodes
- links

**Outputs**

- SVG graph

**Depends on**

- d3 ^7.8.5

**Gates and checkpoints**

- Renders nothing when nodes is empty

**Invoked by**

- Frontend SPA

**Invokes**

- NodeDetail modal

**Notes**

Never exercised. App.jsx always passes links={[]}, so no edges are drawn, and the Neo4j PARENT_OF/RELATES_TO graph is never fetched. Nodes added locally after ingest have no top-level confidence, so they use the 0.5 default radius. DECISIONS.md D6 names this component as the basis of the planned 'cosmos view' over vault notes and their links, which is not implemented.

### List view tab

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/App.jsx`

Flat card list of nodes.

**Entry points**

- `View toggle 'List'`
  - does: Shows one card per node with title (else summary[:50], else 'Untitled'), path joined with ' > ', and confidence %. Clicking a card opens NodeDetail with the node object.
  - changes: nothing

**Inputs**

- nodes list

**Outputs**

- list UI

**Invoked by**

- Frontend SPA

**Invokes**

- NodeDetail modal

### SearchBar

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/components/SearchBar.jsx`, `archive/frontend/src/App.jsx`

Header search box ('Search knowledge...').

**Entry points**

- `Submit search form -> onSearch(query)`
  - does: An empty query reloads all nodes (GET /api/nodes). Otherwise it calls GET /api/search?q= and replaces the node list with the results. On failure it shows the toast 'Search failed'.
  - changes: local node list

**Inputs**

- query text

**Outputs**

- filtered node list

**Depends on**

- lucide-react

**Invoked by**

- User

**Invokes**

- Search API
- Nodes API

**Notes**

ILIKE text search only. The header metrics are not updated after a search.

### NodeDetail modal

`web-app` · status `never-exercised`

Paths: `archive/frontend/src/components/NodeDetail.jsx`

Overlay showing one node's classification path, summary, extracted entities, creation time and id.

**Entry points**

- `Select a node in the Tree, Graph or List view`
  - does: Renders path chips joined by arrows, the summary, entity chips (only if any exist), created_at via toLocaleString, and node_id or id. The X button closes the modal.
  - changes: nothing

**Inputs**

- node object

**Outputs**

- modal UI

**Depends on**

- lucide-react

**Invoked by**

- Tree view tab
- Graph view tab
- List view tab

**Notes**

The onCreateLink prop is declared but never used, so there is no link-editing UI. The modal does not call api.getNode; it shows whatever object it is given. DECISIONS.md D6 plans for it to show 'Overview + Next Steps' for vault notes, which is not implemented.

### setup.sh (stack launcher)

`launcher` · status `never-exercised`

Paths: `archive/setup.sh`

One-shot bash script that checks prerequisites, brings up the docker-compose stack, then prints service status and access URLs.

**Entry points**

- `chmod +x setup.sh && ./setup.sh`
  - does: Runs with set -e. Checks for the docker CLI, for docker-compose or 'docker compose version', and that 'docker info' succeeds. If GROQ_API_KEY is empty and ./.env exists, runs export $(cat .env | grep -v '^#' | xargs). Then runs 'mkdir -p postgres_data neo4j_data redis_data', 'docker-compose pull', 'docker-compose up --build -d' and 'sleep 5'. Probes 'docker-compose exec -T postgres pg_isready -U postgres', 'curl -s http://localhost:7474', 'docker-compose exec -T redis redis-cli ping', 'curl -s http://localhost:8000/health' and 'curl -s http://localhost:3000', printing Ready or Starting for each.
  - changes: Creates the directories postgres_data, neo4j_data and redis_data in the cwd. Pulls and builds Docker images. Creates containers and named volumes. Starts services detached.

**Inputs**

- GROQ_API_KEY from the environment or ./.env

**Outputs**

- console status report, access URLs and a list of useful commands

**Reads**

- .env (exported into the shell, only if GROQ_API_KEY is unset; no archive/.env exists)

**Writes**

- ./postgres_data, ./neo4j_data, ./redis_data directories
- Docker images, containers, volumes

**Depends on**

- bash
- Docker Engine 20.10+ (per docs)
- Docker Compose 2.0+ (per docs)
- docker-compose binary
- curl

**Environment and secret names (names only)**

- GROQ_API_KEY

**Gates and checkpoints**

- Exits 1 if docker is missing, compose is missing or the daemon is not running
- Exits 1 if GROQ_API_KEY is empty or equals the placeholder 'gsk_your_key_here'
- The status probes after the fixed 5s sleep are informational only and do not block

**Invoked by**

- User (DEPLOY.md Step 3, ENGINE-README.md Setup step 3)

**Invokes**

- docker-compose stack

**Notes**

The prerequisite check accepts either 'docker-compose' or 'docker compose', but every later command calls 'docker-compose' only. The directories it creates are not used by compose, which uses named volumes. It prints the useful commands docker-compose logs -f, docker-compose down, docker-compose restart and docker-compose down -v (full reset), plus the Neo4j Browser login (a default credential, not reproduced here). With no archive/.env present, GROQ_API_KEY must be exported in the shell.

### docker-compose stack

`launcher` · status `never-exercised`

Paths: `archive/docker-compose.yml`

Full local orchestration of the 7 services.

**Entry points**

- `docker-compose up --build`
  - does: Builds the backend and frontend and starts all services in the foreground (DEPLOY.md / ENGINE-README.md manual start)
  - changes: Docker images, containers, named volumes postgres_data, neo4j_data, redis_data
- `docker-compose ps`
  - does: Lists containers (DEPLOY.md verification)
  - changes: nothing
- `docker-compose logs -f backend`
  - does: Tails backend logs (DEPLOY.md, setup.sh)
  - changes: nothing
- `docker-compose logs -f frontend`
  - does: Tails frontend logs (DEPLOY.md)
  - changes: nothing
- `docker-compose logs -f [service]`
  - does: Tails the logs of a service, or of all services when none is given (DEPLOY.md, ENGINE-README.md, setup.sh)
  - changes: nothing
- `docker-compose down`
  - does: Stops and removes containers (printed by setup.sh)
  - changes: Removes containers
- `docker-compose restart`
  - does: Restarts services (printed by setup.sh)
  - changes: Container state
- `docker-compose down -v`
  - does: Full reset. ENGINE-README warns that it 'removes data!'
  - changes: Deletes containers and named volumes
- `docker system prune -f`
  - does: Cleans the Docker cache (ENGINE-README troubleshooting)
  - changes: Deletes unused Docker objects
- `docker-compose exec backend pytest`
  - does: Backend test command documented in ENGINE-README. No tests exist and pytest is not in requirements.txt.
  - changes: nothing

**Inputs**

- env interpolation: GROQ_API_KEY, OPENAI_API_KEY, PINECONE_API_KEY, SECRET_KEY, POSTGRES_PASSWORD, NEO4J_PASSWORD

**Outputs**

- Services: postgres (postgres:15-alpine, 5432:5432, DB living_archive, volume postgres_data); neo4j (neo4j:5-community, 7474:7474 and 7687:7687, NEO4J_PLUGINS apoc, volume neo4j_data); redis (redis:7-alpine, 6379:6379, volume redis_data); backend (build ./backend, 8000:8000, bind mount ./backend:/app); celery_worker (build ./backend, 'celery -A app.tasks.reorganization worker --loglevel=info'); celery_beat (build ./backend, 'celery -A app.tasks.reorganization beat --loglevel=info'); frontend (build ./frontend, 3000:80)

**Reads**

- archive/backend/
- archive/frontend/
- shell env (and a .env in the compose project dir, per DEPLOY.md) for interpolation

**Writes**

- Docker named volumes postgres_data, neo4j_data, redis_data

**Depends on**

- Docker Engine 20.10+
- Docker Compose 2.0+
- 4GB+ RAM (DEPLOY.md)

**Environment and secret names (names only)**

- GROQ_API_KEY
- OPENAI_API_KEY
- PINECONE_API_KEY
- SECRET_KEY
- POSTGRES_PASSWORD
- NEO4J_PASSWORD
- POSTGRES_USER (postgres container)
- POSTGRES_DB (postgres container)
- NEO4J_AUTH (neo4j container)
- NEO4J_PLUGINS (neo4j container)
- POSTGRES_SERVER
- NEO4J_URI
- CELERY_BROKER_URL

**Gates and checkpoints**

- postgres healthcheck pg_isready (5s interval, 5s timeout, 5 retries)
- neo4j healthcheck wget --spider :7474 (10s interval, 10s timeout, 5 retries)
- backend waits for postgres healthy, neo4j healthy and redis started
- celery_worker depends_on redis, postgres, neo4j (start order only); celery_beat depends_on redis; frontend depends_on backend

**Invoked by**

- setup.sh
- User

**Invokes**

- Backend container image
- Frontend container image
- Reorganization tasks
- Relational store
- Graph store

**Notes**

File version '3.8'. Defaults exist for SECRET_KEY, POSTGRES_PASSWORD and NEO4J_PASSWORD (values not reproduced here). GROQ_API_KEY has no default. The backend bind mount ./backend:/app overlays the image's copied source. DECISIONS.md D8 notes that Docker Desktop on the 16 GB target laptop competes with Ollama and Adobe, and D1 rejects this seven-service stack.

### render.yaml (Render Blueprint)

`ci` · status `never-exercised`

Paths: `archive/render.yaml`

Cloud deployment blueprint for Render.com (DEPLOY.md Option 1: create a Blueprint from render.yaml, add env vars from .env, deploy).

**Entry points**

- `Render Blueprint from archive/render.yaml`
  - does: Declares: pserv living-archive-postgres (postgres:15-alpine, disk postgres-data 10GB at /var/lib/postgresql/data, POSTGRES_PASSWORD generateValue); pserv living-archive-neo4j (neo4j:5-community, disk neo4j-data 10GB at /data, NEO4J_AUTH literal); pserv living-archive-redis (redis:7-alpine); web living-archive-backend (docker, rootDir backend, ./Dockerfile); web living-archive-frontend (docker, rootDir frontend, ./Dockerfile, no envVars); worker living-archive-celery (docker, rootDir backend, dockerCommand 'celery -A app.tasks.reorganization worker --loglevel=info')
  - changes: Render cloud resources

**Inputs**

- GROQ_API_KEY (sync: false, entered manually, for both backend and worker)

**Outputs**

- 6 Render services

**Reads**

- archive/backend/Dockerfile
- archive/frontend/Dockerfile

**Writes**

- Render services and disks

**Depends on**

- Render.com account

**Environment and secret names (names only)**

- GROQ_API_KEY
- SECRET_KEY (generateValue)
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_DB
- POSTGRES_SERVER (fromService property host)
- NEO4J_AUTH
- NEO4J_URI (fromService property host)
- CELERY_BROKER_URL

**Gates and checkpoints**

- GROQ_API_KEY sync:false means it must be supplied manually in the Render dashboard

**Invoked by**

- User via Render dashboard

**Invokes**

- Backend container image
- Frontend container image
- Reorganization tasks

**Notes**

There is no beat service, so the daily-reorg schedule never fires on Render. Backend NEO4J_URI is the neo4j service's host property rather than a bolt:// URI. The backend CELERY_BROKER_URL has both fromService and a literal value redis://redis:6379/0; the worker has only that literal. Neither host 'redis' nor host 'backend' is defined on Render. The celery worker has no Postgres or Neo4j env. The backend gets no POSTGRES_USER, POSTGRES_DB or NEO4J_PASSWORD and falls back to the config.py defaults. The neo4j pserv has no APOC plugin. The frontend gets no VITE_API_URL, so its bundle defaults to http://localhost:8000/api, and its nginx proxy_pass http://backend:8000 targets a compose-only hostname. NEO4J_AUTH is a literal in the file (value not reproduced).

### Backend container image (Dockerfile + requirements.txt)

`launcher` · status `never-exercised`

Paths: `archive/backend/Dockerfile`, `archive/backend/requirements.txt`

Python 3.11 image for the API, the celery worker and celery beat.

**Entry points**

- `docker build ./backend (via compose 'build: ./backend' or render rootDir backend)`
  - does: FROM python:3.11-slim; WORKDIR /app; COPY requirements.txt .; RUN pip install --no-cache-dir -r requirements.txt; COPY . .; EXPOSE 8000; CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
  - changes: Docker image

**Inputs**

- requirements.txt: fastapi>=0.110, uvicorn[standard]>=0.27, python-multipart>=0.0.9, pydantic>=2.6, pydantic-settings>=2.2, sqlalchemy[asyncio]>=2.0, asyncpg>=0.29, python-jose[cryptography]>=3.3, passlib[bcrypt]>=1.7.4, celery>=5.3, redis>=5.0, neo4j>=5.17, openai>=1.12 (pinecone>=3.0 commented out)

**Outputs**

- image used by the backend, celery_worker and celery_beat services

**Reads**

- archive/backend/

**Depends on**

- Docker
- PyPI

**Invoked by**

- docker-compose stack
- render.yaml

**Invokes**

- Living Archive backend (FastAPI app)
- Reorganization tasks

**Notes**

Both files were newly written during consolidation because the deploy configs required them. requirements.txt line 2: 'NOT yet exercised: no install or run has been performed against this file.' DECISIONS.md D4: 'Neither has been installed or run.' All versions are lower bounds only (no pins, no lock file). pytest is not listed, although ENGINE-README.md documents 'docker-compose exec backend pytest', and no tests exist.

### Frontend container image (Dockerfile + nginx.conf)

`launcher` · status `never-exercised`

Paths: `archive/frontend/Dockerfile`, `archive/frontend/nginx.conf`

Multi-stage build of the SPA, served by nginx on port 80 with an /api reverse proxy.

**Entry points**

- `docker build ./frontend (compose 'build: ./frontend', ports 3000:80; render rootDir frontend)`
  - does: Stage 1 (node:20-alpine AS builder): COPY package*.json, 'npm ci', COPY ., 'npm run build'. Stage 2 (nginx:alpine): copies /app/dist to /usr/share/nginx/html and nginx.conf to /etc/nginx/conf.d/default.conf. EXPOSE 80. CMD nginx -g 'daemon off;'
  - changes: Docker image
- `nginx: listen 80; location / try_files $uri $uri/ /index.html; location /api proxy_pass http://backend:8000 with proxy_http_version 1.1, Upgrade/Connection 'upgrade', Host and proxy_cache_bypass`
  - does: SPA fallback, plus an API proxy to the backend container that can carry websocket upgrades
  - changes: nothing

**Inputs**

- archive/frontend/ source

**Outputs**

- static site on container port 80 (host 3000 in compose)

**Reads**

- archive/frontend/package*.json
- archive/frontend/

**Depends on**

- node:20-alpine
- nginx:alpine

**Invoked by**

- docker-compose stack
- render.yaml

**Invokes**

- Living Archive backend (FastAPI app) via the /api proxy

**Notes**

No package-lock.json exists under archive/frontend, but the build runs 'npm ci'. The Dockerfile declares no ARG or ENV for VITE_API_URL, and neither compose nor render sets it, so the bundle uses the default absolute http://localhost:8000/api. That means the /api proxy is bypassed.

### ENGINE-README.md

`doc` · status `partial`

Paths: `archive/ENGINE-README.md`

Engine overview: features, quick start, architecture diagram, API endpoint list, data flow, environment variable table, ports, troubleshooting, dev and test commands, production checklist.

**Entry points**

- `read`
  - does: Documents POST /api/auth/register, POST /api/auth/token, POST /api/ingest, GET /api/nodes, GET /api/nodes/{id}, GET /api/search?q=, GET /health. Environment table: GROQ_API_KEY (required), SECRET_KEY (required), POSTGRES_PASSWORD, NEO4J_PASSWORD, PINECONE_API_KEY, OPENAI_API_KEY. Ports: 3000, 8000, 5432, 7474, 7687, 6379.
  - changes: nothing

**Environment and secret names (names only)**

- GROQ_API_KEY
- SECRET_KEY
- POSTGRES_PASSWORD
- NEO4J_PASSWORD
- PINECONE_API_KEY
- OPENAI_API_KEY

**Invoked by**

- User

**Invokes**

- setup.sh
- docker-compose stack

**Notes**

Refers to items that do not exist in archive/: a LICENSE file, backend pytest tests, an 'npm test' script, a pgvector fallback and a 'living-archive' directory to cd into. Its /api/auth paths differ from the effective paths as written. It claims 'Vector Search', but /api/search is ILIKE only. Its SECRET_KEY default column disagrees with the docker-compose.yml and config.py defaults.

### DEPLOY.md

`doc` · status `partial`

Paths: `archive/DEPLOY.md`

Deployment guide: local Docker quick deploy, cloud options (Render, AWS ECS, DigitalOcean App Platform), verification steps, service diagram, troubleshooting.

**Entry points**

- `curl -X POST http://localhost:8000/api/ingest -H "Content-Type: application/json" -d '{"type":"knowledge_ingestion","content":{"raw_text":"Machine learning is a subset of artificial intelligence","timestamp":"2024-01-01T00:00:00Z","source":"manual_input"},"context":{"session_id":"test-session","user_preferences":{"auto_link":true,"language":"en"}}}'`
  - does: Documented AI classification smoke test
  - changes: None as written: it sends no Authorization header, so get_current_user rejects it with 401. With a token it would write to Postgres, Neo4j and optionally Pinecone.
- `curl http://localhost:8000/health`
  - does: Health check
  - changes: nothing

**Environment and secret names (names only)**

- GROQ_API_KEY

**Gates and checkpoints**

- Prerequisites: Docker Engine 20.10+, Docker Compose 2.0+, 4GB+ RAM

**Invoked by**

- User

**Invokes**

- setup.sh
- docker-compose stack
- render.yaml (Blueprint)

**Notes**

References ecs-task-definition.json and README.md, neither of which exists in archive/ (the README is now ENGINE-README.md). Step 1 says 'cd living-archive', but the directory is archive/. The 'Files Included' list says '.env - Environment variables (your Groq key included)', yet no .env exists under archive/. Per DECISIONS.md D5, a third-party key in this file was scrubbed, and Step 2 now shows a placeholder. Its port-conflict advice is to edit the compose port mappings.

## Usage flows

### Local stack bring-up (scripted)

1. Export GROQ_API_KEY in the shell (no archive/.env exists; setup.sh reads ./.env only if present). Optionally also export OPENAI_API_KEY, PINECONE_API_KEY, SECRET_KEY, POSTGRES_PASSWORD, NEO4J_PASSWORD.
2. cd archive && chmod +x setup.sh && ./setup.sh
3. setup.sh checks docker, compose, the daemon and GROQ_API_KEY, then runs docker-compose pull and docker-compose up --build -d, sleeps 5 s and probes each service
4. Wait 30-60 s (Neo4j startup), then open http://localhost:3000 (UI), http://localhost:8000/docs (API docs), http://localhost:7474 (Neo4j Browser)
5. Verify with docker-compose ps, curl http://localhost:8000/health and docker-compose logs -f backend
6. NOTE: never performed. README.md says archive/ has not been installed, built or started.

### Local development without Docker

1. cd archive/backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
2. uvicorn app.main:app --reload (needs a reachable Postgres and Neo4j at the configured POSTGRES_SERVER and NEO4J_URI; the defaults are the compose hostnames 'postgres' and 'neo4j')
3. cd archive/frontend && npm install && npm run dev (Vite on :5173, proxy /api -> http://localhost:8000; api.js still defaults to the absolute http://localhost:8000/api)
4. CORS already allows http://localhost:5173

### Register and sign in

1. The SPA loads. With no localStorage 'token', AuthModal renders.
2. Create Account: api.register -> POST /api/auth/register (the backend route as written is /api/auth/auth/register), then api.login
3. Sign In: api.login -> POST /api/auth/token with form username/password (as written: /api/auth/auth/token)
4. The backend verifies the bcrypt hash and returns an HS256 JWT (sub=user id, default 8-day expiry). The client stores it in localStorage 'token'.
5. The App switches to authenticated and calls GET /api/nodes (Bearer)

### Ingest knowledge (core pipeline)

1. User types text in the 'Ingest Knowledge' panel and clicks 'Process & Archive'
2. The SPA POSTs /api/ingest with a Bearer token and payload {type, content{raw_text,timestamp,source}, context{session_id,user_preferences}}
3. The auth dependency validates the JWT (401 otherwise); Pydantic validates the body (422 otherwise)
4. AI engine, via asyncio.gather but effectively sequential: generate_embedding (OpenAI text-embedding-3-small, or the md5 pseudo-vector) and classify (Groq llama-3.3-70b-versatile, fallback llama3-8b-8192, strict JSON)
5. If Pinecone is configured: query the top 5 neighbours. Neighbours scoring >0.8 add path-leaf suggestions (merged, deduplicated, max 5).
6. Insert the nodes row in Postgres and commit
7. BackgroundTasks after the response: Pinecone upsert (if configured) and Neo4j create_node (Concept chain Root->...->leaf with PARENT_OF, plus RELATES_TO to suggested concept names)
8. Response is IngestResponse. The UI prepends the node, shows the toast 'Classified: A > B > C' and updates the header metrics.

### Browse and search

1. The Tree tab (default) groups nodes client-side by classification path under 'Knowledge Root'
2. The Graph tab shows a d3 force layout of the nodes with no edges (links=[])
3. The List tab shows cards with path and confidence
4. Submitting the SearchBar calls GET /api/search?q= (ILIKE on content/summary/title, limit 20) and replaces the list. An empty query reloads GET /api/nodes.
5. Clicking a node opens the NodeDetail modal (path, summary, entities, created_at, id). From the Tree tab it receives a wrapper object, so most fields are blank.
6. The Neo4j graph can only be viewed directly in the Neo4j Browser at :7474

### Scheduled reorganization

1. celery_beat (compose only) sends app.tasks.reorganization.daily_reorganization every 86400 s via Redis
2. celery_worker executes it and returns the literal {status:'completed', recommendations:[]}
3. update_embeddings_batch is never scheduled or called
4. Stub: nothing is analysed or changed

### Render cloud deploy

1. Create a Render Blueprint from archive/render.yaml
2. Enter GROQ_API_KEY manually (sync:false) for the backend and the worker. SECRET_KEY and POSTGRES_PASSWORD are generated.
3. Render builds the backend/ and frontend/ Dockerfiles and starts the postgres, neo4j and redis private services plus the celery worker
4. No beat service, so the reorganization schedule does not run. The frontend has no VITE_API_URL and its nginx proxies to a compose-only 'backend' host, so how it reaches the API on Render is unresolved.

## Relationships

| From | Relation | To |
|---|---|---|
| Living Archive frontend SPA (React + Vite) | all backend calls go through api.js | Frontend API client (api.js) |
| AuthModal tab (Sign In / Create Account) | calls /api/auth/register and /api/auth/token; the backend routes as written are /api/auth/auth/* (path mismat… | Auth API (/api/auth) |
| Ingest Knowledge panel | submits the knowledge_ingestion payload | Ingest API (POST /api/ingest) |
| SearchBar | GET /api/search?q= | Search API (GET /api/search) |
| Living Archive frontend SPA (React + Vite) | loadNodes on auth, on refresh and on an empty search | Nodes API (GET /api/nodes, GET /api/nodes/{node_id}) |
| Ingest API (POST /api/ingest) | requires a get_current_user Bearer JWT | Auth API (/api/auth) |
| Nodes API (GET /api/nodes, GET /api/nodes/{node_id}) | the list route requires get_current_user; the single-node route does not | Auth API (/api/auth) |
| Ingest API (POST /api/ingest) | classify + generate_embedding via asyncio.gather (effectively sequential) | AI engine (Groq classification + embeddings) |
| Ingest API (POST /api/ingest) | query top_k=5 before the insert; upsert as a BackgroundTask | Vector store (Pinecone, optional) |
| Ingest API (POST /api/ingest) | create_node as a BackgroundTask (write-only) | Graph store (Neo4j) |
| Ingest API (POST /api/ingest) | inserts the nodes row; counts store_size | Relational store (PostgreSQL via SQLAlchemy async) |
| Living Archive backend (FastAPI app) | create_all tables at startup | Relational store (PostgreSQL via SQLAlchemy async) |
| Living Archive backend (FastAPI app) | closes the driver at shutdown | Graph store (Neo4j) |
| Graph view tab | does NOT read it; links={[]} is passed and no edges are rendered | Graph store (Neo4j) |
| Tree view tab | onSelect passes the tree-leaf wrapper, not the node | NodeDetail modal |
| WebSocket protocol (WebSocketManager) | intended ws://localhost:8000/ws; no such backend route; client instantiation commented out | Living Archive backend (FastAPI app) |
| Reorganization tasks (Celery worker + beat) | runs as the celery_worker and celery_beat services over Redis broker redis://redis:6379/0 | docker-compose stack |
| setup.sh (stack launcher) | docker-compose pull; docker-compose up --build -d; health probes | docker-compose stack |
| docker-compose stack | build ./backend for backend, celery_worker, celery_beat | Backend container image (Dockerfile + requirements.txt) |
| docker-compose stack | build ./frontend, ports 3000:80 | Frontend container image (Dockerfile + nginx.conf) |
| render.yaml (Render Blueprint) | rootDir backend for the web service and the celery worker | Backend container image (Dockerfile + requirements.txt) |
| render.yaml (Render Blueprint) | rootDir frontend web service | Frontend container image (Dockerfile + nginx.conf) |
| Frontend container image (Dockerfile + nginx.conf) | nginx location /api proxy_pass http://backend:8000 (bypassed by the absolute default API base) | Living Archive backend (FastAPI app) |
| Living Archive frontend SPA (React + Vite) | Vite dev proxy /api -> http://localhost:8000; default API_BASE_URL http://localhost:8000/api | Living Archive backend (FastAPI app) |
| DEPLOY.md | documents launch via chmod +x setup.sh && ./setup.sh | setup.sh (stack launcher) |
| DEPLOY.md | its verification curl omits the Bearer token the route requires | Ingest API (POST /api/ingest) |
| DECISIONS.md (D1) | rejects the cloud stack; the transport is to move to the local Ollama endpoint per skills/local_rag_orchestra… | AI engine (Groq classification + embeddings) |
| DECISIONS.md (D1) | needs a local equivalent | Graph store (Neo4j) |
| DECISIONS.md (D1) | needs a local equivalent (on-disk vector index); pinecone left commented out in requirements.txt | Vector store (Pinecone, optional) |
| DECISIONS.md (D1) | identifies them as stubs; local-first probably removes Redis/Celery | Reorganization tasks (Celery worker + beat) |
| DECISIONS.md (D3/D4) | provenance: consolidated from groot99-droid/crispy-engine; directory structure derived; Dockerfile and requir… | archive/ |
| DECISIONS.md (D5) | third-party gsk_ key scrubbed (it tripped GitHub push protection); secrets belong only in .env, which .gitign… | DEPLOY.md |
| DECISIONS.md (D6) | planned 'cosmos view' = GraphVisualization.jsx over vault notes and their links (not implemented) | Graph view tab |
| DECISIONS.md (D6) | planned to show Overview + Next Steps for the selected vault note (not implemented) | NodeDetail modal |
| DECISIONS.md (D8) | Docker Desktop on a 16 GB laptop competes with Ollama and Adobe; the local-first rewrite is now a memory requ… | docker-compose stack |
| README.md | 'What does not run yet' (lines 107-111): not installed, built, or started; line 50 describes archive/ as inde… | archive/ |
| Router.md | line 64 describes /archive/ as 'Indexes the vault for search + the cosmos view'; line 309: the vault is truth… | archive/ |
| hub/index.html | port collision: the hub instructs python3 -m http.server and http://localhost:8000/hub/, the same host port t… | Living Archive backend (FastAPI app) |
| OBSIDIAN.md | name collision: OBSIDIAN.md line 61 calls Creative-Writing/ (63 finished works) 'the Living Archive', which i… | archive/ |

**Open questions the files could not settle**

- NodeModel (archive/backend/app/models.py line 31) declares a column attribute named 'metadata'. SQLAlchemy's Declarative API reserves that name, so the module may fail at import. Nothing has been run, so this is unverified.
- Does Groq's OpenAI-compatible endpoint accept client.responses.create(..., max_tokens=1000) and return response.output_text? The repo cannot answer this, and nothing has been run.
- archive/frontend/Dockerfile runs 'npm ci', but there is no package-lock.json under archive/frontend. Whether the frontend image builds is unverified.
- GET /api/nodes/{node_id} and GET /api/search return raw SQLAlchemy ORM objects with no response_model. Whether they serialize cleanly is unverified.
- Is the doubled auth prefix (/api/auth + router prefix /auth -> /api/auth/auth/*) intentional? The docs and the frontend both expect /api/auth/*.
- The frontend's default API_BASE_URL is the absolute http://localhost:8000/api, and no build step sets VITE_API_URL, so the nginx /api proxy is always bypassed as configured. The intended production setting is not stated.
- render.yaml sets NEO4J_URI to the neo4j service's 'host' property rather than a bolt:// URI. The backend CELERY_BROKER_URL has both fromService and value, and the worker's literal broker host 'redis' does not exist on Render. There is no beat service. The celery worker gets no Postgres or Neo4j env. The frontend nginx proxies to the compose-only host 'backend'. How the Render deploy is meant to work is unknown.
- README.md (line 50) and Router.md (line 64) say archive/ 'indexes the vault for search + the cosmos view', and DECISIONS.md D6 names GraphVisualization.jsx/NodeDetail.jsx as the cosmos view. No code in archive/ reads the vault, though. This is the planned local-first target (D1/D6) and is not implemented.
- DEPLOY.md references ecs-task-definition.json, README.md and a 'living-archive' directory. ENGINE-README.md references LICENSE, pytest tests and 'npm test'. None of these exist in archive/.
- hub/index.html tells users to serve the repo with python3 -m http.server at localhost:8000, which collides with the backend's 8000:8000 mapping. The files do not say how the two should coexist.
- ENGINE-README.md, docker-compose.yml and config.py each give a different default for SECRET_KEY. Which one is authoritative is not stated (values not reproduced).

## What the verifier corrected

The second agent re-checked the first reading against source. These are the changes it made.

- **corrected**: Ingest runs ai_engine.generate_embedding and ai_engine.classify concurrently (asyncio.gather)
  - evidence: archive/backend/app/services/ai_engine.py lines 49-58 and 78-87 call the synchronous OpenAI client (client.responses.create, openai_client.embeddings.create) inside async defs with no await points, so asyncio.gather in archive/backend/app/api/ingest.py line 43 runs them one after the other.
- **corrected**: DEPLOY.md references a .env 'with your Groq key included'
  - evidence: archive/DEPLOY.md line 127 reads '`.env` - Environment variables (your Groq key included)'. No .env exists under archive/, archive/backend or archive/frontend (ls -la shows none).
- **corrected**: Graph view circle radius is 15+confidence*15
  - evidence: archive/frontend/src/components/GraphVisualization.jsx line 41: r = 15 + (d.confidence || 0.5) * 15. Ingest-local nodes carry classification.confidence, not confidence, so they get 0.5.
- **corrected**: Frontend container image input: VITE_API_URL at build time (optional)
  - evidence: archive/frontend/Dockerfile declares no ARG or ENV for VITE_API_URL, and neither docker-compose.yml nor render.yaml sets it for the frontend, so the bundle uses the default http://localhost:8000/api from archive/frontend/src/services/api.js line 1.
- **corrected**: docker-compose entry point 'docker-compose logs -f backend | docker-compose logs -f frontend | docker-compose logs -f [service]'
  - evidence: These are separate documented commands (DEPLOY.md lines 69-70 and 135, ENGINE-README.md line 138), not a shell pipeline. They are split into separate entry points, with docker-compose down and docker-compose restart added (printed by archive/setup.sh lines 137-140).
- **corrected**: Open question: is there an archive/.env? Glob did not list one
  - evidence: ls -la of archive/, archive/backend and archive/frontend shows no .env and no package-lock.json, so this is resolved rather than open. setup.sh (lines 47-51) therefore needs GROQ_API_KEY exported in the shell.
- **added**: archive/backend/app/services/__init__.py appears in no tool's paths
  - evidence: The file exists (0 bytes) and was added to the backend app paths. All four __init__.py files under archive/backend/app are 0 bytes.
- **added**: Frontend dependency list is complete
  - evidence: archive/frontend/package.json devDependencies also include @types/react ^18.2.55 and @types/react-dom ^18.2.19.
- **added**: (missing) favicon and unused CSS
  - evidence: archive/frontend/index.html line 5 links /vite.svg, but no public/ dir or vite.svg exists. archive/frontend/src/index.css defines .node-card, .animate-slide-in and .animate-pulse-glow, and grep finds no use of them.
- **added**: OAuth2PasswordBearer(tokenUrl='api/auth/token') noted only as the auth gate
  - evidence: archive/backend/app/api/auth.py line 16: the tokenUrl is relative and also differs from the effective /api/auth/auth/token route (line 18 prefix='/auth' plus main.py line 32 prefix '/api/auth').
- **added**: Ingest request gates
  - evidence: archive/backend/app/schemas.py: type is Literal with a default (optional), source defaults to manual_input, and context.session_id is required. ingest.py line 91 ExtractedEntity(**e) and ClassificationResult confidence ge=0 le=1 turn malformed LLM output into a 500. 401 comes from get_current_user and 422 from validation.
- **added**: celery_worker env
  - evidence: archive/docker-compose.yml lines 70-76 also pass POSTGRES_SERVER, POSTGRES_PASSWORD, NEO4J_URI and NEO4J_PASSWORD to celery_worker; the stubs in reorganization.py never use them. Neither compose nor render sets CELERY_RESULT_BACKEND (config.py default only).
- **added**: render.yaml notes
  - evidence: archive/render.yaml: the frontend web service has no envVars (no VITE_API_URL); the neo4j pserv has no NEO4J_PLUGINS; the backend gets no POSTGRES_USER, POSTGRES_DB or NEO4J_PASSWORD; the worker CELERY_BROKER_URL is a literal pointing at host 'redis'. archive/frontend/nginx.conf proxies to host 'backend', which only exists in compose.
- **added**: No code in archive/ implements a 'cosmos view' (open question)
  - evidence: DECISIONS.md D6 (lines 165-167) names GraphVisualization.jsx and NodeDetail.jsx as the planned cosmos view over vault notes and links (Overview + Next Steps). This is a plan and is not implemented in archive/.
- **added**: (missing) name collision
  - evidence: OBSIDIAN.md line 61 labels Creative-Writing/ as 'the Living Archive, 63 finished works'. That is unrelated to this engine.
- **added**: ENGINE-README.md feature claims
  - evidence: archive/ENGINE-README.md line 10 claims 'Vector Search: Semantic similarity search (with Pinecone or fallback)', but archive/backend/app/api/search.py is ILIKE only. Lines 26 and DEPLOY.md line 12 say 'cd living-archive', and no such directory exists.
- **corrected**: DEPLOY.md curl 'Would write to Postgres, Neo4j and optionally Pinecone'
  - evidence: As written it has no Authorization header, and archive/backend/app/api/ingest.py line 34 depends on get_current_user, which raises 401 (auth.py lines 33-44). So the curl as documented mutates nothing.
- **corrected**: README.md lines 107-111, DECISIONS.md D1/D3/D4/D5/D8, Router.md line 64, hub/index.html port 8000, requirements.txt line 2 quotes
  - evidence: All confirmed verbatim or in substance: README.md lines 107-111, DECISIONS.md lines 8-39, 72-117, 121-138 and 329-331, Router.md lines 64 and 309, hub/index.html lines 33-34, archive/backend/requirements.txt line 2. They are kept unchanged; the verdict records that they were checked.
- **unverifiable**: The metadata column name on NodeModel is reserved in SQLAlchemy Declarative and may break import
  - evidence: archive/backend/app/models.py line 31 declares metadata = Column(JSON). Whether this fails depends on SQLAlchemy behaviour that the repo cannot confirm and nothing has been run. It stays in open_questions.
