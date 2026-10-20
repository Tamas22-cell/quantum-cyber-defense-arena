
"""
QUANTUM CYBER DEFENSE ARENA
V22.5 - AUTONOMOUS DEFENSE DASHBOARD

Integrates:
 V21.5 Network Digital Twin
 V22.2 Adaptive Threat Detection
 V22.3 Defense Decision Engine
 V22.4 Defense Strategy Simulation

Creates:
 research_validation/v22/
   autonomous_defense_dashboard_v22_5_results.json
   AUTONOMOUS_DEFENSE_DASHBOARD_V22_5.md

 frontend/public/v22/
   dashboard.html
   defense_data.json

All events and defense outcomes are simulated.
No real network changes.
Standard Python library only.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
V22 = ROOT / "research_validation" / "v22"
PUBLIC = ROOT / "frontend" / "public" / "v22"

SOURCES = {
    "network": ROOT / (
        "frontend/public/v21/intelligence_data.json"
    ),
    "detector": V22 / (
        "adaptive_threat_detection_v22_2_results.json"
    ),
    "detector_timeline": V22 / (
        "adaptive_threat_detection_v22_2_timeline.json"
    ),
    "decisions": V22 / (
        "multi_agent_defense_decision_v22_3_results.json"
    ),
    "decision_timeline": V22 / (
        "multi_agent_defense_decision_v22_3_timeline.json"
    ),
    "strategy": V22 / (
        "defense_strategy_simulation_v22_4_results.json"
    ),
    "strategy_timeline": V22 / (
        "defense_strategy_simulation_v22_4_timeline.json"
    ),
    "strategy_events": V22 / (
        "defense_strategy_simulation_v22_4_events.csv"
    ),
}

OUTPUT_JSON = V22 / (
    "autonomous_defense_dashboard_v22_5_results.json"
)
OUTPUT_MD = V22 / (
    "AUTONOMOUS_DEFENSE_DASHBOARD_V22_5.md"
)
OUTPUT_DATA = PUBLIC / "defense_data.json"
OUTPUT_HTML = PUBLIC / "dashboard.html"

CHECKS = []


def check(name, condition):
    ok = bool(condition)
    CHECKS.append({"name": name, "passed": ok})
    print(f"[{'PASS' if ok else 'FAIL'}] {name}")
    return ok


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(
            lambda: f.read(1024 * 1024), b""
        ):
            digest.update(block)
    return digest.hexdigest()


def load(path):
    with path.open("r", encoding="utf-8-sig") as f:
        if path.suffix == ".csv":
            return list(csv.DictReader(f))
        return json.load(f)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            data, f, indent=2,
            ensure_ascii=False, allow_nan=False
        )


def numeric(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric value")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite number")
    return result


def validate(data):
    expected = {
        "network": (
            "V21.5", "DASHBOARD_INTEGRATION_PASS"
        ),
        "detector": (
            "V22.2", "ADAPTIVE_THREAT_DETECTION_PASS"
        ),
        "detector_timeline": (
            "V22.2", "ADAPTIVE_THREAT_DETECTION_PASS"
        ),
        "decisions": (
            "V22.3", "DEFENSE_DECISION_PASS"
        ),
        "decision_timeline": (
            "V22.3", "DEFENSE_DECISION_PASS"
        ),
        "strategy": (
            "V22.4", "DEFENSE_STRATEGY_SIMULATION_PASS"
        ),
        "strategy_timeline": (
            "V22.4", "DEFENSE_STRATEGY_SIMULATION_PASS"
        ),
    }

    for name, (version, status) in expected.items():
        report = data[name]
        check(
            f"{name}: version and status",
            report.get("version") == version
            and report.get("status") == status
        )

    for name in ("detector", "decisions", "strategy"):
        check(
            f"{name}: zero failed validation checks",
            data[name].get("checks_failed") == 0
        )

    for name in (
        "network", "detector_timeline",
        "decision_timeline", "strategy_timeline"
    ):
        check(
            f"{name}: simulation only",
            data[name].get("simulation_mode") is True
            and data[name].get("is_live") is False
        )

    check(
        "V22.4 decision source fingerprint",
        data["strategy"].get(
            "source_sha256", {}
        ).get("decision_report")
        == sha256(SOURCES["decisions"])
    )

    check(
        "V22.4 network source fingerprint",
        data["strategy"].get(
            "source_sha256", {}
        ).get("intelligence")
        == sha256(SOURCES["network"])
    )

    check(
        "V22.4 strategy effects are hypothetical",
        data["strategy"].get(
            "effects_empirically_verified"
        ) is False
        and data["strategy"].get(
            "external_actions_enabled"
        ) is False
    )

    check(
        "No real actions in decision report",
        data["decisions"].get(
            "real_actions_executed"
        ) == 0
    )

    check(
        "No real actions in strategy report",
        data["strategy"].get(
            "evaluation", {}
        ).get("real_actions_executed") == 0
    )

    if not all(x["passed"] for x in CHECKS):
        raise ValueError("Input validation failed")


def assemble(data):
    network = data["network"]["frames"]
    detection = data["detector_timeline"]["timeline"]
    decision = data["decision_timeline"]["timeline"]
    strategy = data["strategy_timeline"]["timeline"]
    events = data["strategy_events"]

    lengths = list(map(
        len, (network, detection, decision, strategy)
    ))

    check(
        "Four aligned 120-tick timelines",
        lengths == [120, 120, 120, 120]
    )

    if lengths != [120] * 4:
        raise ValueError("Timeline length mismatch")

    check(
        "1200 simulated strategy records",
        len(events) == 1200
    )

    grouped = defaultdict(list)
    seen = set()

    for event in events:
        tick = int(event["tick"])
        node_id = event["node_id"]
        key = (tick, node_id)

        if (
            tick not in range(120)
            or key in seen
            or event["simulation_mode"].lower() != "true"
            or event["real_action_executed"].lower() != "false"
        ):
            raise ValueError(f"Invalid strategy event: {key}")

        seen.add(key)
        grouped[tick].append(event)

    frames = []

    for tick in range(120):
        n = network[tick]
        d = detection[tick]
        a = decision[tick]
        s = strategy[tick]

        if not (
            n["tick"] == d["tick"]
            == a["tick"] == s["tick"] == tick
        ):
            raise ValueError(f"Tick mismatch: {tick}")

        timestamps = {
            n["timestamp"], d["timestamp"],
            a["timestamp"], s["timestamp"]
        }

        if len(timestamps) != 1:
            raise ValueError(
                f"Timestamp mismatch: {tick}"
            )

        if (
            len(n["nodes"]) != 10
            or len(n["links"]) != 11
            or len(grouped[tick]) != 10
        ):
            raise ValueError(
                f"Unexpected node or event count: {tick}"
            )

        decisions = []

        for item in sorted(
            grouped[tick],
            key=lambda x: x["node_id"]
        ):
            decisions.append({
                "node_id": item["node_id"],
                "action": item["proposed_action"],
                "original_risk": numeric(
                    item["original_risk"]
                ),
                "residual_risk": numeric(
                    item["simulated_residual_risk"]
                ),
                "service_impact": numeric(
                    item["simulated_service_impact"]
                ),
                "approval_required": (
                    item["human_approval_required"].lower()
                    == "true"
                ),
            })

        original = numeric(s["mean_original_risk"])
        residual = numeric(
            s["mean_simulated_residual_risk"]
        )
        impact = numeric(
            s["mean_simulated_service_impact"]
        )

        if not all(
            0 <= x <= 1
            for x in (original, residual, impact)
        ):
            raise ValueError(
                f"Invalid strategy metrics: {tick}"
            )

        expected_mean = sum(
            x["residual_risk"] for x in decisions
        ) / len(decisions)

        if not math.isclose(
            expected_mean, residual, abs_tol=0.00001
        ):
            raise ValueError(
                f"Residual risk mismatch: {tick}"
            )

        frames.append({
            "tick": tick,
            "timestamp": n["timestamp"],
            "nodes": n["nodes"],
            "links": n["links"],
            "source_alerts": n["alerts"],
            "traffic_mbps": n["traffic_mbps"],
            "adaptive_detections": d["detections"],
            "detected_nodes": d["detected_nodes"],
            "mean_threshold": d[
                "mean_adaptive_threshold"
            ],
            "human_approval_required": a[
                "human_review_required"
            ],
            "action_counts": s["action_counts"],
            "original_risk": original,
            "residual_risk": residual,
            "service_impact": impact,
            "decisions": decisions,
            "real_actions_executed": 0,
        })

    return frames


DASHBOARD_HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quantum Cyber Defense Arena V22</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
:root{
 --bg:#050918;--panel:#101c32;--border:#243d59;
 --cyan:#30dbf4;--green:#36e9a0;--red:#ff5d81;
 --gold:#f5c96b;--muted:#91abc8
}
*{box-sizing:border-box}
body{
 margin:0;background:var(--bg);color:#eaf7ff;
 font:14px Segoe UI,Arial,sans-serif
}
header{
 padding:28px 4%;
 background:linear-gradient(115deg,#152e55,#050b18);
 border-bottom:1px solid var(--border)
}
header small{letter-spacing:2px;color:var(--cyan)}
h1{font-size:clamp(23px,3vw,38px);margin:10px 0}
header p,.muted{color:var(--muted)}
main{max-width:1500px;margin:auto;padding:18px}
.metrics{
 display:grid;grid-template-columns:repeat(5,minmax(0,1fr));
 gap:12px;margin-bottom:16px
}
.card,.panel{
 background:var(--panel);border:1px solid var(--border);
 border-radius:13px
}
.card{padding:17px}
.card small{color:var(--muted)}
.card strong{display:block;font-size:24px;margin-top:9px}
.layout{
 display:grid;grid-template-columns:minmax(0,1.8fr) minmax(295px,1fr);
 gap:16px
}
.panel{overflow:hidden}
.panel h2{
 margin:0;padding:15px;
 border-bottom:1px solid var(--border);
 font-size:15px
}
#network{
 display:block;width:100%;height:460px;
 background:radial-gradient(#153353,#061020 72%)
}
#chart{width:100%;height:240px;display:block}
.sidebar{display:flex;flex-direction:column;gap:15px}
.section{padding:16px}
.big{font-size:34px;font-weight:bold;color:var(--cyan)}
.controls{
 display:flex;align-items:center;gap:12px;
 padding:15px;flex-wrap:wrap
}
button,select{
 color:white;background:#193651;border:1px solid #416580;
 padding:9px 14px;border-radius:8px;cursor:pointer
}
input[type=range]{flex:1;accent-color:var(--cyan)}
#decisions{padding:12px;max-height:330px;overflow:auto}
.decision{
 padding:10px;margin-bottom:8px;background:#182b47;
 border-left:3px solid var(--cyan);border-radius:5px;
 font-size:12px
}
.legend,#status{
 padding:12px;color:var(--muted);font-size:12px
}
@media(max-width:980px){
 .layout{grid-template-columns:1fr}
 .metrics{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:580px){
 main{padding:10px}
 .metrics{grid-template-columns:repeat(2,1fr)}
 #network{height:335px}
}
</style>
</head>
<body>
<header>
<small>QUANTUM CYBER DEFENSE ARENA / V22.5</small>
<h1>Autonomous Defense Research Dashboard</h1>
<p>Adaptive detection · Defense decisions · Strategy simulation</p>
<p style="color:#f5c96b">SIMULATED REPLAY — NO REAL DEFENSE ACTIONS</p>
</header>
<main>
<div class="metrics">
<div class="card"><small>Simulation tick</small><strong id="tickCard">--</strong></div>
<div class="card"><small>Adaptive detections</small><strong id="detCard">--</strong></div>
<div class="card"><small>Original risk</small><strong id="riskCard">--</strong></div>
<div class="card"><small>Residual risk</small><strong id="resCard">--</strong></div>
<div class="card"><small>Service impact</small><strong id="impCard">--</strong></div>
</div>

<div class="layout">
<div>
<div class="panel">
<h2>Dynamic Cyber Defense Network</h2>
<svg id="network" viewBox="0 0 900 460"></svg>
<div class="legend">
Cyan: normal node · Red: adaptive detection ·
Green: simulated moving traffic
</div>
<div class="controls">
<button id="play">Pause</button>
<button id="restart">Restart</button>
<select id="speed">
<option value="1000">1×</option>
<option value="500" selected>2×</option>
<option value="250">4×</option>
</select>
<input type="range" id="slider" min="0" max="119" value="0">
<span id="tickText">1 / 120</span>
</div>
</div>

<div class="panel" style="margin-top:15px">
<h2>Simulated Risk &amp; Service Impact</h2>
<svg id="chart" viewBox="0 0 800 240"></svg>
<div class="legend">
Cyan: original risk · Green: modeled residual risk ·
Gold: modeled service impact
</div>
</div>
</div>

<div class="sidebar">
<div class="panel">
<h2>Defense Decision Overview</h2>
<div class="section">
<div class="muted">Human approval required</div>
<div class="big" id="approval">--</div>
<p>Simulated traffic: <strong id="traffic">--</strong></p>
<p>Mean adaptive threshold: <strong id="threshold">--</strong></p>
<p class="muted">
Actions are recommendations evaluated under a hypothetical
effect model. No network operations are executed.
</p>
</div>
</div>

<div class="panel">
<h2>Defense Action Distribution</h2>
<div class="section" id="actions"></div>
</div>

<div class="panel">
<h2>Simulated Node Decisions</h2>
<div id="decisions"></div>
</div>
</div>
</div>
<div id="status">Loading synthetic V22 research data...</div>
</main>

<script>
"use strict";
const $=id=>document.getElementById(id);
const graph=d3.select("#network");
const linkLayer=graph.append("g");
const particleLayer=graph.append("g");
const nodeLayer=graph.append("g");

let frames=[],index=0,playing=true,delay=500,timer=null;
let positions=new Map(),particles=null,current=null,cursor=null;

const fmt=value=>Number(value).toFixed(3);

function initGraph(frame){
 const ns=frame.nodes;
 ns.forEach((node,i)=>{
  const a=i*2*Math.PI/ns.length-Math.PI/2;
  positions.set(node.id,{
   x:450+325*Math.cos(a),
   y:225+155*Math.sin(a)
  });
 });

 linkLayer.selectAll("line")
 .data(frame.links,d=>d.id)
 .join("line")
 .attr("x1",d=>positions.get(d.source).x)
 .attr("y1",d=>positions.get(d.source).y)
 .attr("x2",d=>positions.get(d.target).x)
 .attr("y2",d=>positions.get(d.target).y)
 .attr("stroke","#30dbf4")
 .attr("opacity",.33)
 .attr("stroke-width",2);

 const nodes=nodeLayer.selectAll("g")
 .data(ns,d=>d.id).join("g")
 .attr("transform",d=>{
  const p=positions.get(d.id);
  return `translate(${p.x},${p.y})`;
 });

 nodes.append("circle")
 .attr("class","core")
 .attr("r",13)
 .attr("fill","#102942")
 .attr("stroke","#30dbf4")
 .attr("stroke-width",3);

 nodes.append("text")
 .attr("text-anchor","middle")
 .attr("y",32)
 .attr("fill","#eaf7ff")
 .attr("font-size",11)
 .text(d=>d.id.toUpperCase());

 nodes.append("title");

 const dots=frame.links.flatMap(l=>
  [0,1,2].map(i=>({
   id:l.id+"-"+i,linkId:l.id,phase:i/3
  }))
 );

 particles=particleLayer.selectAll("circle")
 .data(dots).join("circle")
 .attr("r",3).attr("fill","#36e9a0");
}

function drawChart(){
 const svg=d3.select("#chart");
 const x=d3.scaleLinear().domain([0,119]).range([45,780]);
 const y=d3.scaleLinear().domain([0,1]).range([215,15]);

 [0,.25,.5,.75,1].forEach(v=>{
  svg.append("line")
   .attr("x1",45).attr("x2",780)
   .attr("y1",y(v)).attr("y2",y(v))
   .attr("stroke","#284561");
  svg.append("text")
   .attr("x",8).attr("y",y(v)+4)
   .attr("fill","#91abc8")
   .attr("font-size",11).text(v);
 });

 const lines=[
  ["original_risk","#30dbf4"],
  ["residual_risk","#36e9a0"],
  ["service_impact","#f5c96b"]
 ];

 lines.forEach(([field,color])=>{
  svg.append("path").datum(frames)
   .attr("d",d3.line()
    .x(d=>x(d.tick))
    .y(d=>y(d[field])))
   .attr("fill","none")
   .attr("stroke",color)
   .attr("stroke-width",2);
 });

 cursor=svg.append("line")
 .attr("y1",15).attr("y2",215)
 .attr("stroke","#ff6485")
 .attr("stroke-dasharray","4 4");
}

function render(i){
 index=i;
 current=frames[i];
 const f=current;

 $("tickCard").textContent=i+1;
 $("detCard").textContent=f.adaptive_detections;
 $("riskCard").textContent=fmt(f.original_risk);
 $("resCard").textContent=fmt(f.residual_risk);
 $("impCard").textContent=fmt(f.service_impact);
 $("approval").textContent=f.human_approval_required;
 $("traffic").textContent=
  Number(f.traffic_mbps).toFixed(1)+" Mbps";
 $("threshold").textContent=fmt(f.mean_threshold);
 $("tickText").textContent=(i+1)+" / 120";
 $("slider").value=i;

 const detected=new Set(f.detected_nodes);
 const byId=new Map(f.nodes.map(n=>[n.id,n]));
 const decisionMap=new Map(
  f.decisions.map(d=>[d.node_id,d])
 );

 nodeLayer.selectAll("g").each(function(d){
  const n=byId.get(d.id);
  const selected=detected.has(d.id);
  d3.select(this).select(".core")
   .attr("stroke",selected?"#ff5d81":"#30dbf4")
   .attr("r",11+Number(n.load)*9);
  const decision=decisionMap.get(d.id);
  d3.select(this).select("title")
   .text(
    d.id+" | Risk "+fmt(n.risk_score)+
    " | Strategy "+(decision?.action||"observe")
   );
 });

 const actions=$("actions");
 actions.replaceChildren();
 Object.entries(f.action_counts).forEach(([name,count])=>{
  const div=document.createElement("p");
  div.textContent=name.replaceAll("_"," ")+": "+count;
  actions.appendChild(div);
 });

 const feed=$("decisions");
 feed.replaceChildren();

 f.decisions
  .filter(d=>d.action!=="observe")
  .slice(0,15)
  .forEach(d=>{
   const div=document.createElement("div");
   div.className="decision";
   div.textContent=
    d.node_id+" · "+d.action.replaceAll("_"," ")+
    " · Risk "+fmt(d.original_risk)+
    " → "+fmt(d.residual_risk)+
    (d.approval_required?" · Approval required":"");
   feed.appendChild(div);
  });

 if(!feed.children.length)
  feed.textContent="No intervention proposals at this tick.";

 const x=45+i/119*735;
 cursor.attr("x1",x).attr("x2",x);
}

function animate(time){
 if(current&&particles&&playing){
  const links=new Map(
   current.links.map(l=>[l.id,l])
  );
  particles.each(function(dot){
   const link=links.get(dot.linkId);
   if(!link)return;
   const a=positions.get(link.source);
   const b=positions.get(link.target);
   const speed=.00022+
    Number(link.traffic_mbps)/650000;
   const t=(dot.phase+time*speed)%1;
   d3.select(this)
    .attr("cx",a.x+(b.x-a.x)*t)
    .attr("cy",a.y+(b.y-a.y)*t);
  });
 }
 requestAnimationFrame(animate);
}

function schedule(){
 clearInterval(timer);
 if(playing&&frames.length){
  timer=setInterval(()=>{
   render((index+1)%frames.length);
  },delay);
 }
}

$("play").onclick=()=>{
 playing=!playing;
 $("play").textContent=playing?"Pause":"Play";
 schedule();
};

$("restart").onclick=()=>{
 playing=true;
 $("play").textContent="Pause";
 render(0);
 schedule();
};

$("speed").onchange=e=>{
 delay=Number(e.target.value);
 schedule();
};

$("slider").oninput=e=>{
 playing=false;
 $("play").textContent="Play";
 schedule();
 render(Number(e.target.value));
};

async function main(){
 try{
  if(typeof d3==="undefined")
   throw Error("D3 library unavailable");

  const response=await fetch(
   "./defense_data.json",{cache:"no-store"}
  );

  if(!response.ok)
   throw Error("Cannot load defense_data.json");

  const data=await response.json();

  if(
   data.version!=="V22.5"||
   data.status!=="DEFENSE_DASHBOARD_PASS"||
   data.simulation_mode!==true||
   !Array.isArray(data.frames)||
   data.frames.length!==120
  )throw Error("Invalid V22.5 dataset");

  frames=data.frames;

  if(frames.some((f,i)=>
   f.tick!==i||
   f.nodes.length!==10||
   f.links.length!==11
  ))throw Error("Invalid network topology");

  initGraph(frames[0]);
  drawChart();
  render(0);
  schedule();

  $("status").textContent=
   "V22.5 ready · 120 simulated frames · "+
   "No real network actions";

 }catch(error){
  $("status").textContent=
   "ERROR: "+error.message;
  $("status").style.color="#ff5d81";
  console.error(error);
 }
}

requestAnimationFrame(animate);
main();
</script>
</body>
</html>
'''


def make_document(report):
    metrics = report["metrics"]
    return f"""# Quantum Cyber Defense Arena

## V22.5 - Autonomous Defense Dashboard

**Status:** {report['status']}

**Checks passed:** {report['checks_passed']}

**Checks failed:** {report['checks_failed']}

### Integrated research modules

- V21.5 Cyber Digital Twin
- V22.2 Adaptive Threat Detection
- V22.3 Defense Decision Engine
- V22.4 Defense Strategy Simulation

### Dataset

- Simulation ticks: {metrics['ticks']}
- Nodes per tick: {metrics['nodes']}
- Network links: {metrics['links']}
- Total strategy records: {metrics['decisions']}
- Simulated intervention proposals: {metrics['intervention_proposals']}

### Dashboard

`frontend/public/v22/dashboard.html`

Includes:

- Animated D3 network visualization
- Moving synthetic traffic particles
- Adaptive detection highlighting
- Proposed defense actions
- Risk and hypothetical service-impact chart
- Pause, replay, speed and timeline controls

### Research limitations

All network data are synthetic.

Defense effects are hypothetical assumptions.
No real firewall operations or node isolation occur.
No measured real-world effectiveness is claimed.

### Next stage

V22.6 - Research Validation and Release
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V22.5 - AUTONOMOUS DEFENSE DASHBOARD")
    print("=" * 70)

    V22.mkdir(parents=True, exist_ok=True)

    data = {}

    for name, path in SOURCES.items():
        if not check(
            f"Source available: {name}",
            path.is_file()
        ):
            continue

        try:
            data[name] = load(path)
            check(
                f"Source readable: {name}",
                True
            )
        except (OSError, ValueError, TypeError):
            check(
                f"Source readable: {name}",
                False
            )

    frames = []
    error = None

    if len(data) == len(SOURCES):
        try:
            validate(data)
            frames = assemble(data)

            check(
                "120 dashboard frames assembled",
                len(frames) == 120
            )
            check(
                "Dashboard generation reproducible",
                frames == assemble(data)
            )
            check(
                "All real action counts zero",
                all(
                    frame["real_actions_executed"] == 0
                    for frame in frames
                )
            )
            check(
                "HTML contains D3 chart and network",
                "d3@7" in DASHBOARD_HTML
                and 'id="network"' in DASHBOARD_HTML
                and 'id="chart"' in DASHBOARD_HTML
            )

        except (
            ValueError, TypeError, KeyError,
            IndexError, OSError
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"
            check("Dashboard assembly completed", False)

    else:
        error = "Not all source files loaded"
        check("All inputs loaded", False)

    passed = sum(x["passed"] for x in CHECKS)
    failed = len(CHECKS) - passed

    status = (
        "DEFENSE_DASHBOARD_PASS"
        if failed == 0 and len(frames) == 120
        else "DEFENSE_DASHBOARD_FAIL"
    )

    metrics = {
        "ticks": len(frames),
        "nodes": 10 if frames else 0,
        "links": 11 if frames else 0,
        "decisions": sum(
            len(f["decisions"]) for f in frames
        ),
        "intervention_proposals": sum(
            sum(
                count for action, count
                in f["action_counts"].items()
                if action not in (
                    "observe", "increase_monitoring"
                )
            )
            for f in frames
        ),
        "real_actions_executed": 0,
    }

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V22.5",
        "status": status,
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "simulation_mode": True,
        "is_live": False,
        "effects_empirically_verified": False,
        "metrics": metrics,
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "source_sha256": {
            name: sha256(path)
            for name, path in SOURCES.items()
            if path.is_file()
        },
        "next_stage": (
            "V22.6 Research Validation and Release"
        ),
    }

    write_json(OUTPUT_JSON, report)

    if status == "DEFENSE_DASHBOARD_PASS":
        write_json(
            OUTPUT_DATA,
            {
                "version": "V22.5",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "effects_empirically_verified": False,
                "frames": frames,
            }
        )

        OUTPUT_HTML.parent.mkdir(
            parents=True, exist_ok=True
        )
        OUTPUT_HTML.write_text(
            DASHBOARD_HTML,
            encoding="utf-8"
        )

        OUTPUT_MD.write_text(
            make_document(report),
            encoding="utf-8"
        )

    print()
    print("=" * 70)
    print("V22.5 AUTONOMOUS DEFENSE DASHBOARD RESULTS")
    print("=" * 70)
    print("SIMULATION TICKS:", metrics["ticks"])
    print("NETWORK NODES:", metrics["nodes"])
    print("NETWORK LINKS:", metrics["links"])
    print("DECISION RECORDS:", metrics["decisions"])
    print(
        "SIMULATED INTERVENTION PROPOSALS:",
        metrics["intervention_proposals"]
    )
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUTPUT_JSON)

    if status == "DEFENSE_DASHBOARD_PASS":
        print("DASHBOARD:", OUTPUT_HTML)
        print("DATA EXPORT:", OUTPUT_DATA)

    if error:
        print("ERROR:", error)

    print("V22.5 RESULT:", status)
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V22.5 FAILED:",
            f"{type(exc).__name__}: {exc}"
        )
        sys.exit(1)
