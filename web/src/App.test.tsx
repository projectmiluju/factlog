import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, expect, test, vi } from "vitest";

import App from "./App";
import type { AnalysisResponse, DashboardSummary } from "./types";

const dashboardSummary: DashboardSummary = {
  total_analyses: 0,
  total_actions: 0,
  anomaly_count: 0,
  accuracy_label: "97.27%",
  recent_analyses: [],
  validation_datasets: [
    {
      dataset_name: "NASA C-MAPSS",
      subset: "FD001",
      model_name: "LogisticRegression",
      model_version: "logistic-regression-balanced-v1",
      metrics: [{ metric_name: "accuracy", metric_value: 0.9727 }],
      notes: ["테스트 요약"],
    },
  ],
};

const analysisResponse: AnalysisResponse = {
  analysis_result_id: 11,
  sensor_record_id: 7,
  anomaly_score: 0.82,
  is_anomaly: true,
  explanation_text: "온도와 진동이 기준치를 초과했습니다.",
  explanation_source: "fallback",
  similar_cases: [],
};

const apiMocks = vi.hoisted(() => ({
  saveSensorRecord: vi.fn(),
  runAnalysis: vi.fn(),
  saveAction: vi.fn(),
  uploadSensorCsv: vi.fn(),
  fetchDashboardSummary: vi.fn(),
}));

vi.mock("./lib/api", () => ({
  saveSensorRecord: apiMocks.saveSensorRecord,
  runAnalysis: apiMocks.runAnalysis,
  saveAction: apiMocks.saveAction,
  uploadSensorCsv: apiMocks.uploadSensorCsv,
  fetchDashboardSummary: apiMocks.fetchDashboardSummary,
}));

beforeEach(() => {
  vi.clearAllMocks();
  apiMocks.fetchDashboardSummary.mockResolvedValue(dashboardSummary);
  apiMocks.saveSensorRecord.mockResolvedValue({ record_id: 7, status: "saved" });
  apiMocks.runAnalysis.mockResolvedValue(analysisResponse);
  apiMocks.saveAction.mockResolvedValue({ action_log_id: 3, analysis_result_id: 11, status: "saved" });
  apiMocks.uploadSensorCsv.mockResolvedValue({ status: "imported", imported_count: 1, record_ids: [7] });
});

test("초기 진입 시 샘플 분석 온보딩 문구를 표시해야 한다", async () => {
  render(<App />);

  expect(screen.getByText("처음이라면 샘플 분석부터")).toBeInTheDocument();
  await waitFor(() => {
    expect(apiMocks.fetchDashboardSummary).toHaveBeenCalledTimes(1);
  });
});

test("분석 실행 중에는 버튼을 비활성화해야 한다", async () => {
  let resolveAnalysis: ((value: AnalysisResponse) => void) | undefined;
  apiMocks.runAnalysis.mockImplementation(
    () =>
      new Promise<AnalysisResponse>((resolve) => {
        resolveAnalysis = resolve;
      }),
  );

  const user = userEvent.setup();
  render(<App />);

  const runButton = screen.getByRole("button", { name: "분석 실행" });
  await user.click(runButton);

  expect(screen.getByRole("button", { name: "분석 중..." })).toBeDisabled();

  resolveAnalysis?.(analysisResponse);

  await waitFor(() => {
    expect(screen.getByText("분석이 완료되었습니다. 결과와 유사 사례를 확인하세요.")).toBeInTheDocument();
  });
});

test("조치 기록 저장 후 성공 메시지를 표시해야 한다", async () => {
  const user = userEvent.setup();
  render(<App />);

  await user.click(screen.getByRole("button", { name: "분석 실행" }));

  await waitFor(() => {
    expect(screen.getByRole("button", { name: "조치 기록 저장" })).toBeInTheDocument();
  });

  await user.click(screen.getByRole("button", { name: "조치 기록 저장" }));

  await waitFor(() => {
    expect(apiMocks.saveAction).toHaveBeenCalledTimes(1);
    expect(screen.getByText("조치 기록을 저장했고 대시보드를 갱신했습니다.")).toBeInTheDocument();
  });
});
