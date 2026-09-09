import { mkdir, readFile } from "node:fs/promises";
import { resolve } from "node:path";
import { chromium, expect } from "@playwright/test";

const artifacts = resolve("web/test-artifacts");
const baseUrl = process.env.WEB_BASE_URL ?? "http://127.0.0.1:4173";
const data = JSON.parse(await readFile("web/public/data.json", "utf8"));
await mkdir(artifacts, { recursive: true });
const browser = await chromium.launch();
const errors = [];
try {
  for (const width of [1440, 390, 320]) {
    const page = await browser.newPage({ viewport: { width, height: 900 } });
    page.on("pageerror", error => errors.push(error.message));
    page.on("console", message => { if (message.type() === "error") errors.push(message.text()); });
    await page.goto(baseUrl, { waitUntil: "networkidle" });
    await expect(page.locator("#version-label")).toHaveText("V2 · e-packager 1.2.6");
    await expect(page.locator("#leaderboard-body tr")).toHaveCount(data.models.length);
    if (!data.models.length) {
      await expect(page.locator("#leader-score")).toHaveText("--");
      await expect(page.locator("#empty-state")).toContainText("V2 暂无已发布成绩");
      await expect(page.locator(".format-gap-section")).toBeHidden();
    }
    for (const tab of ["leaderboard", "scoring", "matrix"]) {
      await page.locator(`[data-tab="${tab}"]`).click();
      await expect(page.locator(`[data-view="${tab}"]`)).toBeVisible();
      if (tab === "matrix" && !data.models.length) await expect(page.locator("#matrix-empty")).toBeVisible();
      expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth), `${width}px ${tab} overflow`).toBe(false);
      await page.screenshot({ path: resolve(artifacts, `${width}-${tab}.png`), fullPage: true });
    }
    await page.close();
  }
  // Exercise populated views without publishing invented benchmark scores.
  const page = await browser.newPage();
  const models = ["Fixture Alpha", "Fixture Beta"].map((model, index) => ({
    model, rank: index + 1, runId: `fixture-${index}`, effort: "high", total: 80 - index * 10,
    raw: 70, skill: 80, skillGain: 10 + index, effectiveFormat: 80, precompileFormat: 90,
    compileRate: 80, passAt1: 70, categories: data.categories.map(c => ({ ...c, score: 80 })),
    capReasons: {}, packFailureReasons: {}, packFailures: 0, packAttempts: 30,
    protocol: "openai_responses", wireProtocol: "openai_responses", observedModels: [], reportUrl: "#",
  }));
  await page.route("**/data.json?*", route => route.fulfill({ json: {
    ...data, models, meta: { ...data.meta, modelCount: 2, latestResultAt: "2026-09-09T00:00:00Z" },
    summary: { ...data.summary, leader: models[0].model, leaderScore: 80, averagePrecompileFormat: 90, averageEffectiveFormat: 80 },
  } }));
  page.on("pageerror", error => errors.push(error.message));
  await page.goto(baseUrl);
  await expect(page.locator("#leaderboard-body tr")).toHaveCount(2);
  await page.locator('[data-sort="skillGain"]').click();
  await expect(page.locator(".model-button").first()).toContainText("Fixture Beta");
  await page.locator("#model-search").fill("Alpha");
  await expect(page.locator("#leaderboard-body tr")).toHaveCount(1);
  await page.locator(".model-button").click();
  await expect(page.locator("#model-dialog")).toBeVisible();
  await expect(page.locator("#dialog-title")).toHaveText("Fixture Alpha");
  await page.locator("#dialog-close").click();
  await page.locator("#model-search").fill("no-match");
  await expect(page.locator("#empty-state")).toContainText("没有匹配的模型");
  expect(errors).toEqual([]);
  console.log("web smoke: V2 desktop/mobile views, empty states, search, sort and details passed");
} finally {
  await browser.close();
}
