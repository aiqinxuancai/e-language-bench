import { readFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const root = resolve(scriptDir, "../..");
const dataPath = resolve(root, "web/public/data.json");
const payload = JSON.parse(await readFile(dataPath, "utf8"));

if (!Array.isArray(payload.models) || payload.models.length === 0) {
  throw new Error("web/public/data.json has no leaderboard data");
}

console.log(`web data: ${payload.models.length} static leaderboard entries`);
