
"""
QUANTUM CYBER DEFENSE ARENA
V21.5 - INTELLIGENCE DASHBOARD INTEGRATION

Combines:
 V20.4 - Digital Twin frames
 V21.2 - Behavioral anomaly timeline
 V21.3 - Threat correlation timeline
 V21.4 - Predictive risk timeline

Creates a separate D3 dashboard.
Does NOT overwrite the existing V20 dashboard.

Synthetic research data only.
Standard library only.
"""

from __future__ import annotations

import hashlib
import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V20 = ROOT / "research_validation" / "v20"
V21 = ROOT / "research_validation" / "v21"
PUBLIC = ROOT / "frontend" / "public" / "v21"

SOURCES = {
    "frames": V20 / "event_streaming_v20_4_frames.json",
    "behavior_report": V21 / "behavioral_anomaly_detection_v21_2_results.json",
    "behavior": V21 / "behavioral_anomaly_detection_v21_2_timeline.json",
    "correlation_report": V21 / "multi_agent_threat_correlation_v21_3_results.json",
    "correlation": V21 / "multi_agent_threat_correlation_v21_3_timeline.json",
    "prediction_report": V21 / "predictive_risk_analytics_v21_4_results.json",
    "prediction": V21 / "predictive_risk_analytics_v21_4_timeline.json",
}

RESULT = V21 / "intelligence_dashboard_integration_v21_5_results.json"
DOCUMENT = V21 / "INTELLIGENCE_DASHBOARD_V21_5.md"
DATA_FILE = PUBLIC / "intelligence_data.json"
HTML_FILE = PUBLIC / "dashboard.html"

CHECKS = []


def check(name, condition):
    passed = bool(condition)
    CHECKS.append({"name": name, "passed": passed})
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    return passed


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        value = json.load(f)
    if not isinstance(value, dict):
        raise ValueError(f"Invalid JSON: {path.name}")
    return value


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False),
        encoding="utf-8"
    )


def bounded(value):
    if isinstance(value, bool):
        return False
    try:
        n = float(value)
        return math.isfinite(n) and 0 <= n <= 1
    except (ValueError, TypeError):
        return False


def validate_sources(reports):
    expectations = {
        "frames": ("V20.4", "EVENT_STREAMING_PASS"),
        "behavior_report": ("V21.2", "BEHAVIORAL_ANOMALY_PASS"),
        "behavior": ("V21.2", "BEHAVIORAL_ANOMALY_PASS"),
        "correlation_report": ("V21.3", "THREAT_CORRELATION_PASS"),
        "correlation": ("V21.3", "THREAT_CORRELATION_PASS"),
        "prediction_report": ("V21.4", "PREDICTIVE_RISK_PASS"),
        "prediction": ("V21.4", "PREDICTIVE_RISK_PASS"),
    }

    for name, (version, status) in expectations.items():
        item = reports[name]
        check(
            f"{name}: version and PASS status",
            item.get("version") == version
            and item.get("status") == status
        )

    for name in ("behavior_report", "correlation_report", "prediction_report"):
        check(
            f"{name}: zero failed checks",
            reports[name].get("checks_failed") == 0
        )

    checksums = [
        (
            reports["behavior_report"].get("source_sha256", {}).get("frames"),
            "frames", "V21.2 frame fingerprint"
        ),
        (
            reports["correlation_report"].get("source_sha256", {}).get("frames"),
            "frames", "V21.3 frame fingerprint"
        ),
        (
            reports["prediction_report"].get("source_sha256", {}).get("frames"),
            "frames", "V21.4 frame fingerprint"
        ),
        (
            reports["prediction_report"].get("source_sha256", {}).get(
                "correlation_timeline"
            ),
            "correlation", "V21.4 correlation fingerprint"
        ),
    ]

    for expected, source, label in checksums:
        check(label, expected == digest(SOURCES[source]))

    check(
        "All inputs are simulation exports",
        all(
            reports[name].get("simulation_mode") is True
            and reports[name].get("is_live") is False
            for name in ("frames", "behavior", "correlation", "prediction")
        )
    )

    return all(item["passed"] for item in CHECKS)


def assemble(reports):
    frames = reports["frames"]["frames"]
    behavior = reports["behavior"]["timeline"]
    correlation = reports["correlation"]["timeline"]
    prediction = reports["prediction"]["timeline"]

    if not (
        len(frames) == len(behavior)
        == len(correlation) == len(prediction) == 120
    ):
        raise ValueError("Expected 120 aligned simulation ticks")

    result = []

    for i in range(120):
        f, b, c, p = (
            frames[i], behavior[i],
            correlation[i], prediction[i]
        )

        if not (
            f["sequence"] == b["tick"]
            == c["tick"] == p["tick"] == i
        ):
            raise ValueError(f"Timeline misalignment at tick {i}")

        if not (
            f["timestamp"] == b["timestamp"]
            == c["timestamp"] == p["timestamp"]
        ):
            raise ValueError(f"Timestamp mismatch at tick {i}")

        nodes = f["network"]["nodes"]
        links = f["network"]["links"]

        if len(nodes) != 10 or len(links) != 11:
            raise ValueError(f"Invalid topology at tick {i}")

        risk = p["observed_risk"]
        forecast = p["predicted_risk"]
        low = p["interval_lower"]
        high = p["interval_upper"]

        if not bounded(risk):
            raise ValueError(f"Invalid risk at tick {i}")

        if forecast is not None:
            if not all(bounded(x) for x in (forecast, low, high)):
                raise ValueError(f"Invalid prediction at tick {i}")
            if not low <= forecast <= high:
                raise ValueError(f"Invalid interval at tick {i}")

        result.append({
            "tick": i,
            "timestamp": f["timestamp"],
            "nodes": nodes,
            "links": links,
            "alerts": f["alerts"],
            "traffic_mbps": f["metrics"]["total_traffic_mbps"],
            "latency_ms": f["metrics"]["mean_latency_ms"],
            "observed_risk": risk,
            "predicted_risk": forecast,
            "interval_lower": low,
            "interval_upper": high,
            "evaluation_split": p["evaluation_split"],
            "behavioral_detections": b["detections"],
            "detected_nodes": b["detected_nodes"],
            "maximum_anomaly_score": b["maximum_anomaly_score"],
            "same_tick_correlations": c["same_tick_correlations"],
            "nearby_correlations": c["nearby_tick_correlations"],
            "correlation_score": c["maximum_correlation_score"],
            "synthetic_injection": f["metrics"]["anomaly_injected"],
        })

    return result


HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quantum Cyber Defense Arena | V21 Intelligence</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
:root{--bg:#050b18;--panel:#101d35;--line:#253f60;
--cyan:#2be7fb;--green:#51e7a5;--red:#ff6485;--muted:#90abc8}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:#e8f4ff;
font:14px Inter,Segoe UI,Arial,sans-serif}
header{padding:25px 4%;background:linear-gradient(110deg,#152c51,#081120);
border-bottom:1px solid var(--line)}
header small{color:var(--cyan);letter-spacing:2px}
h1{margin:10px 0;font-size:clamp(23px,3vw,37px)}
header p{color:var(--muted)}
main{max-width:1500px;margin:auto;padding:20px}
.metrics{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}
.metric,.panel{background:var(--panel);border:1px solid var(--line);border-radius:13px}
.metric{padding:16px}
.metric small{display:block;color:var(--muted)}
.metric strong{display:block;margin-top:8px;font-size:clamp(17px,2.2vw,27px)}
.layout{display:grid;grid-template-columns:minmax(0,1.8fr) minmax(290px,1fr);
gap:15px;margin-top:16px}
.panel{overflow:hidden}
.panel h2{font-size:15px;margin:0;padding:16px;border-bottom:1px solid var(--line)}
#network{width:100%;height:470px;display:block;background:
radial-gradient(ellipse,#123252 0%,#081120 75%)}
#chart{width:100%;height:260px;display:block}
.controls{display:flex;align-items:center;gap:12px;padding:15px;flex-wrap:wrap}
button,select{color:white;background:#193653;border:1px solid #3a6d8b;
border-radius:8px;padding:9px 13px;cursor:pointer}
input[type=range]{flex:1;min-width:100px;accent-color:var(--cyan)}
.sidebar{display:flex;flex-direction:column;gap:15px}
.section{padding:17px}
.large{font-size:38px;font-weight:bold;color:var(--cyan)}
.muted{color:var(--muted);font-size:12px;line-height:1.7}
#events{max-height:360px;overflow:auto;padding:12px}
.event{padding:11px;background:#162b46;border-left:3px solid var(--red);
margin-bottom:9px;border-radius:5px;font-size:12px}
#status{padding:12px;color:var(--cyan);font-size:12px}
.legend{padding:12px;color:var(--muted);font-size:12px}
@media(max-width:950px){.layout{grid-template-columns:1fr}
.metrics{grid-template-columns:repeat(3,1fr)}}
@media(max-width:580px){main{padding:10px}
.metrics{grid-template-columns:repeat(2,1fr)}
#network{height:330px}}
</style>
</head>
<body>
<header>
<small>QUANTUM CYBER DEFENSE ARENA / V21.5</small>
<h1>Advanced Threat Intelligence</h1>
<p>Behavioral analytics · Threat correlation · Predictive risk · SIMULATED REPLAY</p>
</header>
<main>
<div class="metrics">
<div class="metric"><small>Network nodes</small><strong id="nodes">10</strong></div>
<div class="metric"><small>Traffic</small><strong id="traffic">--</strong></div>
<div class="metric"><small>Latency</small><strong id="latency">--</strong></div>
<div class="metric"><small>Behavior anomalies</small><strong id="behavior">--</strong></div>
<div class="metric"><small>Threat correlations</small><strong id="correlations">--</strong></div>
</div>

<div class="layout">
<div>
<div class="panel">
<h2>Cyber Digital Twin — Dynamic Network</h2>
<svg id="network" viewBox="0 0 900 470"></svg>
<div class="legend">● Cyan: normal &nbsp; ● Red: higher risk &nbsp; ● Green: moving traffic particles</div>
<div class="controls">
<button id="play">Pause</button>
<button id="restart">Restart</button>
<select id="speed">
<option value="1000">1×</option>
<option value="500" selected>2×</option>
<option value="250">4×</option>
</select>
<input type="range" id="slider" min="0" max="119" value="0">
<span id="tick">0 / 120</span>
</div>
</div>
<div class="panel" style="margin-top:15px">
<h2>Observed vs Predicted Risk</h2>
<svg id="chart" viewBox="0 0 800 260"></svg>
<div class="legend">Cyan: observed risk · Green: predicted risk · Shaded area: interval</div>
</div>
</div>
<div class="sidebar">
<div class="panel">
<h2>Predictive Risk Analytics</h2>
<div class="section">
<div class="muted">Observed risk</div>
<div class="large" id="risk">--</div>
<p>Next-step forecast: <strong id="prediction">--</strong></p>
<p>Prediction interval: <strong id="interval">--</strong></p>
<p class="muted" id="split">--</p>
<p class="muted">Forecasts use prior simulated observations. These are not probabilities of real attacks.</p>
</div>
</div>
<div class="panel">
<h2>Threat Intelligence Event Feed</h2>
<div id="events"></div>
</div>
</div>
</div>
<div id="status">Loading verified synthetic research data...</div>
</main>
<script>
"use strict";
const $=id=>document.getElementById(id);
const svg=d3.select("#network");
const linksLayer=svg.append("g");
const particlesLayer=svg.append("g");
const nodesLayer=svg.append("g");
let frames=[],index=0,playing=true,delay=500,timer=null;
let positions=new Map(),particleSel=null,current=null;
const color=r=>r>=.75?"#ff6485":r>=.5?"#ffd166":"#2be7fb";
const numeric=x=>Number.isFinite(Number(x))?Number(x):0;
const fmt=x=>x==null?"--":numeric(x).toFixed(3);

function initTopology(f){
  const nodes=f.nodes;
  nodes.forEach((n,i)=>{
    const a=i*2*Math.PI/nodes.length-Math.PI/2;
    positions.set(n.id,{x:450+330*Math.cos(a),y:230+158*Math.sin(a)});
  });
  linksLayer.selectAll("line").data(f.links,d=>d.id).join("line")
   .attr("x1",d=>positions.get(d.source).x)
   .attr("y1",d=>positions.get(d.source).y)
   .attr("x2",d=>positions.get(d.target).x)
   .attr("y2",d=>positions.get(d.target).y)
   .attr("stroke","#2be7fb").attr("opacity",.35).attr("stroke-width",2);

  const groups=nodesLayer.selectAll("g").data(nodes,d=>d.id).join("g")
   .attr("transform",d=>{const p=positions.get(d.id);return `translate(${p.x},${p.y})`});
  groups.append("circle").attr("class","core").attr("r",12)
   .attr("stroke","#2be7fb").attr("stroke-width",3).attr("fill","#112844");
  groups.append("text").attr("text-anchor","middle").attr("y",32)
   .attr("fill","#e1f5ff").attr("font-size",11).text(d=>d.id.toUpperCase());
  groups.append("title");
  const particles=f.links.flatMap(link=>[0,1,2].map(i=>({
    id:link.id+"-"+i,linkId:link.id,phase:i/3
  })));
  particleSel=particlesLayer.selectAll("circle").data(particles)
   .join("circle").attr("r",3).attr("fill","#51e7a5");
}
function render(i){
  index=i;current=frames[i];const f=current;
  $("nodes").textContent=f.nodes.length;
  $("traffic").textContent=numeric(f.traffic_mbps).toFixed(1)+" Mbps";
  $("latency").textContent=numeric(f.latency_ms).toFixed(2)+" ms";
  $("behavior").textContent=f.behavioral_detections;
  $("correlations").textContent=f.same_tick_correlations+f.nearby_correlations;
  $("risk").textContent=fmt(f.observed_risk);
  $("risk").style.color=color(f.observed_risk);
  $("prediction").textContent=fmt(f.predicted_risk);
  $("interval").textContent=f.interval_lower==null?"Warmup":
      fmt(f.interval_lower)+" – "+fmt(f.interval_upper);
  $("split").textContent="Tick "+i+" · "+f.evaluation_split+" · "+f.timestamp;
  $("tick").textContent=(i+1)+" / "+frames.length;
  $("slider").value=i;

  const byNode=new Map(f.nodes.map(n=>[n.id,n]));
  nodesLayer.selectAll("g").each(function(d){
    const node=byNode.get(d.id);
    const selected=f.detected_nodes.includes(d.id);
    d3.select(this).select(".core").attr("stroke",
      selected?"#ff6485":color(node.risk_score))
      .attr("r",10+numeric(node.load)*9);
    d3.select(this).select("title")
      .text(d.id+" | Risk "+fmt(node.risk_score)+" | Load "+fmt(node.load));
  });
  const linkMap=new Map(f.links.map(l=>[l.id,l]));
  linksLayer.selectAll("line")
    .attr("stroke",d=>linkMap.get(d.id).injected_anomaly?"#ff6485":"#2be7fb")
    .attr("stroke-width",d=>linkMap.get(d.id).injected_anomaly?4:2);

  const container=$("events");container.replaceChildren();
  const events=frames.slice(Math.max(0,i-19),i+1)
    .flatMap(x=>x.alerts.map(a=>({...a,tick:x.tick}))).reverse().slice(0,20);
  if(!events.length)container.textContent="No alerts in recent frames.";
  events.forEach(a=>{
    const el=document.createElement("div");
    el.className="event";
    el.textContent="Tick "+a.tick+" · "+a.node_id+" · "+
      (a.category||"Risk alert")+" · Risk "+fmt(a.risk_score);
    container.appendChild(el);
  });
  updateChartCursor(i);
}
function animate(time){
  if(current&&particleSel&&playing){
    const byLink=new Map(current.links.map(l=>[l.id,l]));
    particleSel.each(function(p){
      const l=byLink.get(p.linkId),a=positions.get(l.source),b=positions.get(l.target);
      const progress=(p.phase+time*(.00028+numeric(l.traffic_mbps)/600000))%1;
      d3.select(this).attr("cx",a.x+(b.x-a.x)*progress)
        .attr("cy",a.y+(b.y-a.y)*progress)
        .attr("fill",l.injected_anomaly?"#ff6485":"#51e7a5");
    });
  }
  requestAnimationFrame(animate);
}
let cursor;
function drawChart(){
  const chart=d3.select("#chart");
  const x=d3.scaleLinear().domain([0,119]).range([45,775]);
  const y=d3.scaleLinear().domain([0,1]).range([220,15]);
  [0,.25,.5,.75,1].forEach(value=>{
    chart.append("line").attr("x1",45).attr("x2",775)
      .attr("y1",y(value)).attr("y2",y(value))
      .attr("stroke","#27435f").attr("opacity",.6);
    chart.append("text").attr("x",7).attr("y",y(value)+4)
      .attr("fill","#91abc9").attr("font-size",11).text(value);
  });
  const valid=frames.filter(f=>f.predicted_risk!==null);
  const area=d3.area().x(d=>x(d.tick))
    .y0(d=>y(d.interval_lower)).y1(d=>y(d.interval_upper));
  chart.append("path").datum(valid).attr("d",area)
    .attr("fill","#51e7a5").attr("opacity",.12);
  const line=field=>d3.line().x(d=>x(d.tick)).y(d=>y(d[field]));
  chart.append("path").datum(frames).attr("d",line("observed_risk"))
    .attr("stroke","#2be7fb").attr("stroke-width",2)
    .attr("fill","none");
  chart.append("path").datum(valid).attr("d",line("predicted_risk"))
    .attr("stroke","#51e7a5").attr("stroke-width",2)
    .attr("fill","none");
  cursor=chart.append("line").attr("y1",15).attr("y2",220)
    .attr("stroke","#ffd166").attr("stroke-dasharray","4 4");
}
function updateChartCursor(i){
  if(cursor)cursor.attr("x1",45+i/119*730).attr("x2",45+i/119*730);
}
function schedule(){
  clearInterval(timer);
  if(playing&&frames.length)
    timer=setInterval(()=>render((index+1)%frames.length),delay);
}
$("play").onclick=()=>{
  playing=!playing;$("play").textContent=playing?"Pause":"Play";schedule();
};
$("restart").onclick=()=>{
  playing=true;$("play").textContent="Pause";render(0);schedule();
};
$("speed").onchange=e=>{delay=Number(e.target.value);schedule();};
$("slider").oninput=e=>{
  playing=false;$("play").textContent="Play";
  schedule();render(Number(e.target.value));
};
async function main(){
  try{
    if(typeof d3==="undefined")throw Error("D3 library unavailable");
    const response=await fetch("./intelligence_data.json",{cache:"no-store"});
    if(!response.ok)throw Error("Cannot read intelligence_data.json");
    const data=await response.json();
    if(data.version!=="V21.5"||data.status!=="DASHBOARD_INTEGRATION_PASS"||
       data.simulation_mode!==true||!Array.isArray(data.frames)||
       data.frames.length!==120)throw Error("Invalid V21.5 data");

    frames=data.frames;
    if(frames.some((f,i)=>f.tick!==i||f.nodes.length!==10||f.links.length!==11))
      throw Error("Invalid frame topology or timeline");
    initTopology(frames[0]);drawChart();render(0);schedule();
    $("status").textContent="V21.5 ready · 120 research frames · SIMULATED REPLAY · NOT LIVE";
  }catch(e){
    $("status").textContent="ERROR: "+e.message;
    $("status").style.color="#ff6485";
    console.error(e);
  }
}
requestAnimationFrame(animate);
main();
</script>
</body>
</html>
'''


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V21.5 - INTELLIGENCE DASHBOARD INTEGRATION")
    print("=" * 70)

    V21.mkdir(parents=True, exist_ok=True)
    reports = {}
    errors = []

    for name, path in SOURCES.items():
        exists = check(f"Source available: {name}", path.is_file())
        if not exists:
            errors.append(f"Missing: {path}")
            continue
        try:
            reports[name] = read_json(path)
            check(f"Source readable: {name}", True)
        except (OSError, ValueError) as e:
            check(f"Source readable: {name}", False)
            errors.append(str(e))

    combined = []

    if len(reports) == len(SOURCES):
        try:
            if validate_sources(reports):
                combined = assemble(reports)
                check("All 120 frames aligned", len(combined) == 120)
                check(
                    "No invalid observed risks",
                    all(bounded(f["observed_risk"]) for f in combined)
                )
                check(
                    "Behavior and correlation counts nonnegative",
                    all(
                        f["behavioral_detections"] >= 0
                        and f["same_tick_correlations"] >= 0
                        and f["nearby_correlations"] >= 0
                        for f in combined
                    )
                )
                check(
                    "Combined data deterministic",
                    combined == assemble(reports)
                )
        except (OSError, ValueError, TypeError, KeyError, IndexError) as e:
            errors.append(str(e))
            check("Dashboard assembly completed", False)

    passed = sum(x["passed"] for x in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "DASHBOARD_INTEGRATION_PASS"
        if failed == 0 and len(combined) == 120
        else "DASHBOARD_INTEGRATION_FAIL"
    )

    result = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V21.5",
        "status": status,
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "simulation_mode": True,
        "live_network_monitoring": False,
        "checks_passed": passed,
        "checks_failed": failed,
        "checks": CHECKS,
        "errors": errors,
        "metrics": {
            "frames": len(combined),
            "nodes": 10 if combined else 0,
            "links": 11 if combined else 0,
            "behavioral_detections": sum(
                f["behavioral_detections"] for f in combined
            ),
            "same_tick_correlations": sum(
                f["same_tick_correlations"] for f in combined
            ),
            "forecasts_available": sum(
                f["predicted_risk"] is not None for f in combined
            ),
        },
        "source_sha256": {
            name: digest(path)
            for name, path in SOURCES.items()
            if path.is_file()
        },
        "next_stage": "V21.6 Research Validation and Release",
    }

    write_json(RESULT, result)

    if status == "DASHBOARD_INTEGRATION_PASS":
        write_json(DATA_FILE, {
            "version": "V21.5",
            "status": status,
            "simulation_mode": True,
            "is_live": False,
            "frames": combined,
        })

        # Only create the new dashboard.
        # Never overwrite the existing V20 dashboard.
        HTML_FILE.parent.mkdir(parents=True, exist_ok=True)
        HTML_FILE.write_text(HTML, encoding="utf-8")

        DOCUMENT.write_text(
            "# V21.5 Intelligence Dashboard Integration\n\n"
            f"Status: {status}\n\n"
            f"Checks passed: {passed}\n\n"
            "Inputs: V20.4, V21.2, V21.3, V21.4.\n\n"
            "Outputs:\n"
            "- frontend/public/v21/dashboard.html\n"
            "- frontend/public/v21/intelligence_data.json\n\n"
            "120 aligned synthetic network simulation frames.\n\n"
            "Prediction values and prediction intervals are research"
            " estimates, not real-world attack probabilities.\n\n"
            "V20 dashboard preserved.\n",
            encoding="utf-8"
        )

    print()
    print("=" * 70)
    print("V21.5 INTELLIGENCE DASHBOARD RESULTS")
    print("=" * 70)
    print(f"FRAMES: {len(combined)}")
    print(f"CHECKS PASSED: {passed}")
    print(f"CHECKS FAILED: {failed}")

    if status == "DASHBOARD_INTEGRATION_PASS":
        print(f"DASHBOARD: {HTML_FILE}")
        print(f"DATA EXPORT: {DATA_FILE}")

    print(f"JSON REPORT: {RESULT}")
    print(f"V21.5 RESULT: {status}")
    print("=" * 70)

    return 0 if status == "DASHBOARD_INTEGRATION_PASS" else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print(f"V21.5 FAILED: {type(e).__name__}: {e}")
        sys.exit(1)
