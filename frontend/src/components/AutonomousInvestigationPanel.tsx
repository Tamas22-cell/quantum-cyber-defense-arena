
import { useCallback, useEffect, useState } from "react";
import type { CSSProperties } from "react";

import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  ClipboardList,
  RefreshCw,
  Search,
  ShieldAlert,
} from "lucide-react";

const API_BASE = "http://127.0.0.1:8000";
const REFRESH_MS = 5000;

type Investigation = {
  investigation_id: string;
  event_id: string;
  network: string;
  timestamp: string;
  classification: string;
  severity: string;
  priority: string;
  decision_status: string;
  models_agree: boolean | null;
  classical_score: number | null;
  quantum_score: number | null;
  fusion_score_100: number | null;
  findings: string[];
  recommendations: string[];
  status: string;
};

type InvestigationResponse = {
  version: string;
  mode: string;
  status: string;
  generated_at: string;
  total_available: number;
  investigated: number;
  investigations: Investigation[];
};

const colors = {
  cyan: "#67e8f9",
  blue: "#38bdf8",
  purple: "#c084fc",
  green: "#34d399",
  yellow: "#facc15",
  orange: "#fb923c",
  red: "#fb7185",
  text: "#e2e8f0",
  muted: "#94a3b8",
};

const cardStyle: CSSProperties = {
  background: "linear-gradient(145deg, #101f39, #10172d)",
  border: "1px solid rgba(103, 232, 249, 0.25)",
  borderRadius: 18,
  padding: 20,
  minWidth: 0,
};

function priorityColor(priority: string): string {
  switch (priority) {
    case "P1":
      return colors.red;
    case "P2":
      return colors.orange;
    case "P3":
      return colors.yellow;
    default:
      return colors.green;
  }
}


function formatFusion(value: number | null): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "â€”";
  }

  return `${value.toFixed(2)}/100`;
}

function ScoreBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number | null;
  color: string;
}) {
  const valid = typeof value === "number" && Number.isFinite(value);
  const safe = valid
    ? Math.max(0, Math.min(100, value))
    : 0;

  return (
    <div style={{ marginBottom: 15 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 10,
          color: colors.muted,
          fontSize: 12,
          marginBottom: 7,
        }}
      >
        <span>{label}</span>
        <strong style={{ color }}>
          {valid ? `${value.toFixed(2)}%` : "â€”"}
        </strong>
      </div>

      <div
        style={{
          width: "100%",
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

export default function AutonomousInvestigationPanel() {
  const [data, setData] = useState<InvestigationResponse | null>(
    null
  );
  const [selected, setSelected] = useState<Investigation | null>(
    null
  );
  const [error, setError] = useState<string | null>(null);
  const [paused, setPaused] = useState(false);
  const [showNormal, setShowNormal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [lastSync, setLastSync] = useState("");

  const loadData = useCallback(async () => {
    try {
      const response = await fetch(
        `${API_BASE}/api/investigation/live?limit=30&include_normal=${showNormal}`,
        { cache: "no-store" }
      );

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const json =
        (await response.json()) as InvestigationResponse;

      if (!Array.isArray(json.investigations)) {
        throw new Error("Invalid investigation API response");
      }

      setData(json);
      setError(null);
      setLastSync(new Date().toLocaleTimeString("hu-HU"));

      setSelected((previous) => {
        if (!previous) return null;

        return (
          json.investigations.find(
            (item) => item.event_id === previous.event_id
          ) ?? previous
        );
      });
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Connection error"
      );
    } finally {
      setLoading(false);
    }
  }, [showNormal]);

  useEffect(() => {
    if (paused) return;

    void loadData();

    const timer = window.setInterval(() => {
      void loadData();
    }, REFRESH_MS);

    return () => window.clearInterval(timer);
  }, [loadData, paused]);

  const investigations = data?.investigations ?? [];

  const p1Count = investigations.filter(
    (item) => item.priority === "P1"
  ).length;

  const p2Count = investigations.filter(
    (item) => item.priority === "P2"
  ).length;

  const reviewCount = investigations.filter(
    (item) => item.classification === "REVIEW"
  ).length;

  const disagreements = investigations.filter(
    (item) => item.models_agree === false
  ).length;

  const buttonStyle: CSSProperties = {
    background: "#183d63",
    border: "1px solid #497eac",
    borderRadius: 9,
    padding: "10px 14px",
    color: "#e0f2fe",
    fontWeight: 700,
    fontSize: 12,
    cursor: "pointer",
  };

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
          ...cardStyle,
          background:
            "linear-gradient(115deg, #0c3146, #14203c 60%, #321e4d)",
          borderColor: "#4283ac",
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
                fontSize: 11,
                letterSpacing: 2,
                color: colors.cyan,
                fontWeight: 800,
                marginBottom: 9,
              }}
            >
              QUANTUM CYBER DEFENSE ARENA Â· V8.2
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
              <Search size={28} color={colors.purple} />
              AUTONOMOUS THREAT INVESTIGATION
            </h2>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
                marginBottom: 0,
              }}
            >
              Automated rule-based incident assessment from
              Dynamic Quantum AI Fusion events
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
                size={14}
                style={{
                  display: "inline",
                  marginRight: 7,
                }}
              />
              REFRESH
            </button>

            <button
              type="button"
              style={{
                ...buttonStyle,
                borderColor: showNormal
                  ? colors.green
                  : "#497eac",
              }}
              onClick={() => setShowNormal((value) => !value)}
            >
              {showNormal ? "ALL EVENTS" : "SUSPICIOUS ONLY"}
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 16,
            marginTop: 18,
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
              style={{
                display: "inline",
                marginRight: 6,
              }}
            />
            {error
              ? "API ERROR"
              : data
              ? "INVESTIGATION API CONNECTED"
              : "CONNECTING"}
          </span>

          <span>MODE: RESEARCH SIMULATION</span>
          <span>SYNC: {lastSync || "â€”"}</span>
          <span>REFRESH: 5 SEC</span>

          {paused && (
            <span style={{ color: colors.yellow }}>
              DASHBOARD PAUSED
            </span>
          )}
        </div>
      </div>

      {error && (
        <div
          style={{
            ...cardStyle,
            marginBottom: 18,
            borderColor: colors.red,
            color: colors.red,
          }}
        >
          <AlertTriangle
            size={17}
            style={{
              display: "inline",
              marginRight: 8,
            }}
          />
          API ERROR: {error}
        </div>
      )}

      {loading && !data && (
        <div style={cardStyle}>
          Connecting to Autonomous Investigation API...
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
            {[
              {
                label: "INVESTIGATED",
                value: data.investigated,
                color: colors.cyan,
                icon: <ClipboardList size={19} />,
              },
              {
                label: "P1 CRITICAL",
                value: p1Count,
                color: colors.red,
                icon: <ShieldAlert size={19} />,
              },
              {
                label: "P2 HIGH",
                value: p2Count,
                color: colors.orange,
                icon: <AlertTriangle size={19} />,
              },
              {
                label: "REVIEW CASES",
                value: reviewCount,
                color: colors.yellow,
                icon: <Search size={19} />,
              },
              {
                label: "MODEL DISAGREEMENTS",
                value: disagreements,
                color: colors.purple,
                icon: <BrainCircuit size={19} />,
              },
            ].map((item) => (
              <div key={item.label} style={cardStyle}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    color: item.color,
                    fontWeight: 800,
                    fontSize: 11,
                  }}
                >
                  {item.icon}
                  {item.label}
                </div>

                <div
                  style={{
                    fontSize: 28,
                    fontWeight: 800,
                    marginTop: 15,
                  }}
                >
                  {item.value}
                </div>
              </div>
            ))}
          </div>

          <div
            style={{
              ...cardStyle,
              marginBottom: 18,
            }}
          >
            <h3
              style={{
                marginTop: 0,
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <ClipboardList size={20} color={colors.cyan} />
              AUTONOMOUS INVESTIGATION REPORTS
            </h3>

            <p
              style={{
                fontSize: 12,
                color: colors.muted,
              }}
            >
              {data.investigated} investigations from{" "}
              {data.total_available} buffered synthetic events
            </p>

            <div style={{ overflowX: "auto" }}>
              <table
                style={{
                  width: "100%",
                  minWidth: 700,
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
                      "STATUS",
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
                  {investigations.map((item, index) => (
                    <tr
                      key={`${item.investigation_id}-${index}`}
                      onClick={() => setSelected(item)}
                      style={{
                        cursor: "pointer",
                        borderBottom: "1px solid #33415555",
                      }}
                    >
                      <td style={{ padding: 12 }}>
                        {item.network}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: colors.cyan,
                        }}
                      >
                        {item.event_id}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          fontWeight: 800,
                          color: priorityColor(item.priority),
                        }}
                      >
                        {item.priority}
                      </td>

                      <td style={{ padding: 12 }}>
                        {item.classification}
                      </td>

                      <td style={{ padding: 12 }}>
                        {formatFusion(item.fusion_score_100)}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: colors.green,
                        }}
                      >
                        {item.status}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {investigations.length === 0 && (
                <p
                  style={{
                    padding: 18,
                    color: colors.muted,
                  }}
                >
                  Waiting for simulated events to investigate...
                </p>
              )}
            </div>
          </div>

          {selected && (
            <div
              style={{
                ...cardStyle,
                marginBottom: 18,
                borderColor: colors.purple,
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <h3
                  style={{
                    margin: 0,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                  }}
                >
                  <Search size={19} color={colors.cyan} />
                  INVESTIGATION DETAILS
                </h3>

                <button
                  type="button"
                  style={buttonStyle}
                  onClick={() => setSelected(null)}
                >
                  CLOSE
                </button>
              </div>

              <p
                style={{
                  color: colors.muted,
                  fontSize: 12,
                  marginBottom: 20,
                }}
              >
                {selected.network} Â· {selected.event_id}
              </p>

              <ScoreBar
                label="CLASSICAL ISOLATION FOREST"
                value={
                  selected.classical_score === null
                    ? null
                    : selected.classical_score * 100
                }
                color={colors.blue}
              />

              <ScoreBar
                label="QUANTUM STATE FIDELITY"
                value={
                  selected.quantum_score === null
                    ? null
                    : selected.quantum_score * 100
                }
                color={colors.purple}
              />

              <ScoreBar
                label="HYBRID FUSION RISK SCORE"
                value={selected.fusion_score_100}
                color={priorityColor(selected.priority)}
              />

              <div
                style={{
                  display: "flex",
                  flexWrap: "wrap",
                  gap: 16,
                  color: colors.muted,
                  fontSize: 12,
                  marginTop: 18,
                }}
              >
                <span>
                  PRIORITY:{" "}
                  <strong
                    style={{
                      color: priorityColor(selected.priority),
                    }}
                  >
                    {selected.priority}
                  </strong>
                </span>

                <span>SEVERITY: {selected.severity}</span>

                <span>
                  MODELS:{" "}
                  {selected.models_agree === true
                    ? "AGREE"
                    : selected.models_agree === false
                    ? "DISAGREE"
                    : "UNKNOWN"}
                </span>

                <span>
                  DECISION: {selected.decision_status}
                </span>
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
                  gap: 16,
                  marginTop: 20,
                }}
              >
                <div style={cardStyle}>
                  <h4
                    style={{
                      display: "flex",
                      gap: 8,
                      alignItems: "center",
                      color: colors.cyan,
                      marginTop: 0,
                    }}
                  >
                    <CheckCircle2 size={17} />
                    INVESTIGATION FINDINGS
                  </h4>

                  <ul
                    style={{
                      fontSize: 12,
                      lineHeight: 1.9,
                      color: colors.text,
                      paddingLeft: 18,
                    }}
                  >
                    {selected.findings.map((finding, index) => (
                      <li key={index}>{finding}</li>
                    ))}
                  </ul>
                </div>

                <div style={cardStyle}>
                  <h4
                    style={{
                      display: "flex",
                      gap: 8,
                      alignItems: "center",
                      color: colors.yellow,
                      marginTop: 0,
                    }}
                  >
                    <AlertTriangle size={17} />
                    RECOMMENDED ACTIONS
                  </h4>

                  <ul
                    style={{
                      fontSize: 12,
                      lineHeight: 1.9,
                      color: colors.text,
                      paddingLeft: 18,
                    }}
                  >
                    {selected.recommendations.map((item, index) => (
                      <li key={index}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          <div
            style={{
              ...cardStyle,
              color: colors.muted,
              fontSize: 11,
              lineHeight: 1.7,
            }}
          >
            <strong style={{ color: colors.green }}>
              AUTONOMOUS INVESTIGATION RESEARCH
            </strong>

            <p style={{ marginBottom: 0 }}>
              <Activity
                size={13}
                style={{
                  display: "inline",
                  marginRight: 6,
                }}
              />
              Reports are generated from simulated blockchain
              events using deterministic investigation rules.
              No verified real-world attacks are represented.
              Scores are not calibrated probabilities.
            </p>
          </div>
        </>
      )}
    </section>
  );
}

