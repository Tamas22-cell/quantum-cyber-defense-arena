
import { useEffect, useMemo, useState } from "react";
import type { CSSProperties } from "react";
import {
  Activity,
  AlertTriangle,
  BrainCircuit,
  CheckCircle2,
  Cpu,
  FileJson,
  Pause,
  Play,
  RefreshCw,
  Shield,
  ShieldAlert,
  Zap,
} from "lucide-react";

type V15Event = {
  event_id: string;
  network: string;
  risk_score: number;
  hybrid_decision: string;
  final_decision: string;
  final_priority: string;
  consensus: string;
  manual_review_required: boolean;
  planned_action: string;
  response_status: string;
};

type V15Payload = {
  version?: string;
  mode?: string;
  events?: Record<string, unknown>[];
  response_plans?: Record<string, unknown>[];
};

const C = {
  bg: "#061326",
  panel: "rgba(9, 30, 57, 0.94)",
  border: "rgba(77, 168, 235, 0.31)",
  cyan: "#44e7ff",
  blue: "#5da5ff",
  purple: "#c393ff",
  green: "#51e9ae",
  yellow: "#ffd166",
  red: "#ff6487",
  text: "#e5f4ff",
  muted: "#93b1cb",
};

const panelStyle: CSSProperties = {
  background: C.panel,
  border: `1px solid ${C.border}`,
  borderRadius: 17,
  padding: 20,
  minWidth: 0,
  boxShadow: "0 14px 35px rgba(0,0,0,0.2)",
};

const fmt = (value: number) =>
  value.toLocaleString("en-US");

function getText(
  value: unknown,
  fallback = ""
): string {
  return typeof value === "string"
    ? value
    : fallback;
}

function getRisk(value: unknown): number {
  const n = Number(value);
  return Number.isFinite(n)
    ? Math.max(0, Math.min(100, n))
    : 0;
}

function severityColor(priority: string): string {
  if (priority === "P1") return C.red;
  if (priority === "P2") return C.yellow;
  if (priority === "P3") return C.purple;
  return C.green;
}

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
    <div
      style={{
        ...panelStyle,
        padding: "17px 18px",
      }}
    >
      <div
        style={{
          color: C.muted,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 1.2,
          minHeight: 26,
        }}
      >
        {title}
      </div>

      <div
        style={{
          color,
          fontSize: "clamp(23px, 2.4vw, 36px)",
          fontWeight: 900,
          margin: "10px 0",
          fontVariantNumeric: "tabular-nums",
          textShadow: `0 0 16px ${color}44`,
        }}
      >
        {value}
      </div>

      <div
        style={{
          height: 3,
          width: "45%",
          background: color,
          borderRadius: 10,
          boxShadow: `0 0 12px ${color}`,
        }}
      />
    </div>
  );
}

function StatusPill({
  children,
  color = C.green,
}: {
  children: React.ReactNode;
  color?: string;
}) {
  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        gap: 7,
        border: `1px solid ${color}66`,
        color,
        padding: "7px 10px",
        borderRadius: 8,
        fontSize: 10,
        fontWeight: 800,
        letterSpacing: 0.5,
      }}
    >
      <span
        style={{
          width: 7,
          height: 7,
          borderRadius: "50%",
          background: color,
          boxShadow: `0 0 10px ${color}`,
        }}
      />
      {children}
    </span>
  );
}

function ResearchPipeline() {
  const items = [
    {
      icon: <Cpu size={21} />,
      title: "V15.1",
      name: "THREAT ORCHESTRATOR",
      color: C.cyan,
    },
    {
      icon: <BrainCircuit size={21} />,
      title: "V15.2",
      name: "MULTI-AGENT ENGINE",
      color: C.purple,
    },
    {
      icon: <ShieldAlert size={21} />,
      title: "V15.3",
      name: "RESPONSE SIMULATOR",
      color: C.green,
    },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns:
          "repeat(auto-fit, minmax(190px, 1fr))",
        gap: 14,
        marginBottom: 20,
      }}
    >
      {items.map((item) => (
        <div
          key={item.title}
          style={{
            ...panelStyle,
            borderColor: `${item.color}77`,
            display: "flex",
            alignItems: "center",
            gap: 12,
          }}
        >
          <span
            style={{
              color: item.color,
              filter: `drop-shadow(0 0 9px ${item.color})`,
            }}
          >
            {item.icon}
          </span>

          <div>
            <div
              style={{
                color: item.color,
                fontSize: 18,
                fontWeight: 900,
              }}
            >
              {item.title}
            </div>
            <div
              style={{
                color: C.muted,
                fontSize: 10,
                fontWeight: 800,
                marginTop: 5,
              }}
            >
              {item.name}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

/*
 * Demonstration data is only used when the three
 * exported V15 JSON files are not available.
 *
 * These rows are illustrative and are NOT actual
 * measured V15.1–V15.3 results.
 */
const DEMO_EVENTS: V15Event[] = [
  {
    event_id: "DEMO-0001",
    network: "Ethereum",
    risk_score: 91,
    hybrid_decision: "ANOMALY",
    final_decision: "ANOMALY",
    final_priority: "P1",
    consensus: "UNANIMOUS_ANOMALY",
    manual_review_required: false,
    planned_action: "ESCALATE_CRITICAL",
    response_status: "AWAITING_HUMAN_APPROVAL",
  },
  {
    event_id: "DEMO-0002",
    network: "Polygon",
    risk_score: 63,
    hybrid_decision: "REVIEW",
    final_decision: "REVIEW",
    final_priority: "P3",
    consensus: "UNANIMOUS_REVIEW",
    manual_review_required: true,
    planned_action: "REQUEST_MANUAL_REVIEW",
    response_status: "AWAITING_HUMAN_APPROVAL",
  },
  {
    event_id: "DEMO-0003",
    network: "Arbitrum",
    risk_score: 75,
    hybrid_decision: "ANOMALY",
    final_decision: "ANOMALY",
    final_priority: "P2",
    consensus: "UNANIMOUS_ANOMALY",
    manual_review_required: false,
    planned_action: "QUEUE_HIGH_PRIORITY",
    response_status: "AWAITING_HUMAN_APPROVAL",
  },
  {
    event_id: "DEMO-0004",
    network: "Base",
    risk_score: 22,
    hybrid_decision: "NORMAL",
    final_decision: "NORMAL",
    final_priority: "P4",
    consensus: "UNANIMOUS_NORMAL",
    manual_review_required: false,
    planned_action: "CONTINUE_MONITORING",
    response_status: "SIMULATED_MONITORING",
  },
];

function normalizeEvents(
  rawV151: V15Payload,
  rawV152: V15Payload,
  rawV153: V15Payload
): V15Event[] {
  const a = rawV151.events ?? [];
  const b = rawV152.events ?? [];
  const c = rawV153.response_plans ?? [];

  const v152ById = new Map(
    b.map((row) => [
      getText(row.event_id),
      row,
    ])
  );

  const v153ById = new Map(
    c.map((row) => [
      getText(row.event_id),
      row,
    ])
  );

  return a.map((original) => {
    const id = getText(original.event_id);

    const decision = v152ById.get(id);
    const response = v153ById.get(id);

    return {
      event_id: id,
      network: getText(original.network, "UNKNOWN"),
      risk_score: getRisk(original.risk_score),
      hybrid_decision: getText(
        original.hybrid_decision,
        "UNKNOWN"
      ),
      final_decision: getText(
        decision?.final_decision,
        "UNKNOWN"
      ),
      final_priority: getText(
        decision?.final_priority,
        "UNKNOWN"
      ),
      consensus: getText(
        decision?.consensus,
        "UNKNOWN"
      ),
      manual_review_required:
        decision?.manual_review_required === true,
      planned_action: getText(
        response?.planned_action,
        "UNKNOWN"
      ),
      response_status: getText(
        response?.response_status,
        "UNKNOWN"
      ),
    };
  });
}

function validatePayloads(
  a: V15Payload,
  b: V15Payload,
  c: V15Payload
): boolean {
  if (
    a.version !== "15.1.0" ||
    b.version !== "15.2.0" ||
    c.version !== "15.3.0"
  ) {
    return false;
  }

  if (
    a.mode !== "RESEARCH_SIMULATION" ||
    b.mode !== "RESEARCH_SIMULATION" ||
    c.mode !== "RESEARCH_SIMULATION"
  ) {
    return false;
  }

  if (
    !Array.isArray(a.events) ||
    !Array.isArray(b.events) ||
    !Array.isArray(c.response_plans) ||
    a.events.length === 0
  ) {
    return false;
  }

  const ids = (values: Record<string, unknown>[]) =>
    values.map((v) => getText(v.event_id));

  const first = ids(a.events);
  const second = ids(b.events);
  const third = ids(c.response_plans);

  return (
    first.length === second.length &&
    first.length === third.length &&
    first.every(
      (id, index) =>
        id !== "" &&
        id === second[index] &&
        id === third[index]
    )
  );
}

export default function LiveCommandCenterV15_4() {
  const [events, setEvents] =
    useState<V15Event[]>(DEMO_EVENTS);

  const [source, setSource] = useState<
    "DEMO" | "V15_JSON"
  >("DEMO");

  const [loading, setLoading] = useState(false);
  const [paused, setPaused] = useState(false);
  const [visibleCount, setVisibleCount] = useState(4);
  const [selectedId, setSelectedId] =
    useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);

    try {
      const paths = [
        "/v15/threat_orchestrator_v15_1_results.json",
        "/v15/multi_agent_decision_v15_2_results.json",
        "/v15/autonomous_response_v15_3_results.json",
      ];

      const responses = await Promise.all(
        paths.map((path) =>
          fetch(path, { cache: "no-store" })
        )
      );

      if (responses.some((r) => !r.ok)) {
        throw new Error(
          "V15 JSON files are not available."
        );
      }

      const [a, b, c] = (await Promise.all(
        responses.map((r) => r.json())
      )) as [V15Payload, V15Payload, V15Payload];

      if (!validatePayloads(a, b, c)) {
        throw new Error(
          "V15 result files are incompatible."
        );
      }

      const normalized = normalizeEvents(a, b, c);

      setEvents(normalized);
      setSource("V15_JSON");
      setVisibleCount(4);
      setSelectedId(null);
    } catch {
      setEvents(DEMO_EVENTS);
      setSource("DEMO");
      setVisibleCount(4);
      setSelectedId(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void loadData();
  }, []);

  useEffect(() => {
    if (paused) return;

    const timer = window.setInterval(() => {
      setVisibleCount((current) =>
        Math.min(events.length, current + 1)
      );
    }, 1200);

    return () => window.clearInterval(timer);
  }, [paused, events.length]);

  const visibleEvents = useMemo(
    () => events.slice(0, visibleCount),
    [events, visibleCount]
  );

  const stats = useMemo(() => {
    const priorities = {
      P1: 0,
      P2: 0,
      P3: 0,
      P4: 0,
    };

    let reviews = 0;
    let approvals = 0;

    for (const event of visibleEvents) {
      if (event.final_priority in priorities) {
        priorities[
          event.final_priority as keyof typeof priorities
        ]++;
      }

      if (event.manual_review_required) reviews++;

      if (
        event.response_status ===
        "AWAITING_HUMAN_APPROVAL"
      ) {
        approvals++;
      }
    }

    const meanRisk = visibleEvents.length
      ? Math.round(
          visibleEvents.reduce(
            (total, e) => total + e.risk_score,
            0
          ) / visibleEvents.length
        )
      : 0;

    return {
      ...priorities,
      reviews,
      approvals,
      meanRisk,
    };
  }, [visibleEvents]);

  const selected = useMemo(
    () =>
      visibleEvents.find(
        (event) => event.event_id === selectedId
      ) ?? visibleEvents[0],
    [visibleEvents, selectedId]
  );

  return (
    <section
      style={{
        color: C.text,
        background: `
          radial-gradient(
            circle at 88% 0%,
            rgba(53, 68, 158, 0.23),
            transparent 38%
          ),
          ${C.bg}
        `,
        padding: "clamp(16px, 3vw, 30px)",
        borderRadius: 22,
        border: `1px solid ${C.border}`,
        fontFamily:
          "Inter, Segoe UI, Arial, sans-serif",
        marginTop: 24,
      }}
    >
      <style>
        {`
          @keyframes v15Pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.4; }
          }

          @keyframes v15Appear {
            from {
              opacity: 0;
              transform: translateY(12px);
            }
            to {
              opacity: 1;
              transform: translateY(0);
            }
          }

          .v15-event {
            animation: v15Appear 0.4s ease-out both;
          }

          .v15-event:hover {
            background: rgba(63, 172, 233, 0.12);
            cursor: pointer;
          }

          .v15-button {
            background: #133b61;
            border: 1px solid #397ab4;
            color: #d7f6ff;
            padding: 10px 13px;
            border-radius: 9px;
            display: inline-flex;
            align-items: center;
            gap: 7px;
            cursor: pointer;
            font-weight: 700;
            font-size: 12px;
          }

          .v15-button:hover {
            background: #205a8a;
          }

          .v15-table {
            width: 100%;
            min-width: 850px;
            border-collapse: collapse;
            font-size: 12px;
          }

          .v15-table th {
            text-align: left;
            color: #9ebbd4;
            padding: 13px 12px;
            border-bottom: 1px solid #345675;
            font-size: 10px;
            letter-spacing: 0.9px;
          }

          .v15-table td {
            padding: 13px 12px;
            border-bottom: 1px solid #24415b;
          }

          .v15-grid {
            display: grid;
            grid-template-columns:
              repeat(auto-fit, minmax(155px, 1fr));
            gap: 13px;
          }

          .v15-two {
            display: grid;
            grid-template-columns:
              repeat(auto-fit, minmax(260px, 1fr));
            gap: 15px;
          }
        `}
      </style>

      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 16,
          marginBottom: 24,
        }}
      >
        <div>
          <div
            style={{
              color: C.cyan,
              fontSize: 11,
              fontWeight: 800,
              letterSpacing: 3,
              marginBottom: 10,
            }}
          >
            QUANTUM CYBER DEFENSE ARENA
          </div>

          <h2
            style={{
              fontSize: "clamp(24px, 3vw, 35px)",
              margin: "0 0 8px",
              color: C.text,
            }}
          >
            <Zap
              size={27}
              color={C.cyan}
              style={{
                verticalAlign: "middle",
                marginRight: 10,
              }}
            />
            V15.4 Live Command Center
          </h2>

          <p
            style={{
              color: C.muted,
              margin: 0,
              fontSize: 13,
            }}
          >
            Intelligent Threat Orchestration ·
            Multi-Agent Decisions ·
            Autonomous Response Simulation
          </p>
        </div>

        <div
          style={{
            display: "flex",
            gap: 8,
            flexWrap: "wrap",
            alignItems: "center",
          }}
        >
          <StatusPill
            color={
              source === "V15_JSON"
                ? C.green
                : C.yellow
            }
          >
            {source === "V15_JSON"
              ? "V15 JSON LOADED"
              : "SAMPLE DEMO DATA"}
          </StatusPill>

          <button
            className="v15-button"
            onClick={() => setPaused((v) => !v)}
          >
            {paused ? (
              <Play size={15} />
            ) : (
              <Pause size={15} />
            )}
            {paused ? "RESUME" : "PAUSE"}
          </button>

          <button
            className="v15-button"
            disabled={loading}
            onClick={() => void loadData()}
          >
            <RefreshCw size={15} />
            {loading ? "LOADING" : "REFRESH"}
          </button>
        </div>
      </div>

      <ResearchPipeline />

      <div
        className="v15-grid"
        style={{ marginBottom: 18 }}
      >
        <Metric
          title="EVENTS ANALYZED"
          value={fmt(visibleEvents.length)}
          color={C.cyan}
        />

        <Metric
          title="P1 CRITICAL"
          value={stats.P1}
          color={C.red}
        />

        <Metric
          title="P2 HIGH"
          value={stats.P2}
          color={C.yellow}
        />

        <Metric
          title="MANUAL REVIEWS"
          value={stats.reviews}
          color={C.purple}
        />

        <Metric
          title="AWAITING APPROVAL"
          value={stats.approvals}
          color={C.green}
        />
      </div>

      <div
        className="v15-two"
        style={{ marginBottom: 18 }}
      >
        <div style={panelStyle}>
          <h3
            style={{
              margin: "0 0 10px",
              fontSize: 17,
            }}
          >
            <Activity
              size={18}
              color={C.cyan}
              style={{ verticalAlign: "middle" }}
            />{" "}
            Risk Distribution
          </h3>

          <p
            style={{
              color: C.muted,
              fontSize: 12,
            }}
          >
            Priority distribution across displayed
            research events
          </p>

          {(
            [
              ["P1 CRITICAL", stats.P1, C.red],
              ["P2 HIGH", stats.P2, C.yellow],
              ["P3 REVIEW", stats.P3, C.purple],
              ["P4 NORMAL", stats.P4, C.green],
            ] as const
          ).map(([label, count, color]) => (
            <div
              key={label}
              style={{ marginTop: 18 }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: 7,
                  fontSize: 12,
                }}
              >
                <span>{label}</span>
                <strong style={{ color }}>
                  {count}
                </strong>
              </div>

              <div
                style={{
                  height: 12,
                  borderRadius: 9,
                  background: "#19344d",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${
                      visibleEvents.length
                        ? (count /
                            visibleEvents.length) *
                          100
                        : 0
                    }%`,
                    height: "100%",
                    background: color,
                    transition: "width 0.8s ease",
                    boxShadow: `0 0 14px ${color}`,
                  }}
                />
              </div>
            </div>
          ))}
        </div>

        <div style={panelStyle}>
          <h3
            style={{
              margin: "0 0 10px",
              fontSize: 17,
            }}
          >
            <Shield
              size={18}
              color={C.green}
              style={{ verticalAlign: "middle" }}
            />{" "}
            Response Control
          </h3>

          <div
            style={{
              fontSize: 11,
              letterSpacing: 1,
              color: C.muted,
              marginTop: 24,
            }}
          >
            AVERAGE RISK SCORE
          </div>

          <div
            style={{
              fontSize: 48,
              fontWeight: 900,
              color: C.cyan,
              margin: "8px 0 18px",
            }}
          >
            {stats.meanRisk}
            <span
              style={{
                fontSize: 18,
                color: C.muted,
              }}
            >
              /100
            </span>
          </div>

          <StatusPill color={C.yellow}>
            SIMULATION ONLY
          </StatusPill>

          <p
            style={{
              color: C.muted,
              fontSize: 12,
              lineHeight: 1.8,
              marginTop: 18,
            }}
          >
            Response actions are proposed or
            simulated. No live firewall rules,
            blockchain transactions or external
            systems are modified.
          </p>
        </div>
      </div>

      <div
        style={{
          ...panelStyle,
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 10,
          }}
        >
          <h3 style={{ margin: 0 }}>
            <Activity
              size={18}
              color={C.cyan}
              style={{
                verticalAlign: "middle",
                marginRight: 8,
              }}
            />
            V15 Research Event Stream
          </h3>

          <StatusPill color={C.cyan}>
            {paused
              ? "DISPLAY PAUSED"
              : "ANIMATED PLAYBACK"}
          </StatusPill>
        </div>

        <p
          style={{
            color: C.muted,
            fontSize: 12,
            marginBottom: 17,
          }}
        >
          Historical JSON event playback, not
          live threat collection. Select an event
          to inspect the three-stage result.
        </p>

        <div style={{ overflowX: "auto" }}>
          <table className="v15-table">
            <thead>
              <tr>
                <th>EVENT ID</th>
                <th>NETWORK</th>
                <th>RISK</th>
                <th>HYBRID</th>
                <th>AGENT DECISION</th>
                <th>PRIORITY</th>
                <th>RESPONSE STATUS</th>
              </tr>
            </thead>

            <tbody>
              {visibleEvents.map((event, index) => (
                <tr
                  key={event.event_id}
                  className="v15-event"
                  onClick={() =>
                    setSelectedId(event.event_id)
                  }
                  style={{
                    animationDelay: `${Math.min(
                      index * 30,
                      500
                    )}ms`,
                    background:
                      selected?.event_id ===
                      event.event_id
                        ? "rgba(44,141,205,0.12)"
                        : "transparent",
                  }}
                >
                  <td
                    style={{
                      fontFamily: "monospace",
                      color: C.cyan,
                    }}
                  >
                    {event.event_id}
                  </td>

                  <td>{event.network}</td>

                  <td
                    style={{
                      color: severityColor(
                        event.final_priority
                      ),
                      fontWeight: 800,
                    }}
                  >
                    {event.risk_score}/100
                  </td>

                  <td>{event.hybrid_decision}</td>

                  <td>{event.final_decision}</td>

                  <td
                    style={{
                      color: severityColor(
                        event.final_priority
                      ),
                      fontWeight: 900,
                    }}
                  >
                    {event.final_priority}
                  </td>

                  <td
                    style={{
                      color:
                        event.response_status ===
                        "AWAITING_HUMAN_APPROVAL"
                          ? C.yellow
                          : C.green,
                    }}
                  >
                    {event.response_status}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selected && (
        <div
          className="v15-two"
          style={{ marginBottom: 18 }}
        >
          <div style={panelStyle}>
            <h3
              style={{
                display: "flex",
                gap: 8,
                alignItems: "center",
              }}
            >
              <BrainCircuit
                size={19}
                color={C.purple}
              />
              Multi-Agent Decision Inspector
            </h3>

            <p
              style={{
                color: C.muted,
                fontSize: 12,
              }}
            >
              Event: {selected.event_id}
            </p>

            <p>
              <strong>Hybrid decision:</strong>{" "}
              {selected.hybrid_decision}
            </p>

            <p>
              <strong>Final decision:</strong>{" "}
              {selected.final_decision}
            </p>

            <p>
              <strong>Consensus:</strong>{" "}
              <span
                style={{
                  color: C.purple,
                  overflowWrap: "anywhere",
                }}
              >
                {selected.consensus}
              </span>
            </p>

            <p>
              <strong>Manual review:</strong>{" "}
              {selected.manual_review_required
                ? "REQUIRED"
                : "NOT REQUIRED"}
            </p>
          </div>

          <div style={panelStyle}>
            <h3
              style={{
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <ShieldAlert
                size={19}
                color={C.yellow}
              />
              Autonomous Response Inspector
            </h3>

            <p
              style={{
                color: C.muted,
                fontSize: 12,
              }}
            >
              Selected research incident
            </p>

            <p>
              <strong>Priority:</strong>{" "}
              <span
                style={{
                  color: severityColor(
                    selected.final_priority
                  ),
                }}
              >
                {selected.final_priority}
              </span>
            </p>

            <p>
              <strong>Planned action:</strong>{" "}
              {selected.planned_action}
            </p>

            <p>
              <strong>Status:</strong>{" "}
              {selected.response_status}
            </p>

            <p>
              <strong>External execution:</strong>{" "}
              <span style={{ color: C.green }}>
                NONE
              </span>
            </p>
          </div>
        </div>
      )}

      <div
        style={{
          ...panelStyle,
          borderColor: `${C.yellow}66`,
        }}
      >
        <h3
          style={{
            margin: "0 0 12px",
            display: "flex",
            alignItems: "center",
            gap: 8,
          }}
        >
          <AlertTriangle
            size={18}
            color={C.yellow}
          />
          Research Data Integrity
        </h3>

        <div
          style={{
            display: "flex",
            gap: 12,
            flexWrap: "wrap",
            marginBottom: 12,
          }}
        >
          {source === "V15_JSON" ? (
            <StatusPill color={C.green}>
              <FileJson size={13} />
              V15.1–V15.3 FILES VALIDATED
            </StatusPill>
          ) : (
            <StatusPill color={C.yellow}>
              <AlertTriangle size={13} />
              ILLUSTRATIVE SAMPLE DATA
            </StatusPill>
          )}

          <StatusPill color={C.green}>
            <CheckCircle2 size={13} />
            NO EXTERNAL ACTIONS
          </StatusPill>
        </div>

        <p
          style={{
            color: C.muted,
            fontSize: 12,
            lineHeight: 1.8,
            margin: 0,
          }}
        >
          {source === "V15_JSON"
            ? "The panel displays saved results from the V15.1, V15.2 and V15.3 research simulation pipeline. Animation replays stored events and does not represent real-time detections."
            : "The original V15 JSON exports have not yet been placed in frontend/public/v15, or could not be validated. The panel is therefore showing explicitly labeled illustrative data."}
        </p>
      </div>

      <div
        style={{
          textAlign: "center",
          color: C.muted,
          marginTop: 20,
          fontSize: 11,
          letterSpacing: 1,
        }}
      >
        QUANTUM CYBER DEFENSE ARENA · V15.4
        LIVE COMMAND CENTER · RESEARCH PROTOTYPE
      </div>
    </section>
  );
}
