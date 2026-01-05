import React, { Suspense, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, Sky, PerspectiveCamera } from '@react-three/drei';
import { useJarvisStore } from '../store/jarvisStore';
import SceneObject from './SceneObject';

const Scene3D = () => {
  const { sceneData } = useJarvisStore();
  const controlsRef = useRef();

  return (
    <Canvas
      shadows
      gl={{ antialias: true, alpha: true }}
      className="w-full h-full bg-slate-950"
      camera={{ position: [15, 12, 15], fov: 50 }}
    >
      {/* Lighting - Enhanced for better visibility */}
      <ambientLight intensity={0.8} />
      <directionalLight
        position={[15, 15, 10]}
        intensity={1.5}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-far={100}
        shadow-camera-left={-50}
        shadow-camera-right={50}
        shadow-camera-top={50}
        shadow-camera-bottom={-50}
      />
      <pointLight position={[-15, 10, -15]} intensity={0.8} color="#60a5fa" />
      <pointLight position={[15, 5, 15]} intensity={0.6} color="#f59e0b" />

      {/* Environment */}
      <Sky
        distance={450000}
        sunPosition={[0, 1, 0]}
        inclination={0.5}
        azimuth={0.25}
      />

      {/* Grid */}
      <Grid
        args={[100, 100]}
        cellSize={1}
        cellThickness={0.5}
        cellColor="#6b7280"
        sectionSize={10}
        sectionThickness={1}
        sectionColor="#4b5563"
        fadeDistance={50}
        fadeStrength={1}
        followCamera={false}
        infiniteGrid={true}
      />

      {/* Scene Objects */}
      <Suspense fallback={null}>
        {sceneData?.objects?.map((obj, index) => (
          <SceneObject key={obj.id || index} data={obj} />
        ))}
      </Suspense>

      {/* Controls */}
      <OrbitControls
        ref={controlsRef}
        enableDamping
        dampingFactor={0.05}
        minDistance={2}
        maxDistance={100}
        maxPolarAngle={Math.PI / 2}
      />
    </Canvas>
  );
};

export default Scene3D;
