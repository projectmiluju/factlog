import { useEffect, useState } from "react";

import { ActionPanel } from "./components/ActionPanel";
import { AnalysisPanel } from "./components/AnalysisPanel";
import { DashboardPanel } from "./components/DashboardPanel";
import { InputPanel } from "./components/InputPanel";
import { DEFAULT_FORM, SAMPLE_FORM, TEXT } from "./constants";
import { fetchDashboardSummary, runAnalysis, saveAction, saveSensorRecord, uploadSensorCsv } from "./lib/api";
import type { AnalysisResponse, DashboardSummary, SensorRecordInput } from "./types";

export default function App() {
  const [form, setForm] = useState<SensorRecordInput>(DEFAULT_FORM);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);
  const [dashboard, setDashboard] = useState<DashboardSummary | null>(null);
  const [message, setMessage] = useState<string>("");
  const [error, setError] = useState<string>("");
  const [busy, setBusy] = useState(false);
  const [uploadBusy, setUploadBusy] = useState(false);
  const [savingAction, setSavingAction] = useState(false);

  const refreshDashboard = async () => {
    try {
      const summary = await fetchDashboardSummary();
      setDashboard(summary);
    } catch (refreshError) {
      setError(refreshError instanceof Error ? refreshError.message : "대시보드 조회에 실패했습니다.");
    }
  };

  useEffect(() => {
    void refreshDashboard();
  }, []);

  const updateField = (field: keyof SensorRecordInput, value: string | number) => {
    setForm((current) => ({ ...current, [field]: value }));
  };

  const runManualAnalysis = async (payload: SensorRecordInput) => {
    setBusy(true);
    setError("");
    setMessage("");
    try {
      const savedRecord = await saveSensorRecord(payload);
      const analysisResponse = await runAnalysis(savedRecord.record_id);
      setAnalysis(analysisResponse);
      setMessage("분석이 완료되었습니다. 결과와 유사 사례를 확인하세요.");
      await refreshDashboard();
    } catch (runError) {
      setError(runError instanceof Error ? runError.message : "분석 실행에 실패했습니다.");
    } finally {
      setBusy(false);
    }
  };

  const handleRunAnalysis = async () => {
    await runManualAnalysis(form);
  };

  const handleRunSample = async () => {
    setForm(SAMPLE_FORM);
    await runManualAnalysis(SAMPLE_FORM);
  };

  const handleUploadCsv = async (file: File) => {
    setUploadBusy(true);
    setError("");
    setMessage("");
    try {
      const uploaded = await uploadSensorCsv(file);
      const latestRecordId = uploaded.record_ids[uploaded.record_ids.length - 1];
      if (latestRecordId) {
        const analysisResponse = await runAnalysis(latestRecordId);
        setAnalysis(analysisResponse);
      }
      setMessage(`${uploaded.imported_count}건을 업로드했고 마지막 레코드 기준 분석을 완료했습니다.`);
      await refreshDashboard();
    } catch (uploadError) {
      setError(uploadError instanceof Error ? uploadError.message : "CSV 업로드에 실패했습니다.");
    } finally {
      setUploadBusy(false);
    }
  };

  const handleSaveAction = async (payload: {
    action_taken: string;
    operator_name: string;
    result_note: string;
  }) => {
    if (!analysis) {
      return;
    }

    setSavingAction(true);
    setError("");
    setMessage("");
    try {
      await saveAction({
        analysis_result_id: analysis.analysis_result_id,
        ...payload,
      });
      setMessage("조치 기록을 저장했고 대시보드를 갱신했습니다.");
      await refreshDashboard();
    } catch (saveError) {
      setError(saveError instanceof Error ? saveError.message : "조치 저장에 실패했습니다.");
    } finally {
      setSavingAction(false);
    }
  };

  return (
    <main className="app-shell">
      <section className="hero-card">
        <p className="eyebrow">FactLog</p>
        <h1>{TEXT.appTitle}</h1>
        <p className="lead">{TEXT.appSubtitle}</p>
      </section>
      {message ? <div className="notice success">{message}</div> : null}
      {error ? <div className="notice error">{error}</div> : null}
      <div className="app-grid">
        <div className="stack-column">
          <InputPanel
            busy={busy}
            form={form}
            onChange={updateField}
            onRunAnalysis={handleRunAnalysis}
            onRunSample={handleRunSample}
            onUploadCsv={handleUploadCsv}
            uploadBusy={uploadBusy}
          />
          <AnalysisPanel analysis={analysis} />
          <ActionPanel analysis={analysis} onSave={handleSaveAction} saving={savingAction} />
        </div>
        <DashboardPanel dashboard={dashboard} />
      </div>
    </main>
  );
}
