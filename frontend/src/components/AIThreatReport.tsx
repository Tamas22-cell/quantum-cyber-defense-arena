
import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";
import {
  Activity,
  AlertTriangle,
  Download,
  FileText,
  RefreshCw,
  ShieldCheck,
} from "lucide-react";

const API = "http://127.0.0.1:8000";
const NETWORKS = ["Ethereum", "Polygon", "Base", "Arbitrum"];

type Json = Record<string, unknown>;

type SecurityEvent = {
  id: string;
  network: string;
  type: string;
  risk: number;
  severity: string;
  timestamp: string;
};

type NetworkSummary = {
  network: string;
  events: number;
  highRisk: number;
  averageRisk: number;
  maximumRisk: number;
};

type ReportData = {
  generatedAt: string;
  totalEvents: number;
  activeThreats: number;
  criticalEvents: number;
  averageRisk: number;
  aiPredictions: number | null;
  aiAnomalies: number | null;
  networks: NetworkSummary[];
  criticalIncidents: SecurityEvent[];
};

function obj(value: unknown): Json {
  if (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  ) {
    return value as Json;
  }

  return {};
}

function num(value: unknown, fallback = 0): number {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function str(value: unknown, fallback = "Unknown"): string {
  return typeof value === "string" && value.trim()
    ? value
    : fallback;
}

function optionalNum(value: unknown): number | null {
  if (value === null || value === undefined) return null;

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

function createReport(
  threatsRaw: unknown,
  aiRaw: unknown
): ReportData {
  const threats = obj(threatsRaw);
  const ai = obj(aiRaw);
  const stats = obj(ai.model_statistics);

  const events: SecurityEvent[] = (
    Array.isArray(threats.events) ? threats.events : []
  ).map((entry: unknown, index: number) => {
    const event = obj(entry);

    return {
      id: str(event.id, `EVENT-${index + 1}`),
      network: str(event.network),
      type: str(event.type, "UNKNOWN_EVENT"),
      risk: num(event.risk_score),
      severity: str(event.severity),
      timestamp: str(event.timestamp, ""),
    };
  });

  const networkNames = Array.from(
    new Set([
      ...NETWORKS,
      ...events.map((event) => event.network),
    ])
  );

  const networks: NetworkSummary[] = networkNames.map(
    (network) => {
      const items = events.filter(
        (event) =>
          event.network.toLowerCase() ===
          network.toLowerCase()
      );

      const totalRisk = items.reduce(
        (sum, event) => sum + event.risk,
        0
      );

      return {
        network,
        events: items.length,
        highRisk: items.filter(
          (event) =>
            event.risk >= 80 ||
            event.severity.toUpperCase() === "CRITICAL"
        ).length,
        averageRisk:
          items.length > 0 ? totalRisk / items.length : 0,
        maximumRisk:
          items.length > 0
            ? Math.max(...items.map((event) => event.risk))
            : 0,
      };
    }
  );

  const criticalIncidents = [...events]
    .sort((a, b) => b.risk - a.risk)
    .slice(0, 8);

  return {
    generatedAt: new Date().toISOString(),
    totalEvents: num(threats.total_events, events.length),
    activeThreats: num(threats.active_threats),
    criticalEvents: num(threats.critical_events),
    averageRisk: num(threats.average_risk),
    aiPredictions: optionalNum(
      stats.total_predictions ?? ai.total_predictions
    ),
    aiAnomalies: optionalNum(
      stats.total_anomalies_detected ??
        stats.anomalies_detected ??
        stats.total_anomalies ??
        ai.total_anomalies_detected
    ),
    networks,
    criticalIncidents,
  };
}

const panel: CSSProperties = {
  borderRadius: 18,
  border: "1px solid rgba(104,180,255,.4)",
  background:
    "linear-gradient(135deg,rgba(9,30,65,.96),rgba(45,26,94,.92))",
  padding: 22,
  marginTop: 22,
  color: "#e8f5ff",
  boxShadow: "0 10px 36px rgba(0,0,0,.18)",
};

const metricCard: CSSProperties = {
  padding: 17,
  borderRadius: 12,
  background: "rgba(10,44,89,.65)",
  border: "1px solid rgba(83,188,245,.25)",
};

function Metric({
  title,
  value,
  color,
}: {
  title: string;
  value: string | number;
  color: string;
}) {
  return (
    <div style={metricCard}>
      <div
        style={{
          fontSize: 11,
          fontWeight: 700,
          color: "#a9cbe5",
          letterSpacing: 0.8,
        }}
      >
        {title}
      </div>
      <div
        style={{
          fontSize: 27,
          fontWeight: 800,
          color,
          marginTop: 9,
        }}
      >
        {value}
      </div>
    </div>
  );
}

function AIThreatReport() {
  const [report, setReport] = useState<ReportData | null>(
    null
  );
  const [online, setOnline] = useState(false);
  const [error, setError] = useState("");
  const [refreshCount, setRefreshCount] = useState(0);

  useEffect(() => {
    let active = true;
    let busy = false;

    async function refresh() {
      if (busy) return;
      busy = true;

      try {
        const [threatResponse, aiResponse] =
          await Promise.all([
            fetch(`${API}/api/threats`, {
              cache: "no-store",
            }),
            fetch(`${API}/api/ai/live`, {
              cache: "no-store",
            }),
          ]);

        if (!threatResponse.ok || !aiResponse.ok) {
          throw new Error("Backend API unavailable");
        }

        const [threatData, aiData]: [unknown, unknown] =
          await Promise.all([
            threatResponse.json(),
            aiResponse.json(),
          ]);

        if (!active) return;

        setReport(createReport(threatData, aiData));
        setOnline(true);
        setError("");
      } catch (err) {
        if (!active) return;

        setOnline(false);
        setError(
          err instanceof Error
            ? err.message
            : "Unknown API error"
        );
      } finally {
        busy = false;
      }
    }

    void refresh();

    const interval = window.setInterval(() => {
      void refresh();
    }, 3000);

    return () => {
      active = false;
      window.clearInterval(interval);
    };
  }, [refreshCount]);

  const anomalyRate = useMemo(() => {
    if (
      report?.aiPredictions == null ||
      report.aiAnomalies == null ||
      report.aiPredictions <= 0
    ) {
      return null;
    }

    return (
      (report.aiAnomalies / report.aiPredictions) * 100
    );
  }, [report]);

  function downloadReport() {
    if (!report) return;

    const exportData = {
      report_name: "Quantum Cyber Defense Arena - V5",
      report_type: "Automated AI Threat Report",
      mode: "SIMULATION",
      disclaimer:
        "Synthetic security events. Not verified attacks.",
      ...report,
      aiAnomalyRatePercent: anomalyRate,
    };

    const blob = new Blob(
      [JSON.stringify(exportData, null, 2)],
      { type: "application/json" }
    );

    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");

    anchor.href = url;
    anchor.download = `quantum-threat-report-${Date.now()}.json`;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();

    window.setTimeout(() => {
      URL.revokeObjectURL(url);
    }, 1000);
  }

  return (
    <section style={panel}>
      <header
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 15,
        }}
      >
        <div>
          <h2
            style={{
              margin: 0,
              display: "flex",
              gap: 10,
              alignItems: "center",
              fontSize: 21,
            }}
          >
            <FileText size={23} color="#79e6ff" />
            Automated AI Threat Report V5
          </h2>

          <p
            style={{
              color: "#acc9e3",
              fontSize: 12,
              marginBottom: 0,
            }}
          >
            Blockchain risk intelligence · Simulation
            research dashboard
          </p>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 13,
            flexWrap: "wrap",
          }}
        >
          <span
            style={{
              color: online ? "#75ffbc" : "#ff7b96",
              fontSize: 12,
              fontWeight: 800,
            }}
          >
            ● {online ? "REPORT LIVE" : "REPORT OFFLINE"}
          </span>

          <button
            type="button"
            onClick={() => setRefreshCount((n) => n + 1)}
            style={{
              cursor: "pointer",
              padding: 10,
              borderRadius: 9,
              color: "#c9efff",
              background: "rgba(15,80,135,.65)",
              border: "1px solid #437cae",
            }}
            title="Refresh report"
          >
            <RefreshCw size={17} />
          </button>

          <button
            type="button"
            disabled={!report}
            onClick={downloadReport}
            style={{
              cursor: report ? "pointer" : "not-allowed",
              padding: "10px 15px",
              borderRadius: 9,
              color: "#061f38",
              background: report ? "#72e8ff" : "#7996a6",
              border: "none",
              fontWeight: 800,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <Download size={17} />
            Export JSON
          </button>
        </div>
      </header>

      {error && (
        <p style={{ color: "#ff8ba6", fontSize: 12 }}>
          {error}
        </p>
      )}

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(min(100%,165px),1fr))",
          gap: 13,
          marginTop: 20,
        }}
      >
        <Metric
          title="SECURITY EVENTS"
          value={report?.totalEvents ?? "—"}
          color="#70e7ff"
        />
        <Metric
          title="ACTIVE THREATS"
          value={report?.activeThreats ?? "—"}
          color="#ffd071"
        />
        <Metric
          title="CRITICAL EVENTS"
          value={report?.criticalEvents ?? "—"}
          color="#ff7097"
        />
        <Metric
          title="AI ANOMALIES"
          value={report?.aiAnomalies ?? "—"}
          color="#dc9dff"
        />
        <Metric
          title="AI ANOMALY RATE"
          value={
            anomalyRate == null
              ? "—"
              : `${anomalyRate.toFixed(1)}%`
          }
          color="#7dffc5"
        />
      </div>

      <h3
        style={{
          marginTop: 25,
          display: "flex",
          alignItems: "center",
          gap: 8,
          fontSize: 16,
        }}
      >
        <Activity size={19} color="#7ce8ff" />
        Blockchain Network Risk Analysis
      </h3>

      <div style={{ overflowX: "auto" }}>
        <table
          style={{
            width: "100%",
            minWidth: 540,
            borderCollapse: "collapse",
            fontSize: 12,
            textAlign: "left",
          }}
        >
          <thead>
            <tr style={{ color: "#9edaf5" }}>
              {[
                "NETWORK",
                "EVENTS",
                "HIGH RISK",
                "AVERAGE RISK",
                "MAX RISK",
              ].map((column) => (
                <th
                  key={column}
                  style={{ padding: "12px 10px" }}
                >
                  {column}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {report?.networks.map((item) => (
              <tr
                key={item.network}
                style={{
                  borderTop:
                    "1px solid rgba(130,205,255,.16)",
                }}
              >
                <td style={{ padding: 11, fontWeight: 700 }}>
                  {item.network}
                </td>
                <td style={{ padding: 11 }}>
                  {item.events}
                </td>
                <td
                  style={{
                    padding: 11,
                    color: "#ff93a7",
                  }}
                >
                  {item.highRisk}
                </td>
                <td style={{ padding: 11 }}>
                  {item.averageRisk.toFixed(1)}
                </td>
                <td style={{ padding: 11 }}>
                  {item.maximumRisk}/100
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3
        style={{
          marginTop: 26,
          display: "flex",
          alignItems: "center",
          gap: 8,
          fontSize: 16,
        }}
      >
        <AlertTriangle size={19} color="#ff869d" />
        Highest-Risk Security Incidents
      </h3>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(min(100%,245px),1fr))",
          gap: 12,
          marginTop: 14,
        }}
      >
        {report?.criticalIncidents.map((event) => (
          <div
            key={event.id}
            style={{
              padding: 15,
              borderRadius: 10,
              background: "rgba(8,29,65,.72)",
              border:
                "1px solid rgba(255,111,147,.23)",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                gap: 8,
              }}
            >
              <strong>{event.network}</strong>
              <strong
                style={{
                  color:
                    event.risk >= 80
                      ? "#ff7097"
                      : "#ffd17b",
                }}
              >
                {event.risk}/100
              </strong>
            </div>

            <p
              style={{
                color: "#b8d6eb",
                fontSize: 12,
                marginBottom: 0,
              }}
            >
              {event.type.replaceAll("_", " ")}
            </p>
          </div>
        ))}
      </div>

      <footer
        style={{
          borderTop:
            "1px solid rgba(133,185,255,.22)",
          marginTop: 24,
          paddingTop: 14,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          gap: 10,
          color: "#91bad5",
          fontSize: 11,
        }}
      >
        <span>
          <ShieldCheck size={13} style={{ marginRight: 6 }} />
          RESEARCH SIMULATION · NOT VERIFIED ATTACKS
        </span>
        <span>
          Updated:{" "}
          {report
            ? new Date(
                report.generatedAt
              ).toLocaleTimeString("hu-HU")
            : "Waiting for data"}
        </span>
      </footer>
    </section>
  );
}

export default AIThreatReport;
