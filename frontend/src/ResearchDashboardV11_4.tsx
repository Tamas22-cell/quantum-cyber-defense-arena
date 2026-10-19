
import React, { useState } from "react";

type ModelResult = {
  name: string;
  f1: number;
  std: number;
  color: string;
  description: string;
};

const models: ModelResult[] = [
  {
    name: "Hybrid Fusion",
    f1: 94.06,
    std: 0.0169,
    color: "#21e6b1",
    description: "Hybrid quantum-classical threat detection",
  },
  {
    name: "Quantum AI",
    f1: 93.91,
    std: 0.0174,
    color: "#a78bfa",
    description: "Quantum state fidelity simulation",
  },
  {
    name: "Classical AI",
    f1: 73.57,
    std: 0.0122,
    color: "#38bdf8",
    description: "Classical anomaly detection",
  },
];

const comparisons = [
  {
    name: "Hybrid vs Classical",
    difference: "+20.4891 pp",
    p: "0.00015",
    significant: true,
  },
  {
    name: "Hybrid vs Quantum",
    difference: "+0.1446 pp",
    p: "0.00435",
    significant: true,
  },
  {
    name: "Quantum vs Classical",
    difference: "+20.3445 pp",
    p: "0.00015",
    significant: true,
  },
];

const panel: React.CSSProperties = {
  background:
    "linear-gradient(145deg, rgba(17,27,51,.96), rgba(9,16,34,.98))",
  border: "1px solid rgba(125,160,220,.19)",
  borderRadius: 22,
  padding: 24,
  boxShadow: "0 18px 50px rgba(0,0,0,.22)",
};

const buttonStyle = (
  active: boolean
): React.CSSProperties => ({
  border: active
    ? "1px solid #38bdf8"
    : "1px solid #334155",
  background: active ? "#123954" : "#111c33",
  color: active ? "#e0f2fe" : "#94a3b8",
  padding: "10px 18px",
  borderRadius: 11,
  cursor: "pointer",
  fontWeight: 700,
});

export default function ResearchDashboardV11_4() {
  const [view, setView] = useState<
    "performance" | "statistics"
  >("performance");

  const [selected, setSelected] = useState("Hybrid Fusion");

  const selectedModel =
    models.find((m) => m.name === selected) ?? models[0];

  return (
    <section
      style={{
        width: "100%",
        minHeight: "100vh",
        boxSizing: "border-box",
        padding: "36px 20px 60px",
        color: "#e2e8f0",
        fontFamily:
          "Inter, system-ui, -apple-system, sans-serif",
        background:
          "radial-gradient(ellipse at 12% 5%, #142c51 0%, transparent 45%), radial-gradient(ellipse at 90% 20%, #241446 0%, transparent 40%), #060b18",
      }}
    >
      <div
        style={{
          maxWidth: 1250,
          margin: "0 auto",
          display: "grid",
          gap: 25,
        }}
      >
        <header>
          <div
            style={{
              color: "#22d3ee",
              letterSpacing: 3,
              fontSize: 12,
              fontWeight: 800,
              marginBottom: 12,
            }}
          >
            QUANTUM CYBER DEFENSE ARENA
          </div>

          <h1
            style={{
              fontSize: "clamp(28px, 5vw, 48px)",
              lineHeight: 1.12,
              margin: "0 0 14px",
              background:
                "linear-gradient(90deg,#ffffff,#9dd6ff,#ad9aff)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
            }}
          >
            Advanced Research Dashboard
          </h1>

          <p
            style={{
              color: "#94a3b8",
              lineHeight: 1.7,
              maxWidth: 760,
            }}
          >
            V11.4 — Research visualization based on
            V11.3 statistical validation and 30 synthetic
            benchmark runs.
          </p>
        </header>

        <div
          style={{
            display: "grid",
            gridTemplateColumns:
              "repeat(auto-fit, minmax(200px, 1fr))",
            gap: 15,
          }}
        >
          {[
            ["30", "BENCHMARK RUNS", "#38bdf8"],
            ["6,000", "TEST EVALUATIONS", "#a78bfa"],
            ["94.06%", "BEST MEAN F1", "#21e6b1"],
            ["PASS", "QUALITY CHECK", "#fbbf24"],
          ].map(([value, label, color]) => (
            <div key={label} style={panel}>
              <div
                style={{
                  color,
                  fontSize: 32,
                  fontWeight: 800,
                }}
              >
                {value}
              </div>
              <div
                style={{
                  color: "#94a3b8",
                  fontSize: 11,
                  letterSpacing: 1.6,
                  marginTop: 9,
                  fontWeight: 700,
                }}
              >
                {label}
              </div>
            </div>
          ))}
        </div>

        <nav
          style={{
            display: "flex",
            gap: 10,
            flexWrap: "wrap",
          }}
        >
          <button
            type="button"
            style={buttonStyle(view === "performance")}
            onClick={() => setView("performance")}
          >
            Model Performance
          </button>

          <button
            type="button"
            style={buttonStyle(view === "statistics")}
            onClick={() => setView("statistics")}
          >
            Statistical Validation
          </button>
        </nav>

        {view === "performance" ? (
          <>
            <div style={panel}>
              <h2 style={{ marginTop: 0 }}>
                Mean F1 Performance
              </h2>
              <p style={{ color: "#94a3b8" }}>
                Higher F1 indicates a better
                precision-recall balance on the
                tested synthetic datasets.
              </p>

              <div
                style={{
                  display: "grid",
                  gap: 28,
                  marginTop: 32,
                }}
              >
                {models.map((model) => (
                  <div key={model.name}>
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        gap: 12,
                        marginBottom: 10,
                      }}
                    >
                      <strong>{model.name}</strong>
                      <strong style={{ color: model.color }}>
                        {model.f1.toFixed(2)}%
                      </strong>
                    </div>

                    <div
                      style={{
                        height: 17,
                        borderRadius: 20,
                        background: "#1e293b",
                        overflow: "hidden",
                      }}
                    >
                      <div
                        style={{
                          width: `${model.f1}%`,
                          height: "100%",
                          borderRadius: 20,
                          background: `linear-gradient(90deg,${model.color}75,${model.color})`,
                          boxShadow: `0 0 20px ${model.color}55`,
                          transition: "width .5s ease",
                        }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div style={panel}>
              <h2 style={{ marginTop: 0 }}>
                Model Inspector
              </h2>

              <div
                style={{
                  display: "flex",
                  gap: 10,
                  flexWrap: "wrap",
                  marginBottom: 25,
                }}
              >
                {models.map((model) => (
                  <button
                    type="button"
                    key={model.name}
                    style={buttonStyle(
                      selected === model.name
                    )}
                    onClick={() => setSelected(model.name)}
                  >
                    {model.name}
                  </button>
                ))}
              </div>

              <div
                style={{
                  display: "grid",
                  gridTemplateColumns:
                    "repeat(auto-fit, minmax(180px, 1fr))",
                  gap: 18,
                }}
              >
                <div>
                  <div style={{ color: "#94a3b8" }}>
                    Average F1
                  </div>
                  <div
                    style={{
                      fontSize: 38,
                      fontWeight: 800,
                      color: selectedModel.color,
                    }}
                  >
                    {selectedModel.f1.toFixed(2)}%
                  </div>
                </div>

                <div>
                  <div style={{ color: "#94a3b8" }}>
                    F1 Standard Deviation
                  </div>
                  <div
                    style={{
                      fontSize: 38,
                      fontWeight: 800,
                    }}
                  >
                    {selectedModel.std.toFixed(4)}
                  </div>
                </div>
              </div>

              <p
                style={{
                  color: "#94a3b8",
                  marginBottom: 0,
                  marginTop: 20,
                }}
              >
                {selectedModel.description}
              </p>
            </div>
          </>
        ) : (
          <div style={panel}>
            <h2 style={{ marginTop: 0 }}>
              Statistical Significance
            </h2>

            <p
              style={{
                color: "#94a3b8",
                lineHeight: 1.7,
              }}
            >
              Two-sided paired sign-flip comparisons
              with Holm multiple-testing correction.
              Significance threshold: p &lt; 0.05.
            </p>

            <div
              style={{
                overflowX: "auto",
                marginTop: 25,
              }}
            >
              <table
                style={{
                  width: "100%",
                  borderCollapse: "collapse",
                  textAlign: "left",
                  minWidth: 620,
                }}
              >
                <thead>
                  <tr
                    style={{
                      color: "#94a3b8",
                      borderBottom:
                        "1px solid #334155",
                    }}
                  >
                    <th style={{ padding: 15 }}>
                      Comparison
                    </th>
                    <th style={{ padding: 15 }}>
                      F1 Difference
                    </th>
                    <th style={{ padding: 15 }}>
                      Adjusted p
                    </th>
                    <th style={{ padding: 15 }}>
                      Result
                    </th>
                  </tr>
                </thead>

                <tbody>
                  {comparisons.map((item) => (
                    <tr
                      key={item.name}
                      style={{
                        borderBottom:
                          "1px solid #1e293b",
                      }}
                    >
                      <td style={{ padding: 15 }}>
                        {item.name}
                      </td>
                      <td
                        style={{
                          padding: 15,
                          color: "#21e6b1",
                        }}
                      >
                        {item.difference}
                      </td>
                      <td style={{ padding: 15 }}>
                        {item.p}
                      </td>
                      <td
                        style={{
                          padding: 15,
                          color: item.significant
                            ? "#21e6b1"
                            : "#fbbf24",
                          fontWeight: 700,
                        }}
                      >
                        {item.significant
                          ? "Significant"
                          : "Not significant"}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        <div
          style={{
            ...panel,
            borderColor: "rgba(251,191,36,.3)",
          }}
        >
          <h3
            style={{
              color: "#fbbf24",
              marginTop: 0,
            }}
          >
            Research Limitations
          </h3>

          <p
            style={{
              color: "#cbd5e1",
              lineHeight: 1.8,
              marginBottom: 0,
            }}
          >
            These results are a fixed snapshot of
            V11.3 research outputs. The benchmarks use
            synthetic datasets and a classical quantum
            simulator. Statistical significance in these
            experiments does not demonstrate quantum
            computational advantage or real-world
            cybersecurity effectiveness. Further
            independent validation is required.
          </p>
        </div>

        <footer
          style={{
            color: "#64748b",
            textAlign: "center",
            paddingTop: 12,
            fontSize: 12,
          }}
        >
          QUANTUM CYBER DEFENSE ARENA · V11.4
          RESEARCH DASHBOARD
        </footer>
      </div>
    </section>
  );
}
