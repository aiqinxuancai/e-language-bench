import { mkdir, readFile, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const readmePath = resolve(root, "README.md");
const outputPath = resolve(root, "web/public/data.json");
const readme = await readFile(readmePath, "utf8");

const categoryOrder = ["format", "core", "flow", "abstraction", "repair"];
const tableRows = readme
  .split(/\r?\n/)
  .filter((line) => line.startsWith("|") && line.includes("scorecard.json"));

if (tableRows.length === 0) {
  throw new Error("README leaderboard has no published scorecard rows");
}

const parseNumber = (value) => Number(value.replace(/[+%*`]/g, "").trim());
const models = [];
const scoringVersions = new Set();
const benchmarkVersions = new Set();
const createdTimes = [];

for (const [index, line] of tableRows.entries()) {
  const cells = line
    .slice(1, -1)
    .split("|")
    .map((cell) => cell.trim());
  if (cells.length !== 12) {
    throw new Error(`unexpected leaderboard column count: ${line}`);
  }

  const scorecardMatch = cells[11].match(/\((results\/[^)]+\/scorecard\.json)\)/);
  const reportMatch = cells[11].match(/\((results\/[^)]+\/report\.md)\)/);
  if (!scorecardMatch || !reportMatch) {
    throw new Error(`leaderboard row is missing result links: ${line}`);
  }

  const scorecardRelative = scorecardMatch[1];
  const reportRelative = reportMatch[1];
  const runRoot = dirname(resolve(root, scorecardRelative));
  const scorecard = JSON.parse(await readFile(resolve(root, scorecardRelative), "utf8"));
  const manifest = JSON.parse(await readFile(resolve(runRoot, "manifest.json"), "utf8"));
  const publishedScore = parseNumber(cells[2]);

  if (scorecard.run_status !== "complete") {
    throw new Error(`${scorecard.run_id} is not complete`);
  }
  if (Math.abs(scorecard.total_score - publishedScore) > 0.001) {
    throw new Error(`${scorecard.run_id} score differs from README`);
  }

  scoringVersions.add(scorecard.scoring_version);
  benchmarkVersions.add(scorecard.benchmark_version);
  createdTimes.push(manifest.created_at);

  const [packFailures, packAttempts] = cells[9].split("/").map(Number);
  models.push({
    rank: index + 1,
    model: scorecard.model ?? cells[0],
    provider: scorecard.provider ?? manifest.provider ?? null,
    degraded: scorecard.degraded === true,
    degradationNote: scorecard.degradation_note ?? manifest.degradation_note ?? null,
    effort: cells[1].replaceAll("`", ""),
    total: publishedScore,
    raw: parseNumber(cells[3]),
    skill: parseNumber(cells[4]),
    effectiveFormat: parseNumber(cells[5]),
    precompileFormat: parseNumber(cells[6]),
    compileRate: parseNumber(cells[7]),
    passAt1: parseNumber(cells[8]),
    packFailures,
    packAttempts,
    skillGain: parseNumber(cells[10]),
    runId: scorecard.run_id,
    protocol: scorecard.protocol,
    wireProtocol: scorecard.wire_protocol,
    observedModels: scorecard.observed_models ?? [],
    categories: categoryOrder.map((key) => ({
      key,
      label: scorecard.category_scores[key].label,
      score: scorecard.category_scores[key].score,
      effectiveFormat: scorecard.category_scores[key].format_score,
      precompileFormat: scorecard.category_scores[key].precompile_format_score,
      passAt1: Math.round(scorecard.category_scores[key].pass_at_1 * 1000) / 10,
    })),
    capReasons: scorecard.cap_reason_counts,
    packFailureReasons: scorecard.pack_failure_reason_counts,
    reportUrl: `https://github.com/aiqinxuancai/e-language-bench/blob/main/${reportRelative}`,
    scorecardUrl: `https://github.com/aiqinxuancai/e-language-bench/blob/main/${scorecardRelative}`,
  });
}

if (scoringVersions.size !== 1 || benchmarkVersions.size !== 1) {
  throw new Error("published leaderboard mixes benchmark or scoring versions");
}

const round = (value) => Math.round(value * 100) / 100;
const average = (key) => round(models.reduce((sum, model) => sum + model[key], 0) / models.length);
const byCompile = [...models].sort((a, b) => b.compileRate - a.compileRate || b.total - a.total);
const bySkillGain = [...models].sort((a, b) => b.skillGain - a.skillGain || b.total - a.total);
const latestCreatedAt = createdTimes.sort().at(-1);

const payload = {
  meta: {
    title: "易语言模型基准",
    benchmarkVersion: [...benchmarkVersions][0],
    scoringVersion: [...scoringVersions][0],
    modelCount: models.length,
    samplesPerModel: 30,
    taskCount: 15,
    tracks: ["Raw", "Skill"],
    latestResultAt: latestCreatedAt,
    repositoryUrl: "https://github.com/aiqinxuancai/e-language-bench",
  },
  summary: {
    leader: models[0].model,
    leaderScore: models[0].total,
    compileLeader: byCompile[0].model,
    compileLeaderRate: byCompile[0].compileRate,
    skillLeader: bySkillGain[0].model,
    skillLeaderGain: bySkillGain[0].skillGain,
    averageScore: average("total"),
    averageCompileRate: average("compileRate"),
    averageEffectiveFormat: average("effectiveFormat"),
    averagePrecompileFormat: average("precompileFormat"),
  },
  scoring: {
    weights: [
      { key: "format", label: "格式与工程可靠性", value: 45 },
      { key: "compile", label: "真实无头编译", value: 35 },
      { key: "semantic", label: "隐藏静态语义", value: 20 },
    ],
    formatBreakdown: [
      { label: "严格 JSON、UTF-8 与授权路径", value: 10 },
      { label: "声明字段、顺序与文本语法", value: 25 },
      { label: "流程闭合、名称与类型链接", value: 20 },
      { label: "e-packager 成功回包", value: 15 },
      { label: "重新解包与一致性比较", value: 15 },
      { label: "AutoLinker 成功打开工程", value: 15 },
    ],
  },
  models,
};

await mkdir(dirname(outputPath), { recursive: true });
await writeFile(outputPath, `${JSON.stringify(payload, null, 2)}\n`, "utf8");
console.log(`web data: ${models.length} published runs -> ${outputPath}`);
