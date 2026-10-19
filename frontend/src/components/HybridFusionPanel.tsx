
import { useCallback, useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Atom,
  BrainCircuit,
  CheckCircle2,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

type FusionResult = {
  event_id: string;
  network: string;
  classical_model: string;
  classical_score: number;
  classical_anomaly: boolean;
  quantum_model: string;
  quantum_score: number;
  quantum_anomaly: boolean;
  fusion_score_100: number;
  classification: string;
  severity: string;
  models_agree: boolean;
  decision_status: string;
  explanation: string;
  classical_weight: number;
  quantum_weight: number;
};

type FusionResponse = {
  version: string;
  mode: string;
  results: FusionResult[];
};

const API_URL = "http://127.0.0.1:8000/api/fusion/demo";

function percentage(score: number) {
  return `${(score * 100).toFixed(2)}%`;
}

function riskColor(severity: string) {
  if (severity === "CRITICAL") return "#fb7185";
  if (severity === "HIGH") return "#fb923c";
  if (severity === "MEDIUM") return "#facc15";
  return "#34d399";
}

function ScoreBar({
  label,
  value,
  color,
}: {
  label: string;
  value: number;
  color: string;
}) {
  const safeValue = Math.max(0, Math.min(100, value));

  return (
    <div style={{ marginBottom: 14 }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          marginBottom: 7,
          color: "#cbd5e1",
          fontSize: 12,
        }}
      >
        <span>{label}</span>
        <strong style={{ color }}>{safeValue.toFixed(2)}%</strong>
      </div>

      <div
        style={{
          height: 8,
          background: "#16243a",
          borderRadius: 99,
          overflow: "hidden",
        }}
      >
        <div
          style={{
            width: `${safeValue}%`,
            height: "100%",
            background: color,
            borderRadius: 99,
            boxShadow: `0 0 12px ${color}66`,
            transition: "width 500ms ease",
          }}
        />
      </div>
    </div>
  );
}

export default function HybridFusionPanel() {
  const [data, setData] = useState<FusionResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string>("");

  const loadData = useCallback(async () => {
    try {
      const response = await fetch(API_URL, {
        cache: "no-store",
      });

      if (!response.ok) {
        throw new Error(`API HTTP ${response.status}`);
      }

      const json = (await response.json()) as FusionResponse;

      if (!Array.isArray(json.results)) {
        throw new Error("Invalid Fusion API response");
      }

      setData(json);
      setError(null);
      setLastUpdated(new Date().toLocaleTimeString("hu-HU"));
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Unknown API error"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();

    const timer = window.setInterval(() => {
      void loadData();
    }, 10000);

    return () => window.clearInterval(timer);
  }, [loadData]);

  const results = data?.results ?? [];

  const criticalCount = results.filter(
    (r) => r.severity === "CRITICAL"
  ).length;

  const anomalyCount = results.filter(
    (r) => r.classification === "ANOMALY"
  ).length;

  const agreementCount = results.filter(
    (r) => r.models_agree
  ).length;

  const averageFusion = results.length
    ? results.reduce(
        (total, result) => total + result.fusion_score_100,
        0
      ) / results.length
    : 0;

  const panelStyle: React.CSSProperties = {
    background:
      "linear-gradient(145deg, #101c32 0%, #091222 100%)",
    border: "1px solid #253c60",
    borderRadius: 18,
    padding: 20,
  };

  return (
    <section
      style={{
        color: "#e2e8f0",
        padding: "26px 0",
        width: "100%",
      }}
    >
      <div
        style={{
          ...panelStyle,
          background:
            "linear-gradient(120deg, #102342 0%, #0a1429 55%, #21123a 100%)",
          borderColor: "#3b4c84",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            gap: 18,
            flexWrap: "wrap",
          }}
        >
          <div>
            <div
              style={{
                color: "#67e8f9",
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: 2,
                marginBottom: 8,
              }}
            >
              QUANTUM CYBER DEFENSE ARENA / V7.2
            </div>

            <h2
              style={{
                display: "flex",
                alignItems: "center",
                gap: 12,
                margin: 0,
                fontSize: "clamp(20px, 3vw, 29px)",
                color: "#f8fafc",
              }}
            >
              <Atom color="#a78bfa" size={30} />
              HYBRID QUANTUM AI FUSION
            </h2>

            <p
              style={{
                color: "#94a3b8",
                fontSize: 13,
                marginBottom: 0,
              }}
            >
              Isolation Forest V2 + Qiskit Quantum State Fidelity
              Detection
            </p>
          </div>

          <button
            onClick={() => void loadData()}
            disabled={loading && data === null}
            style={{
              cursor: "pointer",
              background: "#12345a",
              border: "1px solid #3979b9",
              borderRadius: 10,
              padding: "10px 15px",
              color: "#a5f3fc",
              display: "flex",
              gap: 9,
              alignItems: "center",
              fontWeight: 700,
            }}
          >
            <RefreshCw size={16} />
            REFRESH
          </button>
        </div>

        <div
          style={{
            marginTop: 18,
            display: "flex",
            flexWrap: "wrap",
            gap: 14,
            alignItems: "center",
            fontSize: 11,
            color: "#94a3b8",
          }}
        >
          <span>
            <Activity
              size={13}
              style={{
                display: "inline",
                marginRight: 5,
                color: error ? "#fb7185" : "#34d399",
              }}
            />
            {error ? "API ERROR" : data ? "API CONNECTED" : "CONNECTING"}
          </span>

          <span>MODE: RESEARCH SIMULATION</span>
          <span>LAST SYNC: {lastUpdated || "—"}</span>
          <span>REFRESH: 10 SEC</span>
        </div>
      </div>

      {error && (
        <div
          style={{
            ...panelStyle,
            borderColor: "#be123c",
            color: "#fda4af",
            marginBottom: 18,
          }}
        >
          <AlertTriangle
            size={17}
            style={{ display: "inline", marginRight: 8 }}
          />
          Fusion API: {error}. Check the backend on port 8000.
        </div>
      )}

      {loading && data === null && (
        <div style={panelStyle}>
          Connecting to the Hybrid Fusion Engine...
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
                label: "EVENTS ANALYZED",
                value: String(results.length),
                color: "#67e8f9",
                icon: <Activity size={19} />,
              },
              {
                label: "FUSION ANOMALIES",
                value: String(anomalyCount),
                color: "#fb923c",
                icon: <ShieldAlert size={19} />,
              },
              {
                label: "CRITICAL THREATS",
                value: String(criticalCount),
                color: "#fb7185",
                icon: <AlertTriangle size={19} />,
              },
              {
                label: "MODEL AGREEMENTS",
                value: `${agreementCount}/${results.length}`,
                color: "#a78bfa",
                icon: <BrainCircuit size={19} />,
              },
              {
                label: "AVG FUSION SCORE",
                value: `${averageFusion.toFixed(2)}/100`,
                color: "#34d399",
                icon: <Atom size={19} />,
              },
            ].map((item) => (
              <div key={item.label} style={panelStyle}>
                <div
                  style={{
                    color: item.color,
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    fontSize: 11,
                    fontWeight: 800,
                    letterSpacing: 1,
                  }}
                >
                  {item.icon}
                  {item.label}
                </div>
                <div
                  style={{
                    color: "#f8fafc",
                    fontSize: 27,
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
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(min(100%, 320px), 1fr))",
              gap: 16,
            }}
          >
            {results.map((result) => {
              const color = riskColor(result.severity);

              return (
                <article key={result.event_id} style={panelStyle}>
                  <div
                    style={{
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "flex-start",
                      gap: 10,
                      marginBottom: 20,
                    }}
                  >
                    <div>
                      <div
                        style={{
                          fontSize: 11,
                          color: "#67e8f9",
                          fontWeight: 800,
                          letterSpacing: 1,
                        }}
                      >
                        {result.network.toUpperCase()}
                      </div>

                      <h3
                        style={{
                          margin: "7px 0 0",
                          fontSize: 16,
                          color: "#f8fafc",
                        }}
                      >
                        {result.event_id}
                      </h3>
                    </div>

                    <span
                      style={{
                        color,
                        border: `1px solid ${color}77`,
                        background: `${color}16`,
                        borderRadius: 99,
                        padding: "6px 11px",
                        fontSize: 11,
                        fontWeight: 800,
                      }}
                    >
                      {result.severity}
                    </span>
                  </div>

                  <ScoreBar
                    label="CLASSICAL AI / ISOLATION FOREST"
                    value={result.classical_score * 100}
                    color="#38bdf8"
                  />

                  <ScoreBar
                    label="QUANTUM AI / QISKIT"
                    value={result.quantum_score * 100}
                    color="#a78bfa"
                  />

                  <ScoreBar
                    label="HYBRID FUSION RISK SCORE"
                    value={result.fusion_score_100}
                    color={color}
                  />

                  <div
                    style={{
                      borderTop: "1px solid #253c60",
                      paddingTop: 16,
                      marginTop: 20,
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 9,
                        color: result.models_agree
                          ? "#34d399"
                          : "#fbbf24",
                        fontSize: 12,
                        fontWeight: 800,
                      }}
                    >
                      {result.models_agree ? (
                        <CheckCircle2 size={17} />
                      ) : (
                        <AlertTriangle size={17} />
                      )}
                      {result.models_agree
                        ? "MODELS AGREE"
                        : "MODEL DISAGREEMENT"}
                    </div>

                    <div
                      style={{
                        marginTop: 12,
                        color: "#cbd5e1",
                        fontSize: 12,
                      }}
                    >
                      <strong>Decision:</strong>{" "}
                      {result.decision_status}
                    </div>

                    <div
                      style={{
                        marginTop: 7,
                        color: "#cbd5e1",
                        fontSize: 12,
                      }}
                    >
                      <strong>Classification:</strong>{" "}
                      {result.classification}
                    </div>

                    <p
                      style={{
                        marginBottom: 0,
                        color: "#94a3b8",
                        fontSize: 12,
                        lineHeight: 1.7,
                      }}
                    >
                      {result.explanation}
                    </p>
                  </div>
                </article>
              );
            })}
          </div>

          <div
            style={{
              ...panelStyle,
              marginTop: 18,
              display: "flex",
              alignItems: "center",
              gap: 14,
              flexWrap: "wrap",
              justifyContent: "space-between",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <ShieldCheck color="#34d399" size={22} />
              <div>
                <strong style={{ fontSize: 13 }}>
                  HYBRID FUSION RESEARCH STATUS
                </strong>
                <div
                  style={{
                    color: "#94a3b8",
                    fontSize: 11,
                    marginTop: 4,
                  }}
                >
                  Classical model weight:{" "}
                  {percentage(results[0]?.classical_weight ?? 0.5)}
                  {" / "}
                  Quantum model weight:{" "}
                  {percentage(results[0]?.quantum_weight ?? 0.5)}
                </div>
              </div>
            </div>

            <div
              style={{
                color: "#94a3b8",
                fontSize: 11,
                maxWidth: 390,
                lineHeight: 1.6,
              }}
            >
              Synthetic research data only. These scores are not
              calibrated attack probabilities or evidence of
              quantum computational advantage.
            </div>
          </div>
        </>
      )}
    </section>
  );
}
