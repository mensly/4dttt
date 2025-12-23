import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text } from '@react-three/drei';
import * as THREE from 'three';
import type { Player } from '../types';
import './TesseractView.css';

interface TesseractViewProps {
  boardState: (string | null)[][][][]; // 4D array [w][x][y][z]
  onCellClick: (w: number, x: number, y: number, z: number) => void;
  disabled: boolean;
  players: Player[];
}

/**
 * Convert 4D coordinates to 3D position for visualization.
 * We use a simple projection: map 4D (w,x,y,z) to 3D (x,y,z)
 * with w controlling depth/scale of nested cubes.
 */
/**
 * Project 4D coordinates (w,x,y,z) to 3D space for visualization.
 * Uses a nested cube approach where w determines which cube level.
 */
function project4DTo3D(w: number, x: number, y: number, z: number, scale: number = 1.2): [number, number, number] {
  // Map x,y,z from 0-2 to -1, 0, 1 in 3D space
  const x3d = (x - 1) * scale;
  const y3d = (y - 1) * scale;
  const z3d = (z - 1) * scale;
  
  // Use w to offset into nested cubes (w=0,1,2 become outer, middle, inner or vice versa)
  const wOffset = (w - 1) * 0.8; // Offset for nested cubes
  
  return [x3d + wOffset, y3d + wOffset, z3d + wOffset];
}

/**
 * Tesseract wireframe component - shows nested cubes for visualization
 */
function TesseractWireframe() {
  // Create wireframe for nested cubes representing the 3x3x3x3 structure
  const wireframes = useMemo(() => {
    const size = 1.6;
    const cubes = [];
    
    // Draw wireframe cubes for each w-level (w=0,1,2) slightly offset
    for (let w = 0; w < 3; w++) {
      const offset = (w - 1) * 0.8;
      const points: THREE.Vector3[] = [];
      
      // Generate cube vertices
      const vertices = [
        [-size + offset, -size + offset, -size + offset],
        [size + offset, -size + offset, -size + offset],
        [size + offset, size + offset, -size + offset],
        [-size + offset, size + offset, -size + offset],
        [-size + offset, -size + offset, size + offset],
        [size + offset, -size + offset, size + offset],
        [size + offset, size + offset, size + offset],
        [-size + offset, size + offset, size + offset],
      ].map(v => new THREE.Vector3(...v));
      
      // Edges of the cube
      const edges = [
        [0, 1], [1, 2], [2, 3], [3, 0], // bottom face
        [4, 5], [5, 6], [6, 7], [7, 4], // top face
        [0, 4], [1, 5], [2, 6], [3, 7], // vertical edges
      ];
      
      edges.forEach(([i, j]) => {
        points.push(vertices[i], vertices[j]);
      });
      
      const geometry = new THREE.BufferGeometry().setFromPoints(points);
      cubes.push(
        <lineSegments key={w} geometry={geometry}>
          <lineBasicMaterial 
            color={w === 1 ? "#aaa" : "#666"} 
            opacity={w === 1 ? 0.4 : 0.2} 
            transparent 
          />
        </lineSegments>
      );
    }
    
    return cubes;
  }, []);

  return <group>{wireframes}</group>;
}

/**
 * Board cell marker component
 */
function CellMarker({
  position,
  symbol,
  isEmpty,
  color,
  onClick,
  disabled
}: {
  position: [number, number, number];
  symbol: string | null;
  isEmpty: boolean;
  color: string;
  onClick: () => void;
  disabled: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  
  if (isEmpty && !symbol) {
    // Render small transparent marker for empty cells
    return (
      <mesh
        ref={meshRef}
        position={position}
        onClick={disabled ? undefined : onClick}
        onPointerOver={(e) => {
          if (!disabled) {
            e.stopPropagation();
            document.body.style.cursor = 'pointer';
            if (meshRef.current) {
              meshRef.current.scale.set(1.3, 1.3, 1.3);
            }
          }
        }}
        onPointerOut={(e) => {
          document.body.style.cursor = 'default';
          if (meshRef.current) {
            meshRef.current.scale.set(1, 1, 1);
          }
        }}
      >
        <sphereGeometry args={[0.2, 8, 8]} />
        <meshStandardMaterial color="#fff" transparent opacity={0.2} />
      </mesh>
    );
  }

  return (
    <group position={position}>
      <mesh
        ref={meshRef}
        onClick={disabled ? undefined : onClick}
        onPointerOver={(e) => {
          if (!disabled) {
            e.stopPropagation();
            document.body.style.cursor = 'pointer';
            if (meshRef.current) {
              meshRef.current.scale.set(1.2, 1.2, 1.2);
            }
          }
        }}
        onPointerOut={(e) => {
          document.body.style.cursor = 'default';
          if (meshRef.current) {
            meshRef.current.scale.set(1, 1, 1);
          }
        }}
      >
        <boxGeometry args={[0.5, 0.5, 0.5]} />
        <meshStandardMaterial color={color} metalness={0.3} roughness={0.4} />
      </mesh>
      {symbol && (
        <Text
          position={[0, 0, 0.35]}
          fontSize={0.35}
          color="#fff"
          anchorX="center"
          anchorY="middle"
          outlineWidth={0.02}
          outlineColor="#000"
        >
          {symbol}
        </Text>
      )}
    </group>
  );
}

/**
 * Main Tesseract scene component
 */
function TesseractScene({ boardState, onCellClick, disabled, players }: TesseractViewProps) {
  // Get player color mapping
  const playerColors = useMemo(() => {
    const colors: Record<string, string> = {};
    const colorPalette = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];
    
    players.forEach((player, idx) => {
      colors[player.symbol] = colorPalette[idx % colorPalette.length];
    });
    
    return colors;
  }, [players]);

  // Generate all cell markers
  const cells = useMemo(() => {
    const cells = [];
    
    for (let w = 0; w < 3; w++) {
      for (let x = 0; x < 3; x++) {
        for (let y = 0; y < 3; y++) {
          for (let z = 0; z < 3; z++) {
            const symbol = boardState[w][x][y][z];
            const isEmpty = symbol === null || symbol === undefined || symbol === '';
            const color = symbol ? (playerColors[symbol] || '#888') : '#ccc';
            const position = project4DTo3D(w, x, y, z, 1.5);
            
            cells.push(
              <CellMarker
                key={`${w}-${x}-${y}-${z}`}
                position={position as [number, number, number]}
                symbol={symbol}
                isEmpty={isEmpty}
                color={color}
                onClick={() => onCellClick(w, x, y, z)}
                disabled={disabled}
              />
            );
          }
        }
      }
    }
    
    return cells;
  }, [boardState, playerColors, onCellClick, disabled]);

  return (
    <>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} intensity={1} />
      <pointLight position={[-10, -10, -10]} intensity={0.5} />
      
      <TesseractWireframe />
      {cells}
      
      <OrbitControls
        enableDamping
        dampingFactor={0.05}
        minDistance={5}
        maxDistance={20}
        enablePan={true}
      />
    </>
  );
}

/**
 * Main Tesseract View Component
 */
function TesseractView({ boardState, onCellClick, disabled, players }: TesseractViewProps) {
  return (
    <div className="tesseract-view">
      <Canvas camera={{ position: [8, 8, 8], fov: 60 }}>
        <TesseractScene
          boardState={boardState}
          onCellClick={onCellClick}
          disabled={disabled}
          players={players}
        />
      </Canvas>
      <div className="tesseract-legend">
        <div>3D Tesseract Visualization</div>
        <div>Drag to rotate • Scroll to zoom</div>
        <div>Click on empty cells to make a move</div>
      </div>
    </div>
  );
}

export default TesseractView;

