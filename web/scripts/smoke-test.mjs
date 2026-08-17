import { mkdir } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { chromium, expect } from "@playwright/test";

const scriptDir = dirname(fileURLToPath(import.meta.url));
const projectRoot = resolve(scriptDir, "../..");
const artifacts = resolve(projectRoot, "web/test-artifacts");
const baseUrl = process.env.WEB_BASE_URL ?? "http://127.0.0.1:4173";
await mkdir(artifacts, { recursive: true });

const browser = await chromium.launch();
const browserErrors = [];

async function preparePage(viewport) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => {
    if (message.type() === "error") browserErrors.push(`console: ${message.text()}`);
  });
  page.on("pageerror", (error) => browserErrors.push(`pageerror: ${error.message}`));
  await page.goto(baseUrl, { waitUntil: "networkidle" });
  await expect(page.locator("#leaderboard-body tr")).toHaveCount(17);
  await expect(page.locator("#leader-score")).toHaveText("29.50");
  const leaderLayout = await page.locator(".leader-callout").evaluate((element) => {
    const scoreBox = element.querySelector("#leader-score").getBoundingClientRect();
    const name = element.querySelector("#leader-name");
    const nameBox = name.getBoundingClientRect();
    return {
      nameBelowScore: nameBox.top >= scoreBox.bottom,
      nameUnclipped: name.scrollWidth <= name.clientWidth && name.scrollHeight <= name.clientHeight,
    };
  });
  if (!leaderLayout.nameBelowScore || !leaderLayout.nameUnclipped) {
    throw new Error("leader model name must render below the score without clipping");
  }
  await expect(page.getByText("编译率最高", { exact: true })).toHaveCount(0);
  await expect(page.locator(".toolchain-item")).toHaveCount(3);
  for (const project of ["e-packager", "AutoLinker", "e-language-skill"]) {
    await expect(page.locator(`.toolchain-item:has-text("${project}")`)).toBeVisible();
  }
  return page;
}

try {
  const desktop = await preparePage({ width: 1440, height: 1000 });
  await desktop.screenshot({ path: resolve(artifacts, "desktop.png"), fullPage: true });

  await desktop.locator("#model-search").fill("claude-opus-5");
  await expect(desktop.locator("#leaderboard-body tr")).toHaveCount(1);
  await desktop.locator("#model-search").fill("");
  await expect(desktop.locator("#leaderboard-body tr")).toHaveCount(17);

  await desktop.locator("#model-search").fill("hy3");
  await expect(desktop.locator("#leaderboard-body tr")).toHaveCount(1);
  await expect(desktop.locator("#leaderboard-body .score-cell")).toHaveText("9.66");
  await desktop.locator("#model-search").fill("");

  await desktop.locator('[data-tab="scoring"]').click();
  await expect(desktop.locator('[data-view="scoring"]')).toBeVisible();
  await desktop.screenshot({ path: resolve(artifacts, "scoring.png"), fullPage: true });

  await desktop.locator('[data-tab="matrix"]').click();
  await expect(desktop.locator("#matrix-body tr")).toHaveCount(17);
  await desktop.screenshot({ path: resolve(artifacts, "matrix.png"), fullPage: true });

  await desktop.locator('[data-tab="leaderboard"]').click();
  await desktop.locator("#leaderboard-body .model-button").first().click();
  await expect(desktop.locator("#model-dialog")).toBeVisible();
  await expect(desktop.locator("#dialog-title")).toHaveText("gemini-3.6-flash");
  await desktop.screenshot({ path: resolve(artifacts, "detail.png") });
  await desktop.locator("#dialog-close").click();
  await desktop.close();

  const mobile = await preparePage({ width: 390, height: 844 });
  for (const selector of [".model-cell", ".score-cell", ".format-cell", ".mobile-keep"]) {
    const box = await mobile.locator(`#leaderboard-body ${selector}`).first().boundingBox();
    if (!box || box.x < 0 || box.x + box.width > 390) {
      throw new Error(`${selector} is outside the mobile viewport`);
    }
  }
  await mobile.screenshot({ path: resolve(artifacts, "mobile.png"), fullPage: true });
  await mobile.locator("#leaderboard-body .model-button").first().click();
  await expect(mobile.locator("#model-dialog")).toBeVisible();
  await mobile.screenshot({ path: resolve(artifacts, "mobile-detail.png") });
  await mobile.close();

  const narrow = await preparePage({ width: 320, height: 760 });
  for (const selector of [".model-cell", ".score-cell", ".format-cell", ".mobile-keep"]) {
    const box = await narrow.locator(`#leaderboard-body ${selector}`).first().boundingBox();
    if (!box || box.x < 0 || box.x + box.width > 320) {
      throw new Error(`${selector} is outside the 320px viewport`);
    }
  }
  await narrow.screenshot({ path: resolve(artifacts, "mobile-320.png"), fullPage: true });
  await narrow.close();

  if (browserErrors.length > 0) {
    throw new Error(browserErrors.join("\n"));
  }
  console.log(`web smoke: desktop/mobile views and interactions passed (${baseUrl})`);
} finally {
  await browser.close();
}
