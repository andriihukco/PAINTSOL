<template>
  <div id="app">
    <WalletConnector />
    <!-- Other components go here -->
  </div>
</template>

<script>
import WalletConnector from './components/WalletConnector.vue';

export default {
  name: 'App',
  components: {
    WalletConnector,
  },
};
</script>

<style>
#app {
  position: relative;
  min-height: 100vh;
  background-color: #f5f5f5;
  /* Add padding or margins if necessary */
}
</style>