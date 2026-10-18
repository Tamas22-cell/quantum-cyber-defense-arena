
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Stars } from "@react-three/drei";
import { useMemo, useRef } from "react";
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

const NODES: {
  name: string;
  network: string;
  position: Position;
  color: string;
}[] = [
  {
    name: "ETH",
    network: "Ethereum",
    position: [-2, 1, 0],
    color: "#00e5ff",
  },
  {
    name: "BASE",
    network: "Base",
    position: [2, 1, -1],
    color: "#3b82f6",
  },
  {
    name: "ARB",
    network: "Arbitrum",
    position: [-2, -1, 1],
    color: "#a855f7",
  },
  {
    name: "POLY",
    network: "Polygon",
    position: [2, -1, 0],
    color: "#22d3ee",
  },
];

function NetworkNode({
  position,
  color,
  critical,
}: {
  position: Position;
  color: string;
  critical: boolean;
}) {
  const mesh = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!mesh.current) return;

    const time = clock.elapsedTime;

    const pulse = critical
      ? 1 + Math.sin(time * 5) * 0.22
      : 1 + Math.sin(time * 2) * 0.1;

    mesh.current.scale.setScalar(pulse);

    const material =
      mesh.current.material as THREE.MeshStandardMaterial;

    material.emissiveIntensity = critical
      ? 2 + Math.max(0, Math.sin(time * 6)) * 3
      : 1.5;
  });

  return (
    <mesh ref={mesh} position={position}>
      <sphereGeometry args={[0.3, 32, 32]} />
      <meshStandardMaterial
        color={critical ? "#ff1744" : color}
        emissive={critical ? "#ff1744" : color}
        emissiveIntensity={1.5}
        metalness={0.3}
        roughness={0.2}
      />
    </mesh>
  );
}

function Connection({
  end,
  critical,
}: {
  end: Position;
  critical: boolean;
}) {
  const positions = useMemo(
    () => new Float32Array([0, 0, 0, ...end]),
    [end],
  );

  return (
    <line>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <lineBasicMaterial
        color={critical ? "#ff416c" : "#29b6f6"}
        transparent
        opacity={0.6}
      />
    </line>
  );
}

function DataPacket({
  end,
  speed,
  offset,
  critical,
}: {
  end: Position;
  speed: number;
  offset: number;
  critical: boolean;
}) {
  const mesh = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!mesh.current) return;

    const progress =
      (clock.elapsedTime * speed + offset) % 1;

    mesh.current.position.set(
      end[0] * progress,
      end[1] * progress,
      end[2] * progress,
    );

    mesh.current.scale.setScalar(
      0.8 + Math.sin(progress * Math.PI) * 0.5,
    );
  });

  return (
    <mesh ref={mesh}>
      <sphereGeometry args={[0.075, 12, 12]} />
      <meshBasicMaterial
        color={critical ? "#ff1744" : "#00ffcc"}
      />
    </mesh>
  );
}

function NetworkScene({ events = [] }: Props) {
  const group = useRef<THREE.Group>(null);

  const networkRisks = useMemo(() => {
    const risks: Record<string, number> = {};

    for (const event of events) {
      risks[event.network.toLowerCase()] = Math.max(
        risks[event.network.toLowerCase()] ?? 0,
        event.risk_score,
      );
    }

    return risks;
  }, [events]);

  useFrame((_, delta) => {
    if (group.current) {
      group.current.rotation.y += delta * 0.1;
    }
  });

  return (
    <>
      <color attach="background" args={["#061326"]} />

      <ambientLight intensity={0.7} />
      <pointLight position={[5, 5, 5]} intensity={25} />
      <pointLight
        position={[-4, -3, 2]}
        intensity={12}
        color="#9333ea"
      />

      <Stars
        radius={40}
        depth={20}
        count={600}
        factor={2}
        fade
      />

      <group ref={group}>
        <NetworkNode
          position={[0, 0, 0]}
          color="#a855f7"
          critical={false}
        />

        {NODES.map((node, index) => {
          const risk =
            networkRisks[node.network.toLowerCase()] ?? 0;

          const critical = risk >= 80;

          return (
            <group key={node.name}>
              <NetworkNode
                position={node.position}
                color={node.color}
                critical={critical}
              />

              <Connection
                end={node.position}
                critical={critical}
              />

              <DataPacket
                end={node.position}
                speed={0.25 + index * 0.04}
                offset={index * 0.22}
                critical={critical}
              />

              <DataPacket
                end={node.position}
                speed={0.2 + index * 0.03}
                offset={0.5 + index * 0.12}
                critical={critical}
              />
            </group>
          );
        })}
      </group>

      <OrbitControls
        enablePan={false}
        enableDamping
        dampingFactor={0.05}
        minDistance={4}
        maxDistance={12}
      />
    </>
  );
}

export default function CyberNetwork3D({
  events = [],
}: Props) {
  return (
    <div style={{ width: "100%", height: "420px" }}>
      <Canvas camera={{ position: [0, 1.5, 7], fov: 55 }}>
        <NetworkScene events={events} />
      </Canvas>
    </div>
  );
}
