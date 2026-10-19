
import { useCallback, useEffect, useState } from "react";
import type { CSSProperties, ReactNode } from "react";

import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ClipboardList,
  RefreshCw,
  Search,
  Shield,
  ShieldAlert,
  Users,
  X,
} from "lucide-react";

const API_URL = "http://127.0.0.1:8000/api/agents/live";
const REFRESH_MS = 5000;

type AgentFinding = {
  agent: string;
  status: string;
  summary: string;
  findings: string[];
  recommendations: string[];
  confidence_note: string;
};

type AgentReport = {
  report_id: string;
  event_id: string;
  network: string;
  timestamp: string;
  engine_version: string;
  mode: string;
  classification: string;
  severity: string;
  fusion_score_100: number;
  priority: string;
  agent_count: number;
  agent_results: AgentFinding[];
  consensus: string;
  requires_review: boolean;
  executive_summary: string;
  consolidated_findings: string[];
  recommended_actions: string[];
};

type EngineStatistics = {
  version?: string;
  status?: string;
  processed_events?: number;
  review_events?: number;
  anomaly_events?: number;
};

type AgentApiResponse = {
  version: string;
  mode: string;
  status: string;
  generated_at: string;
  total_available: number;
  report_count: number;
  agent_count: number;
  reports: AgentReport[];
  statistics: EngineStatistics;
};

const colors = {
  cyan: "#67e8f9",
  blue: "#38bdf8",
  purple: "#c084fc",
  red: "#fb7185",
  orange: "#fb923c",
  yellow: "#facc15",
  green: "#34d399",
  text: "#e2e8f0",
  muted: "#94a3b8",
};

const panelStyle: CSSProperties = {
  background: "linear-gradient(145deg, #101f39, #10172d)",
  border: "1px solid rgba(103,232,249,0.25)",
  borderRadius: 18,
  padding: 20,
  minWidth: 0,
};

const buttonStyle: CSSProperties = {
  background: "#193c61",
  border: "1px solid #497eac",
  borderRadius: 9,
  padding: "10px 14px",
  color: "#e0f2fe",
  fontWeight: 700,
  fontSize: 12,
  cursor: "pointer",
};

function priorityColor(priority: string): string {
  if (priority === "P1") return colors.red;
  if (priority === "P2") return colors.orange;
  if (priority === "P3") return colors.yellow;
  return colors.green;
}

function classificationColor(value: string): string {
  if (value === "ANOMALY") return colors.red;
  if (value === "REVIEW") return colors.yellow;
  return colors.green;
}

function formatScore(value: number): string {
  return Number.isFinite(value)
    ? `${value.toFixed(2)}/100`
    : "—";
}

function Metric({
  title,
  value,
  icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: ReactNode;
  color: string;
}) {
  return (
    <div style={panelStyle}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 9,
          color,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 0.7,
        }}
      >
        {icon}
        {title}
      </div>

      <div
        style={{
          color: "#f8fafc",
          marginTop: 15,
          fontSize: 29,
          fontWeight: 800,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </div>
    </div>
  );
}

function ScoreBar({
  label,
  score,
  color,
}: {
  label: string;
  score: number;
  color: string;
}) {
  const safe = Number.isFinite(score)
    ? Math.max(0, Math.min(100, score))
    : 0;

  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 10,
          color: colors.muted,
          marginBottom: 7,
          fontSize: 12,
        }}
      >
        <span>{label}</span>
        <strong style={{ color }}>{safe.toFixed(2)}%</strong>
      </div>

      <div
        style={{
          height: 9,
          background: "#1a2e47",
          borderRadius: 99,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${safe}%`,
            height: "100%",
            background: color,
            borderRadius: 99,
            transition: "width 500ms ease",
          }}
        />
      </div>
    </div>
  );
}

function AgentCard({ agent }: { agent: AgentFinding }) {
  const agentColor =
    agent.status === "DISAGREEMENT" ||
    agent.status === "ALERT"
      ? colors.red
      : agent.status === "REVIEW"
        ? colors.yellow
        : colors.green;

  return (
    <div
      style={{
        ...panelStyle,
        borderColor: `${agentColor}55`,
      }}
    >
      <div
        style={{
          color: agentColor,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 0.5,
        }}
      >
        {agent.agent.toUpperCase()}
      </div>

      <div
        style={{
          color: colors.text,
          marginTop: 10,
          fontSize: 13,
          fontWeight: 700,
        }}
      >
        {agent.status}
      </div>

      <p
        style={{
          fontSize: 12,
          color: colors.muted,
          lineHeight: 1.7,
        }}
      >
        {agent.summary}
      </p>

      <strong style={{ fontSize: 12, color: colors.cyan }}>
        FINDINGS
      </strong>

      <ul
        style={{
          paddingLeft: 18,
          color: colors.text,
          fontSize: 12,
          lineHeight: 1.8,
        }}
      >
        {agent.findings.map((finding, index) => (
          <li key={index}>{finding}</li>
        ))}
      </ul>

      <strong style={{ fontSize: 12, color: colors.yellow }}>
        RECOMMENDATIONS
      </strong>

      <ul
        style={{
          paddingLeft: 18,
          color: colors.text,
          fontSize: 12,
          lineHeight: 1.8,
        }}
      >
        {agent.recommendations.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>

      <p
        style={{
          marginBottom: 0,
          color: colors.muted,
          fontSize: 11,
        }}
      >
        {agent.confidence_note}
      </p>
    </div>
  );
}

export default function MultiAgentPanel() {
  const [data, setData] = useState<AgentApiResponse | null>(
    null
  );
  const [selected, setSelected] = useState<AgentReport | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [paused, setPaused] = useState(false);
  const [includeNormal, setIncludeNormal] = useState(false);
  const [lastSync, setLastSync] = useState("");

  const loadData = useCallback(async () => {
    try {
      const params = new URLSearchParams({
        limit: "20",
        include_normal: String(includeNormal),
      });

      const response = await fetch(
        `${API_URL}?${params.toString()}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error(`API HTTP ${response.status}`);
      }

      const result =
        (await response.json()) as AgentApiResponse;

      if (!Array.isArray(result.reports)) {
        throw new Error("Invalid multi-agent API response");
      }

      setData(result);
      setError(null);
      setLastSync(
        new Date().toLocaleTimeString("hu-HU")
      );

      setSelected((previous) => {
        if (!previous) return null;

        return (
          result.reports.find(
            (report) => report.report_id === previous.report_id
          ) ?? previous
        );
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Connection failed"
      );
    } finally {
      setLoading(false);
    }
  }, [includeNormal]);

  useEffect(() => {
    if (paused) return;

    void loadData();

    const interval = window.setInterval(() => {
      void loadData();
    }, REFRESH_MS);

    return () => window.clearInterval(interval);
  }, [loadData, paused]);

  const reports = data?.reports ?? [];

  const p1Count = reports.filter(
    (report) => report.priority === "P1"
  ).length;

  const p2Count = reports.filter(
    (report) => report.priority === "P2"
  ).length;

  const reviewCount = reports.filter(
    (report) => report.requires_review
  ).length;

  const anomalyCount = reports.filter(
    (report) => report.classification === "ANOMALY"
  ).length;

  return (
    <section
      style={{
        width: "100%",
        padding: "26px 0",
        color: colors.text,
      }}
    >
      <div
        style={{
          ...panelStyle,
          background:
            "linear-gradient(115deg, #0b3148, #152342 60%, #30204f)",
          borderColor: "#4989ae",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 16,
          }}
        >
          <div>
            <div
              style={{
                color: colors.cyan,
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: 2,
                marginBottom: 9,
              }}
            >
              QUANTUM CYBER DEFENSE ARENA · V9.3
            </div>

            <h2
              style={{
                display: "flex",
                alignItems: "center",
                flexWrap: "wrap",
                gap: 12,
                fontSize: "clamp(20px, 3vw, 29px)",
                margin: 0,
              }}
            >
              <Users size={28} color={colors.purple} />
              MULTI-AGENT CYBER DEFENSE
            </h2>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
                marginBottom: 0,
              }}
            >
              Threat Analysis Agent · Investigation Agent ·
              Reporting Agent
            </p>
          </div>

          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: 10,
            }}
          >
            <button
              type="button"
              style={buttonStyle}
              onClick={() => setPaused((value) => !value)}
            >
              {paused ? "RESUME" : "PAUSE"}
            </button>

            <button
              type="button"
              style={buttonStyle}
              onClick={() => void loadData()}
            >
              <RefreshCw
                size={15}
                style={{ display: "inline", marginRight: 7 }}
              />
              REFRESH
            </button>

            <button
              type="button"
              style={{
                ...buttonStyle,
                borderColor: includeNormal
                  ? colors.green
                  : colors.blue,
              }}
              onClick={() => setIncludeNormal((value) => !value)}
            >
              {includeNormal ? "SHOW ALL EVENTS" : "SUSPICIOUS ONLY"}
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 16,
            marginTop: 20,
            color: colors.muted,
            fontSize: 11,
          }}
        >
          <span
            style={{
              color: error ? colors.red : colors.green,
            }}
          >
            <Activity
              size={13}
              style={{ display: "inline", marginRight: 6 }}
            />
            {error
              ? "API ERROR"
              : data
                ? "MULTI-AGENT API CONNECTED"
                : "CONNECTING"}
          </span>

          <span>MODE: RESEARCH SIMULATION</span>
          <span>AGENTS: 3</span>
          <span>SYNC: {lastSync || "—"}</span>
          <span>REFRESH: 5 SEC</span>
        </div>
      </div>

      {error && (
        <div
          style={{
            ...panelStyle,
            color: colors.red,
            borderColor: colors.red,
            marginBottom: 18,
          }}
        >
          <AlertTriangle
            size={17}
            style={{ display: "inline", marginRight: 8 }}
          />
          API ERROR: {error}
        </div>
      )}

      {loading && !data && (
        <div style={panelStyle}>
          Connecting to V9.2 Multi-Agent Live API...
        </div>
      )}

      {data && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(180px, 1fr))",
              gap: 14,
              marginBottom: 18,
            }}
          >
            <Metric
              title="REPORTS DISPLAYED"
              value={reports.length}
              color={colors.cyan}
              icon={<ClipboardList size={19} />}
            />

            <Metric
              title="P1 CRITICAL"
              value={p1Count}
              color={colors.red}
              icon={<ShieldAlert size={19} />}
            />

            <Metric
              title="P2 HIGH"
              value={p2Count}
              color={colors.orange}
              icon={<AlertTriangle size={19} />}
            />

            <Metric
              title="REVIEW REQUIRED"
              value={reviewCount}
              color={colors.yellow}
              icon={<Search size={19} />}
            />

            <Metric
              title="ANOMALIES"
              value={anomalyCount}
              color={colors.purple}
              icon={<BrainCircuit size={19} />}
            />
          </div>

          <div
            style={{
              ...panelStyle,
              marginBottom: 18,
            }}
          >
            <h3
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
                marginTop: 0,
              }}
            >
              <Shield size={20} color={colors.cyan} />
              MULTI-AGENT LIVE REPORTS
            </h3>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
              }}
            >
              {data.report_count} displayed reports from{" "}
              {data.total_available} buffered simulation events
            </p>

            <div style={{ overflowX: "auto" }}>
              <table
                style={{
                  width: "100%",
                  minWidth: 760,
                  borderCollapse: "collapse",
                  fontSize: 12,
                  textAlign: "left",
                }}
              >
                <thead>
                  <tr>
                    {[
                      "NETWORK",
                      "EVENT ID",
                      "PRIORITY",
                      "CLASSIFICATION",
                      "FUSION SCORE",
                      "CONSENSUS",
                    ].map((label) => (
                      <th
                        key={label}
                        style={{
                          padding: 12,
                          color: colors.muted,
                          borderBottom: "1px solid #334155",
                        }}
                      >
                        {label}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {reports.map((report) => (
                    <tr
                      key={report.report_id}
                      onClick={() => setSelected(report)}
                      style={{
                        borderBottom: "1px solid #33415555",
                        cursor: "pointer",
                      }}
                    >
                      <td style={{ padding: 12 }}>
                        {report.network}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: colors.cyan,
                        }}
                      >
                        {report.event_id}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: priorityColor(report.priority),
                          fontWeight: 800,
                        }}
                      >
                        {report.priority}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: classificationColor(
                            report.classification
                          ),
                        }}
                      >
                        {report.classification}
                      </td>

                      <td style={{ padding: 12 }}>
                        {formatScore(report.fusion_score_100)}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: report.requires_review
                            ? colors.yellow
                            : colors.green,
                        }}
                      >
                        {report.consensus}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {reports.length === 0 && (
                <p
                  style={{
                    padding: 20,
                    color: colors.muted,
                  }}
                >
                  Waiting for simulated reports...
                </p>
              )}
            </div>
          </div>

          {selected && (
            <div
              style={{
                ...panelStyle,
                borderColor: colors.purple,
                marginBottom: 18,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  flexWrap: "wrap",
                  gap: 12,
                }}
              >
                <h3 style={{ margin: 0 }}>
                  MULTI-AGENT INVESTIGATION
                </h3>

                <button
                  type="button"
                  style={buttonStyle}
                  onClick={() => setSelected(null)}
                >
                  <X size={14} style={{ display: "inline" }} />
                  {" "}CLOSE
                </button>
              </div>

              <p
                style={{
                  color: colors.muted,
                  fontSize: 12,
                  marginTop: 14,
                }}
              >
                {selected.network} · {selected.event_id}
              </p>

              <ScoreBar
                label="HYBRID QUANTUM AI FUSION"
                score={selected.fusion_score_100}
                color={priorityColor(selected.priority)}
              />

              <div
                style={{
                  display: "flex",
                  gap: 14,
                  flexWrap: "wrap",
                  color: colors.muted,
                  fontSize: 12,
                  marginTop: 15,
                }}
              >
                <span>PRIORITY: {selected.priority}</span>
                <span>SEVERITY: {selected.severity}</span>
                <span>AGENTS: {selected.agent_count}</span>
                <span>
                  {selected.requires_review
                    ? "REVIEW REQUIRED"
                    : "NO REVIEW FLAG"}
                </span>
              </div>

              <div
                style={{
                  ...panelStyle,
                  marginTop: 18,
                  borderColor: "#446d93",
                  fontSize: 12,
                  lineHeight: 1.8,
                }}
              >
                <strong style={{ color: colors.cyan }}>
                  EXECUTIVE SUMMARY
                </strong>
                <p style={{ marginBottom: 0 }}>
                  {selected.executive_summary}
                </p>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
                  gap: 14,
                  marginTop: 18,
                }}
              >
                {selected.agent_results.map((agent) => (
                  <AgentCard
                    key={agent.agent}
                    agent={agent}
                  />
                ))}
              </div>

              <div
                style={{
                  ...panelStyle,
                  marginTop: 18,
                }}
              >
                <h4
                  style={{
                    color: colors.cyan,
                    marginTop: 0,
                  }}
                >
                  CONSOLIDATED FINDINGS
                </h4>

                <ul
                  style={{
                    fontSize: 12,
                    lineHeight: 1.9,
                    paddingLeft: 18,
                  }}
                >
                  {selected.consolidated_findings.map(
                    (finding, index) => (
                      <li key={index}>{finding}</li>
                    )
                  )}
                </ul>

                <h4 style={{ color: colors.yellow }}>
                  RECOMMENDED ACTIONS
                </h4>

                <ul
                  style={{
                    fontSize: 12,
                    lineHeight: 1.9,
                    paddingLeft: 18,
                  }}
                >
                  {selected.recommended_actions.map(
                    (action, index) => (
                      <li key={index}>{action}</li>
                    )
                  )}
                </ul>
              </div>
            </div>
          )}

          <div
            style={{
              ...panelStyle,
              fontSize: 11,
              lineHeight: 1.7,
              color: colors.muted,
            }}
          >
            <CheckCircle2
              size={16}
              color={colors.green}
              style={{ display: "inline", marginRight: 8 }}
            />
            <strong style={{ color: colors.green }}>
              MULTI-AGENT RESEARCH ENGINE
            </strong>

            <p style={{ marginBottom: 0 }}>
              Three deterministic rule-based agents analyze
              simulated Hybrid Fusion events. These are not
              independent LLM agents, verified attacks, or
              calibrated probabilities.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
