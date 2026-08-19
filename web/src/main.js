import {
  ArrowRight,
  ArrowUpRight,
  Ban,
  BookOpenCheck,
  ChevronRight,
  CloudOff,
  ExternalLink,
  GitFork,
  Grid3X3,
  ListOrdered,
  PackageOpen,
  PackageX,
  Scale,
  Search,
  SearchX,
  SquareTerminal,
  X,
  createIcons,
} from "lucide";
import "./styles.css";

const iconSet = {
  ArrowRight,
  ArrowUpRight,
  Ban,
  BookOpenCheck,
  ChevronRight,
  CloudOff,
  ExternalLink,
  GitFork,
  Grid3X3,
  ListOrdered,
  PackageOpen,
  PackageX,
  Scale,
  Search,
  SearchX,
  SquareTerminal,
  X,
};

const state = {
  data: null,
  sort: "total",
  query: "",
  tab: "leaderboard",
};

const elements = {
  versionLabel: document.querySelector("#version-label"),
  leaderScore: document.querySelector("#leader-score"),
  leaderName: document.querySelector("#leader-name"),
  resultDate: document.querySelector("#result-date"),
  leaderboardBody: document.querySelector("#leaderboard-body"),
  emptyState: document.querySelector("#empty-state"),
  search: document.querySelector("#model-search"),
  formatGapChart: document.querySelector("#format-gap-chart"),
  gapSummary: document.querySelector("#gap-summary"),
  scoreEquation: document.querySelector("#score-equation"),
  breakdownBar: document.querySelector("#breakdown-bar"),
  breakdownList: document.querySelector("#breakdown-list"),
  matrixHead: document.querySelector("#matrix-head"),
  matrixBody: document.querySelector("#matrix-body"),
  dialog: document.querySelector("#model-dialog"),
  dialogRank: document.querySelector("#dialog-rank"),
  dialogTitle: document.querySelector("#dialog-title"),
  dialogEffort: document.querySelector("#dialog-effort"),
  dialogBody: document.querySelector("#dialog-body"),
};

const capReasonLabels = {
  none: "已通过编译门槛",
  contract_invalid: "响应契约无效",
  validation_failed: "源码预检失败",
  pack_failed: "工程回包失败",
  packed_project_unusable: "回包工程不可用",
  compile_failed: "真实编译失败",
};

const packReasonLabels = {
  source_preflight_failed: "源码预检",
  semantic_method_rebuild_failed: "方法语义重建",
  function_not_found: "函数链接失败",
  other: "其他回包错误",
};

const escapeHtml = (value) =>
  String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");

const score = (value) => Number(value).toFixed(2);
const percentage = (value) => `${Number(value).toFixed(1)}%`;
const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(2)}`;
const clamp = (value) => Math.max(0, Math.min(100, Number(value)));

function refreshIcons() {
  createIcons({ icons: iconSet, attrs: { "stroke-width": 1.8 } });
}

function renderSummary() {
  const { meta, summary } = state.data;
  elements.versionLabel.textContent = `${meta.benchmarkVersion} · ${meta.scoringVersion}`;
  elements.leaderScore.textContent = score(summary.leaderScore);
  elements.leaderName.textContent = summary.leader;
  elements.resultDate.textContent = `最近结果 ${new Intl.DateTimeFormat("zh-CN", {
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).format(new Date(meta.latestResultAt))}`;
}

function sortedModels() {
  const query = state.query.toLocaleLowerCase("zh-CN");
  const filtered = state.data.models.filter((model) =>
    `${model.model} ${model.effort} ${model.provider ?? ""} ${model.degraded ? "降智" : ""}`.toLocaleLowerCase("zh-CN").includes(query),
  );
  return filtered.sort((a, b) => {
    if (state.sort === "skillGain") {
      return b.skillGain - a.skillGain || b.total - a.total;
    }
    return b[state.sort] - a[state.sort] || b.total - a.total || a.rank - b.rank;
  });
}

function renderLeaderboard() {
  const models = sortedModels();
  elements.emptyState.hidden = models.length !== 0;
  elements.leaderboardBody.hidden = models.length === 0;
  elements.leaderboardBody.innerHTML = models
    .map((model, index) => {
      const deltaClass = model.skillGain > 0 ? "positive" : model.skillGain < 0 ? "negative" : "neutral";
      const rankClass = index < 3 && state.sort === "total" ? ` top-${index + 1}` : "";
      return `
        <tr data-run-id="${escapeHtml(model.runId)}">
          <td class="rank-cell"><span class="rank-number${rankClass}">${String(index + 1).padStart(2, "0")}</span></td>
          <td class="model-cell">
            <button class="model-button" type="button" data-open-model="${escapeHtml(model.runId)}">
              <span class="model-identity">
                <strong>${escapeHtml(model.model)}${model.degraded ? '<span class="quality-badge">降智</span>' : ""}</strong>
                <small>${escapeHtml(model.effort)}</small>
              </span>
            </button>
          </td>
          <td class="number-cell score-cell">
            <strong>${score(model.total)}</strong>
            <span class="micro-bar"><i style="width:${clamp(model.total)}%"></i></span>
          </td>
          <td class="number-cell optional-column">${score(model.raw)}</td>
          <td class="number-cell optional-column">
            ${score(model.skill)}
            <small class="delta ${deltaClass}">${signed(model.skillGain)}</small>
          </td>
          <td class="number-cell format-cell">${score(model.effectiveFormat)}</td>
          <td class="number-cell optional-column mobile-keep">${percentage(model.compileRate)}</td>
          <td class="number-cell optional-column">${percentage(model.passAt1)}</td>
          <td class="open-cell">
            <button class="icon-button row-open" type="button" data-open-model="${escapeHtml(model.runId)}" aria-label="查看 ${escapeHtml(model.model)} 评分详情" title="评分详情">
              <span data-lucide="chevron-right" aria-hidden="true"></span>
            </button>
          </td>
        </tr>`;
    })
    .join("");
  refreshIcons();
}

function renderFormatGap() {
  const { summary, models } = state.data;
  elements.gapSummary.innerHTML = `
    <div><span>平均预编译结构</span><strong>${score(summary.averagePrecompileFormat)}</strong></div>
    <span data-lucide="arrow-right" aria-hidden="true"></span>
    <div><span>编译门槛后有效格式</span><strong>${score(summary.averageEffectiveFormat)}</strong></div>
    <p>差额来自无法回包、工程不可用或不能真实编译的样本。</p>`;

  elements.formatGapChart.innerHTML = [...models]
    .sort((a, b) => b.precompileFormat - b.effectiveFormat - (a.precompileFormat - a.effectiveFormat))
    .map(
      (model) => `
        <button class="gap-row" type="button" data-open-model="${escapeHtml(model.runId)}">
          <span class="gap-model">${escapeHtml(model.model)}${model.degraded ? "（降智）" : ""}</span>
          <span class="gap-bars">
            <i class="precompile-bar" style="width:${clamp(model.precompileFormat)}%"></i>
            <i class="effective-bar" style="width:${clamp(model.effectiveFormat)}%"></i>
          </span>
          <span class="gap-values"><b>${score(model.precompileFormat)}</b><em>${score(model.effectiveFormat)}</em></span>
        </button>`,
    )
    .join("");
  refreshIcons();
}

function renderScoring() {
  const { scoring } = state.data;
  elements.scoreEquation.innerHTML = scoring.weights
    .map(
      (item, index) => `
        ${index > 0 ? '<span class="equation-plus">+</span>' : ""}
        <div class="weight-block weight-${escapeHtml(item.key)}">
          <span>${escapeHtml(item.label)}</span>
          <strong>${item.value}</strong>
          <small>分</small>
        </div>`,
    )
    .join("") + `
      <span class="equation-equals">=</span>
      <div class="weight-total"><span>单题总分</span><strong>100</strong><small>编译失败则为 0</small></div>`;

  elements.breakdownBar.innerHTML = scoring.formatBreakdown
    .map((item, index) => `<span class="breakdown-part part-${index + 1}" style="width:${item.value}%" title="${escapeHtml(item.label)} ${item.value} 分"></span>`)
    .join("");
  elements.breakdownList.innerHTML = scoring.formatBreakdown
    .map(
      (item, index) => `
        <div>
          <span class="breakdown-index part-${index + 1}">${String(index + 1).padStart(2, "0")}</span>
          <span>${escapeHtml(item.label)}</span>
          <strong>${item.value}</strong>
        </div>`,
    )
    .join("");
}

function renderMatrix() {
  const categories = state.data.models[0].categories;
  elements.matrixHead.innerHTML = `
    <tr>
      <th scope="col">模型</th>
      <th scope="col" class="number-column">总分</th>
      ${categories.map((category) => `<th scope="col">${escapeHtml(category.label)}</th>`).join("")}
    </tr>`;
  elements.matrixBody.innerHTML = state.data.models
    .map(
      (model) => `
        <tr>
          <th scope="row">
            <button type="button" class="matrix-model" data-open-model="${escapeHtml(model.runId)}">${escapeHtml(model.model)}${model.degraded ? "（降智）" : ""}</button>
          </th>
          <td class="matrix-total">${score(model.total)}</td>
          ${model.categories
            .map(
              (category) => `<td class="heat-cell" style="--heat:${clamp(category.score) / 100}"><span>${score(category.score)}</span></td>`,
            )
            .join("")}
        </tr>`,
    )
    .join("");
}

function failureList(reasons, labels) {
  return Object.entries(reasons)
    .filter(([, count]) => count > 0)
    .sort((a, b) => b[1] - a[1])
    .map(
      ([key, count]) => `
        <div class="failure-row">
          <span>${escapeHtml(labels[key] ?? key)}</span>
          <span class="failure-track"><i style="width:${clamp((count / 30) * 100)}%"></i></span>
          <strong>${count}</strong>
        </div>`,
    )
    .join("");
}

function openModel(runId) {
  const model = state.data.models.find((item) => item.runId === runId);
  if (!model) return;

  elements.dialogRank.textContent = `总分排名 #${model.rank} · ${state.data.meta.scoringVersion}`;
  elements.dialogTitle.textContent = `${model.model}${model.degraded ? "（降智）" : ""}`;
  elements.dialogEffort.textContent = `${model.provider ? `${model.provider} · ` : ""}思考等级 ${model.effort} · ${model.protocol}${model.wireProtocol !== model.protocol ? ` → ${model.wireProtocol}` : ""}${model.degradationNote ? ` · ${model.degradationNote}` : ""}`;
  elements.dialogBody.innerHTML = `
    <section class="detail-score-band">
      <div class="detail-primary-score"><span>总分</span><strong>${score(model.total)}</strong><small>/ 100</small></div>
      <div><span>有效格式</span><strong>${score(model.effectiveFormat)}</strong></div>
      <div><span>编译率</span><strong>${percentage(model.compileRate)}</strong></div>
      <div><span>pass@1</span><strong>${percentage(model.passAt1)}</strong></div>
    </section>

    <section class="detail-section">
      <div class="subsection-heading"><h3>Raw / Skill</h3><p>Skill 增益 <strong class="${model.skillGain >= 0 ? "positive" : "negative"}">${signed(model.skillGain)}</strong></p></div>
      <div class="track-comparison">
        <div><span>Raw</span><i><b style="width:${clamp(model.raw)}%"></b></i><strong>${score(model.raw)}</strong></div>
        <div><span>Skill</span><i><b style="width:${clamp(model.skill)}%"></b></i><strong>${score(model.skill)}</strong></div>
      </div>
    </section>

    <section class="detail-section">
      <div class="subsection-heading"><h3>五类能力</h3><p>编译门槛后的实际得分</p></div>
      <div class="category-bars">
        ${model.categories
          .map(
            (category) => `
              <div><span>${escapeHtml(category.label)}</span><i><b style="width:${clamp(category.score)}%"></b></i><strong>${score(category.score)}</strong></div>`,
          )
          .join("")}
      </div>
    </section>

    <section class="detail-section two-column-detail">
      <div>
        <div class="subsection-heading"><h3>硬门槛状态</h3><p>30 个样本</p></div>
        <div class="failure-list">${failureList(model.capReasons, capReasonLabels)}</div>
      </div>
      <div>
        <div class="subsection-heading"><h3>回包失败</h3><p>${model.packFailures}/${model.packAttempts} 次</p></div>
        <div class="failure-list">${failureList(model.packFailureReasons, packReasonLabels)}</div>
      </div>
    </section>

    <section class="audit-strip">
      <div><span>服务端模型标识</span><strong>${escapeHtml(model.observedModels.join(", ") || "未返回")}</strong></div>
      <div><span>运行编号</span><code>${escapeHtml(model.runId)}</code></div>
      <a href="${escapeHtml(model.reportUrl)}" target="_blank" rel="noreferrer">查看审计报告 <span data-lucide="external-link" aria-hidden="true"></span></a>
    </section>`;
  elements.dialog.showModal();
  refreshIcons();
}

function setTab(tab) {
  state.tab = tab;
  document.querySelectorAll(".tab-button").forEach((button) => {
    const isActive = button.dataset.tab === tab;
    button.classList.toggle("is-active", isActive);
    button.setAttribute("aria-selected", String(isActive));
  });
  document.querySelectorAll(".view-panel").forEach((panel) => {
    const isActive = panel.dataset.view === tab;
    panel.classList.toggle("is-active", isActive);
    panel.hidden = !isActive;
  });
  history.replaceState(null, "", `#${tab}`);
}

function bindEvents() {
  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => setTab(button.dataset.tab));
  });
  document.querySelectorAll(".segment").forEach((button) => {
    button.addEventListener("click", () => {
      state.sort = button.dataset.sort;
      document.querySelectorAll(".segment").forEach((item) => item.classList.toggle("is-active", item === button));
      renderLeaderboard();
    });
  });
  elements.search.addEventListener("input", (event) => {
    state.query = event.target.value.trim();
    renderLeaderboard();
  });
  document.addEventListener("click", (event) => {
    const opener = event.target.closest("[data-open-model]");
    if (opener) openModel(opener.dataset.openModel);
  });
  document.querySelector("#dialog-close").addEventListener("click", () => elements.dialog.close());
  elements.dialog.addEventListener("click", (event) => {
    if (event.target === elements.dialog) elements.dialog.close();
  });
}

async function initialize() {
  try {
    const response = await fetch(`/data.json?ts=${Date.now()}`, { cache: "no-store" });
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    state.data = await response.json();
    renderSummary();
    renderLeaderboard();
    renderFormatGap();
    renderScoring();
    renderMatrix();
    bindEvents();
    const initialTab = ["leaderboard", "scoring", "matrix"].includes(location.hash.slice(1))
      ? location.hash.slice(1)
      : "leaderboard";
    setTab(initialTab);
    refreshIcons();
  } catch (error) {
    elements.leaderboardBody.innerHTML = `<tr class="loading-row error-row"><td colspan="9">评分数据加载失败：${escapeHtml(error.message)}</td></tr>`;
    console.error(error);
  }
}

refreshIcons();
initialize();
