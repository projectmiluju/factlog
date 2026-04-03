import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import type { DashboardSummary } from "../types";
import { SectionCard } from "./SectionCard";

interface DashboardPanelProps {
  dashboard: DashboardSummary | null;
}

export function DashboardPanel({ dashboard }: DashboardPanelProps) {
  const chartData =
    dashboard?.recent_analyses.slice(0, 6).map((item) => ({
      name: item.equipment_name,
      score: Number((item.anomaly_score * 100).toFixed(1)),
    })) ?? [];

  return (
    <SectionCard
      title="4. 대시보드"
      description="최근 분석 이력, 조치 현황, NASA 검증 요약을 한 번에 확인합니다."
    >
      {dashboard ? (
        <div className="dashboard-stack">
          <div className="metric-grid">
            <article className="metric-card">
              <span>총 분석 건수</span>
              <strong>{dashboard.total_analyses}</strong>
            </article>
            <article className="metric-card">
              <span>이상 판정 건수</span>
              <strong>{dashboard.anomaly_count}</strong>
            </article>
            <article className="metric-card">
              <span>조치 기록 건수</span>
              <strong>{dashboard.total_actions}</strong>
            </article>
            <article className="metric-card">
              <span>NASA 정확도</span>
              <strong>{dashboard.accuracy_label}</strong>
            </article>
          </div>
          <div className="dashboard-grid">
            <div className="chart-card">
              <h3>최근 이상 점수</h3>
              <div className="chart-frame">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                    <XAxis dataKey="name" tickLine={false} axisLine={false} />
                    <YAxis tickLine={false} axisLine={false} />
                    <Tooltip />
                    <Bar dataKey="score" fill="#0f766e" radius={[8, 8, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
            <div className="history-card">
              <h3>최근 이력 20건</h3>
              <ul className="history-list">
                {dashboard.recent_analyses.map((item) => (
                  <li key={item.analysis_result_id}>
                    <div>
                      <strong>{item.equipment_name}</strong>
                      <span>{item.timestamp}</span>
                    </div>
                    <div className="case-metrics">
                      <span>{item.is_anomaly ? "이상" : "정상"}</span>
                      <span>{item.action_logged ? "조치 기록 있음" : "조치 대기"}</span>
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div className="validation-card">
            <h3>검증 요약</h3>
            {dashboard.validation_datasets.map((dataset) => (
              <article key={dataset.dataset_name}>
                <div className="validation-heading">
                  <strong>{dataset.dataset_name}</strong>
                  <span>{dataset.model_name} / {dataset.model_version}</span>
                </div>
                <div className="metric-badges">
                  {dataset.metrics.slice(0, 5).map((metric) => (
                    <span className="chip" key={metric.metric_name}>
                      {metric.metric_name}: {(metric.metric_value * 100).toFixed(2)}%
                    </span>
                  ))}
                </div>
              </article>
            ))}
          </div>
        </div>
      ) : (
        <div className="empty-panel">
          <h3>대시보드가 아직 비어 있습니다</h3>
          <p>첫 분석이 저장되면 최근 이력과 검증 요약이 여기에 반영됩니다.</p>
        </div>
      )}
    </SectionCard>
  );
}
