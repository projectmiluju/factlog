export interface SensorRecordInput {
  equipment_name: string;
  equipment_type: string;
  source_dataset: "manual" | "nasa_cmapss" | "aihub";
  timestamp: string;
  temperature: number;
  vibration: number;
  rpm: number;
  torque: number;
  tool_wear: number;
}

export interface SimilarCaseItem {
  analysis_result_id: number;
  sensor_record_id: number;
  equipment_name: string;
  timestamp: string;
  anomaly_score: number;
  similarity_score: number;
}

export interface AnalysisResponse {
  analysis_result_id: number;
  sensor_record_id: number;
  anomaly_score: number;
  is_anomaly: boolean;
  explanation_text: string;
  explanation_source: string;
  similar_cases: SimilarCaseItem[];
}

export interface ActionResponse {
  action_log_id: number;
  analysis_result_id: number;
  status: string;
}

export interface RecentAnalysisItem {
  analysis_result_id: number;
  sensor_record_id: number;
  equipment_name: string;
  timestamp: string;
  anomaly_score: number;
  is_anomaly: boolean;
  explanation_source: string;
  action_logged: boolean;
}

export interface MetricItem {
  metric_name: string;
  metric_value: number;
}

export interface ValidationDatasetItem {
  dataset_name: string;
  subset?: string | null;
  model_name?: string | null;
  model_version?: string | null;
  metrics: MetricItem[];
  notes: string[];
}

export interface DashboardSummary {
  total_analyses: number;
  total_actions: number;
  anomaly_count: number;
  accuracy_label: string;
  recent_analyses: RecentAnalysisItem[];
  validation_datasets: ValidationDatasetItem[];
}
