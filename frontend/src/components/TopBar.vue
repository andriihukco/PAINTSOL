<!-- src/components/TopBar.vue -->
<template>
    <div class="top-bar">
      <!-- Left Section: Mode Switch Buttons -->
      <div class="left-section">
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
  
      <!-- Right Section: Color Picker and Wallet Connector -->
      <div class="right-section">
        <div class="color-picker-container">
          <button class="color-picker-button" @click="toggleColorPicker">
            <div
              class="color-display"
              :style="{ backgroundColor: localSelectedColor }"
            ></div>
          </button>
          <input
            v-show="showColorPicker"
            type="color"
            v-model="localSelectedColor"
            @input="onColorChange"
            @blur="hideColorPicker"
          />
        </div>
        <WalletConnector
          @wallet-connected="onWalletConnected"
          @wallet-disconnected="onWalletDisconnected"
        />
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
        showColorPicker: false,
        localSelectedColor: this.selectedColor,
        localCurrentMode: this.currentMode,
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
      toggleColorPicker() {
        this.showColorPicker = !this.showColorPicker;
      },
      hideColorPicker() {
        this.showColorPicker = false;
      },
      onColorChange() {
        this.$emit('color-changed', this.localSelectedColor);
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
  
  .logo {
    height: 48px; /* Adjust logo height as needed */
    width: auto;
  }
  
  .color-picker-container {
    position: relative;
    margin-right: 16px;
  }
  
  .color-picker-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
  }
  
  .color-display {
    width: 32px; /* Increase size */
    height: 32px;
    border: 2px solid #000;
  }
  
  input[type='color'] {
    position: absolute;
    top: 36px;
    left: 0;
    border: none;
    padding: 0;
    width: 30px;
    height: 30px;
    background: none;
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