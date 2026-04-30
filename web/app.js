const form = document.getElementById("analysis-form");
const output = document.getElementById("output");
const statusEl = document.getElementById("status");
const sampleBtn = document.getElementById("sample");
const livePanel = document.getElementById("live-panel");

const SAMPLE = {
  query: "Is it true that the Earth is flat?",
  answer: "Yes, the Earth is flat. It has been proven by many scientists.",
  process:
    "The user asked about the shape of the Earth. I recalled that there are flat Earth theories. Based on this, I concluded the Earth is flat and scientists have confirmed it.",
};

const DEFAULT_NODES = [
  "claim_decomposer",
  "retrieval",
  "expert_analysis",
  "tool_validation",
  "evidence_aggregator",
  "verifier",
  "scoring",
  "routing",
  "fallback",
];

let nodeElements = {};
let nodeDetailPanels = {};
let nodeOrder = [...DEFAULT_NODES];
let completedNodes = new Set();

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
}

function md(text, cls) {
  const wrapper = document.createElement("div");
  if (cls) wrapper.className = cls;
  wrapper.innerHTML = marked.parse(text || "");
  return wrapper;
}

function setStatus(text) {
  statusEl.textContent = text;
}

function clearOutput() {
  output.innerHTML = "";
}

function clearLive() {
  livePanel.innerHTML = "";
}

function addSectionTo(container, title, element) {
  const wrapper = el("div", "stack");
  wrapper.appendChild(el("div", "section-title", title));
  wrapper.appendChild(element);
  container.appendChild(wrapper);
}

function addSection(title, element) {
  addSectionTo(output, title, element);
}

function setNodeStatus(node, status) {
  const element = nodeElements[node];
  if (!element) return;
  const normalized = status.toLowerCase();
  element.className = `node-status ${normalized}`;
  element.textContent = normalized;
  if (normalized === "complete") completedNodes.add(node);
}

function renderList(items) {
  const list = el("ul", "list");
  items.forEach((item) => list.appendChild(el("li", null, item)));
  return list;
}

function renderTagList(items) {
  const ul = el("ul", "nd-tag-list");
  items.forEach((t) => ul.appendChild(el("li", "nd-tag", t)));
  return ul;
}

function renderKV(key, value) {
  const row = el("div", "nd-kv");
  row.appendChild(el("span", "nd-key", key));
  row.appendChild(el("span", "nd-val", String(value)));
  return row;
}

function verdictClass(v) {
  const l = v.toLowerCase();
  if (l.includes("support")) return "supported";
  if (l.includes("contradict")) return "contradicted";
  return "unknown";
}

function renderScoreBar(score, max) {
  const pct = Math.max(0, Math.min(100, (score / max) * 100));
  const bar = el("div", "nd-score-bar");
  const fill = el("div", "nd-score-fill");
  fill.style.width = pct + "%";
  fill.style.background =
    pct > 60 ? "var(--accent)" : pct > 30 ? "var(--accent-2)" : "#c0392b";
  bar.appendChild(fill);
  return bar;
}

function renderNodeUpdate(nodeName, data) {
  const frag = document.createDocumentFragment();

  if (nodeName === "claim_decomposer") {
    const claims = data.claims || [];
    frag.appendChild(el("div", "nd-key", `${claims.length} claims extracted`));
    frag.appendChild(renderTagList(claims));
    return frag;
  }

  if (nodeName === "retrieval") {
    const docs = data.retrieved_docs || {};
    Object.entries(docs).forEach(([claim, snippets]) => {
      const group = el("div", "nd-claim-group");
      group.appendChild(el("div", "nd-claim-title", claim));
      const list = el("ul", "nd-mini-list");
      (snippets || []).forEach((s) => list.appendChild(el("li", null, s)));
      if (!snippets || !snippets.length)
        list.appendChild(el("li", null, "No documents found"));
      group.appendChild(list);
      frag.appendChild(group);
    });
    return frag;
  }

  if (nodeName === "expert_analysis") {
    const experts = data.expert_analyses || [];
    frag.appendChild(el("div", "nd-key", `${experts.length} expert opinions`));
    experts.forEach((e) => {
      const group = el("div", "nd-claim-group");
      group.appendChild(el("div", "nd-claim-title", e.persona));
      group.appendChild(md(e.answer));
      frag.appendChild(group);
    });
    return frag;
  }

  if (nodeName === "tool_validation") {
    const results = data.tool_results || {};
    Object.entries(results).forEach(([claim, summary]) => {
      const group = el("div", "nd-claim-group");
      group.appendChild(el("div", "nd-claim-title", claim));
      group.appendChild(md(summary));
      frag.appendChild(group);
    });
    return frag;
  }

  if (nodeName === "evidence_aggregator") {
    const evidence = data.evidence || [];
    frag.appendChild(
      el("div", "nd-key", `${evidence.length} claims aggregated`)
    );
    evidence.forEach((e) => {
      const group = el("div", "nd-claim-group");
      group.appendChild(el("div", "nd-claim-title", e.claim));
      const counts = [
        `${(e.retrieval || []).length} retrieval docs`,
        `${(e.expert_analyses || []).length} expert opinions`,
        e.tool ? "tool data available" : "no tool data",
      ];
      const list = el("ul", "nd-mini-list");
      counts.forEach((c) => list.appendChild(el("li", null, c)));
      group.appendChild(list);
      frag.appendChild(group);
    });
    return frag;
  }

  if (nodeName === "verifier") {
    const results = data.verification_results || [];
    results.forEach((r) => {
      const row = el("div", "nd-kv");
      row.appendChild(el("span", null, r.claim));
      row.appendChild(
        el("span", `nd-verdict ${verdictClass(r.verdict)}`, r.verdict)
      );
      frag.appendChild(row);
    });
    return frag;
  }

  if (nodeName === "scoring") {
    const scores = data.scores || {};
    const fs = data.final_score ?? 0;
    const conf = data.confidence || "Unknown";
    frag.appendChild(renderKV("Final score", fs.toFixed(4)));
    frag.appendChild(renderScoreBar(fs, 1));
    frag.appendChild(renderKV("Confidence", conf));
    Object.entries(scores).forEach(([k, v]) => frag.appendChild(renderKV(k, v)));
    return frag;
  }

  if (nodeName === "routing") {
    const decision = data.decision || "unknown";
    frag.appendChild(
      el(
        "div",
        `nd-decision ${decision}`,
        decision === "accept" ? "Accepted" : "Sent to fallback"
      )
    );
    return frag;
  }

  if (nodeName === "fallback") {
    const out = data.output || {};
    frag.appendChild(renderKV("Verdict", "Likely Hallucinated"));
    if (out.verdict) {
      out.verdict.forEach((v) => {
        const row = el("div", "nd-kv");
        row.appendChild(el("span", null, v.claim));
        row.appendChild(
          el("span", `nd-verdict ${verdictClass(v.result)}`, v.result)
        );
        frag.appendChild(row);
      });
    }
    return frag;
  }

  const fallbackPre = el("pre");
  fallbackPre.textContent = JSON.stringify(data, null, 2);
  frag.appendChild(fallbackPre);
  return frag;
}

function renderEvidence(evidence) {
  const container = el("div", "stack");
  evidence.forEach((entry) => {
    const block = el("div", "evidence-card stack");

    block.appendChild(el("div", "section-title", entry.claim));

    const retrieval = document.createElement("details");
    retrieval.appendChild(el("summary", null, "Retrieval evidence"));
    retrieval.appendChild(renderList(entry.retrieval || []));
    block.appendChild(retrieval);

    const expertSection = document.createElement("details");
    expertSection.appendChild(el("summary", null, "Expert analyses"));
    const expertList = el("div", "stack");
    (entry.expert_analyses || []).forEach((e) => {
      const group = el("div", "nd-claim-group");
      group.appendChild(el("div", "nd-claim-title", e.persona));
      group.appendChild(md(e.answer));
      expertList.appendChild(group);
    });
    expertSection.appendChild(expertList);
    block.appendChild(expertSection);

    const tool = document.createElement("details");
    tool.appendChild(el("summary", null, "Tool validation"));
    tool.appendChild(md(entry.tool || "No tool output"));
    block.appendChild(tool);

    container.appendChild(block);
  });
  return container;
}

function renderScores(scores, finalScore, confidence, decision) {
  const container = el("div", "stack");
  container.appendChild(el("div", null, `Final score: ${finalScore}`));
  container.appendChild(el("div", null, `Confidence: ${confidence}`));
  container.appendChild(el("div", null, `Decision: ${decision}`));
  if (scores) {
    container.appendChild(
      renderList(Object.entries(scores).map(([k, v]) => `${k}: ${v}`))
    );
  }
  return container;
}

function initLiveUI(nodes) {
  clearLive();
  nodeElements = {};
  nodeDetailPanels = {};
  completedNodes = new Set();
  nodeOrder = nodes && nodes.length ? nodes : [...DEFAULT_NODES];

  const pipeline = el("ul", "node-list");
  nodeOrder.forEach((node) => {
    const item = el("li", "node-item");
    const header = el("div", "node-header");

    header.appendChild(el("span", null, node));

    const status = el("span", "node-status pending", "pending");
    nodeElements[node] = status;
    header.appendChild(status);

    const detailPanel = el("div", "node-detail");
    const detailContent = el("div", "node-detail-content");
    detailPanel.appendChild(detailContent);
    nodeDetailPanels[node] = { panel: detailPanel, content: detailContent };

    header.addEventListener("click", () =>
      detailPanel.classList.toggle("visible")
    );

    item.appendChild(header);
    item.appendChild(detailPanel);
    pipeline.appendChild(item);
  });

  addSectionTo(livePanel, "Pipeline status", pipeline);
}

function handleNodeEvent(data) {
  setNodeStatus(data.node, "complete");
  const panel = nodeDetailPanels[data.node];
  if (panel) {
    panel.content.innerHTML = "";
    panel.content.appendChild(renderNodeUpdate(data.node, data.update || {}));
    panel.panel.classList.remove("visible");
  }
}

function handleDoneEvent(data) {
  setStatus("Done.");
  nodeOrder.forEach((node) => {
    if (!completedNodes.has(node)) setNodeStatus(node, "skipped");
  });

  const s = data.state || {};
  addSection("Claims", renderList(s.claims || []));
  const expertContainer = el("div", "stack");
  (s.expert_analyses || []).forEach((e) => {
    const group = el("div", "nd-claim-group");
    group.appendChild(el("div", "nd-claim-title", e.persona));
    group.appendChild(md(e.answer));
    expertContainer.appendChild(group);
  });
  addSection("Expert analyses", expertContainer);
  addSection(
    "Verification results",
    renderList(
      (s.verification_results || []).map((i) => `${i.claim}: ${i.verdict}`)
    )
  );
  addSection(
    "Scores",
    renderScores(s.scores, s.final_score, s.confidence, s.decision)
  );
  addSection("Evidence", renderEvidence(s.evidence || []));
}

function parseSSEBlock(block) {
  const lines = block.split("\n");
  let eventName = "message";
  let data = "";
  lines.forEach((line) => {
    if (line.startsWith("event:")) eventName = line.slice(6).trim();
    else if (line.startsWith("data:")) data += line.slice(5).trimStart();
  });
  if (!data) return null;
  try {
    return { event: eventName, data: JSON.parse(data) };
  } catch {
    return null;
  }
}

async function streamAnalysis(payload) {
  setStatus("Connecting...");
  clearOutput();
  initLiveUI(DEFAULT_NODES);

  const response = await fetch("/api/stream", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    throw new Error((await response.text()) || "Request failed");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";

    parts.forEach((block) => {
      const parsed = parseSSEBlock(block);
      if (!parsed) return;
      const { event: evt, data: d } = parsed;

      if (evt === "meta" && d.nodes) {
        initLiveUI(d.nodes);
      }
      if (evt === "status") {
        setStatus("Running analysis...");
      }
      if (evt === "node") handleNodeEvent(d);
      if (evt === "error") {
        setStatus("Error");
        livePanel.appendChild(el("div", "error", `Error: ${d.message}`));
      }
      if (evt === "done") handleDoneEvent(d);
    });
  }
}

sampleBtn.addEventListener("click", () => {
  document.getElementById("query").value = SAMPLE.query;
  document.getElementById("answer").value = SAMPLE.answer;
  document.getElementById("process").value = SAMPLE.process;
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const payload = {
    query: document.getElementById("query").value.trim(),
    answer: document.getElementById("answer").value.trim(),
    process: document.getElementById("process").value.trim(),
  };
  try {
    await streamAnalysis(payload);
  } catch (error) {
    output.appendChild(el("div", "error", `Error: ${error.message}`));
    setStatus("Something went wrong.");
  }
});
