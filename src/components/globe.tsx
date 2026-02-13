"use client";

import { Suspense } from "react";
import { Canvas, useLoader } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { PredictionResult } from "@/lib/api";

function latLonToVector3(lat: number, lon: number, radius: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lon + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -(radius * Math.sin(phi) * Math.cos(theta)),
    radius * Math.cos(phi),
    radius * Math.sin(phi) * Math.sin(theta)
  );
}

function Earth() {
  const basePath = process.env.NEXT_PUBLIC_BASE_PATH || "";
  const texture = useLoader(THREE.TextureLoader, `${basePath}/textures/earth.jpg`);
  texture.colorSpace = THREE.SRGBColorSpace;
  return (
    <mesh>
      <sphereGeometry args={[2, 64, 64]} />
      <meshStandardMaterial map={texture} />
    </mesh>
  );
}

function Marker({ lat, lon }: { lat: number; lon: number }) {
  const position = latLonToVector3(lat, lon, 2.05);
  return (
    <mesh position={position}>
      <sphereGeometry args={[0.05, 16, 16]} />
      <meshBasicMaterial color="red" />
    </mesh>
  );
}

function FallbackSphere() {
  return (
    <mesh>
      <sphereGeometry args={[2, 64, 64]} />
      <meshStandardMaterial color="#1e90ff" />
    </mesh>
  );
}

interface GlobeProps {
  prediction: PredictionResult | null;
}

export function Globe({ prediction }: GlobeProps) {
  return (
    <div className="h-[500px] w-full">
      <Canvas camera={{ position: [0, 0, 5], fov: 45 }}>
        <ambientLight intensity={0.8} />
        <directionalLight position={[5, 3, 5]} intensity={1} />
        <Suspense fallback={<FallbackSphere />}>
          <Earth />
        </Suspense>
        {prediction && (
          <Marker lat={prediction.latitude} lon={prediction.longitude} />
        )}
        <OrbitControls enableZoom enablePan={false} />
      </Canvas>
    </div>
  );
}
