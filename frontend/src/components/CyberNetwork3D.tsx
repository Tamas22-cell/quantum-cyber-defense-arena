
import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { Html, Line, OrbitControls, Stars } from "@react-three/drei";
import * as THREE from "three";

type Position = [number, number, number];

export type NetworkThreat = {
  network: string;
  risk_score: number;
  severity: string;
};

type Props = {
  events?: NetworkThreat[];
};

type NodeDefinition = {
  name: string;
  network: string;
  position: Position;
  color: string;
};

const NODES: NodeDefinition[] = [
  {
    name: "ETH",
    network: "Ethereum",
    position: [-2.1, 1.2, 0.3],
    color: "#00e5ff",
  },
  {
    name: "BASE",
    network: "Base",
    position: [2.1, 1.1, -0.5],
    color: "#398bff",
  },
  {
    name: "ARB",
    network: "Arbitrum",
    position: [-2.0, -1.2, 0.8],
    color: "#a855f7",
  },
  {
    name: "POLY",
    network: "Polygon",
    position: [2.0, -1.1, 0.4],
    color: "#20f4d6",
  },
];

function CyberNode({
  position,
  color,
  label,
  risk,
}: {
  position: Position;
  color: string;
  label: string;
  risk: number;
}) {
  const sphere = useRef<THREE.Mesh>(null);
  const ring = useRef<THREE.Mesh>(null);
  const critical = risk >= 80;
  const activeColor = critical ? "#ff315d" : color;

  useFrame(({ clock }, delta) => {
    const time = clock.elapsedTime;

    if (sphere.current) {
      const pulse = critical
        ? 1 + Math.sin(time * 6) * 0.22
        : 1 + Math.sin(time * 2) * 0.07;

      sphere.current.scale.setScalar(pulse);

      const material =
        sphere.current.material as THREE.MeshStandardMaterial;

      material.emissiveIntensity = critical
        ? 2.5 + Math.max(0, Math.sin(time * 6)) * 2
        : 1.6;
    }

    if (ring.current) {
      ring.current.rotation.z += delta * 0.6;

      const pulse =
        1 + Math.sin(time * (critical ? 5 : 2)) * 0.12;

      ring.current.scale.setScalar(pulse);
    }
  });

  return (
    <group position={position}>
      <mesh ref={sphere}>
        <sphereGeometry args={[0.25, 24, 24]} />
        <meshStandardMaterial
          color={activeColor}
          emissive={activeColor}
          emissiveIntensity={2}
          metalness={0.25}
          roughness={0.2}
        />
      </mesh>

      <mesh ref={ring}>
        <torusGeometry args={[0.39, 0.018, 8, 64]} />
        <meshBasicMaterial
          color={activeColor}
          transparent
          opacity={0.85}
          depthWrite={false}
        />
      </mesh>

      {critical && (
        <mesh>
          <sphereGeometry args={[0.41, 16, 16]} />
          <meshBasicMaterial
            color="#ff315d"
            transparent
            opacity={0.12}
            depthWrite={false}
          />
        </mesh>
      )}

      <Html
        center
        position={[0, 0.57, 0]}
        distanceFactor={9}
        style={{ pointerEvents: "none" }}
      >
        <div
          style={{
            color: activeColor,
            fontSize: 11,
            fontWeight: 800,
            background: "rgba(2,12,31,0.9)",
            border: `1px solid ${activeColor}`,
            borderRadius: 7,
            padding: "5px 9px",
            whiteSpace: "nowrap",
            boxShadow: `0 0 14px ${activeColor}55`,
          }}
        >
          {label}
          {critical ? " ⚠" : ""}
        </div>
      </Html>
    </group>
  );
}

function MovingPacket({
  curve,
  speed,
  offset,
  critical,
  size,
}: {
  curve: THREE.QuadraticBezierCurve3;
  speed: number;
  offset: number;
  critical: boolean;
  size: number;
}) {
  const mesh = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!mesh.current) return;

    const progress =
      (clock.elapsedTime * speed + offset) % 1;

    const point = curve.getPointAt(progress);

    mesh.current.position.copy(point);

    const pulse =
      0.8 + Math.sin(progress * Math.PI) * 0.6;

    mesh.current.scale.setScalar(pulse);
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[size, 12, 12]} />
      <meshBasicMaterial
        color={critical ? "#ff315d" : "#00f5ff"}
        toneMapped={false}
      />
      <pointLight
        color={critical ? "#ff315d" : "#00f5ff"}
        intensity={0.45}
        distance={0.9}
      />
    </mesh>
  );
}

function Connection({
  end,
  index,
  critical,
}: {
  end: Position;
  index: number;
  critical: boolean;
}) {
  const curve = useMemo(
    () =>
      new THREE.QuadraticBezierCurve3(
        new THREE.Vector3(0, 0, 0),
        new THREE.Vector3(
          end[0] * 0.5,
          end[1] * 0.5 + 0.45,
          end[2] * 0.5 + 0.35
        ),
        new THREE.Vector3(...end)
      ),
    [end]
  );

  const points = useMemo(
    () =>
      curve.getPoints(50).map(
        (p) => [p.x, p.y, p.z] as Position
      ),
    [curve]
  );

  return (
    <group>
      <Line
        points={points}
        color={critical ? "#ff315d" : "#00ccff"}
        lineWidth={critical ? 2.5 : 1.6}
        transparent
        opacity={0.75}
      />

      {[0, 1, 2, 3, 4].map((packet) => (
        <MovingPacket
          key={packet}
          curve={curve}
          speed={0.10 + index * 0.015}
          offset={packet * 0.2 + index * 0.07}
          critical={critical}
          size={packet === 0 ? 0.085 : 0.045}
        />
      ))}
    </group>
  );
}

function EnergyRings() {
  const group = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.12;
      group.current.rotation.z += delta * 0.035;
    }
  });

  return (
    <group ref={group}>
      {[1.0, 1.7, 2.5, 3.0].map((radius, index) => (
        <mesh
          key={radius}
          rotation={[
            Math.PI / 2.5 + index * 0.2,
            index * 0.45,
            index * 0.2,
          ]}
        >
          <torusGeometry args={[radius, 0.01, 6, 120]} />
          <meshBasicMaterial
            color={
              index % 2 === 0 ? "#00ddff" : "#a855f7"
            }
            transparent
            opacity={0.25}
            depthWrite={false}
          />
        </mesh>
      ))}
    </group>
  );
}

function Scene({ events = [] }: Props) {
  const networkGroup = useRef<THREE.Group>(null);

  const risks = useMemo(() => {
    const result: Record<string, number> = {};

    for (const event of events) {
      const key = event.network.toLowerCase();

      result[key] = Math.max(
        result[key] ?? 0,
        event.risk_score
      );
    }

    return result;
  }, [events]);

  useFrame((_, delta) => {
    if (networkGroup.current) {
      networkGroup.current.rotation.y += delta * 0.07;
    }
  });

  return (
    <>
      <color attach="background" args={["#061326"]} />

      <ambientLight intensity={0.8} />

      <pointLight
        position={[4, 5, 5]}
        intensity={18}
        color="#00e5ff"
      />

      <pointLight
        position={[-4, -3, 4]}
        intensity={12}
        color="#a855f7"
      />

      <Stars
        radius={45}
        depth={25}
        count={1000}
        factor={2}
        fade
        speed={0.5}
      />

      <group ref={networkGroup}>
        <EnergyRings />

        <CyberNode
          position={[0, 0, 0]}
          color="#bd7fff"
          label="AI CORE"
          risk={0}
        />

        {NODES.map((node, index) => {
          const risk =
            risks[node.network.toLowerCase()] ?? 0;

          return (
            <group key={node.name}>
              <CyberNode
                position={node.position}
                color={node.color}
                label={node.name}
                risk={risk}
              />

              <Connection
                end={node.position}
                index={index}
                critical={risk >= 80}
              />
            </group>
          );
        })}
      </group>

      <OrbitControls
        enablePan={false}
        enableRotate
        enableZoom
        enableDamping
        dampingFactor={0.06}
        minDistance={4}
        maxDistance={11}
      />
    </>
  );
}

export default function CyberNetwork3D({
  events = [],
}: Props) {
  return (
    <div style={{ width: "100%", height: "100%" }}>
      <Canvas
        camera={{
          position: [0, 1.4, 7.5],
          fov: 52,
        }}
        dpr={[1, 1.5]}
        gl={{
          antialias: true,
          alpha: false,
        }}
      >
        <Scene events={events} />
      </Canvas>
    </div>
  );
}
