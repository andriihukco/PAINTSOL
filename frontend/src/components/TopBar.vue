<!-- src/components/TopBar.vue -->
<template>
    <div class="top-bar">
      <!-- Left Section: Color Picker and Mode Switch Buttons -->
      <div class="left-section">
        <!-- Color Picker -->
        <button class="color-picker-button" @click="openColorPickerModal">
          <div
            class="color-display"
            :style="{ backgroundColor: localSelectedColor }"
          ></div>
        </button>
  
        <!-- Mode Switch Buttons -->
        <button
          class="mode-button"
          :class="{ active: localCurrentMode === 'paint' }"
          @click="switchToPaintMode"
        >
          🎨
        </button>
        <button
          class="mode-button"
          :class="{ active: localCurrentMode === 'grab' }"
          @click="switchToGrabMode"
        >
          ✋
        </button>
      </div>
  
      <!-- Center Section: Logo -->
      <div class="center-section">
        <img src="@/assets/logo.png" alt="Logo" class="logo" />
      </div>
  
      <!-- Right Section: Wallet Connector -->
      <div class="right-section">
        <WalletConnector
          @wallet-connected="onWalletConnected"
          @wallet-disconnected="onWalletDisconnected"
        />
      </div>
  
      <!-- Color Picker Modal -->
      <div v-if="showColorPickerModal" class="modal-overlay" @click.self="closeColorPickerModal">
        <div class="modal-content">
          <h3>Select a Color</h3>
          <input
            type="color"
            v-model="localSelectedColor"
          />
          <div class="modal-buttons">
            <button @click="confirmColor">Confirm</button>
            <button @click="closeColorPickerModal">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </template>
  
  <script>
  import WalletConnector from './WalletConnector.vue';
  
  export default {
    name: 'TopBar',
    components: {
      WalletConnector,
    },
    emits: ['color-changed', 'wallet-connected', 'wallet-disconnected', 'mode-changed'],
    props: {
      selectedColor: {
        type: String,
        default: '#000000',
      },
      currentMode: {
        type: String,
        default: 'paint',
      },
    },
    data() {
      return {
        localSelectedColor: this.selectedColor,
        localCurrentMode: this.currentMode,
        showColorPickerModal: false,
      };
    },
    watch: {
      selectedColor(newColor) {
        this.localSelectedColor = newColor;
      },
      currentMode(newMode) {
        this.localCurrentMode = newMode;
      },
    },
    methods: {
      openColorPickerModal() {
        this.showColorPickerModal = true;
      },
      closeColorPickerModal() {
        // Reset the local color to the current selected color
        this.localSelectedColor = this.selectedColor;
        this.showColorPickerModal = false;
      },
      confirmColor() {
        // Emit the color change to the parent component
        this.$emit('color-changed', this.localSelectedColor);
        this.showColorPickerModal = false;
      },
      onWalletConnected(address) {
        this.$emit('wallet-connected', address);
      },
      onWalletDisconnected() {
        this.$emit('wallet-disconnected');
      },
      switchToPaintMode() {
        this.localCurrentMode = 'paint';
        this.$emit('mode-changed', 'paint');
      },
      switchToGrabMode() {
        this.localCurrentMode = 'grab';
        this.$emit('mode-changed', 'grab');
      },
    },
  };
  </script>
  
  <style scoped>
  .top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #512da8; /* Purple background */
    padding: 8px 16px;
    border-bottom: 1px solid #ccc;
    position: fixed;
    top: 0;
    left: 0; /* Ensure no gap on the left */
    width: 100%; /* Cover the full width */
    height: 64px; /* Increase the height */
    box-sizing: border-box;
    z-index: 1000;
  }
  
  .left-section,
  .center-section,
  .right-section {
    display: flex;
    align-items: center;
  }
  
  .left-section {
    flex: 1;
  }
  
  .center-section {
    flex: 1;
    justify-content: center;
  }
  
  .right-section {
    flex: 1;
    justify-content: flex-end;
  }
  
  .mode-button {
    background: none;
    border: none;
    font-size: 28px; /* Increase icon size */
    cursor: pointer;
    margin-right: 12px;
    color: #ffffffaa;
  }
  
  .mode-button.active {
    color: #ffffff;
  }
  
  .mode-button:hover {
    color: #ffffff;
  }
  
  .color-picker-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    margin-right: 12px;
  }
  
  .color-display {
    width: 32px; /* Adjust size */
    height: 32px;
    border: 2px solid #000;
  }
  
  .logo {
    height: 48px; /* Adjust logo height as needed */
    width: auto;
  }
  
  .modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 2000;
  }
  
  .modal-content {
    background-color: #fff;
    padding: 24px;
    border-radius: 8px;
    text-align: center;
  }
  
  .modal-buttons {
    margin-top: 16px;
  }
  
  .modal-buttons button {
    margin: 0 8px;
    padding: 8px 16px;
    cursor: pointer;
  }
  
  @media (max-width: 600px) {
    .mode-button {
      font-size: 24px;
    }
  
    .color-display {
      width: 28px;
      height: 28px;
    }
  
    .logo {
      height: 40px;
    }
  }
  </style>