
import { useEffect, useMemo, useState } from "react";

type BlockchainTx = {
  transaction_hash: string;
  value_eth: number | string;
  gas_limit: number;
};

type IngestionData = {
  network: string;
  collected_at: string;
  block: {
    number: number;
    hash: string;
    datetime_utc: string;
    transaction_count: number;
  };
  transactions: BlockchainTx[];
};

type AnomalyTx = {
  transaction_hash: string;
  anomaly_score: number;
  classification: string;
};

type AnomalyData = {
  summary: {
    transactions_analyzed: number;
    statistical_outliers: number;
    average_anomaly_score: number;
  };
  transactions: AnomalyTx[];
};

type IntegrationData = {
  summary: {
    transactions_integrated: number;
    quantum_model_available: boolean;
    quantum_results_available: number;
  };
  transactions: {
    transaction_hash: string;
    hybrid_decision: string;
  }[];
};

type DashboardData = {
  ingestion: IngestionData;
  anomaly: AnomalyData;
  integration: IntegrationData;
};

const BASE = import.meta.env.BASE_URL;

const COLORS = {
  cyan: "#36e4ff",
  purple: "#aa79ff",
  green: "#51edb6",
  orange: "#ffba67",
  red: "#ff6b93",
  text: "#d9ecff",
  muted: "#8ca7c4",
};

function shortHash(hash: string) {
  if (!hash || hash.length < 18) return hash;
  return `${hash.slice(0, 12)}...${hash.slice(-8)}`;
}

function scoreText(value: number) {
  return Number.isFinite(value) ? value.toFixed(5) : "N/A";
}

function panelStyle(): React.CSSProperties {
  return {
    background: "rgba(9, 21, 43, 0.88)",
    border: "1px solid rgba(54, 228, 255, 0.17)",
    borderRadius: 18,
    padding: 20,
    boxShadow: "0 12px 32px rgba(0,0,0,0.18)",
    minWidth: 0,
  };
}

export default function BlockchainIntelligenceV16_5() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");
  const [activeIndex, setActiveIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const paths = [
          `${BASE}v16/blockchain_ingestion_v16_1_results.json`,
          `${BASE}v16/blockchain_anomaly_v16_3_results.json`,
          `${BASE}v16/ai_quantum_integration_v16_4_results.json`,
        ];

        const responses = await Promise.all(
          paths.map((path) => fetch(path))
        );

        for (const response of responses) {
          if (!response.ok) {
            throw new Error(
              `JSON betöltési hiba: HTTP ${response.status}`
            );
          }
        }

        const [ingestion, anomaly, integration] =
          await Promise.all(responses.map((r) => r.json()));

        if (
          ingestion?.network !== "ethereum-mainnet" ||
          !Array.isArray(ingestion?.transactions) ||
          !Array.isArray(anomaly?.transactions) ||
          !Array.isArray(integration?.transactions) ||
          !anomaly?.summary ||
          !integration?.summary
        ) {
          throw new Error("Érvénytelen V16 adatstruktúra.");
        }

        const sourceHashes = new Set(
          ingestion.transactions.map(
            (tx: BlockchainTx) => tx.transaction_hash.toLowerCase()
          )
        );

        const anomalyHashes = new Set(
          anomaly.transactions.map(
            (tx: AnomalyTx) => tx.transaction_hash.toLowerCase()
          )
        );

        const integrationHashes = new Set(
          integration.transactions.map(
            (tx: { transaction_hash: string }) =>
              tx.transaction_hash.toLowerCase()
          )
        );

        if (
          sourceHashes.size !== anomalyHashes.size ||
          sourceHashes.size !== integrationHashes.size ||
          [...sourceHashes].some(
            (hash) =>
              !anomalyHashes.has(hash) ||
              !integrationHashes.has(hash)
          )
        ) {
          throw new Error(
            "A V16 adatfájlok tranzakcióazonosítói eltérnek."
          );
        }

        if (!cancelled) {
          setData({ ingestion, anomaly, integration });
        }
      } catch (caught) {
        if (!cancelled) {
          setError(
            caught instanceof Error
              ? caught.message
              : "Ismeretlen adatbetöltési hiba."
          );
        }
      }
    }

    void load();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (!data?.anomaly.transactions.length) return;

    const timer = window.setInterval(() => {
      setActiveIndex(
        (previous) =>
          (previous + 1) % data.anomaly.transactions.length
      );
    }, 2000);

    return () => window.clearInterval(timer);
  }, [data]);

  const ordered = useMemo(() => {
    if (!data) return [];

    const txIndex = new Map(
      data.ingestion.transactions.map((tx) => [
        tx.transaction_hash.toLowerCase(),
        tx,
      ])
    );

    return data.anomaly.transactions
      .map((row) => ({
        ...row,
        source: txIndex.get(row.transaction_hash.toLowerCase()),
      }))
      .sort((a, b) => b.anomaly_score - a.anomaly_score);
  }, [data]);

  if (error) {
    return (
      <section style={{ ...panelStyle(), color: COLORS.red }}>
        V16.5 – Blockchain Intelligence: {error}
      </section>
    );
  }

  if (!data) {
    return (
      <section style={{ ...panelStyle(), color: COLORS.cyan }}>
        V16.5 – Ethereum research data loading...
      </section>
    );
  }

  const { ingestion, anomaly, integration } = data;
  const current = ordered[activeIndex % (ordered.length || 1)];

  const maxScore = Math.max(
    ...ordered.map((tx) => tx.anomaly_score),
    0.000001
  );

  const minScore = Math.min(
    ...ordered.map((tx) => tx.anomaly_score),
    maxScore
  );

  const quantumReady =
    integration.summary.quantum_model_available === true;

  const flagged = anomaly.summary.statistical_outliers;

  return (
    <section className="qv16-root">
      <style>{`
        .qv16-root {
          color: ${COLORS.text};
          background:
            radial-gradient(ellipse at 85% 0%, rgba(74,43,143,.26), transparent 47%),
            radial-gradient(ellipse at 0% 100%, rgba(0,160,205,.12), transparent 46%),
            #061022;
          border: 1px solid rgba(54,228,255,.22);
          border-radius: 24px;
          padding: clamp(16px, 3vw, 32px);
          margin: 30px 0;
          font-family: Inter, system-ui, sans-serif;
          overflow: hidden;
          box-shadow: 0 22px 65px rgba(0,0,0,.3);
        }

        .qv16-heading {
          display: flex;
          justify-content: space-between;
          align-items: center;
          gap: 18px;
          flex-wrap: wrap;
          margin-bottom: 24px;
        }

        .qv16-title {
          font-size: clamp(21px, 3vw, 31px);
          font-weight: 800;
          letter-spacing: .025em;
          margin: 7px 0;
          color: #ecf7ff;
        }

        .qv16-eyebrow {
          color: ${COLORS.cyan};
          font-size: 11px;
          letter-spacing: .22em;
          font-weight: 700;
        }

        .qv16-subtitle {
          font-size: 12px;
          color: ${COLORS.muted};
          line-height: 1.7;
        }

        .qv16-badge {
          color: ${COLORS.green};
          border: 1px solid rgba(81,237,182,.35);
          background: rgba(81,237,182,.07);
          padding: 9px 13px;
          border-radius: 30px;
          font-size: 11px;
          font-weight: 700;
        }

        .qv16-metrics {
          display: grid;
          grid-template-columns: repeat(4, minmax(0,1fr));
          gap: 12px;
          margin-bottom: 16px;
        }

        .qv16-grid {
          display: grid;
          grid-template-columns: minmax(0,1.25fr) minmax(0,1fr);
          gap: 16px;
        }

        .qv16-card {
          background: rgba(9,21,43,.88);
          border: 1px solid rgba(54,228,255,.17);
          border-radius: 18px;
          padding: 20px;
          min-width: 0;
        }

        .qv16-label {
          font-size: 10px;
          letter-spacing: .11em;
          color: ${COLORS.muted};
          text-transform: uppercase;
        }

        .qv16-value {
          font-size: clamp(20px,2.7vw,30px);
          font-weight: 800;
          margin-top: 10px;
          font-variant-numeric: tabular-nums;
          overflow-wrap: anywhere;
        }

        .qv16-card-title {
          font-size: 14px;
          color: #e4f4ff;
          font-weight: 750;
          letter-spacing: .04em;
          margin: 0 0 17px;
        }

        .qv16-bars {
          display: flex;
          flex-direction: column;
          gap: 13px;
        }

        .qv16-bar-row {
          display: grid;
          grid-template-columns: 110px minmax(0,1fr) 65px;
          gap: 12px;
          align-items: center;
          font-size: 11px;
        }

        .qv16-bar-track {
          height: 9px;
          border-radius: 20px;
          background: rgba(116,157,200,.12);
          overflow: hidden;
        }

        .qv16-bar-fill {
          height: 100%;
          background: linear-gradient(90deg,#21b9e3,#9d70ff);
          border-radius: 20px;
          transform-origin: left center;
          animation: qv16-grow .9s ease-out both;
        }

        .qv16-event {
          padding: 12px;
          border-radius: 12px;
          background: rgba(54,228,255,.035);
          border: 1px solid rgba(54,228,255,.12);
          margin-bottom: 10px;
          animation: qv16-fade .5s ease-out;
        }

        .qv16-network {
          height: 190px;
          position: relative;
          margin: 0 0 16px;
          border: 1px solid rgba(54,228,255,.1);
          border-radius: 16px;
          background:
            linear-gradient(rgba(54,228,255,.035) 1px, transparent 1px),
            linear-gradient(90deg,rgba(54,228,255,.035) 1px, transparent 1px);
          background-size: 24px 24px;
          overflow: hidden;
        }

        .qv16-node {
          position: absolute;
          width: 9px;
          height: 9px;
          border-radius: 50%;
          background: ${COLORS.cyan};
          box-shadow: 0 0 15px ${COLORS.cyan};
          animation: qv16-pulse 2.4s ease-in-out infinite;
        }

        .qv16-scan {
          position: absolute;
          left: 0;
          right: 0;
          height: 2px;
          background: linear-gradient(90deg, transparent, #36e4ff, transparent);
          box-shadow: 0 0 15px #36e4ff;
          animation: qv16-scan 5s linear infinite;
        }

        .qv16-footer {
          font-size: 11px;
          color: ${COLORS.muted};
          line-height: 1.7;
          margin-top: 16px;
          border-top: 1px solid rgba(54,228,255,.12);
          padding-top: 14px;
        }

        @keyframes qv16-grow {
          from { transform: scaleX(0); }
          to { transform: scaleX(1); }
        }

        @keyframes qv16-pulse {
          0%,100% { opacity:.4; transform:scale(.85); }
          50% { opacity:1; transform:scale(1.5); }
        }

        @keyframes qv16-scan {
          from { top:0%; }
          to { top:100%; }
        }

        @keyframes qv16-fade {
          from { opacity:.3; transform:translateY(7px); }
          to { opacity:1; transform:translateY(0); }
        }

        @media(max-width:850px) {
          .qv16-metrics { grid-template-columns:repeat(2,minmax(0,1fr)); }
          .qv16-grid { grid-template-columns:1fr; }
        }

        @media(max-width:450px) {
          .qv16-bar-row { grid-template-columns:78px minmax(0,1fr) 58px; gap:6px; }
          .qv16-card { padding:14px; }
        }

        @media(prefers-reduced-motion:reduce) {
          .qv16-root *, .qv16-root *::before, .qv16-root *::after {
            animation: none !important;
          }
        }
      `}</style>

      <header className="qv16-heading">
        <div>
          <div className="qv16-eyebrow">
            QUANTUM CYBER DEFENSE ARENA / V16.5
          </div>
          <h2 className="qv16-title">
            Blockchain Threat Intelligence
          </h2>
          <div className="qv16-subtitle">
            Ethereum Mainnet · Historical Snapshot ·
            AI Anomaly Research
          </div>
        </div>

        <span className="qv16-badge">
          ● REAL BLOCKCHAIN DATA
        </span>
      </header>

      <div className="qv16-metrics">
        <div className="qv16-card">
          <div className="qv16-label">Ethereum block</div>
          <div className="qv16-value" style={{ color: COLORS.cyan }}>
            {ingestion.block.number.toLocaleString("en-US")}
          </div>
        </div>

        <div className="qv16-card">
          <div className="qv16-label">Block transactions</div>
          <div className="qv16-value">
            {ingestion.block.transaction_count}
          </div>
        </div>

        <div className="qv16-card">
          <div className="qv16-label">Analyzed sample</div>
          <div className="qv16-value" style={{ color: COLORS.purple }}>
            {anomaly.summary.transactions_analyzed}
          </div>
        </div>

        <div className="qv16-card">
          <div className="qv16-label">Statistical outliers</div>
          <div className="qv16-value" style={{ color: COLORS.orange }}>
            {flagged}
          </div>
        </div>
      </div>

      <div className="qv16-grid">
        <div className="qv16-card">
          <h3 className="qv16-card-title">
            ◈ Isolation Forest / Anomaly Scores
          </h3>

          <div className="qv16-bars">
            {ordered.slice(0, 8).map((tx) => {
              const relative =
                maxScore === minScore
                  ? 100
                  : 12 +
                    (88 * (tx.anomaly_score - minScore)) /
                      (maxScore - minScore);

              const isOutlier =
                tx.classification === "STATISTICAL_OUTLIER";

              return (
                <div
                  className="qv16-bar-row"
                  key={tx.transaction_hash}
                >
                  <span
                    title={tx.transaction_hash}
                    style={{
                      color: isOutlier
                        ? COLORS.orange
                        : COLORS.muted,
                    }}
                  >
                    {tx.transaction_hash.slice(0, 11)}…
                  </span>

                  <div className="qv16-bar-track">
                    <div
                      className="qv16-bar-fill"
                      style={{
                        width: `${relative}%`,
                        background: isOutlier
                          ? "linear-gradient(90deg,#ffba67,#ff6b93)"
                          : undefined,
                      }}
                    />
                  </div>

                  <span style={{ textAlign: "right" }}>
                    {scoreText(tx.anomaly_score)}
                  </span>
                </div>
              );
            })}
          </div>

          <div className="qv16-subtitle" style={{ marginTop: 19 }}>
            Scores are relative to this research sample;
            bar lengths are visualization-normalized,
            not calibrated threat probabilities.
          </div>
        </div>

        <div className="qv16-card">
          <h3 className="qv16-card-title">
            ◈ Transaction Network Visualization
          </h3>

          <div
            className="qv16-network"
            aria-label="Animated visualization of stored transaction observations"
          >
            <div className="qv16-scan" />

            {ordered.map((tx, index) => {
              const x =
                8 + ((index * 47 + 13) % 85);
              const y =
                12 + ((index * 29 + 17) % 75);

              return (
                <div
                  className="qv16-node"
                  key={tx.transaction_hash}
                  title={shortHash(tx.transaction_hash)}
                  style={{
                    left: `${x}%`,
                    top: `${y}%`,
                    background:
                      tx.classification === "STATISTICAL_OUTLIER"
                        ? COLORS.orange
                        : COLORS.cyan,
                    boxShadow:
                      tx.classification === "STATISTICAL_OUTLIER"
                        ? `0 0 15px ${COLORS.orange}`
                        : undefined,
                    animationDelay: `${index * 0.15}s`,
                  }}
                />
              );
            })}
          </div>

          <div className="qv16-label">
            Animated display of saved observations
          </div>

          {current && (
            <div
              className="qv16-event"
              key={current.transaction_hash}
              style={{ marginTop: 12 }}
            >
              <div
                style={{
                  color: COLORS.cyan,
                  fontSize: 12,
                  fontWeight: 700,
                  overflowWrap: "anywhere",
                }}
              >
                {shortHash(current.transaction_hash)}
              </div>

              <div
                className="qv16-subtitle"
                style={{ marginTop: 9 }}
              >
                Value: {current.source?.value_eth ?? "N/A"} ETH
              </div>

              <div
                className="qv16-subtitle"
                style={{ marginTop: 5 }}
              >
                Score: {scoreText(current.anomaly_score)}
              </div>

              <div
                style={{
                  color:
                    current.classification === "STATISTICAL_OUTLIER"
                      ? COLORS.orange
                      : COLORS.green,
                  fontSize: 11,
                  marginTop: 9,
                  fontWeight: 700,
                }}
              >
                {current.classification}
              </div>
            </div>
          )}
        </div>

        <div className="qv16-card">
          <h3 className="qv16-card-title">
            ◈ AI–Quantum Integration
          </h3>

          <div className="qv16-label">
            Classical AI / Isolation Forest
          </div>

          <div
            style={{
              color: COLORS.green,
              fontWeight: 800,
              marginTop: 9,
              marginBottom: 17,
            }}
          >
            EXECUTED
          </div>

          <div className="qv16-label">Quantum model</div>

          <div
            style={{
              color: quantumReady ? COLORS.green : COLORS.orange,
              fontWeight: 800,
              marginTop: 9,
              marginBottom: 17,
            }}
          >
            {quantumReady
              ? "RESULTS PROVIDED"
              : "NOT EXECUTED"}
          </div>

          <div className="qv16-label">
            Hybrid comparison
          </div>

          <div
            style={{
              color: quantumReady ? COLORS.cyan : COLORS.muted,
              fontWeight: 800,
              marginTop: 9,
            }}
          >
            {quantumReady
              ? "OUTPUTS AVAILABLE"
              : "AWAITING QUANTUM DATA"}
          </div>
        </div>

        <div className="qv16-card">
          <h3 className="qv16-card-title">
            ◈ Research Provenance
          </h3>

          <div className="qv16-subtitle">
            <strong style={{ color: COLORS.text }}>
              Source network:
            </strong>{" "}
            Ethereum Mainnet
          </div>

          <div className="qv16-subtitle" style={{ marginTop: 10 }}>
            <strong style={{ color: COLORS.text }}>
              Block time:
            </strong>{" "}
            {ingestion.block.datetime_utc}
          </div>

          <div className="qv16-subtitle" style={{ marginTop: 10 }}>
            <strong style={{ color: COLORS.text }}>
              Collection time:
            </strong>{" "}
            {ingestion.collected_at}
          </div>

          <div
            className="qv16-subtitle"
            style={{ marginTop: 10, overflowWrap: "anywhere" }}
          >
            <strong style={{ color: COLORS.text }}>
              Block hash:
            </strong>{" "}
            {ingestion.block.hash}
          </div>

          <div
            style={{
              marginTop: 17,
              color: COLORS.green,
              fontSize: 11,
              fontWeight: 700,
            }}
          >
            READ-ONLY RESEARCH MODE
          </div>
        </div>
      </div>

      <footer className="qv16-footer">
        V16.5 · Research visualization of a saved Ethereum
        blockchain snapshot. No continuously updating blockchain
        feed, confirmed attack labels, or validated quantum
        advantage. Statistical anomalies are not confirmed
        malicious transactions.
      </footer>
    </section>
  );
}
