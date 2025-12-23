import React from 'react';
import type { Player } from '../types';
import './GridView.css';

interface GridViewProps {
  boardState: (string | null)[][][][]; // 4D array [w][x][y][z]
  onCellClick: (w: number, x: number, y: number, z: number) => void;
  disabled: boolean;
  currentPlayerId: string;
  players: Player[];
}

/**
 * Convert 4D coordinates to 2D grid position.
 * grid_row = w * 3 + y
 * grid_col = x * 3 + z
 */
function coordToGrid(w: number, x: number, y: number, z: number): [number, number] {
  const gridRow = w * 3 + y;
  const gridCol = x * 3 + z;
  return [gridRow, gridCol];
}

/**
 * Convert 2D grid position to 4D coordinates.
 */
function gridToCoord(row: number, col: number): [number, number, number, number] {
  const w = Math.floor(row / 3);
  const y = row % 3;
  const x = Math.floor(col / 3);
  const z = col % 3;
  return [w, x, y, z];
}

function GridView({ boardState, onCellClick, disabled, players }: GridViewProps) {
  // Create 9×9 grid from 4D board state
  const grid: (string | null)[][] = Array(9).fill(null).map(() => Array(9).fill(null));
  
  for (let w = 0; w < 3; w++) {
    for (let x = 0; x < 3; x++) {
      for (let y = 0; y < 3; y++) {
        for (let z = 0; z < 3; z++) {
          const [row, col] = coordToGrid(w, x, y, z);
          grid[row][col] = boardState[w][x][y][z];
        }
      }
    }
  }

  const handleCellClick = (row: number, col: number) => {
    console.log('GridView handleCellClick called', { row, col, disabled });
    if (disabled) {
      console.log('Click blocked: disabled is true');
      return;
    }
    const [w, x, y, z] = gridToCoord(row, col);
    const cellValue = grid[row][col];
    console.log('Cell value:', cellValue, 'isEmpty:', cellValue === null || cellValue === undefined || cellValue === '');
    // Check if cell is truly empty (null, undefined, or empty string)
    if (cellValue === null || cellValue === undefined || cellValue === '') {
      console.log('Calling onCellClick with:', { w, x, y, z });
      onCellClick(w, x, y, z);
    } else {
      console.log('Click blocked: cell is not empty');
    }
  };

  const getPlayerColor = (symbol: string | null): string => {
    if (!symbol) return '';
    const player = players.find(p => p.symbol === symbol);
    if (!player) return '';
    
    // Generate a color based on player symbol (simple hash)
    const colors = ['#667eea', '#764ba2', '#f093fb', '#4facfe', '#43e97b', '#fa709a'];
    const index = player.player_id.charCodeAt(0) % colors.length;
    return colors[index];
  };

  return (
    <div className="grid-view">
      <div className="grid-header">
        <div className="grid-header-row">
          <div className="grid-header-cell"></div>
          {Array.from({ length: 9 }, (_, i) => (
            <div key={i} className="grid-header-cell">{i}</div>
          ))}
        </div>
      </div>
      <div className="grid-body">
        {grid.map((row, rowIdx) => (
          <div key={rowIdx} className="grid-row">
            <div className="grid-row-label">{rowIdx}</div>
            {row.map((cell, colIdx) => {
              // Check if cell is truly empty - null, undefined, or empty string
              const isEmpty = cell === null || cell === undefined || cell === '';
              const color = isEmpty ? '' : getPlayerColor(cell);
              const cellDisabled = disabled || !isEmpty;
              
              return (
                <div
                  key={`${rowIdx}-${colIdx}`}
                  className={`grid-cell ${isEmpty ? 'empty' : 'filled'} ${cellDisabled ? 'disabled' : 'clickable'}`}
                  style={color ? { color, borderColor: color } : undefined}
                  onClick={() => handleCellClick(rowIdx, colIdx)}
                  title={isEmpty ? `Position (${Math.floor(rowIdx/3)}, ${Math.floor(colIdx/3)}, ${rowIdx%3}, ${colIdx%3})` : `Player: ${cell}`}
                >
                  {isEmpty ? '·' : cell}
                </div>
              );
            })}
          </div>
        ))}
      </div>
      <div className="grid-legend">
        <div>Mini-board regions:</div>
        <div>W0: rows 0-2, W1: rows 3-5, W2: rows 6-8</div>
        <div>X0: cols 0-2, X1: cols 3-5, X2: cols 6-8</div>
      </div>
    </div>
  );
}

export default GridView;

