import streamlit as st
import requests
import json
import sqlite3
import time
from datetime import datetime
from pathlib import Path
import base64

# ----------------- Configuration -----------------
DB_PATH = Path(__file__).parent / "memory.db"
N8N_WEBHOOK_URL_PROD = "http://localhost:5678/webhook/paper-search"
N8N_WEBHOOK_URL_TEST = "http://localhost:5678/webhook-test/paper-search"
CURRENT_WEBHOOK = N8N_WEBHOOK_URL_PROD

# ----------------- Database -----------------
def get_conn():
    # Adding timeout to prevent 'database is locked' errors during n8n writes
    conn = sqlite3.connect(DB_PATH, timeout=20.0, check_same_thread=False)
    return conn

def get_latest_search_from_db(min_id=0):
    """Fetch the most recent search log from the DB, ensuring it is newer than min_id."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            """
            SELECT id, query, search_query, top_results, created_at
            FROM search_history
            WHERE id > ?
            ORDER BY id DESC
            LIMIT 1
            """, (min_id,)
        )
        row = cur.fetchone()
        conn.close()
        if row:
            return {
                "id": row[0],
                "query": row[1],
                "search_query": row[2],
                "top_results": json.loads(row[3]) if row[3] else [],
                "created_at": row[4],
            }
    except Exception:
        pass
    return None

def get_max_id():
    """Get the current maximum ID in the search_history table."""
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM search_history")
        row = cur.fetchone()
        conn.close()
        return row[0] if row and row[0] else 0
    except:
        return 0

def get_favorites():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT title, link, added_at FROM favorites ORDER BY added_at DESC")
        rows = cur.fetchall()
        conn.close()
        return [{"title": r[0], "link": r[1], "added_at": r[2]} for r in rows]
    except:
        return []

def get_history(limit=50):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT query, search_query, created_at FROM search_history ORDER BY id DESC LIMIT ?", (limit,))
        rows = cur.fetchall()
        conn.close()
        return [{"query": r[0], "search_query": r[1], "created_at": r[2]} for r in rows]
    except:
        return []

# ----------------- UI & CSS -----------------
st.set_page_config(page_title="Paper Search Agent", page_icon="🔬", layout="wide")

# LOAD FONTS & GLOBAL STYLES
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;800&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
<style>
    /* --- Global & Background --- */
    html, body, .stApp {
        font-family: 'Inter', sans-serif;
        background-color: #FAFAFA;
    }
    
    /* --- Big Bold Navigation --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 15px;
        background-color: #FFFFFF;
        padding: 20px 10px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.03);
        margin-bottom: 2rem;
        display: flex;
        justify-content: center;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 80px; 
        flex-grow: 1;
        border: none !important;
        background-color: transparent;
        display: flex;
        justify-content: center;
        text-align: center;
    }
    
    /* Target the text wrapper directly */
    .stTabs [data-baseweb="tab"] p, 
    .stTabs [data-baseweb="tab"] div {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.7rem !important; /* BASE SIZE */
        font-weight: 700 !important;
        color: #94A3B8 !important;
    }
    
    /* Active State Targeting */
    .stTabs [aria-selected="true"] {
        border-bottom: 4px solid #2563EB !important;
    }

    .stTabs [aria-selected="true"] p, 
    .stTabs [aria-selected="true"] div {
        color: #2563EB !important;
        font-weight: 800 !important;
        font-size: 2.1rem !important; /* ACTIVE SIZE */
    }
    
    /* --- Hero Section --- */
    .hero-container {
        position: relative;
        background: linear-gradient(135deg, #EFF6FF 0%, #FFFFFF 100%);
        border: 1px solid #DBEAFE;
        border-radius: 20px;
        padding: 5rem 3rem; /* Expanded padding */
        text-align: center;
        margin-bottom: 4rem;
        box-shadow: 0 10px 30px -10px rgba(37, 99, 235, 0.1);
        overflow: hidden;
    }
    
    /* Background Image Overlay */
    /* ... (Style unchanged for internal elements) ... */
    .hero-bg-img {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 120%;
        opacity: 0.1; 
        pointer-events: none;
        z-index: 0;
        filter: grayscale(100%);
    }
    
    .hero-content {
        position: relative;
        z-index: 1;
    }
    
    .hero-title {
        font-family: 'Outfit', sans-serif;
        font-size: 5rem; /* INCREASED SIZE */
        font-weight: 800;
        background: linear-gradient(90deg, #1E3A8A 0%, #3B82F6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        letter-spacing: -0.03em;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.8rem; /* INCREASED SIZE */
        color: #475569;
        font-weight: 500;
        margin-bottom: 3rem;
        max-width: 900px;
        margin-left: auto;
        margin-right: auto;
        line-height: 1.6;
    }

    /* --- Paper Cards (Rich & Alive) --- */
    /* ... (Wrapper styles unchanged) ... */
    .paper-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 16px;
        padding: 30px; /* More padding */
        height: 100%;
        position: relative;
        overflow: hidden;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        flex-direction: column;
    }
    
    .paper-card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; width: 6px; height: 100%;
        background: linear-gradient(to bottom, #3B82F6, #60A5FA);
    }
    
    .paper-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border-color: #93C5FD;
    }
    
    .card-type {
        font-size: 0.9rem; /* INCREASED SIZE */
        font-weight: 800;
        text-transform: uppercase;
        color: #94A3B8;
        letter-spacing: 0.1em;
        margin-bottom: 12px;
    }
    
    .card-title {
        font-family: 'Outfit', sans-serif;
        font-size: 1.6rem; /* INCREASED SIZE */
        font-weight: 700;
        color: #0F172A;
        text-decoration: none;
        margin-bottom: 16px;
        line-height: 1.35;
    }
    
    .card-title:hover {
        color: #2563EB;
        text-decoration: underline;
    }
    
    .metrics-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    
    .metric-pill {
        background: #F1F5F9;
        padding: 6px 14px;
        border-radius: 8px;
        font-size: 1rem; /* INCREASED SIZE */
        font-weight: 600;
        color: #475569;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* --- Hide Streamlit Chrome --- */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
</style>
""", unsafe_allow_html=True)

# ----------------- Main App Logic -----------------

def main():
    global CURRENT_WEBHOOK
    
    # Main Tab Navigation
    tab_search, tab_fav, tab_history, tab_settings = st.tabs([
        "🔍 Research Search", "⭐ Paper Collection", "📜 Search History", "⚙️ Engine & Config"
    ])

    # --- SIDEBAR (Persistent Controls) ---
    with st.sidebar:
        st.title("⚙️ System Control")
        st.markdown("Use this to fix stuck results or clear corrupted data.")
        if st.button("☢️ Nuclear Reset", help="Wipe all history and clear stuck results", width="stretch"):
            clear_all_history()
            st.session_state.clear()
            # We also want to clear any rerun buffers
            if 'rerun_query' in st.session_state: del st.session_state['rerun_query']
            if 'auto_run_search' in st.session_state: del st.session_state['auto_run_search']
            st.success("Database and Cache Wiped!")
            st.rerun()
        st.divider()
        st.info("Current Engine: **n8n Orchestrator**")
        st.caption(f"Endpoint: `{st.session_state.get('engine_url', CURRENT_WEBHOOK)}`")


    # --- TAB 1: SEARCH ---
    with tab_search:
        # Load Pipeline Image for Background
        try:
            import base64
            with open("pipeline.png", "rb") as f:
                img_data = f.read()
            b64_img = base64.b64encode(img_data).decode()
            bg_image_html = f'<img src="data:image/png;base64,{b64_img}" class="hero-bg-img" />'
        except:
            bg_image_html = "" # Fallback if image missing

        # Hero Section with Background Overlay
        st.markdown(f"""
        <div class="hero-container">
            {bg_image_html}
            <div class="hero-content">
                <div class="hero-title">Discover Knowledge.</div>
                <div class="hero-subtitle">
                    The advanced retrieval agent that connects ArXiv, Google Scholar, and Semantic Web into one powerful pipeline.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Search Bar (Centered & Large)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            st.markdown("### 👇 **Start your research here:**")
            
            # Check for rerun query
            default_query = st.session_state.get('rerun_query', "")
            auto_run_flag = st.session_state.get('auto_run_search', False)
            
            # CACHE BUSTER: We change the widget key if a rerun is triggered 
            # to force Streamlit to recreate the input field.
            widget_key = "search_bar_input"
            if auto_run_flag:
                widget_key = f"search_bar_{int(time.time())}"

            query_input = st.text_input(
                "Search Query", 
                value=default_query, 
                placeholder="e.g. 'Transformer architectures alignment 2024'", 
                label_visibility="collapsed",
                key=widget_key
            )
            
            if default_query:
                st.session_state['rerun_query'] = ""
                st.session_state['auto_run_search'] = True

            run_search = st.button("🔎 Search Papers", type="primary", width="stretch")
            
        # Execute search
        should_search = False
        if run_search and query_input:
            should_search = True
            st.session_state['auto_run_search'] = False
        elif auto_run_flag and query_input:
            should_search = True
            st.session_state['auto_run_search'] = False
            
        if should_search:
            # IMMEDIATELY clear results from view so user doesn't see old data
            st.session_state['active_results'] = None
            res = handle_search(query_input)
            if res:
                st.session_state['active_results'] = res
            st.rerun()

        # --- RESULTS DISPLAY ---
        if st.session_state.get('active_results'):
            res = st.session_state['active_results']
            st.divider()
            st.markdown(f"### 🎯 Results for: *{res['query']}*")
            
            display_structured_results(res, res['query'])
            
            if st.button("🗑️ Clear Results & Search Again"):
                st.session_state['active_results'] = None
                st.session_state['last_raw_response'] = None
                st.rerun()

        # --- ONBOARDING / CONNECTION CHECK ---
        if not query_input:
            with st.expander("🔌 First Time Setup Guide (Click to Expand)", expanded=False):
                st.markdown("""
                ### 👋 Welcome to Research Agent!
                To use this app, you need to have the **n8n neural backend** running on your machine.
                
                **1. Ensure n8n is running:**
                - Open your n8n dashboard (usually `http://localhost:5678`).
                - Make sure the **Paper Search Agent** workflow is **Active** (Green toggle).
                
                **2. Verify Connection:**
                The app is currently trying to connect to: 
                """, unsafe_allow_html=True)
                st.code(CURRENT_WEBHOOK, language="text")
                
                st.markdown("""
                If your n8n is on a different URL (e.g., Cloud or Docker), go to the **⚙️ Engine & Config** tab above to update it.
                """)
                
                if st.button("Test Connection Now"):
                    try:
                        # quick ping with empty query just to check 404 vs connection error
                        requests.post(CURRENT_WEBHOOK, json={"query": "ping"}, timeout=5)
                        st.success("✅ Connection Successful! You are ready to search.")
                    except Exception as e:
                        st.error(f"❌ Connection Failed: {e}")
                        st.info("Tip: Go to the '⚙️ Engine & Config' tab to fix your URL.")

        if query_input:
           pass # Handled above

    # --- TAB 2: FAVORITES ---
    with tab_fav:
        render_favorites_page()

    # --- TAB 3: HISTORY ---
    with tab_history:
        render_history_page()

    with tab_settings:
        st.header("⚙️ Engine & Config")
        st.markdown("Configure which n8n backend this app talks to.")

        # Load current value into session
        if "engine_url" not in st.session_state:
            st.session_state["engine_url"] = CURRENT_WEBHOOK

        new_url = st.text_input(
            "n8n Webhook URL",
            value=st.session_state["engine_url"],
            placeholder="http://localhost:5678/webhook/paper-search"
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save Engine URL"):
                st.session_state["engine_url"] = new_url
                CURRENT_WEBHOOK = new_url
                st.success(f"Engine updated to:\n{new_url}")

        with col2:
            if st.button("↩️ Reset to Default"):
                st.session_state["engine_url"] = N8N_WEBHOOK_URL_PROD
                CURRENT_WEBHOOK = N8N_WEBHOOK_URL_PROD
                st.info("Reset to default production webhook.")

def render_paper_card(result):
    """Renders a Bold, Graphical Grid Card."""
    title = result.get('title', 'Untitled Result')
    link = result.get('link', '#')
    source = result.get('source', 'WEB').upper().replace('_', ' ')
    year = result.get('year', 'N/A')
    cited = result.get('cited_by', '0')
    snippet = result.get('snippet', 'No detailed abstract available for this paper.')
    
    # Graphic Icon based on source
    icon = "📄"
    if "arxiv" in source.lower(): icon = "⚛️"
    elif "scholar" in source.lower(): icon = "🎓"
    
    # COMPACT HTML to avoid Markdown code-block interpretation
    return f"""
    <div class="paper-card">
        <div class="card-type">{icon} {source}</div>
        <a href="{link}" target="_blank" class="card-title">{title}</a>
        <div class="metrics-row">
            <div class="metric-pill">📅 {year}</div>
            <div class="metric-pill">💬 {cited} Citations</div>
        </div>
        <div style="font-size: 0.9rem; color: #64748B; line-height: 1.5; flex-grow: 1;">
            {snippet[:200]}...
        </div>
        <a href="{link}" target="_blank" style="display: block; margin-top: 16px; text-align: center; background: #EFF6FF; color: #2563EB; padding: 8px; border-radius: 8px; text-decoration: none; font-weight: 600; font-size: 0.9rem;">
            Read Full Paper →
        </a>
    </div>
    """.replace('\n', '').replace('    ', '')


def handle_search(query):
    # --- GET PRE-SEARCH ANCHOR ---
    # We find the current max ID in the DB so we only look for IDs > this one.
    # This is the ONLY way to guarantee we don't pick up old cached results.
    if not query or query.strip() == "[object Object]" or query.strip().lower() == "object":
        st.error("Blocked corrupted query metadata. Please type a fresh search.")
        return
    anchor_id = None
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT MAX(id) FROM search_history")
        row = cur.fetchone()
        anchor_id = row[0] if (row and row[0] is not None) else 0
        conn.close()
    except Exception as e:
        st.error(f"❌ Database Access Error: {e}. Please ensure memory_api.py is not locking the file.")
        return 

    if anchor_id is None:
        anchor_id = 0
        
    st.markdown(f"### 🔎 Analyzing: *{query}*")
    search_start_time = datetime.utcnow().isoformat()
    
    with st.status("🚀 Launching Agents...", expanded=True) as status:
        st.write("📡 Connecting to Neural Backend...")
        try:
            target_url = st.session_state.get("engine_url", CURRENT_WEBHOOK)
            payload = {
                "query": query,
                "request_id": f"req_{int(time.time())}",
                "timestamp": search_start_time
            }
            response = requests.post(target_url, json=payload, timeout=90)

            if response.status_code != 200:
                st.error(f"Workflow error {response.status_code} at {target_url}")
                return None
                
            if response.status_code == 200:
                st.write(f"✅ Search complete. Analyzing results...")
                
                # Poll DB for the specific record created after anchor_id
                found_result = None
                polling_place = st.empty() # Placeholder for status updates
                
                with st.spinner("⏳ Wait! Syncing search results..."):
                    for i in range(25):  # up to ~25s
                        time.sleep(1)
                        try:
                            conn = get_conn()
                            cur = conn.cursor()
                            cur.execute("""
                                SELECT id, query, search_query, top_results, created_at
                                FROM search_history
                                WHERE id > ?
                                ORDER BY id ASC
                                LIMIT 1
                            """, (anchor_id,))
                            row = cur.fetchone()
                            conn.close()

                            if row:
                                papers_data = json.loads(row[3]) if row[3] else []
                                found_result = {
                                    "id": row[0],
                                    "query": row[1],
                                    "search_query": row[2],
                                    "top_results": papers_data,
                                    "created_at": row[4],
                                }
                                break
                            else:
                                if i % 5 == 0:
                                    polling_place.info(f"⏳ Polling DB (attempt {i+1}/25) — no new rows > {anchor_id} yet")
                        except Exception as e:
                            polling_place.write(f"⚠️ DB poll error: {e}")
                
                if found_result:
                    status.update(label=f"Insight Generated (ID: {found_result['id']})", state="complete", expanded=False)
                    return found_result
                else:
                    # FALLBACK: If DB write fails or lags too much, show raw response
                    status.update(label="Sync Timeout - Showing Raw Output", state="complete", expanded=False)
                    return None
            else:
                st.error(f"Workflow Connection Error ({response.status_code})")
                return None
        except Exception as e:
            st.error(f"Search Interrupted: {str(e)}")
            return None

def display_structured_results(data, query):
    results = data.get("top_results", [])
    if not results:
        st.warning("No results found.")
        return

    # ---- YEAR FALLBACK WARNING ----
    # If backend had to ignore year filter, it marked papers with year_warning = true
    if any(r.get("year_warning") for r in results):
        # extract year from query for nicer message
        import re
        m = re.search(r"\b(19|20)\d{2}\b", query)
        year_txt = m.group(0) if m else "that year"
        st.warning(f"No papers found exactly for {year_txt}. Showing closest matches instead.")
    
    # GRID LAYOUT for cards
    # We will create rows of 2 columns
    for i in range(0, len(results), 2):
        col1, col2 = st.columns(2)
        
        # Card 1
        with col1:
            st.markdown(render_paper_card(results[i]), unsafe_allow_html=True)
            
        # Card 2 (if exists)
        if i + 1 < len(results):
            with col2:
                st.markdown(render_paper_card(results[i+1]), unsafe_allow_html=True)

def render_favorites_page():
    st.markdown("### ⭐ Your Collection")
    favs = get_favorites()
    if not favs:
        st.info("No favorites yet.")
    else:
        for f in favs:
            st.write(f"- [{f['title']}]({f['link']})")

# --- History Logic ---
def delete_history_item(history_id):
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM search_history WHERE id = ?", (history_id,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def clear_all_history():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("DELETE FROM search_history")
        conn.commit()
        conn.close()
        return True
    except:
        return False

def render_history_page():
    st.markdown("### 📜 Research Log")
    
    # Clean up layout
    col1, col2, col3 = st.columns([3, 2, 1])
    with col1:
        st.caption("Review your past queries. Click to re-run.")
    with col2:
        if st.button("🧹 Clean Corrupted", help="Remove entries with invalid data"):
            try:
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("""
                    DELETE FROM search_history 
                    WHERE query LIKE '%object%' 
                    OR search_query LIKE '%object%'
                    OR LENGTH(search_query) < 3
                """)
                deleted = cur.rowcount
                conn.commit()
                conn.close()
                st.success(f"✅ Cleaned {deleted} corrupted entries")
                st.rerun()
            except Exception as e:
                st.error(f"Cleanup failed: {e}")
    with col3:
        if st.button("🗑️ Clear All", type="secondary"):
            if clear_all_history():
                st.success("History cleared.")
                st.rerun()

    # Get FULL history with IDs
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT id, query, search_query, top_results, created_at FROM search_history ORDER BY id DESC")
        rows = cur.fetchall()
        conn.close()
        hist = [{"id": r[0], "query": r[1], "search_query": r[2], "top_results": r[3], "created_at": r[4]} for r in rows]
    except:
        hist = []

    if not hist:
        st.info("No search history found.")
        return

    for h in hist:
        # ABSOLUTE VALIDATION
        # We handle cases where query might be a string-dict like "{'query': '...'}"
        def get_clean_text(val):
            val_str = str(val).strip()
            # AGGRESSIVE BLOCKLIST for Corrupted Data
            bad_markers = ["object Object", "[object", "object object", "{object", "{}", "undefined", "null"]
            if not val_str or any(m in val_str.lower() for m in bad_markers) or val_str.lower() == "object":
                return ""
            return val_str

        raw_q = get_clean_text(h.get('query', ''))
        raw_k = get_clean_text(h.get('search_query', ''))
        
        # Validation for Banner
        is_corrupted = False
        if not raw_k or not raw_q:
            is_corrupted = True
            
        display_query = raw_q if raw_q else "⚠️ Corrupted Search Entry (Bad Metadata)"
        clean_keywords = raw_k if raw_k else "❌ CORRUPTED TOKENS"
        
        # Parse Results
        try:
            saved_results = json.loads(h.get('top_results', '[]')) if isinstance(h.get('top_results'), str) else h.get('top_results', [])
        except:
            saved_results = []
        
        result_count = len(saved_results)
        
        with st.expander(f"📅 {h['created_at']} — {display_query} ({result_count} results)", expanded=False):
            if is_corrupted:
                st.error("🚨 **System Alert**: This entry contains dead metadata ('object Object'). This usually happens when the n8n backend is outdated or misconfigured.")
                st.info("💡 **Fix**: Use the **☢️ Nuclear Reset** button in the sidebar to wipe this corrupted history.")
            
            # ACTION BUTTONS (TOP)
            c1, c2, c3 = st.columns([1, 1, 4])
            with c1:
                # Direct Rerun logic (only if we have a valid query)
                if not is_corrupted and display_query.strip():
                    if st.button("🔄 Rerun Search", key=f"rerun_{h['id']}", type="primary"):
                        st.session_state['rerun_query'] = display_query
                        st.session_state['auto_run_search'] = True
                        st.rerun()
                else:
                    st.button("🔄 Rerun Search", key=f"rerun_{h['id']}", disabled=True)
            with c2:
                if st.button("🗑️ Delete Log", key=f"del_{h['id']}"):
                    delete_history_item(h['id'])
                    st.rerun()
            
            st.divider()
            
            # --- THE BLUE BANNER ---
            banner_color = "#E0F2FE" if not is_corrupted else "#FEF2F2"
            border_color = "#0284C7" if not is_corrupted else "#EF4444"
            text_color = "#0369A1" if not is_corrupted else "#991B1B"
            
            st.markdown(f"""
            <div style="background-color: {banner_color}; padding: 18px; border-left: 10px solid {border_color}; border-radius: 12px; margin-bottom: 25px;">
                <span style="color: {text_color}; font-weight: 900; font-size: 1.1rem; display: block; margin-bottom: 5px; text-transform: uppercase;">🎯 Active Search Keywords</span>
                <span style="font-family: monospace; font-size: 1.5rem; color: {text_color}; font-weight: 700;">{clean_keywords}</span>
            </div>
            """, unsafe_allow_html=True)
            
            if not is_corrupted and raw_q != raw_k:
                 st.markdown(f"**🗣️ Original Input:** *{raw_q}*")
            
            # Show the saved results
            if saved_results:
                st.markdown("### 📄 Paper Collection Snapshot:")
                for i in range(0, len(saved_results), 2):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(render_paper_card(saved_results[i]), unsafe_allow_html=True)
                    if i + 1 < len(saved_results):
                        with col2:
                            st.markdown(render_paper_card(saved_results[i+1]), unsafe_allow_html=True)
            else:
                st.info("No papers were indexed for this specific session.")

if __name__ == "__main__":
    main()