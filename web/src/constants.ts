import type { SensorRecordInput } from "./types";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export const TEXT = {
  appTitle: "근거 기반 설비 이상 감지 대시보드",
  appSubtitle:
    "센서 입력부터 AI 분석, 조치 기록, 최근 이력 확인까지 한 화면 흐름으로 연결합니다.",
  sampleTitle: "처음이라면 샘플 분석부터",
  sampleBody:
    "아직 축적된 사례가 없다면 샘플 입력으로 첫 분석을 실행해 근거와 유사 사례 흐름을 확인하세요.",
  emptyCases: "아직 축적된 유사 사례가 없습니다. 첫 기록이 다음 판단의 근거가 됩니다.",
  saveAction: "조치 기록 저장",
  runAnalysis: "분석 실행",
  uploadCsv: "CSV 업로드",
} as const;

export const DEFAULT_FORM: SensorRecordInput = {
  equipment_name: "MILL-01",
  equipment_type: "milling_machine",
  source_dataset: "manual",
  timestamp: "2026-04-04T09:00:00Z",
  temperature: 304.5,
  vibration: 0.16,
  rpm: 1480,
  torque: 36,
  tool_wear: 14,
};

export const SAMPLE_FORM: SensorRecordInput = {
  equipment_name: "MILL-DEMO-01",
  equipment_type: "milling_machine",
  source_dataset: "manual",
  timestamp: "2026-04-04T09:30:00Z",
  temperature: 311.5,
  vibration: 0.23,
  rpm: 1280,
  torque: 44,
  tool_wear: 27,
};
