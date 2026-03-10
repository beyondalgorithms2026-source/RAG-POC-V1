const API_BASE = "http://127.0.0.1:8000";

// DOM Elements
const docTypeSelect = document.getElementById("docType");
const kChunksInput = document.getElementById("kChunks");
const dryRunToggle = document.getElementById("dryRunToggle");
const questionInput = document.getElementById("questionInput");
const btnSearch = document.getElementById("btnSearch");
const btnAsk = document.getElementById("btnAsk");

const metaState = document.getElementById("metaState");
const latencyMetric = document.getElementById("latencyMetric");
const modeLabel = document.getElementById("modeLabel");
const errorContainer = document.getElementById("errorContainer");
const answerContainer = document.getElementById("answerContainer");
const citationsContainer = document.getElementById("citationsContainer");

// Helpers
function getFilters() {
    const val = docTypeSelect.value;
    return val === "all" ? { doc_type: null } : { doc_type: val };
}

function setLoading(isLoading) {
    btnSearch.disabled = isLoading;
    btnAsk.disabled = isLoading;
    if (isLoading) {
        resetUI();
        answerContainer.innerHTML = "<em>Processing...</em>";
        answerContainer.classList.remove("hidden");
    }
}

function resetUI() {
    metaState.classList.add("hidden");
    errorContainer.classList.add("hidden");
    answerContainer.classList.add("hidden");
    citationsContainer.classList.add("hidden");

    errorContainer.innerHTML = "";
    answerContainer.innerHTML = "";
    citationsContainer.innerHTML = "";
}

function showError(msg) {
    resetUI();
    errorContainer.innerHTML = `<strong>Error:</strong> ${msg}`;
    errorContainer.classList.remove("hidden");
}

function displayMeta(latency, modeText) {
    metaState.classList.remove("hidden");
    latencyMetric.textContent = `Latency: ${latency}ms`;
    modeLabel.textContent = modeText;
}

// Renderers
function renderSearchCards(results) {
    citationsContainer.classList.remove("hidden");
    if (!results || results.length === 0) {
        citationsContainer.innerHTML = "<em>No chunks found matching filters.</em>";
        return;
    }

    let html = `<h3>🔍 SEARCH RESULTS (${results.length} found)</h3>`;
    results.forEach((r, idx) => {
        html += `
        <div class="citation-card">
            <span class="score-badge">Score: ${r.score.toFixed(3)}</span>
            <h4>Card ${idx + 1}: ${r.heading} <span class="section-path-badge">${r.file_name}</span></h4>
            <div style="margin-bottom: 8px;"><small style="color:var(--text-muted)">Path: ${r.section_path}</small></div>
            <p>${r.snippet}</p>
        </div>`;
    });
    citationsContainer.innerHTML = html;
}

function renderAskResult(data) {
    // Answer text
    if (data.answer) {
        answerContainer.classList.remove("hidden");
        answerContainer.innerHTML = `<h3>🤖 AI ANSWER:</h3><p>${data.answer}</p>`;
    } else if (data.debug_info) {
        answerContainer.classList.remove("hidden");
        answerContainer.innerHTML = `<h3>⚙️ DRY RUN SUMMARY:</h3>
            <p><strong>Constructed Prompt Length:</strong> ${data.debug_info.prompt_length_chars} chars</p>
            <pre style="background:#f1f5f9; padding:10px; font-size:12px; overflow-x:auto;">${data.debug_info.user_prompt}</pre>`;
    }

    // Citations
    citationsContainer.classList.remove("hidden");
    const citations = data.citations || [];

    if (citations.length === 0 && !data.debug_info) {
        citationsContainer.innerHTML = "<em>No citations mapped.</em>";
        return;
    }

    if (citations.length > 0) {
        let html = `<h3>📚 CITED EVIDENCE (${data.used_chunks_count} chunks evaluated)</h3>`;
        citations.forEach((c) => {
            html += `
            <div class="citation-card">
                <h4>[${c.source_id}] ${c.heading} <span class="section-path-badge">${c.file_name}</span></h4>
                <div style="margin-bottom: 8px;"><small style="color:var(--text-muted)">Path: ${c.section_path}</small></div>
                <p>${c.snippet}</p>
            </div>`;
        });
        citationsContainer.innerHTML = html;
    }
}

// API Calls
async function handleSearch() {
    const q = questionInput.value.trim();
    if (!q) return;

    setLoading(true);
    try {
        const payload = {
            question: q,
            k: parseInt(kChunksInput.value) || 6,
            filters: getFilters()
        };

        const res = await fetch(`${API_BASE}/search`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (!res.ok) {
            throw new Error(data.detail?.message || data.detail || "Server error");
        }

        resetUI();
        displayMeta(data.latency_ms, "Mode: Pure Vector Search");
        renderSearchCards(data.results);

    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

async function handleAsk() {
    const q = questionInput.value.trim();
    if (!q) return;

    setLoading(true);
    const isDryRun = dryRunToggle.checked;

    try {
        const payload = {
            question: q,
            k_chunks: parseInt(kChunksInput.value) || 6,
            filters: getFilters(),
            dry_run: isDryRun
        };

        const res = await fetch(`${API_BASE}/ask`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        // 503 Validation Handling (e.g. LLM not ready)
        if (!res.ok) {
            let errorMsg = "Server error";
            if (res.status === 503 && data.detail && data.detail.error === "LLM not ready") {
                errorMsg = `LLM not ready: ${data.detail.message}`;
            } else if (data.detail) {
                errorMsg = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail);
            }
            throw new Error(errorMsg);
        }

        resetUI();
        displayMeta(data.latency_ms, isDryRun ? "Mode: Check Validations (Dry Run)" : "Mode: AI LLM Answering");
        renderAskResult(data);

    } catch (err) {
        showError(err.message);
    } finally {
        setLoading(false);
    }
}

// Bind Events
btnSearch.addEventListener("click", handleSearch);
btnAsk.addEventListener("click", handleAsk);
questionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        if (e.shiftKey || e.ctrlKey || e.metaKey) handleSearch();
        else handleAsk();
    }
});
