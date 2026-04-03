import { TEXT } from "../constants";
import type { AnalysisResponse } from "../types";
import { SectionCard } from "./SectionCard";

interface AnalysisPanelProps {
  analysis: AnalysisResponse | null;
}

export function AnalysisPanel({ analysis }: AnalysisPanelProps) {
  return (
    <SectionCard
      title="2. 분석 결과"
      description="이상 점수, 설명 근거, 과거 유사 사례를 한 번에 확인합니다."
    >
      {analysis ? (
        <div className="analysis-grid">
          <article className={`status-tile ${analysis.is_anomaly ? "is-alert" : "is-normal"}`}>
            <span>이상 점수</span>
            <strong>{(analysis.anomaly_score * 100).toFixed(1)}%</strong>
            <p>{analysis.is_anomaly ? "이상 가능성이 높습니다." : "즉시 이상으로 보기 어렵습니다."}</p>
          </article>
          <article className="explanation-card">
            <span className="chip">근거 출처: {analysis.explanation_source}</span>
            <p>{analysis.explanation_text}</p>
          </article>
          <article className="cases-card">
            <h3>유사 사례</h3>
            {analysis.similar_cases.length > 0 ? (
              <ul className="case-list">
                {analysis.similar_cases.map((caseItem) => (
                  <li key={caseItem.analysis_result_id}>
                    <div>
                      <strong>{caseItem.equipment_name}</strong>
                      <span>{caseItem.timestamp}</span>
                    </div>
                    <div className="case-metrics">
                      <span>유사도 {(caseItem.similarity_score * 100).toFixed(1)}%</span>
                      <span>점수 {(caseItem.anomaly_score * 100).toFixed(1)}%</span>
                    </div>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="empty-copy">{TEXT.emptyCases}</p>
            )}
          </article>
        </div>
      ) : (
        <div className="empty-panel">
          <h3>{TEXT.sampleTitle}</h3>
          <p>{TEXT.sampleBody}</p>
        </div>
      )}
    </SectionCard>
  );
}
