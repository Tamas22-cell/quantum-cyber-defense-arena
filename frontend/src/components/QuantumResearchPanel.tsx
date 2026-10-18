
import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  Atom,
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

const API_BASE = "http://127.0.0.1:8000";

type JsonRecord = Record<string, unknown>;

type MetricStats = {
  mean: number;
  std: number;
  min: number;
  max: number;
};

type ModelSummary = Record<string, MetricStats>;

type BenchmarkData = {
  version: string;
  quantum: {
    model: string;
    summary: ModelSummary;
  };
  classical: {
    model: string;
    summary: ModelSummary;
  };
};

type StatisticalComparison = {
  sample_size: number;
  quantum_mean: number;
  classical_mean: number;
  mean_difference: number;
  confidence_interval_95: {
    lower: number;
    upper: number;
  };
  paired_t_test: {
    p_value: number | null;
  };
  wilcoxon_signed_rank: {
    p_value: number | null;
  };
  quantum_wins: number;
  classical_wins: number;
  ties: number;
};

type StatisticsData = {
  version: string;
  f1_score: StatisticalComparison;
  runtime: {
    quantum_mean_ms: number;
    classical_mean_ms: number;
    quantum_to_classical_ratio: number | null;
  };
};

function isRecord(value: unknown): value is JsonRecord {
  return (
    typeof value === "object" &&
    value !== null &&
    !Array.isArray(value)
  );
}

function isBenchmark(value: unknown): value is BenchmarkData {
  if (!isRecord(value)) return false;

  const quantum = value.quantum;
  const classical = value.classical;

  return (
    isRecord(quantum) &&
    isRecord(classical) &&
    isRecord(quantum.summary) &&
    isRecord(classical.summary)
  );
}

function isStatistics(value: unknown): value is StatisticsData {
  if (!isRecord(value)) return false;

  const f1 = value.f1_score;
  const runtime = value.runtime;

  return (
    isRecord(f1) &&
    isRecord(runtime) &&
    isRecord(f1.confidence_interval_95) &&
    isRecord(f1.paired_t_test) &&
    typeof f1.mean_difference === "number"
  );
}

function pct(value: number | undefined): string {
  return typeof value === "number" && Number.isFinite(value)
    ? `${(value * 100).toFixed(2)}%`
    : "—";
}

function metricMean(
  summary: ModelSummary,
  key: string
): number | undefined {
  return summary[key]?.mean;
}

function MetricCard({
  label,
  value,
  subtitle,
  color,
}: {
  label: string;
  value: string;
  subtitle: string;
  color: string;
}) {
  return (
    <div
      style={{
        padding: 17,
        borderRadius: 13,
        border: "1px solid rgba(108,188,255,.29)",
        background: "rgba(8,28,63,.6)",
      }}
    >
      <div
        style={{
          fontSize: 11,
          letterSpacing: 1,
          fontWeight: 750,
          color: "#b5cce5",
        }}
      >
        {label}
      </div>

      <div
        style={{
          margin: "13px 0 6px",
          fontWeight: 800,
          fontSize: 27,
          color,
        }}
      >
        {value}
      </div>

      <div style={{ fontSize: 11, color: "#9bb6d2" }}>
        {subtitle}
      </div>
    </div>
  );
}

export default function QuantumResearchPanel() {
  const [benchmark, setBenchmark] =
    useState<BenchmarkData | null>(null);
  const [statistics, setStatistics] =
    useState<StatisticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [refreshIndex, setRefreshIndex] = useState(0);

  useEffect(() => {
    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError("");

      try {
        const [benchmarkResponse, statisticsResponse] =
          await Promise.all([
            fetch(`${API_BASE}/api/quantum/benchmark`, {
              signal: controller.signal,
            }),
            fetch(`${API_BASE}/api/quantum/statistics`, {
              signal: controller.signal,
            }),
          ]);

        if (!benchmarkResponse.ok) {
          throw new Error(
            `Benchmark API: HTTP ${benchmarkResponse.status}`
          );
        }

        if (!statisticsResponse.ok) {
          throw new Error(
            `Statistics API: HTTP ${statisticsResponse.status}`
          );
        }

        const benchmarkJSON: unknown =
          await benchmarkResponse.json();

        const statisticsJSON: unknown =
          await statisticsResponse.json();

        if (
          !isBenchmark(benchmarkJSON) ||
          !isStatistics(statisticsJSON)
        ) {
          throw new Error("Unexpected quantum API response");
        }

        setBenchmark(benchmarkJSON);
        setStatistics(statisticsJSON);
      } catch (err) {
        if (controller.signal.aborted) return;

        setError(
          err instanceof Error
            ? err.message
            : "Unknown quantum research API error"
        );
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    void load();

    return () => controller.abort();
  }, [refreshIndex]);

  const q = benchmark?.quantum.summary;
  const c = benchmark?.classical.summary;
  const f1 = statistics?.f1_score;
  const runtime = statistics?.runtime;

  const chartData =
    q && c
      ? [
          {
            name: "Accuracy",
            Quantum: (metricMean(q, "accuracy") ?? 0) * 100,
            Classical: (metricMean(c, "accuracy") ?? 0) * 100,
          },
          {
            name: "Precision",
            Quantum: (metricMean(q, "precision") ?? 0) * 100,
            Classical: (metricMean(c, "precision") ?? 0) * 100,
          },
          {
            name: "Recall",
            Quantum: (metricMean(q, "recall") ?? 0) * 100,
            Classical: (metricMean(c, "recall") ?? 0) * 100,
          },
          {
            name: "F1-score",
            Quantum: (metricMean(q, "f1_score") ?? 0) * 100,
            Classical: (metricMean(c, "f1_score") ?? 0) * 100,
          },
        ]
      : [];

  return (
    <section
      style={{
        marginTop: 22,
        padding: 23,
        borderRadius: 18,
        border: "1px solid rgba(116,141,255,.48)",
        background:
          "linear-gradient(130deg,rgba(10,40,88,.96),rgba(55,34,112,.94))",
        boxShadow: "0 12px 42px rgba(0,0,0,.24)",
        color: "#eaf6ff",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          flexWrap: "wrap",
          gap: 14,
          marginBottom: 20,
        }}
      >
        <div>
          <h2
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              margin: 0,
              fontSize: 21,
            }}
          >
            <Atom size={24} color="#9fc7ff" />
            Quantum Research Dashboard V6.4
          </h2>

          <p style={{ fontSize: 12, color: "#aec7e4" }}>
            Quantum State Fidelity vs Isolation Forest
            · Research benchmark · Synthetic data
          </p>
        </div>

        <button
          onClick={() => setRefreshIndex((v) => v + 1)}
          disabled={loading}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 8,
            padding: "10px 14px",
            borderRadius: 9,
            background: "rgba(42,122,220,.22)",
            color: "#dcecff",
            border: "1px solid rgba(116,188,255,.45)",
            cursor: loading ? "wait" : "pointer",
          }}
        >
          <RefreshCw size={15} />
          {loading ? "Loading..." : "Refresh"}
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: 16,
            marginBottom: 18,
            borderRadius: 10,
            border: "1px solid rgba(255,112,143,.5)",
            background: "rgba(110,22,53,.2)",
            color: "#ffafc4",
          }}
        >
          <AlertTriangle size={17} style={{ verticalAlign: "middle" }} />
          {" "}Research API: {error}
        </div>
      )}

      {benchmark && statistics && q && c && f1 && (
        <>
          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(min(100%,180px),1fr))",
              gap: 13,
              marginBottom: 22,
            }}
          >
            <MetricCard
              label="QUANTUM F1"
              value={pct(metricMean(q, "f1_score"))}
              subtitle="Mean over benchmark experiments"
              color="#6becc9"
            />

            <MetricCard
              label="CLASSICAL F1"
              value={pct(metricMean(c, "f1_score"))}
              subtitle="Isolation Forest"
              color="#8bc5ff"
            />

            <MetricCard
              label="F1 DIFFERENCE"
              value={`${(f1.mean_difference * 100).toFixed(2)} pp`}
              subtitle="Quantum minus classical"
              color="#f4c46a"
            />

            <MetricCard
              label="PAIRED T-TEST"
              value={
                f1.paired_t_test.p_value === null
                  ? "N/A"
                  : f1.paired_t_test.p_value.toFixed(4)
              }
              subtitle="p-value, exploratory comparison"
              color="#c69dff"
            />
          </div>

          <div
            style={{
              padding: 17,
              borderRadius: 13,
              background: "rgba(7,25,57,.55)",
              border: "1px solid rgba(104,158,239,.24)",
              marginBottom: 18,
            }}
          >
            <h3
              style={{
                display: "flex",
                alignItems: "center",
                gap: 9,
                margin: "0 0 18px",
                fontSize: 16,
              }}
            >
              <Activity size={18} color="#65dcff" />
              Quantum vs Classical Performance
            </h3>

            <div style={{ width: "100%", height: 270 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <CartesianGrid
                    stroke="rgba(144,182,226,.15)"
                    vertical={false}
                  />
                  <XAxis
                    dataKey="name"
                    stroke="#a2bedb"
                    tick={{ fontSize: 11 }}
                  />
                  <YAxis
                    domain={[0, 100]}
                    stroke="#a2bedb"
                    tick={{ fontSize: 11 }}
                    unit="%"
                  />
                  <Tooltip
                    contentStyle={{
                      background: "#101e3b",
                      border: "1px solid #45618a",
                      borderRadius: 10,
                      color: "#e9f4ff",
                    }}
                  />
                  <Legend />
                  <Bar
                    dataKey="Quantum"
                    fill="#5eead4"
                    radius={[5, 5, 0, 0]}
                  />
                  <Bar
                    dataKey="Classical"
                    fill="#8ba9ff"
                    radius={[5, 5, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div
            style={{
              display: "grid",
              gridTemplateColumns:
                "repeat(auto-fit,minmax(min(100%,260px),1fr))",
              gap: 14,
            }}
          >
            <div style={{
              ...{
                padding: 18,
                borderRadius: 13,
                background: "rgba(7,25,57,.55)",
                border: "1px solid rgba(104,158,239,.24)",
              },
            }}>
              <h3 style={{ fontSize: 15, marginTop: 0 }}>
                <FlaskConical size={16} /> Statistical Validation
              </h3>

              <p>
                Quantum wins: <strong>{f1.quantum_wins}</strong>
                {" / "}
                {f1.sample_size}
              </p>

              <p>
                Classical wins: <strong>{f1.classical_wins}</strong>
              </p>

              <p>
                95% CI:
                {" "}
                <strong>
                  {(f1.confidence_interval_95.lower * 100).toFixed(2)}
                  {" to "}
                  {(f1.confidence_interval_95.upper * 100).toFixed(2)}
                  {" pp"}
                </strong>
              </p>

              <p>
                Wilcoxon p:
                {" "}
                <strong>
                  {statistics.f1_score.wilcoxon_signed_rank.p_value?.toFixed(4) ??
                    "N/A"}
                </strong>
              </p>

              <p style={{ fontSize: 11, color: "#9cb8d7" }}>
                Exploratory tests on synthetic samples.
              </p>
            </div>

            <div style={{
              padding: 18,
              borderRadius: 13,
              background: "rgba(7,25,57,.55)",
              border: "1px solid rgba(104,158,239,.24)",
            }}>
              <h3 style={{ fontSize: 15, marginTop: 0 }}>
                <Clock3 size={16} /> Runtime Comparison
              </h3>

              <p>
                Quantum:{" "}
                <strong>{runtime?.quantum_mean_ms.toFixed(2)} ms</strong>
              </p>

              <p>
                Classical:{" "}
                <strong>{runtime?.classical_mean_ms.toFixed(2)} ms</strong>
              </p>

              <p>
                Runtime ratio:{" "}
                <strong>
                  {runtime?.quantum_to_classical_ratio?.toFixed(1) ?? "—"}x
                </strong>
              </p>

              <p style={{ fontSize: 11, color: "#9cb8d7" }}>
                CPU-based Statevector simulation; not QPU hardware.
              </p>
            </div>
          </div>

          <p
            style={{
              marginTop: 17,
              marginBottom: 0,
              color: "#a8bfd8",
              textAlign: "center",
              fontSize: 11,
            }}
          >
            <CheckCircle2
              size={13}
              style={{ verticalAlign: "middle" }}
            />
            {" "}V6.4 Research Mode · Reproducible synthetic
            experiments · No verified quantum advantage
          </p>
        </>
      )}
    </section>
  );
}
