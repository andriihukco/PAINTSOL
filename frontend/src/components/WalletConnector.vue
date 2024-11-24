<!-- src/components/WalletConnector.vue -->
<template>
  <div class="wallet-connector">
    <div v-if="!walletAddress">
      <button class="connect-button" @click="connectWallet">Connect Wallet</button>
    </div>
    <div v-else>
      <div class="wallet-info">
        <span class="wallet-address">{{ truncatedAddress }}</span>
        <span class="token-balance">{{ tokenBalance }} $PAINT</span>
        <button class="disconnect-button" @click="disconnectWallet">Disconnect</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'WalletConnector',
  emits: ['wallet-connected', 'wallet-disconnected'],
  setup(props, { emit }) {
    const walletAddress = ref(null);
    const tokenBalance = ref('Loading...');
    const isPhantomInstalled = ref(false);

    // Truncated wallet address for display
    const truncatedAddress = computed(() => {
      if (!walletAddress.value) return '';
      const address = walletAddress.value;
      return `${address.slice(0, 4)}...${address.slice(-4)}`;
    });

    // Check if Phantom is installed
    const checkIfPhantomInstalled = () => {
      if (window.solana && window.solana.isPhantom) {
        isPhantomInstalled.value = true;
      } else {
        isPhantomInstalled.value = false;
        alert('Phantom Wallet not found. Please install it from https://phantom.app/');
      }
    };

    // Connect to Phantom Wallet
    const connectWallet = async () => {
      try {
        const resp = await window.solana.connect();
        walletAddress.value = resp.publicKey.toString();
        emit('wallet-connected', walletAddress.value);
        // Fetch token balance after connecting
        await fetchTokenBalance();
      } catch (err) {
        console.error('Error connecting to Phantom Wallet:', err);
      }
    };

    // Disconnect Wallet
    const disconnectWallet = async () => {
      try {
        await window.solana.disconnect();
        walletAddress.value = null;
        tokenBalance.value = null;
        emit('wallet-disconnected');
      } catch (err) {
        console.error('Error disconnecting from Phantom Wallet:', err);
      }
    };

    // Fetch Token Balance from Backend
    const fetchTokenBalance = async () => {
      try {
        const backendUrl = 'http://localhost:8000/get_token_balance/';
        const response = await fetch(backendUrl, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ address: walletAddress.value }),
        });

        if (response.ok) {
          const data = await response.json();
          const roundedBalance = Math.floor(data.balance);
          tokenBalance.value = roundedBalance;
        } else {
          const errorData = await response.json();
          console.error('Error fetching token balance:', errorData.detail);
          tokenBalance.value = 'Error fetching balance';
        }
      } catch (error) {
        console.error('Network error:', error);
        tokenBalance.value = 'Network error';
      }
    };

    // On component mount, check for Phantom
    checkIfPhantomInstalled();

    return {
      walletAddress,
      tokenBalance,
      connectWallet,
      disconnectWallet,
      truncatedAddress,
    };
  },
};
</script>


<style scoped>
.wallet-connector {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 1000;
  font-family: Arial, sans-serif;
}

.connect-button,
.disconnect-button {
  background-color: #512da8;
  color: #fff;
  border: none;
  padding: 10px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.connect-button:hover,
.disconnect-button:hover {
  background-color: #311b92;
}

.wallet-info {
  display: flex;
  align-items: center;
  background-color: #ffffffee;
  padding: 8px 12px;
  border: 1px solid #ccc;
  border-radius: 6px;
}

.wallet-address {
  margin-right: 12px;
  font-weight: bold;
  color: #333;
}

.token-balance {
  margin-right: 12px;
  color: #666;
}

.disconnect-button {
  background-color: #d32f2f;
}

.disconnect-button:hover {
  background-color: #b71c1c;
}

</style>