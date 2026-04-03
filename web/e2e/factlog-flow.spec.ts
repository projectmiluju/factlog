import { expect, test } from "@playwright/test";

test("입력부터 분석, 조치 기록, 대시보드 반영까지 완료해야 한다", async ({ page }) => {
  await page.goto("/");

  await expect(
    page.getByRole("heading", { name: "근거 기반 설비 이상 감지 대시보드" }),
  ).toBeVisible();
  await expect(page.getByText("처음이라면 샘플 분석부터")).toBeVisible();

  await page.getByRole("button", { name: "분석 실행", exact: true }).click();

  await expect(page.getByText("분석이 완료되었습니다. 결과와 유사 사례를 확인하세요.")).toBeVisible();
  await expect(page.getByText("근거 출처:")).toBeVisible();
  await expect(page.getByRole("button", { name: "조치 기록 저장" })).toBeVisible();

  await page.getByLabel("조치 내용").fill("냉각 장치 점검 후 회전수 재보정");
  await page.getByLabel("담당자").fill("PO-AI 테스트");
  await page.getByLabel("결과 메모").fill("이상 점수 재확인 예정");
  await page.getByRole("button", { name: "조치 기록 저장" }).click();

  await expect(page.getByText("조치 기록을 저장했고 대시보드를 갱신했습니다.")).toBeVisible();
  await expect(page.getByText("조치 기록 건수")).toBeVisible();
  await expect(page.locator(".history-list").getByText("MILL-01").first()).toBeVisible();
  await expect(page.locator(".history-list").getByText("조치 기록 있음").first()).toBeVisible();
});
