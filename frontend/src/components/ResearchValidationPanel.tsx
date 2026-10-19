
import { useCallback, useEffect, useState } from "react";
import type { CSSProperties } from "react";

import {
  Activity,
  AlertTriangle,
  Atom,
  BarChart3,
  BrainCircuit,
  CheckCircle2,
  Clock3,
  FlaskConical,
  RefreshCw,
} from "lucide-react";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

type Metrics = {
  accuracy: number;
  precision: number;
  recall: number;
  f1: number;
};

type Comparison = {
  classical_f1: number;
  quantum_f1: number;
  hybrid_f1: number;
  differences: {
    quantum_vs_classical_pp: number;
    hybrid_vs_classical_pp: number;
    hybrid_vs_quantum_pp: number;
  };
};

type ConfidenceInterval = {
  model_a: string;
  model_b: string;
  f1_difference_pp: number;
  ci_95_lower_pp: number;
  ci_95_upper_pp: number;
  excludes_zero: boolean;
};

type StatisticalResults = {
  version: string;
  mode: string;
  model_comparison: Comparison;
  confidence_intervals: ConfidenceInterval[];
  hybrid_reviews: {
    review_count: number;
    review_rate_percent: number;
    decisive_coverage_percent: number;
  };
  runtime: {
    classical_ms_per_event: number;
    quantum_plus_fusion_ms_per_event: number;
  };
};

type BenchmarkResults = {
  version: string;
  summary: {
    sample_count: number;
    classical: Metrics;
    quantum: Metrics;
    hybrid_conservative: Metrics;
  };
};

const STATS_URL =
  "http://127.0.0.1:8000/api/research/v10-2";

const BENCHMARK_URL =
  "http://127.0.0.1:8000/api/research/v10-1";

const COLORS = {
  cyan: "#67e8f9",
  blue: "#38bdf8",
  purple: "#c084fc",
  green: "#34d399",
  yellow: "#facc15",
  orange: "#fb923c",
  red: "#fb7185",
};

const panelStyle: CSSProperties = {
  background:
    "linear-gradient(145deg, #102543, #10172e)",
  border: "1px solid rgba(103,232,249,0.24)",
  borderRadius: 18,
  padding: 20,
  minWidth: 0,
};

function percent(value: number): string {
  return `${(value * 100).toFixed(2)}%`;
}

function MetricCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color: string;
}) {
  return (
    <div style={panelStyle}>
      <div
        style={{
          color,
          fontSize: 11,
          fontWeight: 800,
          letterSpacing: 1,
        }}
      >
        {label}
      </div>

      <div
        style={{
          color: "#f8fafc",
          fontSize: 29,
          fontWeight: 800,
          marginTop: 14,
        }}
      >
        {value}
      </div>
    </div>
  );
}

export default function ResearchValidationPanel() {
  const [stats, setStats] =
    useState<StatisticalResults | null>(null);

  const [benchmark, setBenchmark] =
    useState<BenchmarkResults | null>(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);

    try {
      const [statsResponse, benchmarkResponse] =
        await Promise.all([
          fetch(STATS_URL, { cache: "no-store" }),
          fetch(BENCHMARK_URL, { cache: "no-store" }),
        ]);

      if (!statsResponse.ok || !benchmarkResponse.ok) {
        throw new Error(
          `Research API unavailable: ${statsResponse.status} / ${benchmarkResponse.status}`
        );
      }

      const statsJson =
        (await statsResponse.json()) as StatisticalResults;

      const benchmarkJson =
        (await benchmarkResponse.json()) as BenchmarkResults;

      if (
        !statsJson.model_comparison ||
        !benchmarkJson.summary
      ) {
        throw new Error("Invalid research results format");
      }

      setStats(statsJson);
      setBenchmark(benchmarkJson);
      setError(null);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unknown research API error"
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadData();
  }, [loadData]);

  const models = benchmark
    ? [
        {
          name: "Classical",
          color: COLORS.blue,
          ...benchmark.summary.classical,
        },
        {
          name: "Quantum",
          color: COLORS.purple,
          ...benchmark.summary.quantum,
        },
        {
          name: "Hybrid",
          color: COLORS.green,
          ...benchmark.summary.hybrid_conservative,
        },
      ]
    : [];

  const chartData = models.map((model) => ({
    name: model.name,
    Accuracy: Number((model.accuracy * 100).toFixed(2)),
    Precision: Number((model.precision * 100).toFixed(2)),
    Recall: Number((model.recall * 100).toFixed(2)),
    F1: Number((model.f1 * 100).toFixed(2)),
  }));

  return (
    <section
      style={{
        width: "100%",
        padding: "28px 0",
        color: "#e2e8f0",
      }}
    >
      <div
        style={{
          ...panelStyle,
          background:
            "linear-gradient(110deg, #0a2b45, #172045 60%, #302047)",
          borderColor: "#4d609d",
          marginBottom: 18,
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
            flexWrap: "wrap",
            gap: 14,
          }}
        >
          <div>
            <div
              style={{
                color: COLORS.cyan,
                fontSize: 11,
                fontWeight: 800,
                letterSpacing: 2,
                marginBottom: 9,
              }}
            >
              QUANTUM CYBER DEFENSE ARENA · V10.3
            </div>

            <h2
              style={{
                display: "flex",
                alignItems: "center",
                gap: 11,
                fontSize: "clamp(20px, 3vw, 29px)",
                margin: 0,
              }}
            >
              <FlaskConical
                size={29}
                color={COLORS.purple}
              />
              RESEARCH VALIDATION LAB
            </h2>

            <p
              style={{
                color: "#94a3b8",
                fontSize: 12,
                marginBottom: 0,
              }}
            >
              Classical vs Quantum vs Hybrid ·
              Overlapping Synthetic Benchmark
            </p>
          </div>

          <button
            type="button"
            onClick={() => void loadData()}
            style={{
              display: "flex",
              alignItems: "center",
              gap: 8,
              cursor: "pointer",
              background: "#175a81",
              border: "1px solid #4cc9f0",
              color: "white",
              borderRadius: 9,
              padding: "10px 14px",
              fontWeight: 800,
            }}
          >
            <RefreshCw size={16} />
            REFRESH
          </button>
        </div>

        <div
          style={{
            color: "#94a3b8",
            fontSize: 11,
            marginTop: 18,
          }}
        >
          <Activity
            size={14}
            style={{
              display: "inline",
              marginRight: 7,
              color: error ? COLORS.red : COLORS.green,
            }}
          />
          {error
            ? "RESEARCH API ERROR"
            : stats
            ? "RESEARCH DATA CONNECTED"
            : "CONNECTING"}
        </div>
      </div>

      {loading && (
        <div style={panelStyle}>
          Loading V10 research results...
        </div>
      )}

      {error && (
        <div
          style={{
            ...panelStyle,
            color: COLORS.red,
            borderColor: COLORS.red,
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
          {error}
        </div>
      )}

      {stats && benchmark && (
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
            <MetricCard
              label="CLASSICAL F1"
              value={percent(
                benchmark.summary.classical.f1
              )}
              color={COLORS.blue}
            />

            <MetricCard
              label="QUANTUM F1"
              value={percent(
                benchmark.summary.quantum.f1
              )}
              color={COLORS.purple}
            />

            <MetricCard
              label="HYBRID F1"
              value={percent(
                benchmark.summary.hybrid_conservative.f1
              )}
              color={COLORS.green}
            />

            <MetricCard
              label="TEST EVENTS"
              value={String(
                benchmark.summary.sample_count
              )}
              color={COLORS.cyan}
            />

            <MetricCard
              label="REVIEW RATE"
              value={`${stats.hybrid_reviews.review_rate_percent.toFixed(2)}%`}
              color={COLORS.yellow}
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
              <BarChart3
                size={21}
                color={COLORS.cyan}
              />
              MODEL PERFORMANCE COMPARISON
            </h3>

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
                <BarChart data={chartData}>
                  <CartesianGrid
                    stroke="#47556955"
                    strokeDasharray="4 4"
                  />

                  <XAxis
                    dataKey="name"
                    stroke="#94a3b8"
                  />

                  <YAxis
                    domain={[0, 100]}
                    stroke="#94a3b8"
                  />

                  <Tooltip
                    contentStyle={{
                      background: "#0b1e35",
                      border: "1px solid #406083",
                      borderRadius: 10,
                    }}
                  />

                  <Legend />

                  <Bar
                    dataKey="Accuracy"
                    fill={COLORS.blue}
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="Precision"
                    fill={COLORS.purple}
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="Recall"
                    fill={COLORS.cyan}
                    radius={[4, 4, 0, 0]}
                  />

                  <Bar
                    dataKey="F1"
                    fill={COLORS.green}
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit, minmax(min(100%, 340px), 1fr))",
              gap: 16,
              marginBottom: 18,
            }}
          >
            <div style={panelStyle}>
              <h3>
                <BrainCircuit
                  size={19}
                  style={{
                    display: "inline",
                    marginRight: 9,
                    color: COLORS.purple,
                  }}
                />
                F1 DIFFERENCE
              </h3>

              <p style={{ color: "#cbd5e1" }}>
                Quantum vs Classical
              </p>

              <div
                style={{
                  fontSize: 30,
                  color: COLORS.green,
                  fontWeight: 800,
                }}
              >
                +
                {stats.model_comparison.differences
                  .quantum_vs_classical_pp.toFixed(2)}
                {" pp"}
              </div>

              <p
                style={{
                  color: "#94a3b8",
                  fontSize: 12,
                }}
              >
                Percentage-point difference on this
                synthetic dataset.
              </p>
            </div>

            <div style={panelStyle}>
              <h3>
                <Clock3
                  size={19}
                  style={{
                    display: "inline",
                    marginRight: 9,
                    color: COLORS.cyan,
                  }}
                />
                INFERENCE RUNTIME
              </h3>

              <p style={{ fontSize: 12 }}>
                Classical AI:{" "}
                <strong>
                  {stats.runtime.classical_ms_per_event.toFixed(3)}
                  {" ms"}
                </strong>
              </p>

              <p style={{ fontSize: 12 }}>
                Quantum + Fusion:{" "}
                <strong>
                  {stats.runtime.quantum_plus_fusion_ms_per_event.toFixed(3)}
                  {" ms"}
                </strong>
              </p>

              <p
                style={{
                  color: "#94a3b8",
                  fontSize: 11,
                }}
              >
                Different operations were timed;
                this is not evidence of quantum speedup.
              </p>
            </div>
          </div>

          <div
            style={{
              ...panelStyle,
              marginBottom: 18,
            }}
          >
            <h3>
              <Atom
                size={20}
                style={{
                  display: "inline",
                  marginRight: 9,
                  color: COLORS.purple,
                }}
              />
              95% BOOTSTRAP CONFIDENCE INTERVALS
            </h3>

            {stats.confidence_intervals.map(
              (item, index) => (
                <div
                  key={`${item.model_a}-${item.model_b}-${index}`}
                  style={{
                    padding: "14px 0",
                    borderBottom:
                      "1px solid #334155",
                  }}
                >
                  <div
                    style={{
                      fontSize: 13,
                      fontWeight: 800,
                      color: COLORS.cyan,
                    }}
                  >
                    {item.model_a}
                    {" vs "}
                    {item.model_b}
                  </div>

                  <div
                    style={{
                      marginTop: 8,
                      fontSize: 13,
                    }}
                  >
                    Difference:{" "}
                    <strong>
                      {item.f1_difference_pp.toFixed(3)}
                      {" pp"}
                    </strong>
                  </div>

                  <div
                    style={{
                      marginTop: 5,
                      fontSize: 13,
                    }}
                  >
                    95% CI:{" "}
                    {item.ci_95_lower_pp.toFixed(3)}
                    {" to "}
                    {item.ci_95_upper_pp.toFixed(3)}
                    {" pp"}
                  </div>

                  <div
                    style={{
                      marginTop: 7,
                      fontSize: 11,
                      color: item.excludes_zero
                        ? COLORS.green
                        : COLORS.yellow,
                    }}
                  >
                    {item.excludes_zero
                      ? "Interval excludes zero"
                      : "Interval includes zero"}
                  </div>
                </div>
              )
            )}
          </div>

          <div
            style={{
              ...panelStyle,
              display: "flex",
              gap: 13,
              alignItems: "flex-start",
            }}
          >
            <CheckCircle2
              size={22}
              color={COLORS.yellow}
            />
            <div
              style={{
                fontSize: 12,
                color: "#94a3b8",
                lineHeight: 1.7,
              }}
            >
              RESEARCH SIMULATION ONLY. All results
              come from synthetic labeled events.
              Bootstrap confidence intervals do not
              establish real-world generalization,
              and quantum calculations were simulated.
              No quantum computational advantage
              has been demonstrated.
            </div>
          </div>
        </>
      )}
    </section>
  );
}
