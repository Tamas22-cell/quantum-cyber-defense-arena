
import QuantumResearchPanel from "./components/QuantumResearchPanel";
import HybridFusionPanel from "./components/HybridFusionPanel";

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
  mode: string;
  total_events: number;
  active_threats: number;
  critical_events?: number;
  average_risk?: number;
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
  blue: "#75caff",
  red: "#ff587f",
  yellow: "#ffd166",
  purple: "#d9acff",
  green: "#68efb5",
};

const panelStyle: CSSProperties = {
  background: "rgba(16, 45, 83, 0.80)",
  border: "1px solid rgba(112, 202, 255, 0.30)",
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
          justifyContent: "space-between",
          gap: 10,
          color: "#bbd7ee",
          fontSize: 12,
          fontWeight: 700,
          letterSpacing: 1,
        }}
      >
        <span>{title.toUpperCase()}</span>
        <span style={{ color }}>{icon}</span>
      </div>

      <div
        style={{
          color,
          fontSize: "clamp(29px, 3vw, 40px)",
          fontWeight: 800,
          textAlign: "center",
          padding: "20px 0 12px",
          textShadow: `0 0 24px ${color}55`,
          fontVariantNumeric: "tabular-nums",
        }}
      >
        {value}
      </div>

      <div
        style={{
          color: "#8eb4d1",
          fontSize: 11,
          textAlign: "center",
        }}
      >
        Simulated security telemetry
      </div>
    </div>
  );
}

function App() {
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
          throw new Error(`API HTTP ${response.status}`);
        }

        const data: ApiData = await response.json();

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

        setOnline(true);
        setEvents(list);
        setTotalEvents(data.total_events ?? list.length);

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
          console.error("Cyber API error:", error);
          setOnline(false);
        }
      } finally {
        fetching = false;
      }
    }

    void update();

    const interval = window.setInterval(() => {
      void update();
    }, 2000);

    return () => {
      alive = false;
      window.clearInterval(interval);
      controller.abort();
    };
  }, [paused]);

  const stats = useMemo(() => {
    const active = events.filter(
      (event) => event.risk_score >= 60
    ).length;

    const critical = events.filter(
      (event) => event.risk_score >= 80
    ).length;

    const average = events.length
      ? Math.round(
          events.reduce(
            (sum, event) => sum + event.risk_score,
            0
          ) / events.length
        )
      : 0;

    return {
      active,
      critical,
      average,
    };
  }, [events]);

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
          padding: "22px clamp(16px, 4vw, 48px)",
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
            alignItems: "center",
            gap: 14,
          }}
        >
          <Shield size={36} color={colors.cyan} />

          <div>
            <div
              style={{
                fontSize: 18,
                fontWeight: 800,
                letterSpacing: 1,
              }}
            >
              QUANTUM CYBER DEFENSE
            </div>

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
            flexWrap: "wrap",
            alignItems: "center",
            gap: 16,
          }}
        >
          <span
            style={{
              border: "1px solid #edbf66",
              borderRadius: 8,
              color: colors.yellow,
              padding: "9px 12px",
              fontSize: 11,
              fontWeight: 800,
            }}
          >
            SIMULATION MODE
          </span>

          <span
            style={{
              color: online ? colors.green : colors.red,
              fontSize: 12,
              fontWeight: 800,
            }}
          >
            ● API {online ? "ONLINE" : "OFFLINE"}
          </span>

          <button
            type="button"
            onClick={() => setPaused((value) => !value)}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              background: "#256eaa",
              border: "1px solid #72d2ff",
              color: "white",
              padding: "10px 18px",
              borderRadius: 9,
              cursor: "pointer",
              fontWeight: 700,
            }}
          >
            {paused ? (
              <Play size={17} />
            ) : (
              <Pause size={17} />
            )}

            {paused ? "Resume" : "Pause"}
          </button>
        </div>
      </header>

      <main
        style={{
          maxWidth: 1500,
          padding: "30px clamp(16px, 4vw, 48px)",
          margin: "auto",
        }}
      >
        <div style={{ marginBottom: 28 }}>
          <div
            style={{
              color: colors.cyan,
              letterSpacing: 2,
              fontSize: 11,
              fontWeight: 800,
            }}
          >
            REAL-TIME SECURITY INTELLIGENCE
          </div>

          <h1
            style={{
              margin: "12px 0",
              fontSize: "clamp(26px, 4vw, 40px)",
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
            Blockchain Security · AI Monitoring · Quantum
            Research
          </p>
        </div>

        {/* MAIN SECURITY METRICS */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(min(100%, 210px), 1fr))",
            gap: 16,
            marginBottom: 20,
          }}
        >
          <Metric
            title="Total Events"
            value={totalEvents}
            color={colors.cyan}
            icon={<Activity />}
          />

          <Metric
            title="Active Threats"
            value={stats.active}
            color={colors.red}
            icon={<ShieldAlert />}
          />

          <Metric
            title="Critical Events"
            value={stats.critical}
            color={colors.yellow}
            icon={<AlertTriangle />}
          />

          <Metric
            title="Average Risk"
            value={`${stats.average}/100`}
            color={colors.purple}
            icon={<BrainCircuit />}
          />
        </div>

        {/* LIVE ANALYTICS AND 3D NETWORK */}

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(min(100%, 350px), 1fr))",
            gap: 20,
            marginBottom: 20,
          }}
        >
          <section style={panelStyle}>
            <h3
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <Activity
                color={colors.cyan}
                size={21}
              />
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

            <div
              style={{
                height: 320,
                width: "100%",
              }}
            >
              <ResponsiveContainer
                width="100%"
                height="100%"
              >
                <AreaChart data={history}>
                  <defs>
                    <linearGradient
                      id="riskFill"
                      x1="0"
                      x2="0"
                      y1="0"
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
                    tick={{
                      fontSize: 10,
                    }}
                  />

                  <YAxis
                    stroke="#b9d6e9"
                    domain={[0, 100]}
                    tick={{
                      fontSize: 11,
                    }}
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#102945",
                      border: "1px solid #528bb3",
                      borderRadius: 10,
                      color: "white",
                    }}
                  />

                  <Area
                    type="monotone"
                    dataKey="risk"
                    name="Average Risk"
                    stroke="#d5b3ff"
                    strokeWidth={3}
                    fill="url(#riskFill)"
                    isAnimationActive
                    animationDuration={650}
                  />

                  <Area
                    type="monotone"
                    dataKey="threats"
                    name="Active Threats"
                    stroke={colors.green}
                    strokeWidth={2}
                    fill="transparent"
                    isAnimationActive
                    animationDuration={650}
                  />
                </AreaChart>
              </ResponsiveContainer>
            </div>
          </section>

          {/* 3D CYBER NETWORK */}

          <section style={panelStyle}>
            <h3
              style={{
                display: "flex",
                alignItems: "center",
                gap: 10,
              }}
            >
              <Globe2
                color={colors.cyan}
                size={21}
              />

              Cyber Network

              <span
                style={{
                  marginLeft: "auto",
                  color: colors.green,
                  fontSize: 10,
                }}
              >
                3D LIVE
              </span>
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
                width: "100%",
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
            <Zap
              color={colors.cyan}
              size={21}
            />

            Security Event Stream

            <span
              style={{
                marginLeft: "auto",
                color: colors.green,
                fontSize: 12,
              }}
            >
              {events.length} EVENTS
            </span>
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
                borderCollapse: "collapse",
                minWidth: 650,
                fontSize: 12,
                textAlign: "left",
              }}
            >
              <thead>
                <tr style={{ color: "#acd9ed" }}>
                  {[
                    "NETWORK",
                    "EVENT TYPE",
                    "RISK SCORE",
                    "SEVERITY",
                    "TIME",
                  ].map((name) => (
                    <th
                      key={name}
                      style={{
                        padding: 13,
                        borderBottom:
                          "1px solid #528bb355",
                      }}
                    >
                      {name}
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
                      borderBottom:
                        "1px solid #528bb322",
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
                        color: riskColor(
                          event.risk_score
                        ),
                        fontWeight: 800,
                      }}
                    >
                      {event.risk_score}/100
                    </td>

                    <td style={{ padding: 13 }}>
                      <span
                        style={{
                          borderRadius: 7,
                          padding: "5px 9px",
                          background:
                            riskColor(
                              event.risk_score
                            ) + "22",
                          color: riskColor(
                            event.risk_score
                          ),
                          fontWeight: 800,
                        }}
                      >
                        {event.severity}
                      </span>
                    </td>

                    <td style={{ padding: 13 }}>
                      {formatTime(event.timestamp)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {!events.length && (
              <p
                style={{
                  padding: 20,
                  textAlign: "center",
                  color: "#a9cbe2",
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
              borderColor: riskColor(
                selected.risk_score
              ),
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: 16,
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
                  color: riskColor(
                    selected.risk_score
                  ),
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

        {/* V5 - AUTOMATED AI THREAT REPORT */}

        <AIThreatReport />

        {/* V6.4 - QUANTUM RESEARCH DASHBOARD */}

        <QuantumResearchPanel />

        {/* V7.2 - HYBRID QUANTUM AI FUSION */}

        <HybridFusionPanel />

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
          QUANTUM CYBER DEFENSE ARENA · RESEARCH
          ENVIRONMENT

          <p>
            Simulated telemetry. No real attacks or
            verified cybersecurity incidents are
            represented.
          </p>
        </footer>
      </main>
    </div>
  );
}

export default App;
