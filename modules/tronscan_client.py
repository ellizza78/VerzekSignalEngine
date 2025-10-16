"""
TronScan API Client - Automated USDT TRC20 Payment Verification
"""

import requests
import os
from datetime import datetime
from typing import Optional, Dict, List
from utils.logger import log_event


class TronScanClient:
    """
    Client for TronScan API to verify USDT TRC20 transactions
    """
    
    def __init__(self):
        self.api_key = os.environ.get('TRONSCAN_API_KEY', '')
        self.base_url = "https://apilist.tronscanapi.com/api"
        self.usdt_contract = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"  # USDT TRC20
        self.wallet_address = os.environ.get('USDT_TRC20_WALLET', '')
    
    def verify_transaction(self, tx_hash: str, expected_amount: float) -> Dict:
        """
        Verify a USDT TRC20 transaction
        
        Returns:
            {
                'verified': bool,
                'amount': float,
                'from_address': str,
                'to_address': str,
                'timestamp': str,
                'confirmations': int,
                'status': str
            }
        """
        try:
            # Get transaction details
            url = f"{self.base_url}/transaction-info"
            params = {'hash': tx_hash}
            
            headers = {}
            if self.api_key:
                headers['TRON-PRO-API-KEY'] = self.api_key
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                log_event("TRONSCAN", f"API error: {response.status_code}")
                return {
                    'verified': False,
                    'error': f'API returned {response.status_code}'
                }
            
            data = response.json()
            
            # Check if transaction exists
            if not data or 'contractRet' not in data:
                return {
                    'verified': False,
                    'error': 'Transaction not found'
                }
            
            # Check transaction success
            if data.get('contractRet') != 'SUCCESS':
                return {
                    'verified': False,
                    'error': f"Transaction failed: {data.get('contractRet')}"
                }
            
            # Parse TRC20 transfer
            transfer_info = self._parse_trc20_transfer(data)
            
            if not transfer_info:
                return {
                    'verified': False,
                    'error': 'Not a valid USDT TRC20 transfer'
                }
            
            # Verify recipient address
            if transfer_info['to_address'].lower() != self.wallet_address.lower():
                return {
                    'verified': False,
                    'error': f"Wrong recipient address. Expected {self.wallet_address}"
                }
            
            # Verify amount (with 0.01 USDT tolerance for fees)
            amount_usdt = transfer_info['amount']
            tolerance = 0.01
            
            if abs(amount_usdt - expected_amount) > tolerance:
                return {
                    'verified': False,
                    'error': f"Amount mismatch. Expected {expected_amount}, got {amount_usdt}"
                }
            
            # Get confirmations
            confirmations = data.get('confirmations', 0)
            
            # CRITICAL: Require minimum 19 confirmations for TRC20 finality
            MIN_CONFIRMATIONS = 19
            
            if confirmations < MIN_CONFIRMATIONS:
                return {
                    'verified': False,
                    'error': f'Insufficient confirmations: {confirmations}/{MIN_CONFIRMATIONS}. Wait for more confirmations.',
                    'amount': amount_usdt,
                    'confirmations': confirmations,
                    'required_confirmations': MIN_CONFIRMATIONS,
                    'tx_hash': tx_hash
                }
            
            # Successful verification with sufficient confirmations
            result = {
                'verified': True,
                'amount': amount_usdt,
                'from_address': transfer_info['from_address'],
                'to_address': transfer_info['to_address'],
                'timestamp': datetime.fromtimestamp(data.get('timestamp', 0) / 1000).isoformat(),
                'confirmations': confirmations,
                'status': 'confirmed',
                'tx_hash': tx_hash
            }
            
            log_event("TRONSCAN", f"Verified TX {tx_hash}: {amount_usdt} USDT from {transfer_info['from_address']}")
            
            return result
            
        except requests.exceptions.Timeout:
            log_event("ERROR", "TronScan API timeout")
            return {'verified': False, 'error': 'API timeout'}
            
        except Exception as e:
            log_event("ERROR", f"TronScan verification failed: {str(e)}")
            return {'verified': False, 'error': str(e)}
    
    def _parse_trc20_transfer(self, tx_data: dict) -> Optional[Dict]:
        """Parse TRC20 transfer from transaction data"""
        try:
            # Check for TRC20 transfer event
            trc20_transfers = tx_data.get('trc20TransferInfo', [])
            
            for transfer in trc20_transfers:
                # Check if it's USDT
                if transfer.get('contract_address', '').lower() == self.usdt_contract.lower():
                    # USDT has 6 decimals
                    amount = float(transfer.get('amount_str', 0)) / 1_000_000
                    
                    return {
                        'from_address': transfer.get('from_address', ''),
                        'to_address': transfer.get('to_address', ''),
                        'amount': amount,
                        'contract': transfer.get('contract_address', '')
                    }
            
            return None
            
        except Exception as e:
            log_event("ERROR", f"Failed to parse TRC20 transfer: {str(e)}")
            return None
    
    def get_wallet_transactions(self, limit: int = 20) -> List[Dict]:
        """
        Get recent transactions for the wallet
        """
        try:
            url = f"{self.base_url}/token_trc20/transfers"
            params = {
                'relatedAddress': self.wallet_address,
                'contract_address': self.usdt_contract,
                'limit': limit
            }
            
            headers = {}
            if self.api_key:
                headers['TRON-PRO-API-KEY'] = self.api_key
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code != 200:
                return []
            
            data = response.json()
            transfers = data.get('token_transfers', [])
            
            result = []
            for transfer in transfers:
                amount = float(transfer.get('quant', 0)) / 1_000_000
                result.append({
                    'tx_hash': transfer.get('transaction_id'),
                    'from': transfer.get('from_address'),
                    'to': transfer.get('to_address'),
                    'amount': amount,
                    'timestamp': datetime.fromtimestamp(transfer.get('block_ts', 0) / 1000).isoformat()
                })
            
            return result
            
        except Exception as e:
            log_event("ERROR", f"Failed to get wallet transactions: {str(e)}")
            return []
    
    def check_minimum_confirmations(self, tx_hash: str, min_confirmations: int = 19) -> bool:
        """
        Check if transaction has minimum confirmations
        TronScan recommends 19 confirmations for finality
        """
        try:
            url = f"{self.base_url}/transaction-info"
            params = {'hash': tx_hash}
            
            headers = {}
            if self.api_key:
                headers['TRON-PRO-API-KEY'] = self.api_key
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                confirmations = data.get('confirmations', 0)
                return confirmations >= min_confirmations
            
            return False
            
        except Exception as e:
            log_event("ERROR", f"Failed to check confirmations: {str(e)}")
            return False


# Global TronScan client instance
tronscan_client = TronScanClient()
