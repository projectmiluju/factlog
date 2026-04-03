import type { ChangeEvent } from "react";

import { TEXT } from "../constants";
import type { SensorRecordInput } from "../types";
import { SectionCard } from "./SectionCard";

interface InputPanelProps {
  form: SensorRecordInput;
  busy: boolean;
  uploadBusy: boolean;
  onChange: (field: keyof SensorRecordInput, value: string | number) => void;
  onRunAnalysis: () => void;
  onUploadCsv: (file: File) => void;
  onRunSample: () => void;
}

const NUMERIC_FIELDS: Array<keyof SensorRecordInput> = [
  "temperature",
  "vibration",
  "rpm",
  "torque",
  "tool_wear",
];

export function InputPanel({
  form,
  busy,
  uploadBusy,
  onChange,
  onRunAnalysis,
  onUploadCsv,
  onRunSample,
}: InputPanelProps) {
  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      onUploadCsv(file);
      event.target.value = "";
    }
  };

  return (
    <SectionCard
      title="1. 센서 입력"
      description="설비 센서값을 직접 입력하거나 CSV 파일로 업로드합니다."
      aside={
        <button className="ghost-button" onClick={onRunSample} type="button">
          샘플 분석 실행
        </button>
      }
    >
      <div className="input-grid">
        <label>
          설비명
          <input
            value={form.equipment_name}
            onChange={(event) => onChange("equipment_name", event.target.value)}
          />
        </label>
        <label>
          설비 유형
          <input
            value={form.equipment_type}
            onChange={(event) => onChange("equipment_type", event.target.value)}
          />
        </label>
        <label>
          데이터 소스
          <select
            value={form.source_dataset}
            onChange={(event) =>
              onChange("source_dataset", event.target.value as SensorRecordInput["source_dataset"])
            }
          >
            <option value="manual">manual</option>
            <option value="nasa_cmapss">nasa_cmapss</option>
            <option value="aihub">aihub</option>
          </select>
        </label>
        <label>
          측정 시각
          <input
            value={form.timestamp}
            onChange={(event) => onChange("timestamp", event.target.value)}
          />
        </label>
        {NUMERIC_FIELDS.map((field) => (
          <label key={field}>
            {field}
            <input
              type="number"
              step="0.01"
              value={form[field]}
              onChange={(event) => onChange(field, Number(event.target.value))}
            />
          </label>
        ))}
      </div>
      <div className="button-row">
        <button className="primary-button" disabled={busy} onClick={onRunAnalysis} type="button">
          {busy ? "분석 중..." : TEXT.runAnalysis}
        </button>
        <label className={`upload-button ${uploadBusy ? "is-disabled" : ""}`}>
          {uploadBusy ? "업로드 중..." : TEXT.uploadCsv}
          <input disabled={uploadBusy} hidden onChange={handleFileChange} type="file" accept=".csv" />
        </label>
      </div>
    </SectionCard>
  );
}
