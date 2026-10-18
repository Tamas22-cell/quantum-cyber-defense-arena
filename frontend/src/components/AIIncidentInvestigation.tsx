
import { useEffect, useState } from "react";
import type { CSSProperties } from "react";

const API_URL = "http://127.0.0.1:8000/api/ai/live";

type Incident = {
  id: string;
  network: string;
  type: string;
  risk: number;
  score: number | null;
  classification: string;
  timestamp: string;
};

type JsonObject = Record<string, unknown>;

function obj(value: unknown): JsonObject {
  return value && typeof value === "object" && !Array.isArray(value)
    ? (value as JsonObject)
    : {};
}

function num(value: unknown, fallback = 0): number {
  const n = Number(value);
  return value != null && Number.isFinite(n) ? n : fallback;
}

function str(value: unknown, fallback = "UNKNOWN"): string {
  return typeof value === "string" && value.trim()
    ? value
    : fallback;
}

const panel: CSSProperties = {
  background: "linear-gradient(135deg, #091c39, #25144f)",
  border: "1px solid rgba(90,180,255,.4)",
  borderRadius: 18,
  padding: 24,
  color: "#e9f6ff",
  marginTop: 24,
  boxShadow: "0 0 35px rgba(53,107,255,.12)",
};

export default function AIIncidentInvestigation() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [selected, setSelected] = useState<Incident | null>(null);
  const [online, setOnline] = useState(false);

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const response = await fetch(API_URL, {
          cache: "no-store",
        });

        if (!response.ok) throw new Error("API unavailable");

        const raw: unknown = await response.json();
        const data = obj(raw);

        const list = Array.isArray(data.recent_anomalies)
          ? data.recent_anomalies
          : [];

        const mapped: Incident[] = list.map((item, index) => {
          const event = obj(item);
          const nested = obj(event.event);
          const ai = obj(event.ai_detection);

          return {
            id: str(
              event.id ?? event.event_id ?? nested.id,
              `INC-${index + 1}`
            ),
            network: str(event.network ?? nested.network),
            type: str(
              event.type ?? event.event_type ?? nested.type,
              "ANOMALY"
            ),
            risk: num(event.risk_score ?? nested.risk_score),
            score:
              ai.anomaly_score == null &&
              event.anomaly_score == null
                ? null
                : num(ai.anomaly_score ?? event.anomaly_score),
            classification: str(
              ai.classification ?? event.classification,
              "ANOMALY"
            ),
            timestamp: str(
              event.timestamp ?? nested.timestamp,
              "N/A"
            ),
          };
        });

        if (!active) return;

        setIncidents(mapped);
        setOnline(true);
        setSelected((previous) =>
          previous
            ? mapped.find((item) => item.id === previous.id) ??
              previous
            : mapped[0] ?? null
        );
      } catch {
        if (active) setOnline(false);
      }
    }

    void load();
    const timer = window.setInterval(() => void load(), 4000);

    return () => {
      active = false;
      window.clearInterval(timer);
    };
  }, []);

  return (
    <section style={panel}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          gap: 12,
          flexWrap: "wrap",
          alignItems: "center",
        }}
      >
        <div>
          <h2 style={{ margin: 0, color: "#dff8ff" }}>
            🛡️ AI Incident Investigation V4
          </h2>
          <p style={{ color: "#9cbbd9", fontSize: 12 }}>
            Blockchain Threat Forensics · Isolation Forest
          </p>
        </div>

        <strong style={{ color: online ? "#54ffc0" : "#ff718b" }}>
          ● {online ? "INVESTIGATION ONLINE" : "API OFFLINE"}
        </strong>
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns:
            "repeat(auto-fit, minmax(min(100%, 280px), 1fr))",
          gap: 18,
          marginTop: 20,
        }}
      >
        <div
          style={{
            background: "rgba(5,20,50,.65)",
            border: "1px solid rgba(90,180,255,.25)",
            borderRadius: 12,
            padding: 16,
          }}
        >
          <h3 style={{ color: "#75dfff", fontSize: 15 }}>
            ⚡ Detected Incidents ({incidents.length})
          </h3>

          <div style={{ maxHeight: 390, overflowY: "auto" }}>
            {incidents.map((incident, index) => (
              <button
                key={`${incident.id}-${index}`}
                type="button"
                onClick={() => setSelected(incident)}
                style={{
                  display: "block",
                  width: "100%",
                  textAlign: "left",
                  padding: 14,
                  marginBottom: 9,
                  cursor: "pointer",
                  borderRadius: 9,
                  color: "#eef7ff",
                  background:
                    selected?.id === incident.id
                      ? "rgba(87,84,215,.45)"
                      : "rgba(27,53,101,.45)",
                  border:
                    selected?.id === incident.id
                      ? "1px solid #8e9dff"
                      : "1px solid rgba(106,164,255,.18)",
                }}
              >
                <div style={{ fontWeight: 800 }}>
                  {incident.network}
                  <span style={{ float: "right", color: "#ff7a9f" }}>
                    RISK {incident.risk}
                  </span>
                </div>
                <div
                  style={{
                    color: "#aac7e2",
                    fontSize: 11,
                    marginTop: 6,
                  }}
                >
                  {incident.type.replaceAll("_", " ")}
                </div>
              </button>
            ))}

            {incidents.length === 0 && (
              <p style={{ color: "#a8bdd8" }}>
                {online
                  ? "No recent AI incidents."
                  : "Waiting for AI connection..."}
              </p>
            )}
          </div>
        </div>

        <div
          style={{
            background: "rgba(5,20,50,.65)",
            border: "1px solid rgba(171,116,255,.35)",
            borderRadius: 12,
            padding: 20,
          }}
        >
          <h3 style={{ color: "#d2b0ff", fontSize: 15 }}>
            🔬 Incident Forensic Analysis
          </h3>

          {selected ? (
            <>
              <div
                style={{
                  fontSize: 26,
                  fontWeight: 900,
                  color: "#ff789e",
                  margin: "20px 0",
                }}
              >
                {selected.classification}
              </div>

              {[
                ["Incident ID", selected.id],
                ["Blockchain", selected.network],
                ["Event Type", selected.type],
                ["Risk Score", `${selected.risk}/100`],
                [
                  "AI Anomaly Score",
                  selected.score === null
                    ? "N/A"
                    : selected.score.toFixed(5),
                ],
                ["Timestamp", selected.timestamp],
              ].map(([label, value]) => (
                <div
                  key={label}
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    gap: 15,
                    borderBottom:
                      "1px solid rgba(160,190,255,.12)",
                    padding: "12px 0",
                    fontSize: 12,
                  }}
                >
                  <span style={{ color: "#9db9d4" }}>{label}</span>
                  <strong
                    style={{
                      textAlign: "right",
                      overflowWrap: "anywhere",
                    }}
                  >
                    {value}
                  </strong>
                </div>
              ))}

              <p
                style={{
                  marginTop: 20,
                  fontSize: 12,
                  color: "#a8c5e5",
                  lineHeight: 1.7,
                }}
              >
                This event was flagged by the experimental
                Isolation Forest detection engine. The AI score
                indicates statistical deviation from its training
                data, not proof of malicious activity.
              </p>
            </>
          ) : (
            <p style={{ color: "#a6bfdc" }}>
              Select an incident to view its investigation.
            </p>
          )}
        </div>
      </div>

      <p
        style={{
          marginTop: 18,
          textAlign: "center",
          color: "#8eabc8",
          fontSize: 11,
        }}
      >
        RESEARCH SIMULATION · NOT VERIFIED BLOCKCHAIN ATTACKS
      </p>
    </section>
  );
}
