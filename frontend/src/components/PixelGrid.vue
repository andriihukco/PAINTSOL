<!-- src/components/PixelGrid.vue -->
<template>
    <div class="pixel-grid-container">
      <canvas
        ref="canvas"
        :width="canvasWidth"
        :height="canvasHeight"
        @mousedown="onMouseDown"
        @mousemove="onMouseMove"
        @mouseup="onMouseUp"
        @mouseleave="onMouseLeave"
        @wheel.prevent="onWheel"
      ></canvas>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PixelGrid',
    props: {
      gridSize: {
        type: Number,
        default: 2000,
      },
      cellSize: {
        type: Number,
        default: 10,
      },
      selectedColor: {
        type: String,
        default: '#000000',
      },
      walletAddress: {
        type: String,
        default: null,
      },
      currentMode: {
        type: String,
        default: 'paint',
      },
    },
    data() {
      return {
        canvasWidth: window.innerWidth,
        canvasHeight: window.innerHeight - 56,
        context: null,
        isPanning: false,
        startX: 0,
        startY: 0,
        offsetX: 0,
        offsetY: 0,
        scale: 1,
        cellColors: {},
        isDrawing: false,
        socket: null,
        hoveredCellX: null,
        hoveredCellY: null,
      };
    },
    mounted() {
      this.context = this.$refs.canvas.getContext('2d');
      this.adjustCanvasSize();
      this.fetchGridState();
      this.setupWebSocket();
      window.addEventListener('resize', this.onResize);
    },
    beforeUnmount() {
      window.removeEventListener('resize', this.onResize);
      if (this.socket) {
        this.socket.close();
      }
    },
    methods: {
      adjustCanvasSize() {
        this.canvasWidth = window.innerWidth;
        this.canvasHeight = window.innerHeight - 56;
        this.drawGrid();
      },
      async fetchGridState() {
        try {
          const response = await fetch('http://localhost:8000/grid');
          if (response.ok) {
            const data = await response.json();
            this.cellColors = data;
            this.drawGrid();
          } else {
            console.error('Error fetching grid state');
          }
        } catch (error) {
          console.error('Network error:', error);
        }
      },
      setupWebSocket() {
        this.socket = new WebSocket('ws://localhost:8000/ws');
  
        this.socket.onmessage = (event) => {
          const data = JSON.parse(event.data);
          const key = `${data.x},${data.y}`;
          this.cellColors[key] = data.color;
          this.drawGrid();
        };
  
        this.socket.onclose = () => {
          console.warn('WebSocket connection closed');
        };
      },
      drawGrid() {
        const ctx = this.context;
        const gridSize = this.gridSize;
        const cellSize = this.cellSize;
        const width = this.canvasWidth;
        const height = this.canvasHeight;
  
        // Clear the canvas
        ctx.clearRect(0, 0, width, height);
  
        // Apply transformations
        ctx.save();
        ctx.translate(this.offsetX, this.offsetY);
        ctx.scale(this.scale, this.scale);
  
        // Calculate visible bounds
        const startX = Math.max(0, Math.floor(-this.offsetX / (this.scale * cellSize)));
        const endX = Math.min(
          gridSize,
          Math.ceil((width - this.offsetX) / (this.scale * cellSize))
        );
        const startY = Math.max(0, Math.floor(-this.offsetY / (this.scale * cellSize)));
        const endY = Math.min(
          gridSize,
          Math.ceil((height - this.offsetY) / (this.scale * cellSize))
        );
  
        // Draw colored cells
        for (let x = startX; x < endX; x++) {
          for (let y = startY; y < endY; y++) {
            const key = `${x},${y}`;
            if (this.cellColors[key]) {
              ctx.fillStyle = this.cellColors[key];
            } else {
              ctx.fillStyle = '#ffffff';
            }
            ctx.fillRect(x * cellSize, y * cellSize, cellSize, cellSize);
          }
        }
  
        // Highlight the hovered cell
        if (
          this.hoveredCellX !== null &&
          this.hoveredCellY !== null &&
          this.currentMode === 'paint'
        ) {
          ctx.fillStyle = 'rgba(0, 0, 0, 0.2)'; // Semi-transparent overlay
          ctx.fillRect(
            this.hoveredCellX * cellSize,
            this.hoveredCellY * cellSize,
            cellSize,
            cellSize
          );
        }
  
        // Draw grid lines
        ctx.strokeStyle = '#e0e0e0';
        ctx.lineWidth = 1 / this.scale;
  
        // Vertical lines
        for (let x = startX; x <= endX; x++) {
          ctx.beginPath();
          ctx.moveTo(x * cellSize, startY * cellSize);
          ctx.lineTo(x * cellSize, endY * cellSize);
          ctx.stroke();
        }
  
        // Horizontal lines
        for (let y = startY; y <= endY; y++) {
          ctx.beginPath();
          ctx.moveTo(startX * cellSize, y * cellSize);
          ctx.lineTo(endX * cellSize, y * cellSize);
          ctx.stroke();
        }
  
        // Restore context
        ctx.restore();
      },
      onResize() {
        this.adjustCanvasSize();
      },
      onMouseDown(event) {
        if (this.currentMode === 'paint' && event.button === 0) {
          // Left-click: color a cell
          const { cellX, cellY } = this.getCellCoordinates(event);
  
          if (cellX === null || cellY === null) {
            return;
          }
  
          // Send the color change to the backend
          this.updatePixelOnServer(cellX, cellY, this.selectedColor);
        } else if (
          this.currentMode === 'grab' &&
          (event.button === 0 || event.button === 1 || event.button === 2)
        ) {
          // Start panning
          this.isPanning = true;
          this.startX = event.clientX - this.offsetX;
          this.startY = event.clientY - this.offsetY;
        }
      },
      onMouseMove(event) {
        if (this.isPanning) {
          this.offsetX = event.clientX - this.startX;
          this.offsetY = event.clientY - this.startY;
          this.requestRedraw();
        } else if (this.currentMode === 'paint') {
          const { cellX, cellY } = this.getCellCoordinates(event);
  
          if (cellX !== this.hoveredCellX || cellY !== this.hoveredCellY) {
            this.hoveredCellX = cellX;
            this.hoveredCellY = cellY;
            this.requestRedraw();
          }
        }
      },
      onMouseUp() {
        if (this.isPanning) {
          this.isPanning = false;
        }
      },
      onMouseLeave() {
        this.hoveredCellX = null;
        this.hoveredCellY = null;
        this.requestRedraw();
      },
      onWheel(event) {
        const zoomFactor = 0.001;
        const delta = -event.deltaY * zoomFactor;
        const newScale = this.scale + delta;
  
        if (newScale < 0.1 || newScale > 10) {
          return;
        }
  
        const rect = this.$refs.canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;
  
        const worldX = (mouseX - this.offsetX) / this.scale;
        const worldY = (mouseY - this.offsetY) / this.scale;
  
        this.scale = newScale;
  
        this.offsetX = mouseX - worldX * this.scale;
        this.offsetY = mouseY - worldY * this.scale;
  
        this.requestRedraw();
      },
      requestRedraw() {
        if (!this.isDrawing) {
          this.isDrawing = true;
          requestAnimationFrame(() => {
            this.drawGrid();
            this.isDrawing = false;
          });
        }
      },
      async updatePixelOnServer(x, y, color) {
        if (!this.walletAddress) {
          alert('Please connect your wallet to paint pixels.');
          return;
        }
  
        try {
          const message = `${x},${y},${color}`;
          const encodedMessage = new TextEncoder().encode(message);
          const signedMessage = await window.solana.signMessage(encodedMessage, 'utf8');
          const signatureBase64 = btoa(
            String.fromCharCode(...new Uint8Array(signedMessage.signature))
          );
  
          const response = await fetch('http://localhost:8000/grid/pixel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              x,
              y,
              color,
              wallet_address: this.walletAddress,
              signature: signatureBase64,
            }),
          });
  
          if (response.ok) {
            // Update local grid state after successful backend update
            const key = `${x},${y}`;
            this.cellColors[key] = color;
            this.drawGrid();
          } else {
            const errorData = await response.json();
            console.error('Error updating pixel:', errorData.detail);
            alert(`Error updating pixel: ${errorData.detail}`);
          }
        } catch (error) {
          console.error('Error updating pixel:', error);
          alert('Error updating pixel. Please try again.');
        }
      },
      getCellCoordinates(event) {
        const rect = this.$refs.canvas.getBoundingClientRect();
        const x = (event.clientX - rect.left - this.offsetX) / (this.scale * this.cellSize);
        const y = (event.clientY - rect.top - this.offsetY) / (this.scale * this.cellSize);
  
        const cellX = Math.floor(x);
        const cellY = Math.floor(y);
  
        if (cellX < 0 || cellX >= this.gridSize || cellY < 0 || cellY >= this.gridSize) {
          return { cellX: null, cellY: null };
        }
  
        return { cellX, cellY };
      },
    },
  };
  </script>
  
  <style scoped>
  .pixel-grid-container {
    width: 100%;
    height: calc(100% - 56px);
    overflow: hidden;
    position: relative;
  }
  
  canvas {
    display: block;
    background-color: #f8f8f8;
    cursor: crosshair;
    width: 100%;
    height: 100%;
  }
  
  canvas:active {
    cursor: grabbing;
  }
  
  canvas.grabbing {
    cursor: grabbing !important;
  }
  
  canvas.painting {
    cursor: crosshair !important;
  }
  </style>