import { useState } from "react";

import { TEXT } from "../constants";
import type { AnalysisResponse } from "../types";
import { SectionCard } from "./SectionCard";

interface ActionPanelProps {
  analysis: AnalysisResponse | null;
  saving: boolean;
  onSave: (payload: { action_taken: string; operator_name: string; result_note: string }) => Promise<void>;
}

export function ActionPanel({ analysis, saving, onSave }: ActionPanelProps) {
  const [actionTaken, setActionTaken] = useState("냉각 점검 및 회전수 보정");
  const [operatorName, setOperatorName] = useState("현장 담당자");
  const [resultNote, setResultNote] = useState("이상 경향 재확인 필요");

  const handleSubmit = async () => {
    await onSave({
      action_taken: actionTaken,
      operator_name: operatorName,
      result_note: resultNote,
    });
  };

  return (
    <SectionCard
      title="3. 조치 기록"
      description="실제 조치를 저장해 다음 분석에서 재사용할 수 있는 현장 지식으로 남깁니다."
    >
      {analysis ? (
        <div className="action-grid">
          <label>
            조치 내용
            <textarea value={actionTaken} onChange={(event) => setActionTaken(event.target.value)} rows={3} />
          </label>
          <label>
            담당자
            <input value={operatorName} onChange={(event) => setOperatorName(event.target.value)} />
          </label>
          <label>
            결과 메모
            <textarea value={resultNote} onChange={(event) => setResultNote(event.target.value)} rows={3} />
          </label>
          <button className="primary-button" disabled={saving} onClick={handleSubmit} type="button">
            {saving ? "저장 중..." : TEXT.saveAction}
          </button>
        </div>
      ) : (
        <p className="empty-copy">먼저 분석을 실행하면 조치 기록을 저장할 수 있습니다.</p>
      )}
    </SectionCard>
  );
}
