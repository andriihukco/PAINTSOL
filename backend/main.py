from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import time
import nacl.signing
import nacl.encoding
import base64
import asyncio
import requests
import base58

app = FastAPI()

# CORS configuration
origins = [
    "http://localhost:8080",
    "http://127.0.0.1:8080",
    # Add your production frontend URL here
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Origins allowed to communicate with the backend
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)

# In-memory data stores (use a database in production)
grid_state = {}         # Key: 'x,y', Value: color
user_cooldowns = {}     # Key: wallet_address, Value: timestamp of last action

# WebSocket connections
connected_clients = []

# Data models
class WalletAddress(BaseModel):
    address: str

class PixelUpdate(BaseModel):
    x: int
    y: int
    color: str
    wallet_address: str
    signature: str  # Base64-encoded signature

class GridState(BaseModel):
    grid: dict  # Key: 'x,y', Value: color

# Endpoint to fetch the grid state
@app.get("/grid")
async def get_grid():
    return grid_state

# Endpoint to update a pixel
@app.post("/grid/pixel")
async def update_pixel(pixel: PixelUpdate):
    wallet_address = pixel.wallet_address
    x = pixel.x
    y = pixel.y
    color = pixel.color
    signature = pixel.signature

    # Validate input
    if not (0 <= x < 2000 and 0 <= y < 2000):
        raise HTTPException(status_code=400, detail="Invalid pixel coordinates.")

    if not color.startswith("#") or len(color) != 7:
        raise HTTPException(status_code=400, detail="Invalid color format.")

    # Verify signature
    message = f"{x},{y},{color}"
    if not verify_signature(wallet_address, signature, message):
        raise HTTPException(status_code=401, detail="Signature verification failed.")

    # Check cooldown (example: 60 seconds)
    current_time = time.time()
    cooldown_period = 1  # seconds

    last_action_time = user_cooldowns.get(wallet_address, 0)
    if current_time - last_action_time < cooldown_period:
        remaining = cooldown_period - (current_time - last_action_time)
        raise HTTPException(
            status_code=429,
            detail=f"Cooldown period active. Try again in {int(remaining)} seconds.",
        )

    # Update grid state
    key = f"{x},{y}"
    grid_state[key] = color

    # Update user's last action time
    user_cooldowns[wallet_address] = current_time

    # Broadcast the update to all connected clients
    await broadcast_pixel_update(x, y, color)

    return {"status": "success"}

# Endpoint to get the token balance of a wallet
@app.post("/get_token_balance/")
async def get_token_balance(wallet: WalletAddress):
    # The token mint address (replace with your actual token's mint address)
    token_mint_address = 'iecG5qVPr33H5L4DJeYPrEe9Kmi2hKvWfoHbe33pump'

    # Solana RPC endpoint
    url = "https://api.mainnet-beta.solana.com"
    headers = {
        "Content-Type": "application/json"
    }

    # JSON RPC payload to get token accounts by owner
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getTokenAccountsByOwner",
        "params": [
            wallet.address,
            {
                "mint": token_mint_address
            },
            {
                "encoding": "jsonParsed"
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()

        # Check for errors in the response
        if 'error' in data:
            raise HTTPException(status_code=500, detail=f"Solana RPC error: {data['error']['message']}")

        # Extract and sum the balances from all accounts holding the token
        total_balance = 0
        accounts = data.get('result', {}).get('value', [])

        for account in accounts:
            amount = account['account']['data']['parsed']['info']['tokenAmount']['uiAmount']
            total_balance += amount

        return {"balance": total_balance}

    except requests.exceptions.RequestException as e:
        # Handle network exceptions
        raise HTTPException(status_code=500, detail=f"Network error: {str(e)}")
    except Exception as e:
        # Handle other exceptions
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# WebSocket endpoint for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection alive
    except WebSocketDisconnect:
        connected_clients.remove(websocket)

# Function to broadcast pixel updates to all connected clients
async def broadcast_pixel_update(x: int, y: int, color: str):
    message = {"x": x, "y": y, "color": color}
    for client in connected_clients:
        try:
            await client.send_json(message)
        except:
            pass  # Ignore failed sends

# Function to verify the signature
def verify_signature(wallet_address: str, signature: str, message: str) -> bool:
    try:
        # Decode the public key from the wallet address (assumed to be in base58)
        public_key_bytes = base58.b58decode(wallet_address)
        verify_key = nacl.signing.VerifyKey(public_key_bytes)

        # Decode the signature (assumed to be base64-encoded)
        signature_bytes = base64.b64decode(signature)

        # Verify the signature
        verify_key.verify(message.encode('utf-8'), signature_bytes)
        return True
    except Exception as e:
        print(f"Signature verification error: {e}")
        return False

