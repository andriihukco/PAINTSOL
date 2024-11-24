<!-- src/components/TopBar.vue -->
<template>
    <div class="top-bar">
      <!-- Left side: Color Picker -->
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
  
      <!-- Right side: Wallet Connector -->
      <WalletConnector
        @wallet-connected="onWalletConnected"
        @wallet-disconnected="onWalletDisconnected"
      />
    </div>
  </template>
  
  <script>
  import WalletConnector from './WalletConnector.vue';
  
  export default {
    name: 'TopBar',
    components: {
      WalletConnector,
    },
    emits: ['color-changed', 'wallet-connected', 'wallet-disconnected'],
    props: {
      selectedColor: {
        type: String,
        default: '#000000',
      },
    },
    data() {
      return {
        showColorPicker: false,
        localSelectedColor: this.selectedColor,
      };
    },
    watch: {
      selectedColor(newColor) {
        this.localSelectedColor = newColor;
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
    },
  };
  </script>
  
  <style scoped>
  /* Your existing styles */
  </style>
  <style scoped>
  .top-bar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background-color: #ffffff;
    padding: 8px 16px;
    border-bottom: 1px solid #ccc;
    position: fixed;
    top: 0;
    width: 100%;
    z-index: 1000;
  }
  
  .color-picker-container {
    position: relative;
  }
  
  .color-picker-button {
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
  }
  
  .color-display {
    width: 24px;
    height: 24px;
    border: 1px solid #000;
  }
  
  input[type='color'] {
    position: absolute;
    top: 28px;
    left: 0;
    border: none;
    padding: 0;
    width: 30px;
    height: 30px;
    background: none;
    cursor: pointer;
  }
  </style>