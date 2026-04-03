import { defineConfig } from "@playwright/test";

export default defineConfig({
  testDir: "./e2e",
  timeout: 30_000,
  use: {
    baseURL: "http://127.0.0.1:4173",
    headless: true,
  },
  webServer: [
    {
      command: "mkdir -p .tmp && python3 -m uvicorn factlog_ml.api:app --host 127.0.0.1 --port 8000",
      cwd: "..",
      env: {
        FACTLOG_DB_PATH: ".tmp/factlog-e2e.db",
      },
      url: "http://127.0.0.1:8000/health",
      reuseExistingServer: true,
    },
    {
      command: "npm run dev -- --host 127.0.0.1 --port 4173",
      cwd: ".",
      url: "http://127.0.0.1:4173",
      reuseExistingServer: true,
    },
  ],
});
