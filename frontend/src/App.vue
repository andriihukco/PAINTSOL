<!-- App.vue -->
<template>
  <div id="app">
    <TopBar
      :selectedColor="selectedColor"
      @color-changed="onColorChanged"
      @wallet-connected="onWalletConnected"
      @wallet-disconnected="onWalletDisconnected"
    />
    <PixelGrid
      :gridSize="2000"
      :cellSize="10"
      :selectedColor="selectedColor"
      :walletAddress="walletAddress"
    />
  </div>
</template>

<script>
import TopBar from './components/TopBar.vue';
import PixelGrid from './components/PixelGrid.vue';

export default {
  name: 'App',
  components: {
    TopBar,
    PixelGrid,
  },
  data() {
    return {
      selectedColor: '#000000',
      walletAddress: null,
    };
  },
  methods: {
    onColorChanged(newColor) {
      this.selectedColor = newColor;
    },
    onWalletConnected(address) {
      console.log('Wallet connected:', address);
      this.walletAddress = address;
    },
    onWalletDisconnected() {
      console.log('Wallet disconnected');
      this.walletAddress = null;
    },
  },
};
</script>

<style>
#app {
  position: relative;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  margin: 0;
  padding-top: 56px; /* Adjust according to the top bar height */
}
</style>