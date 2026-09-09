import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const dataPath = resolve(root, "web/public/data.json");
const payload = JSON.parse(await readFile(dataPath, "utf8"));

if (payload.meta.benchmarkVersion !== "v2-compile" || payload.meta.ePackagerVersion !== "1.2.6") {
  throw new Error("Only V2 results using e-packager 1.2.6 can be published");
}
if (!Array.isArray(payload.models) || payload.meta.modelCount !== payload.models.length) {
  throw new Error("Invalid leaderboard model count");
}
for (const model of payload.models) {
  if (!/^[a-zA-Z0-9._-]+$/.test(model.runId)) throw new Error("Invalid run ID");
  const manifest = JSON.parse(await readFile(resolve(root, "web/public/reports", model.runId, "manifest.json"), "utf8"));
  if (manifest.benchmark_version !== "v2-compile" || manifest.e_packager_version !== "1.2.6") {
    throw new Error(`Not a V2 run: ${model.runId}`);
  }
}

console.log(`web data: ${payload.models.length} static leaderboard entries`);
