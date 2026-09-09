import { readdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const dataPath = resolve(root, "web/public/data.json");
const reportsDir = resolve(root, "web/public/reports");
const existing = JSON.parse(await readFile(dataPath, "utf8"));
const categoryOrder = ["format", "core", "flow", "abstraction", "repair"];
const labels = Object.fromEntries(existing.categories.map((item) => [item.key, item.label]));
const providerFor = (manifest) => String(manifest.base_url ?? "").includes("volces.com")
  ? "火山引擎" : String(manifest.base_url ?? "").includes("rightapi.ai") ? "RIGHT 中转站" : manifest.provider ?? null;
const entries = await readdir(reportsDir, { withFileTypes: true }).catch(() => []);
const models = [];
for (const entry of entries.filter((item) => item.isDirectory() && /^[a-zA-Z0-9._-]+$/.test(item.name))) {
  const runId = entry.name;
  try {
    const manifest = JSON.parse(await readFile(resolve(reportsDir, runId, "manifest.json"), "utf8"));
    const scorecard = JSON.parse(await readFile(resolve(reportsDir, runId, "scorecard.json"), "utf8"));
    if (manifest.benchmark_version !== "v2-compile" || manifest.e_packager_version !== "1.2.7" || JSON.stringify(manifest.tracks) !== '["raw"]') continue;
    if (scorecard.run_status !== "complete" || typeof scorecard.total_score !== "number") continue;
    const raw = scorecard.track_scores?.raw ?? {};
    models.push({
      runId, model: scorecard.model ?? manifest.model, provider: providerFor(manifest),
      effort: scorecard.reasoning_effort ?? manifest.reasoning_effort,
      protocol: scorecard.protocol ?? manifest.protocol,
      wireProtocol: scorecard.wire_protocol ?? manifest.wire_protocol ?? scorecard.protocol,
      degraded: Boolean(scorecard.degraded ?? manifest.degraded),
      degradationNote: scorecard.degradation_note ?? manifest.degradation_note ?? null,
      total: scorecard.total_score, effectiveFormat: raw.format_score ?? 0,
      precompileFormat: raw.precompile_format_score ?? raw.format_score ?? 0,
      compileRate: raw.compile_rate ?? 0, passAt1: raw.pass_at_1 ?? 0,
      packAttempts: raw.pack_attempt_count ?? 0, packFailures: raw.pack_failure_count ?? 0,
      capReasons: scorecard.cap_reason_counts ?? {}, packFailureReasons: scorecard.pack_failure_reason_counts ?? {},
      observedModels: scorecard.observed_models ?? [],
      categories: categoryOrder.map((key) => ({ key, label: scorecard.category_scores?.[key]?.label ?? labels[key] ?? key, score: scorecard.category_scores?.[key]?.score ?? 0 })),
      reportUrl: `reports/${runId}/report.md`,
    });
  } catch { /* Ignore incomplete local report directories. */ }
}
models.sort((a, b) => b.total - a.total || a.model.localeCompare(b.model));
models.forEach((model, index) => { model.rank = index + 1; });
const mean = (values) => values.length ? values.reduce((sum, value) => sum + value, 0) / values.length : null;
const manifests = await Promise.all(models.map((model) => readFile(resolve(reportsDir, model.runId, "manifest.json"), "utf8")));
const summary = {
  leader: models[0]?.model ?? null, leaderScore: models[0]?.total ?? null,
  compileLeader: models.toSorted((a, b) => b.compileRate - a.compileRate || b.total - a.total)[0]?.model ?? null,
  compileLeaderRate: models.length ? Math.max(...models.map((model) => model.compileRate)) : null,
  averageScore: mean(models.map((model) => model.total)), averageCompileRate: mean(models.map((model) => model.compileRate)),
  averageEffectiveFormat: mean(models.map((model) => model.effectiveFormat)), averagePrecompileFormat: mean(models.map((model) => model.precompileFormat)),
};
const payload = { ...existing, meta: { ...existing.meta, modelCount: models.length, latestResultAt: manifests.map((text) => JSON.parse(text).created_at).sort().at(-1) ?? null, samplesPerModel: 20, taskCount: 20, tracks: ["Raw"], benchmarkVersion: "v2-compile", ePackagerVersion: "1.2.7" }, summary, models };
await writeFile(dataPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
console.log(`web data: ${models.length} V2 leaderboard entries`);
