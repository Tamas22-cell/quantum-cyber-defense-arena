/* Standalone Vercel research demonstration: all readings are SYNTHETIC. */
const nativeFetch = window.fetch.bind(window);
const networks = ["Ethereum", "Base", "Arbitrum", "Polygon"];
const kind = ["Suspicious transfer", "Bridge anomaly", "Unusual volume", "Contract interaction"];
function snapshot() {
  const tick = Math.floor(Date.now()/3000);
  const events = Array.from({length: 14}, (_, i) => {
    const score = 22 + ((i*23 + tick*7) % 76);
    return { id: "SIM-"+(1000+i), event_id: "SIM-"+(1000+i), network: networks[i%4],
      type: kind[i%4], risk_score: score, severity: score>79?"CRITICAL":score>59?"HIGH":score>39?"MEDIUM":"LOW",
      timestamp: new Date(Date.now()-i*43000).toISOString(), source:"0xSIM"+i+"A", destination:"0xSIM"+i+"B",
      mode:"SIMULATION", classification:score>60?"ANOMALY":"NORMAL",
      anomaly_score:Number((score/100).toFixed(3)), ai_detection:{anomaly_score:Number((score/100).toFixed(3)),classification:score>60?"ANOMALY":"NORMAL"} };
  });
  return events;
}
function payload(path: string) {
  const events = snapshot();
  const anomalies = events.filter(e=>e.risk_score>60);
  const now = new Date().toISOString();
  const classifications = events.map(e=>({event_id:e.id,network:e.network,timestamp:e.timestamp,
    classical_score:e.risk_score/100,quantum_score:Math.max(0,(e.risk_score-8)/100),
    fusion_score:e.risk_score/100,fusion_score_100:e.risk_score,classification:e.classification,
    severity:e.severity,models_agree:true,decision_status:e.risk_score>70?"INVESTIGATE":"MONITOR",
    explanation:"Synthetic research simulation — not a real-world alert",
    classical_model:"IsolationForest (demo)", quantum_model:"Quantum-inspired (demo)",
    classical_anomaly:e.risk_score>60,quantum_anomaly:e.risk_score>65,
    classical_weight:0.6,quantum_weight:0.4}));
  if(path==="/api/threats") return {total_events:events.length, events};
  if(path==="/api/ai/live") return {status:"SIMULATION",mode:"SIMULATION",model:"IsolationForest",model_version:"2.0.0",
    model_statistics:{model:"IsolationForest",model_version:"2.0.0",total_predictions:240+Math.floor(Date.now()/3000)%1000,total_anomalies_detected:anomalies.length},
    recent_anomalies:anomalies,total_predictions:240,total_anomalies_detected:anomalies.length};
  if(path==="/api/fusion/demo") return {version:"demo",mode:"SIMULATION",results:classifications};
  if(path==="/api/fusion/dynamic/live") return {version:"demo",mode:"SIMULATION",status:"SIMULATION",
    statistics:{processed_events:240+Math.floor(Date.now()/3000)%1000,fusion_anomalies:anomalies.length,review_events:3,model_disagreements:2},
    total_events:events.length,events:classifications,last_error:null};
  if(path==="/api/investigation/live") return {version:"demo",mode:"SIMULATION",status:"SIMULATION",generated_at:now,
    total_available:events.length,investigated:anomalies.length,
    investigations:classifications.filter(x=>x.fusion_score_100>60).map((x,i)=>({
      investigation_id:"INV-SIM-"+i,event_id:x.event_id,network:x.network,timestamp:x.timestamp,
      classification:x.classification,severity:x.severity,priority:x.fusion_score_100>80?"P1":"P2",
      decision_status:x.decision_status,models_agree:true,classical_score:x.classical_score*100,
      quantum_score:x.quantum_score*100,fusion_score_100:x.fusion_score_100,
      findings:["Synthetic anomaly pattern detected in test data"],recommendations:["Verify using real backend before acting"],
      status:"COMPLETED"}))};
  if(path==="/api/agents/live") return {version:"demo",mode:"SIMULATION",status:"SIMULATION",generated_at:now,
    total_available:events.length,report_count:anomalies.length,agent_count:3,
    statistics:{version:"demo",status:"SIMULATION",processed_events:240,review_events:3,anomaly_events:anomalies.length},
    reports:classifications.filter(x=>x.fusion_score_100>60).map((x,i)=>({
      report_id:"AG-SIM-"+i,event_id:x.event_id,network:x.network,timestamp:x.timestamp,
      engine_version:"demo",mode:"SIMULATION",classification:"ANOMALY",severity:x.severity,
      fusion_score_100:x.fusion_score_100,priority:"P2",agent_count:3,
      agent_results:["Detection Agent","Quantum Agent","Review Agent"].map(agent=>({agent,status:"COMPLETED",
        summary:"Synthetic research assessment",findings:["Demonstration event"],recommendations:["Human review"],
        confidence_note:"Not a validated security finding"})),
      consensus:"REVIEW",requires_review:true,executive_summary:"Synthetic event: research demo only",
      consolidated_findings:["Synthetic anomaly"],recommended_actions:["Connect a real backend for live detection"]}))};
  const m=(mean:number)=>({mean,std:0.018,min:mean-0.03,max:mean+0.03});
  if(path==="/api/quantum/benchmark") return {version:"demo",
    quantum:{model:"Quantum-inspired (simulation)",summary:{accuracy:m(.88),precision:m(.86),recall:m(.84),f1_score:m(.85),f1:m(.85),runtime_ms:m(8.4)}},
    classical:{model:"Classical (simulation)",summary:{accuracy:m(.86),precision:m(.83),recall:m(.82),f1_score:m(.825),f1:m(.825),runtime_ms:m(2.1)}}};
  if(path==="/api/quantum/statistics") return {version:"demo",f1_score:{sample_size:40,quantum_mean:.85,
    classical_mean:.825,mean_difference:.025,confidence_interval_95:{lower:-.005,upper:.055},
    paired_t_test:{p_value:.12},wilcoxon_signed_rank:{p_value:.15},quantum_wins:23,classical_wins:15,ties:2},
    runtime:{quantum_mean_ms:8.4,classical_mean_ms:2.1,quantum_to_classical_ratio:4}};
  const metrics=(n:number)=>({accuracy:n+.02,precision:n+.01,recall:n-.01,f1:n});
  if(path==="/api/research/v10-1") return {version:"demo",summary:{sample_count:250,
    classical:metrics(.82),quantum:metrics(.84),hybrid_conservative:metrics(.86)}};
  if(path==="/api/research/v10-2") return {version:"demo",mode:"SIMULATION",
    model_comparison:{classical_f1:.82,quantum_f1:.84,hybrid_f1:.86,
      differences:{quantum_vs_classical_pp:2,hybrid_vs_classical_pp:4,hybrid_vs_quantum_pp:2}},
    confidence_intervals:[{model_a:"Hybrid",model_b:"Classical",f1_difference_pp:4,
      ci_95_lower_pp:-1,ci_95_upper_pp:9,excludes_zero:false}],
    hybrid_reviews:{review_count:21,review_rate_percent:8.4,decisive_coverage_percent:91.6},
    runtime:{classical_ms_per_event:2.1,quantum_plus_fusion_ms_per_event:8.4}};
  return null;
}
window.fetch = (input: RequestInfo | URL, init?: RequestInit): Promise<Response> => {
  const url = typeof input==="string"?input: input instanceof URL?input.href:input.url;
  if(url.startsWith("http://127.0.0.1:8000/") || url.startsWith("http://localhost:8000/")) {
    const parsed = new URL(url);
    const body = payload(parsed.pathname);
    return Promise.resolve(new Response(JSON.stringify(body??{status:"SIMULATION",events:[],results:[]}),{
      status:200,headers:{"content-type":"application/json","x-demo-mode":"synthetic"}}));
  }
  return nativeFetch(input,init);
};
const banner = document.createElement("div");
banner.textContent = "RESEARCH SIMULATION · SYNTHETIC DATA · NO LIVE BACKEND";
banner.setAttribute("role","status");
banner.style.cssText = "position:fixed;bottom:0;left:0;right:0;z-index:9999;text-align:center;background:#0b1635eF;border-top:1px solid #3adfeb;color:#a5f3fc;padding:7px 12px;font:700 10px system-ui;letter-spacing:1px;pointer-events:none";
document.addEventListener("DOMContentLoaded",()=>document.body.appendChild(banner));
