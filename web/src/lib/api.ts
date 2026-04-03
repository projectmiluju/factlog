import { API_BASE_URL } from "../constants";
import type {
  ActionResponse,
  AnalysisResponse,
  DashboardSummary,
  SensorRecordInput,
} from "../types";

interface SaveSensorRecordResponse {
  record_id: number;
  status: string;
}

interface UploadResponse {
  status: string;
  imported_count: number;
  record_ids: number[];
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, init);
  if (!response.ok) {
    const payload = await response.json().catch(() => ({ detail: "요청 실패" }));
    const message =
      typeof payload.detail === "string"
        ? payload.detail
        : Array.isArray(payload.detail)
          ? payload.detail.map((item: { column_name: string; message: string }) => `${item.column_name}: ${item.message}`).join(", ")
          : "요청 실패";
    throw new Error(message);
  }
  return response.json() as Promise<T>;
}

export function saveSensorRecord(sensor_record: SensorRecordInput): Promise<SaveSensorRecordResponse> {
  return request<SaveSensorRecordResponse>("/api/sensor-records", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sensor_record }),
  });
}

export function uploadSensorCsv(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append("file", file);
  return request<UploadResponse>("/api/uploads/csv", {
    method: "POST",
    body: formData,
  });
}

export function runAnalysis(sensorRecordId: number): Promise<AnalysisResponse> {
  return request<AnalysisResponse>("/api/analysis", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sensor_record_id: sensorRecordId }),
  });
}

export function saveAction(payload: {
  analysis_result_id: number;
  action_taken: string;
  operator_name: string;
  result_note: string;
}): Promise<ActionResponse> {
  return request<ActionResponse>("/api/actions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}

export function fetchDashboardSummary(): Promise<DashboardSummary> {
  return request<DashboardSummary>("/api/dashboard/summary");
}
