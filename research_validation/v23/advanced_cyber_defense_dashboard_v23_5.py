
"""
QUANTUM CYBER DEFENSE ARENA
V23.5 - ADVANCED CYBER DEFENSE DASHBOARD

Integrates:
  V22.5 - Network Digital Twin
  V23.2 - Intelligent Threat Fusion
  V23.3 - Defense Policy Optimization
  V23.4 - Defense Orchestration

Generates:
  frontend/public/v23/dashboard.html
  frontend/public/v23/defense_data.json
  research_validation/v23/
      advanced_cyber_defense_dashboard_v23_5_results.json
      ADVANCED_CYBER_DEFENSE_DASHBOARD_V23_5.md

All data and decisions are simulated.
No real network or firewall actions.
Python standard library only.
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
V23 = ROOT / "research_validation" / "v23"
PUBLIC = ROOT / "frontend" / "public" / "v23"

SOURCES = {
    "network": ROOT / (
        "frontend/public/v22/defense_data.json"
    ),
    "fusion_report": V23 / (
        "intelligent_threat_fusion_v23_2_results.json"
    ),
    "fusion_events": V23 / (
        "intelligent_threat_fusion_v23_2_events.csv"
    ),
    "fusion_timeline": V23 / (
        "intelligent_threat_fusion_v23_2_timeline.json"
    ),
    "policy_report": V23 / (
        "adaptive_defense_policy_optimization_v23_3_results.json"
    ),
    "policy_timeline": V23 / (
        "adaptive_defense_policy_optimization_v23_3_timeline.json"
    ),
    "orchestration_report": V23 / (
        "multi_agent_defense_orchestration_v23_4_results.json"
    ),
    "orchestration_events": V23 / (
        "multi_agent_defense_orchestration_v23_4_events.csv"
    ),
    "orchestration_timeline": V23 / (
        "multi_agent_defense_orchestration_v23_4_timeline.json"
    ),
}

OUT_REPORT = V23 / (
    "advanced_cyber_defense_dashboard_v23_5_results.json"
)
OUT_MD = V23 / (
    "ADVANCED_CYBER_DEFENSE_DASHBOARD_V23_5.md"
)
OUT_DATA = PUBLIC / "defense_data.json"
OUT_HTML = PUBLIC / "dashboard.html"

PROFILES = (
    "balanced",
    "service_first",
    "risk_first",
)

ACTIONS = {
    "observe",
    "increase_monitoring",
    "rate_limit",
    "isolate_node",
    "request_review",
}

CHECKS = []


def check(name, condition, detail=""):
    passed = bool(condition)
    CHECKS.append({
        "name": name,
        "passed": passed,
        "detail": str(detail),
    })
    print(f"[{'PASS' if passed else 'FAIL'}] {name}")
    if not passed and detail:
        print("    " + str(detail))
    return passed


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(
            lambda: handle.read(1024 * 1024),
            b"",
        ):
            digest.update(block)
    return digest.hexdigest()


def read_json(path):
    with path.open("r", encoding="utf-8-sig") as f:
        result = json.load(f)

    if not isinstance(result, dict):
        raise ValueError(
            f"Invalid JSON object: {path.name}"
        )
    return result


def read_csv(path):
    with path.open(
        "r", encoding="utf-8-sig", newline=""
    ) as f:
        records = list(csv.DictReader(f))

    if not records:
        raise ValueError(
            f"Empty CSV: {path.name}"
        )
    return records


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(
            value,
            f,
            indent=2,
            ensure_ascii=False,
            allow_nan=False,
        )


def number(value):
    if isinstance(value, bool):
        raise ValueError("Boolean numeric input")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("Non-finite measurement")
    return result


def boolean(value):
    if isinstance(value, bool):
        return value
    if str(value).lower() == "true":
        return True
    if str(value).lower() == "false":
        return False
    raise ValueError(f"Invalid boolean: {value}")


def rnd(value):
    return round(float(value), 6)


def load_inputs():
    loaded = {}

    for name, path in SOURCES.items():
        if not check(
            f"Source available: {name}",
            path.is_file(),
            str(path),
        ):
            continue

        try:
            loaded[name] = (
                read_csv(path)
                if path.suffix == ".csv"
                else read_json(path)
            )
            check(f"Source readable: {name}", True)
        except (OSError, ValueError, TypeError) as e:
            check(
                f"Source readable: {name}",
                False,
                str(e),
            )

    return loaded


def validate_inputs(data):
    expected = {
        "network": (
            "V22.5", "DEFENSE_DASHBOARD_PASS"
        ),
        "fusion_report": (
            "V23.2", "INTELLIGENT_THREAT_FUSION_PASS"
        ),
        "fusion_timeline": (
            "V23.2", "INTELLIGENT_THREAT_FUSION_PASS"
        ),
        "policy_report": (
            "V23.3", "DEFENSE_POLICY_OPTIMIZATION_PASS"
        ),
        "policy_timeline": (
            "V23.3", "DEFENSE_POLICY_OPTIMIZATION_PASS"
        ),
        "orchestration_report": (
            "V23.4", "DEFENSE_ORCHESTRATION_PASS"
        ),
        "orchestration_timeline": (
            "V23.4", "DEFENSE_ORCHESTRATION_PASS"
        ),
    }

    for name, (version, status) in expected.items():
        item = data[name]
        check(
            f"{name}: validated version and status",
            item.get("version") == version
            and item.get("status") == status
            and item.get("simulation_mode") is True,
        )

    for name in (
        "fusion_report",
        "policy_report",
        "orchestration_report",
    ):
        check(
            f"{name}: zero failed checks",
            data[name].get("checks_failed") == 0,
        )

    check(
        "Source network is replay-only",
        data["network"].get("is_live") is False,
    )

    check(
        "All three policy profiles available",
        set(
            data["policy_report"]["configuration"][
                "profiles"
            ]
        ) == set(PROFILES),
    )

    check(
        "No external orchestration actions",
        data["orchestration_report"].get(
            "external_actions_enabled"
        ) is False,
    )

    check(
        "Orchestration source fingerprint valid",
        data["orchestration_report"].get(
            "source_sha256", {}
        ).get("policy_report")
        == sha256(SOURCES["policy_report"]),
    )

    check(
        "Policy source fingerprint valid",
        data["policy_report"].get(
            "source_sha256", {}
        ).get("fusion_report")
        == sha256(SOURCES["fusion_report"]),
    )

    check(
        "1200 fused observations",
        len(data["fusion_events"]) == 1200,
    )

    check(
        "3600 orchestration events",
        len(data["orchestration_events"]) == 3600,
    )

    if not all(item["passed"] for item in CHECKS):
        raise ValueError(
            "V23.5 source validation failed"
        )


def assemble(data):
    network = data["network"]["frames"]
    fusion = data["fusion_timeline"]["timeline"]
    policies = data["policy_timeline"]["timeline"]
    orchestration = data[
        "orchestration_timeline"
    ]["timeline"]

    if any(
        len(items) != 120
        for items in (
            network, fusion, policies, orchestration
        )
    ):
        raise ValueError(
            "Expected four complete 120-tick timelines"
        )

    events_by_tick = defaultdict(list)
    event_ids = set()

    for event in data["orchestration_events"]:
        tick = int(event["tick"])
        event_id = event["event_id"]

        if (
            tick < 0 or tick >= 120
            or event_id in event_ids
            or event["profile"] not in PROFILES
            or event["proposed_action"] not in ACTIONS
            or boolean(event["real_action_executed"])
            or not boolean(event["simulation_mode"])
        ):
            raise ValueError(
                f"Invalid orchestration event: {event_id}"
            )

        event_ids.add(event_id)
        events_by_tick[tick].append(event)

    fusion_by_tick = defaultdict(list)
    fusion_keys = set()

    for event in data["fusion_events"]:
        tick = int(event["tick"])
        node_id = event["node_id"]
        key = (tick, node_id)

        if (
            tick not in range(120)
            or key in fusion_keys
            or not boolean(event["simulation_mode"])
        ):
            raise ValueError(
                f"Invalid fusion event: {key}"
            )

        fusion_keys.add(key)
        fusion_by_tick[tick].append(event)

    combined = []

    for tick in range(120):
        n = network[tick]
        f = fusion[tick]
        p = policies[tick]
        o = orchestration[tick]

        if not (
            n["tick"] == f["tick"]
            == p["tick"] == o["tick"] == tick
        ):
            raise ValueError(
                f"Timeline mismatch at tick {tick}"
            )

        if len({
            n["timestamp"],
            f["timestamp"],
            p["timestamp"],
            o["timestamp"],
        }) != 1:
            raise ValueError(
                f"Timestamp mismatch at tick {tick}"
            )

        if (
            len(n["nodes"]) != 10
            or len(n["links"]) != 11
            or len(fusion_by_tick[tick]) != 10
            or len(events_by_tick[tick]) != 30
        ):
            raise ValueError(
                f"Network or event count mismatch: {tick}"
            )

        threat_nodes = sorted(
            [
                {
                    "node_id": e["node_id"],
                    "score": number(e["fusion_score"]),
                    "priority": e["priority"],
                    "detected": boolean(
                        e["adaptive_detection"]
                    ),
                }
                for e in fusion_by_tick[tick]
            ],
            key=lambda x: x["node_id"],
        )

        decisions = sorted(
            [
                {
                    "node_id": e["node_id"],
                    "profile": e["profile"],
                    "proposed_action": e[
                        "proposed_action"
                    ],
                    "status": e[
                        "orchestration_status"
                    ],
                    "approval_required": boolean(
                        e["human_approval_required"]
                    ),
                    "residual_risk": number(
                        e["proposal_residual_risk"]
                    ),
                    "service_impact": number(
                        e["proposal_service_impact"]
                    ),
                }
                for e in events_by_tick[tick]
            ],
            key=lambda x: (
                x["profile"], x["node_id"]
            ),
        )

        profiles = {}

        for name in PROFILES:
            policy_data = p["profiles"][name]
            orchestration_data = o["profiles"][name]

            profiles[name] = {
                "mean_weighted_cost": number(
                    policy_data["mean_weighted_cost"]
                ),
                "mean_residual_risk": number(
                    policy_data["mean_residual_risk"]
                ),
                "mean_service_impact": number(
                    policy_data["mean_service_impact"]
                ),
                "approval_pending": int(
                    orchestration_data[
                        "approval_pending"
                    ]
                ),
                "validated_plans": int(
                    orchestration_data[
                        "validated_simulation_plans"
                    ]
                ),
                "action_counts": policy_data[
                    "action_counts"
                ],
            }

        combined.append({
            "tick": tick,
            "timestamp": n["timestamp"],
            "nodes": n["nodes"],
            "links": n["links"],
            "source_alerts": n["source_alerts"],
            "traffic_mbps": n["traffic_mbps"],
            "original_risk": n["original_risk"],
            "mean_fusion_score": number(
                f["mean_fusion_score"]
            ),
            "max_fusion_score": number(
                f["maximum_fusion_score"]
            ),
            "adaptive_detections": int(
                f["adaptive_detections"]
            ),
            "high_priority_nodes": f[
                "high_priority_nodes"
            ],
            "threat_nodes": threat_nodes,
            "profiles": profiles,
            "decisions": decisions,
            "real_actions_executed": 0,
        })

    return combined


def validate_combined(frames):
    check(
        "Exactly 120 combined frames",
        len(frames) == 120,
    )

    check(
        "Every frame contains ten threat nodes",
        all(
            len(frame["threat_nodes"]) == 10
            for frame in frames
        ),
    )

    check(
        "Every frame contains 30 profile decisions",
        all(
            len(frame["decisions"]) == 30
            for frame in frames
        ),
    )

    check(
        "All profile keys present",
        all(
            set(frame["profiles"]) == set(PROFILES)
            for frame in frames
        ),
    )

    check(
        "All fusion scores bounded",
        all(
            0 <= item["score"] <= 1
            for frame in frames
            for item in frame["threat_nodes"]
        ),
    )

    check(
        "All modeled service impacts bounded",
        all(
            0 <= item["service_impact"] <= 1
            for frame in frames
            for item in frame["decisions"]
        ),
    )

    check(
        "All approvals remain proposals",
        all(
            item["status"] == "PENDING_HUMAN_APPROVAL"
            for frame in frames
            for item in frame["decisions"]
            if item["approval_required"]
        ),
    )

    check(
        "No real network actions",
        all(
            frame["real_actions_executed"] == 0
            for frame in frames
        ),
    )

    check(
        "All frames have stable node/link topology",
        all(
            len(frame["nodes"]) == 10
            and len(frame["links"]) == 11
            for frame in frames
        ),
    )


HTML = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Quantum Cyber Defense Arena — V23</title>
<script src="https://cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js"></script>
<style>
:root{
 --bg:#040816;--panel:#101d34;--border:#29415c;
 --cyan:#26e6ff;--green:#46edab;--red:#ff6486;
 --gold:#ffd36c;--muted:#8faac7
}
*{box-sizing:border-box}
body{
 margin:0;background:var(--bg);color:#e7f5ff;
 font:14px Segoe UI,Arial,sans-serif
}
header{
 padding:28px 4%;
 background:linear-gradient(120deg,#16315a,#050b1a);
 border-bottom:1px solid var(--border)
}
header small{
 color:var(--cyan);letter-spacing:2px
}
h1{
 font-size:clamp(24px,3.2vw,40px);
 margin:10px 0
}
header p{color:var(--muted)}
main{max-width:1500px;margin:auto;padding:18px}
.metrics{
 display:grid;
 grid-template-columns:repeat(5,minmax(0,1fr));
 gap:12px;margin-bottom:16px
}
.card,.panel{
 background:var(--panel);
 border:1px solid var(--border);
 border-radius:14px
}
.card{padding:16px}
.card small{color:var(--muted)}
.card strong{
 display:block;font-size:25px;margin-top:9px
}
.layout{
 display:grid;
 grid-template-columns:minmax(0,1.8fr) minmax(285px,1fr);
 gap:16px
}
.panel{overflow:hidden}
.panel h2{
 margin:0;padding:15px;
 border-bottom:1px solid var(--border);
 font-size:15px
}
#network{
 width:100%;height:470px;display:block;
 background:radial-gradient(ellipse,#163457,#060c1c 75%)
}
#chart{
 width:100%;height:270px;display:block
}
.controls{
 display:flex;gap:12px;
 align-items:center;padding:15px;flex-wrap:wrap
}
button,select{
 padding:9px 13px;border-radius:8px;
 border:1px solid #44728e;
 background:#173453;color:#fff;cursor:pointer
}
input[type=range]{
 flex:1;min-width:100px;accent-color:var(--cyan)
}
.sidebar{
 display:flex;flex-direction:column;gap:15px
}
.section{padding:16px}
.big{
 font-size:36px;font-weight:bold;color:var(--cyan)
}
.muted,.legend,#status{
 color:var(--muted);font-size:12px;line-height:1.6
}
.legend,#status{padding:12px}
#feed{
 padding:12px;max-height:390px;overflow:auto
}
.event{
 background:#182f4d;
 padding:10px;margin-bottom:8px;
 border-left:3px solid var(--cyan);
 border-radius:5px;font-size:12px
}
.profileGrid{
 display:grid;grid-template-columns:1fr 1fr;
 gap:10px;margin-top:12px
}
.profileGrid div{
 padding:12px;border:1px solid var(--border);
 border-radius:8px
}
.profileGrid strong{
 display:block;margin-top:6px
}
@media(max-width:960px){
 .layout{grid-template-columns:1fr}
 .metrics{grid-template-columns:repeat(3,1fr)}
}
@media(max-width:600px){
 main{padding:10px}
 .metrics{grid-template-columns:repeat(2,1fr)}
 #network{height:340px}
 .profileGrid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<header>
<small>QUANTUM CYBER DEFENSE ARENA / V23.5</small>
<h1>Advanced Autonomous Cyber Defense</h1>
<p>Threat Fusion · Policy Optimization · Multi-Agent Orchestration</p>
<p style="color:#ffd36c">
SIMULATED REPLAY — NO REAL NETWORK ACTIONS
</p>
</header>

<main>
<div class="metrics">
<div class="card"><small>Simulation tick</small><strong id="tickCard">--</strong></div>
<div class="card"><small>Fusion risk</small><strong id="fusionCard">--</strong></div>
<div class="card"><small>Adaptive detections</small><strong id="detectCard">--</strong></div>
<div class="card"><small>Pending approvals</small><strong id="approvalCard">--</strong></div>
<div class="card"><small>Traffic</small><strong id="trafficCard">--</strong></div>
</div>

<div class="layout">
<div>
<div class="panel">
<h2>Dynamic Cyber Threat Network</h2>
<svg id="network" viewBox="0 0 900 470"></svg>
<div class="legend">
● Cyan: normal · ● Gold: elevated priority ·
● Red: high-priority node · ● Green: moving traffic
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
<h2>Simulated Policy Comparison</h2>
<svg id="chart" viewBox="0 0 800 270"></svg>
<div class="legend">
Cyan: threat fusion score ·
Green: balanced residual risk ·
Gold: service-first residual risk ·
Red: risk-first residual risk
</div>
</div>
</div>

<div class="sidebar">
<div class="panel">
<h2>Defense Policy Profiles</h2>
<div class="section">
<label for="profile">Selected policy</label>
<select id="profile">
<option value="balanced">Balanced</option>
<option value="service_first">Service First</option>
<option value="risk_first">Risk First</option>
</select>
<div class="profileGrid">
<div><span class="muted">Residual risk</span>
<strong id="residual">--</strong></div>
<div><span class="muted">Service impact</span>
<strong id="impact">--</strong></div>
<div><span class="muted">Weighted cost</span>
<strong id="cost">--</strong></div>
<div><span class="muted">Pending reviews</span>
<strong id="pending">--</strong></div>
</div>
<p class="muted">
All effects are hypothetical model estimates,
not verified real-world defense outcomes.
</p>
</div>
</div>

<div class="panel">
<h2>Proposed Defense Actions</h2>
<div class="section" id="actions"></div>
</div>

<div class="panel">
<h2>Multi-Agent Decision Feed</h2>
<div id="feed"></div>
</div>
</div>
</div>

<div id="status">Loading V23 simulated research data...</div>
</main>

<script>
"use strict";

const $=id=>document.getElementById(id);
const svg=d3.select("#network");
const linksLayer=svg.append("g");
const particlesLayer=svg.append("g");
const nodesLayer=svg.append("g");

let frames=[];
let tickIndex=0;
let playing=true;
let delay=500;
let timer=null;
let current=null;
let points=null;
let cursor=null;
let positions=new Map();

const colors={
 normal:"#26e6ff",
 low:"#26e6ff",
 medium:"#ffd36c",
 high:"#ff6486",
 critical:"#ff6486"
};

const fmt=value=>Number(value).toFixed(3);

function initNetwork(frame){
 const nodes=frame.nodes;

 nodes.forEach((node,i)=>{
  const angle=i*2*Math.PI/nodes.length-Math.PI/2;
  positions.set(node.id,{
   x:450+330*Math.cos(angle),
   y:230+155*Math.sin(angle)
  });
 });

 linksLayer.selectAll("line")
  .data(frame.links,d=>d.id)
  .join("line")
  .attr("x1",d=>positions.get(d.source).x)
  .attr("y1",d=>positions.get(d.source).y)
  .attr("x2",d=>positions.get(d.target).x)
  .attr("y2",d=>positions.get(d.target).y)
  .attr("stroke","#26e6ff")
  .attr("opacity",.32)
  .attr("stroke-width",2);

 const groups=nodesLayer.selectAll("g")
  .data(nodes,d=>d.id)
  .join("g")
  .attr("transform",d=>{
   const p=positions.get(d.id);
   return `translate(${p.x},${p.y})`;
  });

 groups.append("circle")
  .attr("class","core")
  .attr("r",13)
  .attr("fill","#102744")
  .attr("stroke","#26e6ff")
  .attr("stroke-width",3);

 groups.append("text")
  .attr("text-anchor","middle")
  .attr("y",32)
  .attr("fill","#eaf7ff")
  .attr("font-size",11)
  .text(d=>d.id.toUpperCase());

 groups.append("title");

 const dots=frame.links.flatMap(link=>
  [0,1,2].map(i=>({
   id:link.id+"-"+i,
   linkId:link.id,
   phase:i/3
  }))
 );

 points=particlesLayer.selectAll("circle")
  .data(dots)
  .join("circle")
  .attr("r",3)
  .attr("fill","#46edab");
}

function drawChart(){
 const chart=d3.select("#chart");
 const x=d3.scaleLinear()
  .domain([0,119]).range([45,775]);
 const y=d3.scaleLinear()
  .domain([0,1]).range([230,15]);

 [0,.25,.5,.75,1].forEach(value=>{
  chart.append("line")
   .attr("x1",45).attr("x2",775)
   .attr("y1",y(value)).attr("y2",y(value))
   .attr("stroke","#29415c");

  chart.append("text")
   .attr("x",8).attr("y",y(value)+4)
   .attr("fill","#8faac7")
   .attr("font-size",11)
   .text(value);
 });

 const series=[
  [f=>f.mean_fusion_score,"#26e6ff"],
  [f=>f.profiles.balanced.mean_residual_risk,"#46edab"],
  [f=>f.profiles.service_first.mean_residual_risk,"#ffd36c"],
  [f=>f.profiles.risk_first.mean_residual_risk,"#ff6486"]
 ];

 series.forEach(([getter,color])=>{
  const line=d3.line()
   .x(d=>x(d.tick))
   .y(d=>y(getter(d)));

  chart.append("path")
   .datum(frames)
   .attr("d",line)
   .attr("fill","none")
   .attr("stroke",color)
   .attr("stroke-width",2);
 });

 cursor=chart.append("line")
  .attr("y1",15).attr("y2",230)
  .attr("stroke","#fff")
  .attr("stroke-dasharray","4 4");
}

function render(index){
 tickIndex=index;
 current=frames[index];

 const f=current;
 const selected=$("profile").value;
 const profile=f.profiles[selected];

 $("tickCard").textContent=index+1;
 $("fusionCard").textContent=fmt(f.mean_fusion_score);
 $("detectCard").textContent=f.adaptive_detections;
 $("approvalCard").textContent=profile.approval_pending;
 $("trafficCard").textContent=
  Number(f.traffic_mbps).toFixed(1)+" Mbps";

 $("residual").textContent=fmt(profile.mean_residual_risk);
 $("impact").textContent=fmt(profile.mean_service_impact);
 $("cost").textContent=fmt(profile.mean_weighted_cost);
 $("pending").textContent=profile.approval_pending;
 $("tickText").textContent=(index+1)+" / 120";
 $("slider").value=index;

 const threats=new Map(
  f.threat_nodes.map(t=>[t.node_id,t])
 );
 const networkNodes=new Map(
  f.nodes.map(n=>[n.id,n])
 );

 nodesLayer.selectAll("g").each(function(d){
  const threat=threats.get(d.id);
  const node=networkNodes.get(d.id);

  d3.select(this).select(".core")
   .attr("stroke",colors[threat.priority]||"#26e6ff")
   .attr("r",11+Number(node.load)*9);

  d3.select(this).select("title").text(
   d.id+" | Fusion "+fmt(threat.score)+
   " | Priority "+threat.priority
  );
 });

 const actions=$("actions");
 actions.replaceChildren();

 Object.entries(profile.action_counts).forEach(([action,count])=>{
  const p=document.createElement("p");
  p.textContent=action.replaceAll("_"," ")+": "+count;
  actions.appendChild(p);
 });

 const feed=$("feed");
 feed.replaceChildren();

 const selectedEvents=f.decisions
  .filter(d=>d.profile===selected)
  .filter(d=>
   d.proposed_action!=="observe"
  );

 selectedEvents.forEach(event=>{
  const el=document.createElement("div");
  el.className="event";
  el.textContent=
   event.node_id+" · "+
   event.proposed_action.replaceAll("_"," ")+
   " · "+event.status.replaceAll("_"," ")+
   " · Risk "+fmt(event.residual_risk);
  feed.appendChild(el);
 });

 if(!selectedEvents.length){
  feed.textContent="No intervention proposals at this tick.";
 }

 const xpos=45+index/119*730;
 cursor.attr("x1",xpos).attr("x2",xpos);
}

function animate(time){
 if(current&&points&&playing){
  const linkMap=new Map(
   current.links.map(link=>[link.id,link])
  );

  points.each(function(point){
   const link=linkMap.get(point.linkId);
   if(!link)return;

   const a=positions.get(link.source);
   const b=positions.get(link.target);

   const speed=.00023+
    Number(link.traffic_mbps)/700000;

   const t=(point.phase+time*speed)%1;

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
   render((tickIndex+1)%frames.length);
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

$("profile").onchange=()=>{
 if(frames.length)render(tickIndex);
};

async function main(){
 try{
  if(typeof d3==="undefined"){
   throw Error("D3 library unavailable");
  }

  const response=await fetch(
   "./defense_data.json",
   {cache:"no-store"}
  );

  if(!response.ok){
   throw Error("Cannot load V23 defense_data.json");
  }

  const data=await response.json();

  if(
   data.version!=="V23.5"||
   data.status!=="ADVANCED_DEFENSE_DASHBOARD_PASS"||
   data.simulation_mode!==true||
   !Array.isArray(data.frames)||
   data.frames.length!==120
  ){
   throw Error("Invalid V23.5 research data");
  }

  frames=data.frames;

  if(frames.some((f,i)=>
   f.tick!==i||
   f.nodes.length!==10||
   f.links.length!==11||
   f.threat_nodes.length!==10||
   f.decisions.length!==30
  )){
   throw Error("Invalid timeline or topology");
  }

  initNetwork(frames[0]);
  drawChart();
  render(0);
  schedule();

  $("status").textContent=
   "V23.5 READY · 120 ticks · "+
   "3600 simulated proposals · "+
   "NO REAL NETWORK ACTIONS";

 }catch(error){
  $("status").textContent="ERROR: "+error.message;
  $("status").style.color="#ff6486";
  console.error(error);
 }
}

requestAnimationFrame(animate);
main();
</script>
</body>
</html>
'''


def make_markdown(report):
    metrics = report["metrics"]

    return f"""# Quantum Cyber Defense Arena

## V23.5 - Advanced Cyber Defense Dashboard

**Status:** {report['status']}

**Checks passed:** {report['checks_passed']}

**Checks failed:** {report['checks_failed']}

### Integrated modules

- V22.5: Network Digital Twin
- V23.2: Intelligent Threat Fusion
- V23.3: Adaptive Defense Policy Optimization
- V23.4: Multi-Agent Defense Orchestration

### Research dataset

- Simulation ticks: {metrics['ticks']}
- Network nodes: {metrics['nodes']}
- Network links: {metrics['links']}
- Fusion observations: {metrics['fusion_observations']}
- Orchestration events: {metrics['orchestration_events']}
- Policy profiles: {metrics['profiles']}

### Interactive dashboard

`frontend/public/v23/dashboard.html`

Features:

- Animated D3 network
- Moving synthetic traffic
- Threat-fusion node coloring
- Three selectable defense policy profiles
- Risk-comparison line chart
- Pending-approval statistics
- Multi-agent simulated decision feed
- Play, pause, restart and timeline controls

### Limitations

All telemetry is synthetic.
The fusion scoring is a heuristic.
The policy costs are hypothetical.
Agents are deterministic software roles.
No real defense actions are performed.
No field effectiveness is demonstrated.

### Next stage

V23.6 - Final Research Validation and Release
"""


def main():
    print("=" * 70)
    print("QUANTUM CYBER DEFENSE ARENA")
    print("V23.5 - ADVANCED CYBER DEFENSE DASHBOARD")
    print("=" * 70)

    V23.mkdir(parents=True, exist_ok=True)

    data = load_inputs()
    frames = []
    error = None

    if len(data) == len(SOURCES):
        try:
            validate_inputs(data)

            frames = assemble(data)
            validate_combined(frames)

            check(
                "Dashboard assembly reproducible",
                frames == assemble(data),
            )

            check(
                "HTML includes D3 library",
                "d3@7" in HTML,
            )

            check(
                "HTML includes network graph",
                'id="network"' in HTML,
            )

            check(
                "HTML includes policy selector",
                'id="profile"' in HTML,
            )

            check(
                "HTML includes risk chart",
                'id="chart"' in HTML,
            )

            check(
                "HTML includes replay controls",
                all(
                    marker in HTML
                    for marker in (
                        'id="play"',
                        'id="restart"',
                        'id="slider"',
                    )
                ),
            )

        except (
            OSError,
            ValueError,
            TypeError,
            KeyError,
            IndexError,
        ) as exc:
            error = f"{type(exc).__name__}: {exc}"
            check(
                "Complete dashboard integration",
                False,
                error,
            )

    else:
        error = (
            f"Loaded {len(data)} of "
            f"{len(SOURCES)} source files"
        )
        check(
            "All dashboard sources loaded",
            False,
            error,
        )

    passed = sum(
        item["passed"]
        for item in CHECKS
    )
    failed = len(CHECKS) - passed

    status = (
        "ADVANCED_DEFENSE_DASHBOARD_PASS"
        if failed == 0 and len(frames) == 120
        else "ADVANCED_DEFENSE_DASHBOARD_FAIL"
    )

    metrics = {
        "ticks": len(frames),
        "nodes": 10 if frames else 0,
        "links": 11 if frames else 0,
        "fusion_observations": sum(
            len(frame["threat_nodes"])
            for frame in frames
        ),
        "orchestration_events": sum(
            len(frame["decisions"])
            for frame in frames
        ),
        "profiles": len(PROFILES),
        "real_actions_executed": 0,
    }

    report = {
        "project": "Quantum Cyber Defense Arena",
        "version": "V23.5",
        "module": "Advanced Cyber Defense Dashboard",
        "created_utc": datetime.now(
            timezone.utc
        ).isoformat(),
        "status": status,
        "simulation_mode": True,
        "is_live": False,
        "trained_ai_model_used": False,
        "external_actions_enabled": False,
        "effects_empirically_verified": False,
        "metrics": metrics,
        "source_sha256": {
            name: sha256(path)
            for name, path in SOURCES.items()
            if path.is_file()
        },
        "checks": CHECKS,
        "checks_passed": passed,
        "checks_failed": failed,
        "error": error,
        "next_stage": (
            "V23.6 Final Research Validation and Release"
        ),
    }

    write_json(OUT_REPORT, report)

    if status == "ADVANCED_DEFENSE_DASHBOARD_PASS":
        write_json(
            OUT_DATA,
            {
                "version": "V23.5",
                "status": status,
                "simulation_mode": True,
                "is_live": False,
                "effects_empirically_verified": False,
                "frames": frames,
            },
        )

        OUT_HTML.parent.mkdir(
            parents=True, exist_ok=True
        )
        OUT_HTML.write_text(
            HTML,
            encoding="utf-8",
        )

        OUT_MD.write_text(
            make_markdown(report),
            encoding="utf-8",
        )

    print()
    print("=" * 70)
    print("V23.5 ADVANCED DEFENSE DASHBOARD RESULTS")
    print("=" * 70)
    print("SIMULATION TICKS:", metrics["ticks"])
    print("NETWORK NODES:", metrics["nodes"])
    print("NETWORK LINKS:", metrics["links"])
    print(
        "FUSION OBSERVATIONS:",
        metrics["fusion_observations"],
    )
    print(
        "ORCHESTRATION EVENTS:",
        metrics["orchestration_events"],
    )
    print("POLICY PROFILES:", metrics["profiles"])
    print("REAL ACTIONS EXECUTED: 0")
    print("CHECKS PASSED:", passed)
    print("CHECKS FAILED:", failed)
    print("JSON REPORT:", OUT_REPORT)

    if status == "ADVANCED_DEFENSE_DASHBOARD_PASS":
        print("DASHBOARD:", OUT_HTML)
        print("DATA EXPORT:", OUT_DATA)

    if error:
        print("ERROR:", error)

    print("V23.5 RESULT:", status)
    print("=" * 70)

    return (
        0 if status == "ADVANCED_DEFENSE_DASHBOARD_PASS"
        else 1
    )


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print(
            "V23.5 FAILED:",
            f"{type(exc).__name__}: {exc}",
        )
        sys.exit(1)
