
import LiveCommandCenterV15_4 from "./components/LiveCommandCenterV15_4";
import BlockchainIntelligenceV16_5 from "./components/BlockchainIntelligenceV16_5";

import { useEffect, useMemo, useState } from "react";
import type { CSSProperties, ReactNode } from "react";

import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  Globe2,
  Pause,
  Play,
  Shield,
  ShieldAlert,
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

import CyberNetwork3D from "./components/CyberNetwork3D";
import AIThreatPanel from "./components/AIThreatPanel";
import AIIncidentInvestigation from "./components/AIIncidentInvestigation";
import AIThreatReport from "./components/AIThreatReport";
import QuantumResearchPanel from "./components/QuantumResearchPanel";
import HybridFusionPanel from "./components/HybridFusionPanel";
import DynamicFusionPanel from "./components/DynamicFusionPanel";
import AutonomousInvestigationPanel from "./components/AutonomousInvestigationPanel";
import MultiAgentPanel from "./components/MultiAgentPanel";
import ResearchValidationPanel from "./components/ResearchValidationPanel";

import ResearchDashboardV11_4 from "./ResearchDashboardV11_4";

import "./App.css";

type Severity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

type Threat = {
  id: string;
  timestamp: string;
  network: string;
  type: string;
  risk_score: number;
  severity: Severity;
  source: string;
  destination: string;
  mode: string;
};

type ApiData = {
  total_events: number;
  events: Threat[];
};

type ChartPoint = {
  time: string;
  risk: number;
  threats: number;
};

const API_URL = "http://127.0.0.1:8000/api/threats";

const colors = {
  cyan: "#6cf8eb",
  red: "#ff587f",
  yellow: "#ffd166",
  purple: "#d9acff",
  green: "#68efb5",
};

const panelStyle: CSSProperties = {
  background: "rgba(16,45,83,.8)",
  border: "1px solid rgba(112,202,255,.3)",
  borderRadius: 18,
  padding: 20,
  minWidth: 0,
  boxShadow: "0 12px 38px rgba(0,0,0,.18)",
};

function riskColor(score: number): string {
  if (score >= 80) return colors.red;
  if (score >= 60) return colors.yellow;
  if (score >= 35) return colors.purple;
  return colors.green;
}

function formatTime(value: string): string {
  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "--:--:--"
    : date.toLocaleTimeString("hu-HU");
}

function Metric({
  label,
  value,
  accent,
  icon,
}: {
  label: string;
  value: string | number;
  accent: string;
  icon: ReactNode;
}) {
  return (
    <div style={panelStyle}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          color: "#bbd7ee",
          fontSize: 12,
          fontWeight: 700,
        }}
      >
        <span>{label}</span>
        <span style={{ color: accent }}>{icon}</span>
      </div>

      <div
        style={{
          textAlign: "center",
          fontSize: 35,
          fontWeight: 800,
          color: accent,
          padding: "20px 0 12px",
        }}
      >
        {value}
      </div>

      <div
        style={{
          textAlign: "center",
          color: "#8eb4d1",
          fontSize: 11,
        }}
      >
        Simulated security telemetry
      </div>
    </div>
  );
}

export default function App() {
  const [events, setEvents] = useState<Threat[]>([]);
  const [totalEvents, setTotalEvents] = useState(0);
  const [history, setHistory] = useState<ChartPoint[]>([]);
  const [online, setOnline] = useState(false);
  const [paused, setPaused] = useState(false);

  const [selected, setSelected] = useState<Threat | null>(
    null
  );

  useEffect(() => {
    if (paused) return;

    let alive = true;
    let fetching = false;

    const controller = new AbortController();

    async function update() {
      if (fetching) return;

      fetching = true;

      try {
        const response = await fetch(API_URL, {
          cache: "no-store",
          signal: controller.signal,
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const data = (await response.json()) as ApiData;

        if (!alive || !Array.isArray(data.events)) {
          return;
        }

        const list = data.events;

        const active = list.filter(
          (event) => event.risk_score >= 60
        ).length;

        const average = list.length
          ? Math.round(
              list.reduce(
                (sum, event) => sum + event.risk_score,
                0
              ) / list.length
            )
          : 0;

        setEvents(list);
        setTotalEvents(data.total_events ?? list.length);
        setOnline(true);

        setHistory((previous) => [
          ...previous.slice(-39),
          {
            time: new Date().toLocaleTimeString("hu-HU"),
            risk: average,
            threats: active,
          },
        ]);
      } catch (error) {
        if (alive && !controller.signal.aborted) {
          console.error("Cyber API error", error);
          setOnline(false);
        }
      } finally {
        fetching = false;
      }
    }

    void update();

    const timer = window.setInterval(
      () => void update(),
      2000
    );

    return () => {
      alive = false;
      window.clearInterval(timer);
      controller.abort();
    };
  }, [paused]);

  const stats = useMemo(
    () => ({
      active: events.filter(
        (event) => event.risk_score >= 60
      ).length,

      critical: events.filter(
        (event) => event.risk_score >= 80
      ).length,

      average: events.length
        ? Math.round(
            events.reduce(
              (sum, event) => sum + event.risk_score,
              0
            ) / events.length
          )
        : 0,
    }),
    [events]
  );

  return (
    <div
      style={{
        minHeight: "100vh",
        background:
          "radial-gradient(ellipse at 85% 0%, #39275e 0%, transparent 38%), linear-gradient(135deg, #071b31, #12355a 58%, #151d3e)",
        color: "#f3f9ff",
        fontFamily: "Inter, Arial, sans-serif",
      }}
    >
      <header
        style={{
          padding: "22px clamp(16px,4vw,48px)",
          borderBottom: "1px solid #47739977",
          background: "#071a2dbb",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          flexWrap: "wrap",
          gap: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            gap: 14,
            alignItems: "center",
          }}
        >
          <Shield size={36} color={colors.cyan} />

          <div>
            <strong
              style={{
                fontSize: 18,
                letterSpacing: 1,
              }}
            >
              QUANTUM CYBER DEFENSE
            </strong>

            <div
              style={{
                color: colors.cyan,
                fontSize: 10,
                letterSpacing: 2,
                marginTop: 5,
              }}
            >
              AI SECURITY OPERATIONS ARENA
            </div>
          </div>
        </div>

        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 16,
            flexWrap: "wrap",
          }}
        >
          <span
            style={{
              padding: "9px 12px",
              border: "1px solid #edbf66",
              borderRadius: 8,
              color: colors.yellow,
              fontSize: 11,
              fontWeight: 800,
            }}
          >
            SIMULATION MODE
          </span>

          <strong
            style={{
              fontSize: 12,
              color: online ? colors.green : colors.red,
            }}
          >
            ● API {online ? "ONLINE" : "OFFLINE"}
          </strong>

          <button
            type="button"
            onClick={() => setPaused((value) => !value)}
            style={{
              display: "flex",
              gap: 8,
              alignItems: "center",
              background: "#256eaa",
              border: "1px solid #72d2ff",
              color: "white",
              padding: "10px 18px",
              borderRadius: 9,
              cursor: "pointer",
            }}
          >
            {paused ? <Play size={17} /> : <Pause size={17} />}
            {paused ? "Resume" : "Pause"}
          </button>
        </div>
      </header>

      <main
        style={{
          maxWidth: 1500,
          padding: "30px clamp(16px,4vw,48px)",
          margin: "auto",
        }}
      >
        <div style={{ marginBottom: 28 }}>
          <div
            style={{
              color: colors.cyan,
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: 2,
            }}
          >
            REAL-TIME SECURITY INTELLIGENCE
          </div>

          <h1
            style={{
              margin: "12px 0",
              fontSize: "clamp(26px,4vw,40px)",
            }}
          >
            Cyber Threat Command Center
          </h1>

          <p
            style={{
              color: "#afd0e6",
              margin: 0,
            }}
          >
            Blockchain Security · AI Monitoring · Quantum Research
          </p>
        </div>

        {/* MAIN SECURITY METRICS */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit,minmax(min(100%,210px),1fr))",
            gap: 16,
            marginBottom: 20,
          }}
        >
          <Metric
            label="TOTAL EVENTS"
            value={totalEvents}
            accent={colors.cyan}
            icon={<Activity />}
          />

          <Metric
            label="ACTIVE THREATS"
            value={stats.active}
            accent={colors.red}
            icon={<ShieldAlert />}
          />

          <Metric
            label="CRITICAL EVENTS"
            value={stats.critical}
            accent={colors.yellow}
            icon={<AlertTriangle />}
          />

          <Metric
            label="AVERAGE RISK"
            value={`${stats.average}/100`}
            accent={colors.purple}
            icon={<BrainCircuit />}
          />
        </div>

        {/* LIVE ANALYTICS AND 3D NETWORK */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit,minmax(min(100%,350px),1fr))",
            gap: 20,
            marginBottom: 20,
          }}
        >
          <section style={panelStyle}>
            <h3
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
              }}
            >
              <Activity color={colors.cyan} size={21} />
              Threat Activity
            </h3>

            <p
              style={{
                color: "#b5d1e5",
                fontSize: 12,
              }}
            >
              Automatically updating risk analytics
            </p>

            <div style={{ height: 320 }}>
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={history}>
                  <defs>
                    <linearGradient
                      id="riskFill"
                      x1="0"
                      y1="0"
                      x2="0"
                      y2="1"
                    >
                      <stop
                        offset="0%"
                        stopColor="#b18bff"
                        stopOpacity={0.55}
                      />
                      <stop
                        offset="100%"
                        stopColor="#b18bff"
                        stopOpacity={0.02}
                      />
                    </linearGradient>
                  </defs>

                  <CartesianGrid
                    stroke="#91b6d333"
                    strokeDasharray="4 4"
                  />

                  <XAxis
                    dataKey="time"
                    stroke="#b9d6e9"
                    tick={{ fontSize: 10 }}
                  />

                  <YAxis
                    stroke="#b9d6e9"
                    domain={[0, 100]}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#102945",
                      border: "1px solid #528bb3",
                      borderRadius: 10,
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="risk"
                    name="Average Risk"
                    stroke="#d5b3ff"
                    strokeWidth={3}
                    fill="url(#riskFill)"
                  />

                  <Area
                    type="monotone"
                    dataKey="threats"
                    name="Active Threats"
                    stroke={colors.green}
                    fill="transparent"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          <section style={panelStyle}>
            <h3
              style={{
                display: "flex",
                gap: 10,
                alignItems: "center",
              }}
            >
              <Globe2 size={21} color={colors.cyan} />
              Cyber Network

              <small
                style={{
                  marginLeft: "auto",
                  color: colors.green,
                }}
              >
                3D LIVE
              </small>
            </h3>

            <p
              style={{
                color: "#b5d1e5",
                fontSize: 12,
              }}
            >
              Interactive blockchain network visualization
            </p>

            <div
              style={{
                height: 320,
                overflow: "hidden",
                borderRadius: 12,
                background: "#06162988",
              }}
            >
              <CyberNetwork3D events={events} />
            </div>
          </section>
        </div>

        {/* SECURITY EVENT STREAM */}

        <section style={panelStyle}>
          <h3
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
            }}
          >
            <Zap color={colors.cyan} size={21} />
            Security Event Stream

            <small
              style={{
                marginLeft: "auto",
                color: colors.green,
              }}
            >
              {events.length} EVENTS
            </small>
          </h3>

          <p
            style={{
              color: "#b5d1e5",
              fontSize: 12,
            }}
          >
            Simulated threats · Click a row for details
          </p>

          <div style={{ overflowX: "auto" }}>
            <table
              style={{
                width: "100%",
                minWidth: 650,
                borderCollapse: "collapse",
                fontSize: 12,
                textAlign: "left",
              }}
            >
              <thead>
                <tr>
                  {[
                    "NETWORK",
                    "EVENT TYPE",
                    "RISK SCORE",
                    "SEVERITY",
                    "TIME",
                  ].map((label) => (
                    <th
                      key={label}
                      style={{
                        padding: 13,
                        borderBottom: "1px solid #528bb355",
                        color: "#acd9ed",
                      }}
                    >
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>

              <tbody>
                {events.map((event) => (
                  <tr
                    key={event.id}
                    onClick={() => setSelected(event)}
                    style={{
                      cursor: "pointer",
                      borderBottom: "1px solid #528bb322",
                    }}
                  >
                    <td style={{ padding: 13 }}>
                      {event.network}
                    </td>

                    <td style={{ padding: 13 }}>
                      {event.type.replaceAll("_", " ")}
                    </td>

                    <td
                      style={{
                        padding: 13,
                        color: riskColor(event.risk_score),
                        fontWeight: 800,
                      }}
                    >
                      {event.risk_score}/100
                    </td>

                    <td
                      style={{
                        padding: 13,
                        color: riskColor(event.risk_score),
                      }}
                    >
                      {event.severity}
                    </td>

                    <td style={{ padding: 13 }}>
                      {formatTime(event.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {events.length === 0 && (
              <p
                style={{
                  padding: 20,
                  textAlign: "center",
                }}
              >
                Waiting for simulated security events...
              </p>
            )}
          </div>
        </section>

        {/* SELECTED EVENT INVESTIGATION */}

        {selected && (
          <section
            style={{
              ...panelStyle,
              marginTop: 20,
              borderColor: riskColor(selected.risk_score),
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h3>Threat Investigation</h3>

              <button
                type="button"
                onClick={() => setSelected(null)}
                style={{
                  background: "#224d74",
                  border: "1px solid #82b5dc",
                  color: "white",
                  padding: "8px 15px",
                  borderRadius: 8,
                  cursor: "pointer",
                }}
              >
                Close
              </button>
            </div>

            <p>Network: {selected.network}</p>
            <p>Type: {selected.type}</p>

            <p>
              Risk Score:{" "}
              <strong
                style={{
                  color: riskColor(selected.risk_score),
                }}
              >
                {selected.risk_score}/100
              </strong>
            </p>

            <p>Severity: {selected.severity}</p>

            <p style={{ overflowWrap: "anywhere" }}>
              Source: {selected.source}
            </p>

            <p style={{ overflowWrap: "anywhere" }}>
              Destination: {selected.destination}
            </p>

            <p>Data: SIMULATED — NOT REAL ATTACKS</p>
          </section>
        )}

        {/* V3 - AI THREAT INTELLIGENCE */}
        <AIThreatPanel />

        {/* V4 - AI INCIDENT INVESTIGATION */}
        <AIIncidentInvestigation />

        {/* V5 - AUTOMATED THREAT REPORT */}
        <AIThreatReport />

        {/* V6.4 - QUANTUM RESEARCH */}
        <QuantumResearchPanel />

        {/* V7.2 - HYBRID QUANTUM AI FUSION */}
        <HybridFusionPanel />

        {/* V7.5 - DYNAMIC HYBRID FUSION */}
        <DynamicFusionPanel />

        {/* V8.2 - AUTONOMOUS INVESTIGATION */}
        <AutonomousInvestigationPanel />

        {/* V9.3 - MULTI-AGENT CYBER DEFENSE */}
        <MultiAgentPanel />

        {/* V10.3 - RESEARCH VALIDATION */}
        <ResearchValidationPanel />

        {/* V11.4 - ADVANCED RESEARCH DASHBOARD */}
        <ResearchDashboardV11_4 />

        {/* V15.4 - LIVE COMMAND CENTER */}
        <LiveCommandCenterV15_4 />

        {/* V16.5 - REAL BLOCKCHAIN INTELLIGENCE */}
        <BlockchainIntelligenceV16_5 />

        {/* FOOTER */}
        <footer
          style={{
            marginTop: 25,
            padding: 15,
            textAlign: "center",
            color: "#87b2d3",
            fontSize: 11,
          }}
        >
          QUANTUM CYBER DEFENSE ARENA · RESEARCH ENVIRONMENT

          <p>
            Simulated security telemetry and historical
            Ethereum research data. Statistical outliers
            are not verified cybersecurity incidents.
          </p>
        </footer>
      </main>
    </div>
  );
}
