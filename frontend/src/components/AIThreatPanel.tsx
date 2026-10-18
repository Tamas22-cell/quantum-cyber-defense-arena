
import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

const API_URL = "http://127.0.0.1:8000/api/ai/live";

type JsonRecord = Record<string, unknown>;

type AIEvent = {
  id: string;
  network: string;
  type: string;
  risk: number | null;
  score: number | null;
  classification: string;
};

type AIState = {
  status: string;
  model: string;
  version: string;
  predictions: number;
  detected: number;
  events: AIEvent[];
};

function objectOf(value: unknown): JsonRecord {
  if (
    value !== null &&
    typeof value === "object" &&
    !Array.isArray(value)
  ) {
    return value as JsonRecord;
  }
  return {};
}

function numberOf(value: unknown): number | null {
  if (typeof value === "number" && Number.isFinite(value)) {
    return value;
  }
  if (typeof value === "string" && value.trim() !== "") {
    const n = Number(value);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

function textOf(value: unknown, fallback: string): string {
  return typeof value === "string" && value.trim()
    ? value
    : fallback;
}

function parseAI(json: unknown): AIState {
  const root = objectOf(json);
  const stats = objectOf(root.model_statistics);

  const source = Array.isArray(root.recent_anomalies)
    ? root.recent_anomalies
    : [];

  const events: AIEvent[] = source.map((value, index) => {
    const entry = objectOf(value);
    const nested = objectOf(entry.event);
    const ai = objectOf(
      entry.ai_detection ?? entry.ai_result
    );

    return {
      id: textOf(
        entry.id ?? entry.event_id ?? nested.id,
        `AI-${index + 1}`
      ),
      network: textOf(
        entry.network ?? nested.network,
        "UNKNOWN"
      ),
      type: textOf(
        entry.type ?? nested.type,
        "ANOMALY"
      ),
      risk: numberOf(
        entry.risk_score ?? nested.risk_score
      ),
      score: numberOf(
        ai.anomaly_score ?? entry.anomaly_score
      ),
      classification: textOf(
        ai.classification ?? entry.classification,
        "ANOMALY"
      ),
    };
  });

  return {
    status: textOf(root.status, "UNKNOWN"),
    model: textOf(
      root.model ?? stats.model,
      "IsolationForest"
    ),
    version: textOf(
      stats.model_version ?? root.model_version,
      "2.0.0"
    ),
    predictions:
      numberOf(
        stats.total_predictions ??
          root.total_predictions
      ) ?? 0,
    detected:
      numberOf(
        stats.total_anomalies ?? stats.total_anomalies_detected ??
          stats.anomalies_detected ??
          root.total_anomalies_detected ??
          root.anomalies_detected ??
          root.total_anomalies
      ) ?? events.length,
    events,
  };
}

const panel: CSSProperties = {
  marginTop: 22,
  padding: 24,
  width: "100%",
  boxSizing: "border-box",
  color: "#eaf7ff",
  border: "1px solid rgba(112,174,255,.45)",
  borderRadius: 18,
  background:
    "linear-gradient(125deg,rgba(8,36,83,.96),rgba(65,30,130,.91))",
  boxShadow: "0 0 35px rgba(67,110,255,.15)",
};

const card: CSSProperties = {
  padding: 18,
  borderRadius: 13,
  background: "rgba(7,25,62,.65)",
  border: "1px solid rgba(103,196,255,.32)",
  minWidth: 0,
};

function Metric({
  title,
  value,
  subtitle,
  color,
}: {
  title: string;
  value: string;
  subtitle: string;
  color: string;
}) {
  return (
    <div style={card}>
      <div
        style={{
          fontSize: 11,
          letterSpacing: 1,
          color: "#bad7ee",
          fontWeight: 700,
        }}
      >
        {title}
      </div>

      <div
        style={{
          fontSize: 30,
          fontWeight: 800,
          color,
          margin: "12px 0 8px",
          textShadow: `0 0 18px ${color}55`,
        }}
      >
        {value}
      </div>

      <div style={{ fontSize: 11, color: "#a9c5db" }}>
        {subtitle}
      </div>
    </div>
  );
}

export default function AIThreatPanel() {
  const [data, setData] = useState<AIState | null>(null);
  const [connected, setConnected] = useState(false);
  const [updated, setUpdated] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    let loading = false;

    async function load() {
      if (loading) return;
      loading = true;

      try {
        const response = await fetch(API_URL, {
          cache: "no-store",
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const json: unknown = await response.json();
        const result = parseAI(json);

        if (!active) return;

        setData(result);
        setConnected(
          result.status.toUpperCase() === "ONLINE"
        );
        setUpdated(
          new Date().toLocaleTimeString("hu-HU")
        );
        setError("");
      } catch (err) {
        if (!active) return;

        setConnected(false);
        setError(
          err instanceof Error
            ? err.message
            : "Connection failed"
        );
      } finally {
        loading = false;
      }
    }

    void load();

    const timer = window.setInterval(() => {
      void load();
    }, 3000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  const predictions = data?.predictions ?? 0;
  const detected = data?.detected ?? 0;

  const rate =
    predictions > 0
      ? (detected / predictions) * 100
      : null;

  return (
    <section style={panel}>
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
        }}
      >
        <div>
          <h2 style={{ margin: 0, fontSize: 22 }}>
            🧠 AI Threat Intelligence V3
          </h2>

          <p
            style={{
              color: "#b7d5ef",
              fontSize: 12,
            }}
          >
            Isolation Forest · Live AI Anomaly Detection
          </p>
        </div>

        <div
          style={{
            fontWeight: 800,
            fontSize: 12,
            color: connected ? "#70ffc3" : "#ff829b",
          }}
        >
          ● AI API {connected ? "ONLINE" : "OFFLINE"}
        </div>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit,minmax(180px,1fr))",
          gap: 14,
          marginTop: 15,
        }}
      >
        <Metric
          title="AI PREDICTIONS"
          value={data ? String(predictions) : "—"}
          subtitle="Processed simulated events"
          color="#67eaff"
        />

        <Metric
          title="ANOMALIES DETECTED"
          value={data ? String(detected) : "—"}
          subtitle="AI-classified anomalies"
          color="#ff6f93"
        />

        <Metric
          title="ANOMALY RATE"
          value={
            rate === null
              ? "—"
              : `${rate.toFixed(1)}%`
          }
          subtitle="Detected / total predictions"
          color="#ffd36e"
        />

        <Metric
          title="MODEL STATUS"
          value={connected ? "ONLINE" : "OFFLINE"}
          subtitle={`${data?.model ?? "IsolationForest"} V${data?.version ?? "2.0.0"}`}
          color="#76ffc8"
        />
      </div>

      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
          marginTop: 24,
          marginBottom: 12,
        }}
      >
        <strong>⚡ Recent AI Anomalies</strong>

        <span
          style={{
            color: "#99dfee",
            fontSize: 11,
          }}
        >
          Auto-refresh: 3s · Updated: {updated || "Waiting"}
        </span>
      </div>

      {error && (
        <p
          style={{
            color: "#ff9aab",
            fontSize: 12,
          }}
        >
          AI API: {error}
        </p>
      )}

      <div
        style={{
          overflowX: "auto",
          maxHeight: 350,
          overflowY: "auto",
          borderRadius: 12,
          background: "rgba(4,17,40,.5)",
        }}
      >
        <table
          style={{
            width: "100%",
            minWidth: 540,
            borderCollapse: "collapse",
            fontSize: 12,
          }}
        >
          <thead>
            <tr
              style={{
                color: "#99dcec",
                textAlign: "left",
              }}
            >
              {[
                "NETWORK",
                "EVENT",
                "RISK",
                "AI SCORE",
                "RESULT",
              ].map((title) => (
                <th
                  key={title}
                  style={{ padding: 13 }}
                >
                  {title}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {(data?.events ?? [])
              .slice(0, 12)
              .map((event, index) => (
                <tr
                  key={`${event.id}-${index}`}
                  style={{
                    borderTop:
                      "1px solid rgba(135,195,255,.12)",
                  }}
                >
                  <td style={{ padding: 12 }}>
                    {event.network}
                  </td>

                  <td style={{ padding: 12 }}>
                    {event.type.replaceAll("_", " ")}
                  </td>

                  <td
                    style={{
                      padding: 12,
                      color:
                        event.risk !== null &&
                        event.risk >= 80
                          ? "#ff738b"
                          : "#ffd36e",
                    }}
                  >
                    {event.risk === null
                      ? "—"
                      : `${event.risk}/100`}
                  </td>

                  <td style={{ padding: 12 }}>
                    {event.score === null
                      ? "—"
                      : event.score.toFixed(4)}
                  </td>

                  <td
                    style={{
                      padding: 12,
                      fontWeight: 800,
                      color: "#ff7898",
                    }}
                  >
                    {event.classification}
                  </td>
                </tr>
              ))}
          </tbody>
        </table>

        {data && data.events.length === 0 && (
          <p
            style={{
              padding: 18,
              textAlign: "center",
              color: "#b4ccdf",
              fontSize: 12,
            }}
          >
            No recent AI anomalies.
          </p>
        )}
      </div>

      <p
        style={{
          marginTop: 16,
          color: "#a5bed8",
          textAlign: "center",
          fontSize: 11,
        }}
      >
        RESEARCH SIMULATION · AI detections are
        experimental, not verified real-world attacks.
      </p>
    </section>
  );
}
