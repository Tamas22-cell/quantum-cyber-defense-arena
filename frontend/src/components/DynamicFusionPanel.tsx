
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Atom,
  BrainCircuit,
  CheckCircle2,
  RefreshCw,
  Radio,
  ShieldAlert,
  ShieldCheck,
  Zap,
} from "lucide-react";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

const API_URL =
  "http://127.0.0.1:8000/api/fusion/dynamic/live";

const REFRESH_INTERVAL = 3000;

type DynamicEvent = {
  event_id?: string;
  id?: string;
  network?: string;
  timestamp?: string;
  classical_score?: number;
  quantum_score?: number;
  fusion_score?: number;
  fusion_score_100?: number;
  classification?: string;
  severity?: string;
  models_agree?: boolean;
  decision_status?: string;
  explanation?: string;
};

type DynamicStatistics = {
  processed_events?: number;
  fusion_anomalies?: number;
  review_events?: number;
  model_disagreements?: number;
};

type DynamicResponse = {
  version: string;
  mode: string;
  status: string;
  statistics: DynamicStatistics;
  total_events: number;
  events: DynamicEvent[];
  last_error: string | null;
};

type HistoryPoint = {
  time: string;
  events: number;
  anomalies: number;
  reviews: number;
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

const panelStyle: React.CSSProperties = {
  background:
    "linear-gradient(145deg, #102543, #10172e)",
  border: "1px solid rgba(103, 232, 249, 0.25)",
  borderRadius: 18,
  padding: 20,
  minWidth: 0,
  boxShadow: "0 12px 35px rgba(0,0,0,0.18)",
};

function safeNumber(value: unknown): number {
  return typeof value === "number" && Number.isFinite(value)
    ? value
    : 0;
}

function formatScore(value: number | undefined): string {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "—";
  }

  return value.toFixed(2);
}

function severityColor(severity?: string): string {
  switch (severity) {
    case "CRITICAL":
      return colors.red;
    case "HIGH":
      return colors.orange;
    case "MEDIUM":
      return colors.yellow;
    default:
      return colors.green;
  }
}

function Metric({
  label,
  value,
  color,
  icon,
}: {
  label: string;
  value: string | number;
  color: string;
  icon: React.ReactNode;
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
          letterSpacing: 1,
        }}
      >
        {icon}
        {label}
      </div>

      <div
        style={{
          color: "#f8fafc",
          fontSize: 29,
          fontWeight: 800,
          marginTop: 15,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </div>
    </div>
  );
}

function RiskBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number | undefined;
  color: string;
}) {
  const safe = Math.max(0, Math.min(100, safeNumber(value)));

  return (
    <div style={{ marginBottom: 15 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 10,
          fontSize: 12,
          marginBottom: 7,
          color: colors.muted,
        }}
      >
        <span>{label}</span>
        <strong style={{ color }}>
          {formatScore(value)}%
        </strong>
      </div>

      <div
        style={{
          height: 9,
          borderRadius: 99,
          background: "#162b45",
          overflow: "hidden",
        }}
      >
        <div
          style={{
            height: "100%",
            width: `${safe}%`,
            borderRadius: 99,
            background: color,
            boxShadow: `0 0 12px ${color}66`,
            transition: "width 600ms ease",
          }}
        />
      </div>
    </div>
  );
}

function normalizedPercentage(
  value: number | undefined
): number | undefined {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return undefined;
  }

  return Math.max(0, Math.min(100, value * 100));
}

function fusionPercentage(
  event: DynamicEvent
): number | undefined {
  if (typeof event.fusion_score_100 === "number") {
    return event.fusion_score_100;
  }

  return normalizedPercentage(event.fusion_score);
}

function eventIdentifier(event: DynamicEvent): string {
  return event.event_id ?? event.id ?? "UNKNOWN";
}

export default function DynamicFusionPanel() {
  const [data, setData] = useState<DynamicResponse | null>(
    null
  );
  const [history, setHistory] = useState<HistoryPoint[]>(
    []
  );
  const [selected, setSelected] = useState<
    DynamicEvent | null
  >(null);
  const [error, setError] = useState<string | null>(
    null
  );
  const [lastSync, setLastSync] = useState("");
  const [loading, setLoading] = useState(true);
  const [paused, setPaused] = useState(false);

  const loadData = useCallback(async () => {
    try {
      const response = await fetch(API_URL, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const json =
        (await response.json()) as DynamicResponse;

      if (!Array.isArray(json.events)) {
        throw new Error("Invalid Dynamic Fusion response");
      }

      setData(json);
      setError(json.last_error ?? null);

      const time = new Date().toLocaleTimeString(
        "hu-HU"
      );

      setLastSync(time);

      const stats = json.statistics ?? {};

      setHistory((previous) => {
        const next: HistoryPoint = {
          time,
          events: safeNumber(
            stats.processed_events ??
              json.total_events
          ),
          anomalies: safeNumber(
            stats.fusion_anomalies
          ),
          reviews: safeNumber(
            stats.review_events
          ),
        };

        const last = previous[previous.length - 1];

        if (
          last &&
          last.events === next.events &&
          last.anomalies === next.anomalies &&
          last.reviews === next.reviews
        ) {
          return previous;
        }

        return [...previous.slice(-39), next];
      });
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Connection error"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (paused) return;

    void loadData();

    const timer = window.setInterval(() => {
      void loadData();
    }, REFRESH_INTERVAL);

    return () => {
      window.clearInterval(timer);
    };
  }, [loadData, paused]);

  const stats = data?.statistics ?? {};
  const events = data?.events ?? [];

  const isConnected = data?.status === "ONLINE" && !error;

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
            "linear-gradient(110deg, #092b42, #132046 60%, #31204c)",
          borderColor: "#367ba7",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            gap: 16,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: colors.cyan,
                fontSize: 11,
                letterSpacing: 2,
                fontWeight: 800,
                marginBottom: 10,
              }}
            >
              QUANTUM CYBER DEFENSE ARENA · V7.5
            </div>

            <h2
              style={{
                fontSize: "clamp(20px, 3vw, 30px)",
                margin: 0,
                display: "flex",
                alignItems: "center",
                gap: 12,
                flexWrap: "wrap",
              }}
            >
              <Atom size={29} color={colors.purple} />
              DYNAMIC HYBRID FUSION
            </h2>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
                marginBottom: 0,
              }}
            >
              Live simulated blockchain events · Isolation
              Forest + Quantum State Fidelity
            </p>
          </div>

          <div
            style={{
              display: "flex",
              alignItems: "center",
              flexWrap: "wrap",
              gap: 10,
            }}
          >
            <button
              type="button"
              onClick={() => setPaused((value) => !value)}
              style={{
                cursor: "pointer",
                background: "#1d4262",
                border: "1px solid #507d9f",
                color: "#f8fafc",
                borderRadius: 9,
                padding: "10px 14px",
                fontWeight: 800,
              }}
            >
              {paused ? "RESUME" : "PAUSE"}
            </button>

            <button
              type="button"
              onClick={() => void loadData()}
              style={{
                cursor: "pointer",
                background: "#175a81",
                border: "1px solid #4cc9f0",
                color: "#e0f2fe",
                borderRadius: 9,
                padding: "10px 14px",
                display: "flex",
                alignItems: "center",
                gap: 8,
                fontWeight: 800,
              }}
            >
              <RefreshCw size={15} />
              REFRESH
            </button>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            flexWrap: "wrap",
            gap: 16,
            color: colors.muted,
            fontSize: 11,
            marginTop: 20,
          }}
        >
          <span
            style={{
              color: isConnected
                ? colors.green
                : colors.red,
            }}
          >
            <Radio
              size={13}
              style={{
                display: "inline",
                marginRight: 6,
              }}
            />
            {isConnected ? "LIVE CONNECTED" : "OFFLINE"}
          </span>

          <span>
            MODE: RESEARCH SIMULATION
          </span>

          <span>
            SYNC: {lastSync || "—"}
          </span>

          <span>
            REFRESH: 3 SEC
          </span>

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
            ...panelStyle,
            borderColor: colors.red,
            color: colors.red,
            marginBottom: 18,
          }}
        >
          <AlertTriangle
            size={18}
            style={{
              display: "inline",
              marginRight: 8,
            }}
          />
          API ERROR: {error}
        </div>
      )}

      {loading && !data && (
        <div style={panelStyle}>
          Connecting to Dynamic Fusion Engine...
        </div>
      )}

      {data && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(185px, 1fr))",
              gap: 14,
              marginBottom: 18,
            }}
          >
            <Metric
              label="PROCESSED EVENTS"
              value={
                stats.processed_events ??
                data.total_events
              }
              color={colors.cyan}
              icon={<Activity size={19} />}
            />

            <Metric
              label="FUSION ANOMALIES"
              value={stats.fusion_anomalies ?? 0}
              color={colors.red}
              icon={<ShieldAlert size={19} />}
            />

            <Metric
              label="REVIEW REQUIRED"
              value={stats.review_events ?? 0}
              color={colors.yellow}
              icon={<AlertTriangle size={19} />}
            />

            <Metric
              label="MODEL DISAGREEMENTS"
              value={stats.model_disagreements ?? 0}
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
                marginTop: 0,
                display: "flex",
                gap: 10,
                alignItems: "center",
                fontSize: 16,
              }}
            >
              <Zap color={colors.cyan} size={21} />
              LIVE FUSION ANALYTICS
            </h3>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
              }}
            >
              Cumulative anomaly and review counts from
              the running research simulation
            </p>

            <div
              style={{
                width: "100%",
                height: 260,
              }}
            >
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <AreaChart data={history}>
                  <CartesianGrid
                    stroke="#47556955"
                    strokeDasharray="4 4"
                  />

                  <XAxis
                    dataKey="time"
                    stroke="#94a3b8"
                    tick={{ fontSize: 10 }}
                  />

                  <YAxis
                    stroke="#94a3b8"
                    tick={{ fontSize: 11 }}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#0b1e35",
                      border: "1px solid #406083",
                      borderRadius: 10,
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="anomalies"
                    name="Fusion Anomalies"
                    stroke={colors.red}
                    fill="#fb718533"
                    strokeWidth={2}
                  />

                  <Area
                    type="monotone"
                    dataKey="reviews"
                    name="Review Required"
                    stroke={colors.yellow}
                    fill="#facc1522"
                    strokeWidth={2}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
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
              <Radio color={colors.green} size={20} />
              LIVE BLOCKCHAIN FUSION EVENTS
            </h3>

            <p
              style={{
                color: colors.muted,
                fontSize: 12,
              }}
            >
              Latest 30 synthetic events · Select any
              event to inspect both detection models
            </p>

            <div
              style={{
                overflowX: "auto",
              }}
            >
              <table
                style={{
                  borderCollapse: "collapse",
                  width: "100%",
                  minWidth: 700,
                  fontSize: 12,
                }}
              >
                <thead>
                  <tr>
                    {[
                      "NETWORK",
                      "EVENT ID",
                      "FUSION SCORE",
                      "CLASSIFICATION",
                      "SEVERITY",
                      "AGREEMENT",
                    ].map((label) => (
                      <th
                        key={label}
                        style={{
                          textAlign: "left",
                          padding: 12,
                          color: colors.muted,
                          borderBottom:
                            "1px solid #334155",
                        }}
                      >
                        {label}
                      </th>
                    ))}
                  </tr>
                </thead>

                <tbody>
                  {events.map((event, index) => (
                    <tr
                      key={`${eventIdentifier(event)}-${index}`}
                      onClick={() => setSelected(event)}
                      style={{
                        cursor: "pointer",
                        borderBottom:
                          "1px solid #33415555",
                      }}
                    >
                      <td style={{ padding: 12 }}>
                        {event.network ?? "Unknown"}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: colors.cyan,
                        }}
                      >
                        {eventIdentifier(event)}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: severityColor(
                            event.severity
                          ),
                          fontWeight: 800,
                        }}
                      >
                        {formatScore(
                          fusionPercentage(event)
                        )}
                        /100
                      </td>

                      <td style={{ padding: 12 }}>
                        {event.classification ?? "—"}
                      </td>

                      <td
                        style={{
                          padding: 12,
                          color: severityColor(
                            event.severity
                          ),
                        }}
                      >
                        {event.severity ?? "—"}
                      </td>

                      <td style={{ padding: 12 }}>
                        {event.models_agree === true
                          ? "AGREE"
                          : event.models_agree === false
                          ? "REVIEW"
                          : "—"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
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
                  justifyContent:
                    "space-between",
                  alignItems: "center",
                  gap: 12,
                }}
              >
                <h3 style={{ margin: 0 }}>
                  EVENT INVESTIGATION
                </h3>

                <button
                  type="button"
                  onClick={() => setSelected(null)}
                  style={{
                    cursor: "pointer",
                    background: "#243b55",
                    color: "white",
                    border: "1px solid #64748b",
                    padding: "8px 14px",
                    borderRadius: 8,
                  }}
                >
                  CLOSE
                </button>
              </div>

              <p
                style={{
                  color: colors.muted,
                  fontSize: 12,
                }}
              >
                {selected.network ?? "Unknown"} ·{" "}
                {eventIdentifier(selected)}
              </p>

              <RiskBar
                label="CLASSICAL ISOLATION FOREST"
                value={normalizedPercentage(
                  selected.classical_score
                )}
                color={colors.blue}
              />

              <RiskBar
                label="QUANTUM STATE FIDELITY"
                value={normalizedPercentage(
                  selected.quantum_score
                )}
                color={colors.purple}
              />

              <RiskBar
                label="HYBRID FUSION SCORE"
                value={fusionPercentage(selected)}
                color={severityColor(
                  selected.severity
                )}
              />

              <p
                style={{
                  color:
                    selected.models_agree === false
                      ? colors.yellow
                      : colors.green,
                  fontWeight: 800,
                  fontSize: 12,
                }}
              >
                {selected.models_agree === true ? (
                  <>
                    <CheckCircle2
                      size={16}
                      style={{
                        display: "inline",
                        marginRight: 8,
                      }}
                    />
                    MODELS AGREE
                  </>
                ) : (
                  <>
                    <AlertTriangle
                      size={16}
                      style={{
                        display: "inline",
                        marginRight: 8,
                      }}
                    />
                    MODEL REVIEW
                  </>
                )}
              </p>

              <p style={{ fontSize: 12 }}>
                DECISION:{" "}
                {selected.decision_status ?? "—"}
              </p>

              <p
                style={{
                  color: colors.muted,
                  fontSize: 12,
                  lineHeight: 1.7,
                }}
              >
                {selected.explanation ??
                  "No explanation available."}
              </p>
            </div>
          )}

          <div
            style={{
              ...panelStyle,
              display: "flex",
              gap: 13,
              flexWrap: "wrap",
              alignItems: "center",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
              }}
            >
              {isConnected ? (
                <ShieldCheck
                  size={22}
                  color={colors.green}
                />
              ) : (
                <AlertTriangle
                  size={22}
                  color={colors.red}
                />
              )}

              <strong style={{ fontSize: 12 }}>
                DYNAMIC FUSION RESEARCH ENGINE
              </strong>
            </div>

            <p
              style={{
                color: colors.muted,
                fontSize: 11,
                maxWidth: 500,
                margin: 0,
                lineHeight: 1.6,
              }}
            >
              Research simulation only. Synthetic blockchain
              events are not verified attacks. Fusion scores
              are not calibrated attack probabilities or
              evidence of quantum computational advantage.
            </p>
          </div>
        </>
      )}
    </section>
  );
}
