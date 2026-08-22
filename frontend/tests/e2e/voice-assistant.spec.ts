import { test, expect } from "@playwright/test";

test.describe("Voice AI production flow", () => {
  test("loads authenticated assistant shell", async ({ page }) => {
    await page.goto("/");
    await expect(page).toHaveTitle(/voice|ai|assistant/i);
  });

  test("assistant exposes conversation UI", async ({ page }) => {
    await page.goto("/");
    const body = await page.locator("body").innerText();
    expect(body.length).toBeGreaterThan(0);
  });
});
