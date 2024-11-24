from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
from typing import List

app = FastAPI()

# Set the origins that are allowed to make requests to this API
origins = [
    "http://localhost:8080",  # Frontend origin
    "http://127.0.0.1:8080",  # Sometimes localhost resolves to 127.0.0.1
    # Add other origins if necessary
]

# Add CORS middleware to the app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,            # Origins allowed to communicate with the backend
    allow_credentials=True,
    allow_methods=["*"],              # Allow all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],              # Allow all headers
)

# Endpoint models
class WalletAddress(BaseModel):
    address: str

class PixelData(BaseModel):
    x: int
    y: int
    color: str

@app.post("/get_token_balance/")
async def get_token_balance(wallet: WalletAddress):
    # the token adress
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