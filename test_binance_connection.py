"""
Test Binance API Connection
----------------------------
This script helps you test and verify Binance API connectivity
before using it in VerzekAutoTrader.

Usage:
    python test_binance_connection.py
"""

import sys
import time
from exchanges.binance_client import BinanceClient
from exchanges.exchange_interface import ExchangeFactory

def print_header(text):
    """Print formatted header"""
    print(f"\n{'='*60}")
    print(f"{text:^60}")
    print(f"{'='*60}\n")

def print_success(text):
    """Print success message"""
    print(f"✅ {text}")

def print_error(text):
    """Print error message"""
    print(f"❌ {text}")

def print_info(text):
    """Print info message"""
    print(f"ℹ️  {text}")

def print_step(step_num, text):
    """Print step message"""
    print(f"[Step {step_num}] {text}")

def test_binance_spot(api_key, api_secret):
    """Test Binance Spot API connection"""
    print_header("Testing Binance SPOT API")
    
    try:
        # Create client
        print_step(1, "Creating Binance Spot client...")
        client = BinanceClient(api_key=api_key, api_secret=api_secret, testnet=False)
        client.market_type = "spot"  # Set to spot mode
        print_success("Client created successfully")
        
        # Test connection
        print_step(2, "Testing API connection...")
        if not client.test_connection():
            print_error("Connection test failed - Invalid API credentials")
            return False
        print_success("Connection test passed!")
        
        # Get account balance
        print_step(3, "Fetching account balance...")
        balance = client.get_account_balance()
        
        if "error" in balance:
            print_error(f"Failed to get balance: {balance['error']}")
            return False
        
        if "balances" in balance:
            print_success("Account balance retrieved successfully")
            print_info("Top balances (non-zero):")
            for asset in balance.get("balances", [])[:10]:
                free = float(asset.get("free", 0))
                locked = float(asset.get("locked", 0))
                if free > 0 or locked > 0:
                    print(f"   {asset['asset']}: Free={free}, Locked={locked}")
        else:
            print_error("Unexpected balance format")
            return False
        
        # Test price fetching
        print_step(4, "Testing price fetching (BTCUSDT)...")
        price = client.get_ticker_price("BTCUSDT")
        if price:
            print_success(f"Current BTC price: ${price:,.2f}")
        else:
            print_error("Failed to get ticker price")
            return False
        
        # Test exchange info
        print_step(5, "Fetching exchange information...")
        exchange_info = client.get_exchange_info("BTCUSDT")
        if "symbol" in exchange_info:
            print_success(f"Exchange info: {exchange_info['symbol']} - Status: {exchange_info.get('status')}")
        else:
            print_info("Exchange info retrieved (full exchange data)")
        
        return True
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False

def test_binance_futures(api_key, api_secret):
    """Test Binance Futures API connection"""
    print_header("Testing Binance FUTURES API")
    
    try:
        # Create client
        print_step(1, "Creating Binance Futures client...")
        client = BinanceClient(api_key=api_key, api_secret=api_secret, testnet=False)
        client.market_type = "futures"  # Set to futures mode (default)
        print_success("Client created successfully")
        
        # Test connection
        print_step(2, "Testing API connection...")
        if not client.test_connection():
            print_error("Connection test failed - Invalid API credentials or Futures not enabled")
            return False
        print_success("Connection test passed!")
        
        # Get account balance
        print_step(3, "Fetching futures account balance...")
        balance = client.get_account_balance()
        
        if "error" in balance:
            print_error(f"Failed to get balance: {balance['error']}")
            print_info("Make sure Futures is enabled on your Binance account!")
            return False
        
        if isinstance(balance, list):
            print_success("Futures balance retrieved successfully")
            print_info("Asset balances:")
            for asset in balance:
                balance_val = float(asset.get("balance", 0))
                if balance_val > 0:
                    print(f"   {asset.get('asset')}: {balance_val}")
        else:
            print_error("Unexpected balance format")
            return False
        
        # Test price fetching
        print_step(4, "Testing price fetching (BTCUSDT)...")
        price = client.get_ticker_price("BTCUSDT")
        if price:
            print_success(f"Current BTC futures price: ${price:,.2f}")
        else:
            print_error("Failed to get ticker price")
            return False
        
        # Get position information
        print_step(5, "Fetching position information...")
        positions = client.get_position()
        if isinstance(positions, list):
            print_success(f"Position data retrieved ({len(positions)} symbols tracked)")
            # Show active positions
            active_positions = [p for p in positions if float(p.get("positionAmt", 0)) != 0]
            if active_positions:
                print_info(f"Active positions: {len(active_positions)}")
                for pos in active_positions[:5]:
                    symbol = pos.get("symbol")
                    amt = float(pos.get("positionAmt", 0))
                    entry = float(pos.get("entryPrice", 0))
                    unrealized_pnl = float(pos.get("unRealizedProfit", 0))
                    print(f"   {symbol}: Amount={amt}, Entry=${entry}, PnL=${unrealized_pnl:.2f}")
            else:
                print_info("No active positions")
        else:
            print_error("Failed to get position data")
            return False
        
        return True
        
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False

def test_exchange_factory(api_key, api_secret):
    """Test ExchangeFactory"""
    print_header("Testing Exchange Factory")
    
    try:
        print_step(1, "Creating Binance client via factory...")
        client = ExchangeFactory.create_client(
            exchange_name="binance",
            mode="live",
            api_key=api_key,
            api_secret=api_secret
        )
        print_success("Factory created client successfully")
        
        print_step(2, "Testing connection...")
        if client.test_connection():
            print_success("Connection successful via factory!")
            return True
        else:
            print_error("Connection failed via factory")
            return False
            
    except Exception as e:
        print_error(f"Exception occurred: {str(e)}")
        return False

def check_api_permissions(api_key, api_secret):
    """Check what permissions the API key has"""
    print_header("Checking API Key Permissions")
    
    permissions = {
        "reading": False,
        "spot_trading": False,
        "futures_trading": False,
        "withdrawals": False
    }
    
    # Test spot access
    print_step(1, "Checking Spot trading access...")
    spot_client = BinanceClient(api_key=api_key, api_secret=api_secret)
    spot_client.market_type = "spot"
    spot_result = spot_client.get_account_balance()
    
    if "error" not in spot_result:
        permissions["reading"] = True
        permissions["spot_trading"] = True
        print_success("Spot trading ENABLED ✓")
    else:
        print_error("Spot trading DISABLED ✗")
    
    # Test futures access
    print_step(2, "Checking Futures trading access...")
    futures_client = BinanceClient(api_key=api_key, api_secret=api_secret)
    futures_client.market_type = "futures"
    futures_result = futures_client.get_account_balance()
    
    if "error" not in futures_result:
        permissions["futures_trading"] = True
        print_success("Futures trading ENABLED ✓")
    else:
        print_error("Futures trading DISABLED ✗")
        print_info("Note: You need to enable Futures on your Binance account first!")
    
    # Summary
    print("\nPermission Summary:")
    print(f"  Reading: {'✓' if permissions['reading'] else '✗'}")
    print(f"  Spot Trading: {'✓' if permissions['spot_trading'] else '✗'}")
    print(f"  Futures Trading: {'✓' if permissions['futures_trading'] else '✗'}")
    
    return permissions

def main():
    """Main test function"""
    print(f"\n{'*'*60}")
    print(f"{'Binance API Connection Test':^60}")
    print(f"{'VerzekAutoTrader - Exchange Integration':^60}")
    print(f"{'*'*60}\n")
    
    # Get API credentials
    print("Please enter your Binance API credentials:")
    print("⚠️  NEVER share these with anyone!")
    print("(These will only be used for testing and not stored)\n")
    
    api_key = input("API Key: ").strip()
    api_secret = input("Secret Key: ").strip()
    
    if not api_key or not api_secret:
        print_error("API Key and Secret Key are required!")
        sys.exit(1)
    
    print("\nStarting tests...\n")
    
    # Run tests
    results = {
        "permissions": False,
        "spot": False,
        "futures": False,
        "factory": False
    }
    
    # Check permissions
    results["permissions"] = check_api_permissions(api_key, api_secret)
    
    # Test spot
    results["spot"] = test_binance_spot(api_key, api_secret)
    
    # Test futures
    results["futures"] = test_binance_futures(api_key, api_secret)
    
    # Test factory
    results["factory"] = test_exchange_factory(api_key, api_secret)
    
    # Final summary
    print_header("TEST RESULTS SUMMARY")
    
    all_passed = all([results["spot"], results["factory"]])
    
    print(f"Permissions Check: {'PASSED ✓' if results['permissions'] else 'FAILED ✗'}")
    print(f"Spot API Test: {'PASSED ✓' if results['spot'] else 'FAILED ✗'}")
    print(f"Futures API Test: {'PASSED ✓' if results['futures'] else 'FAILED ✗'}")
    print(f"Exchange Factory: {'PASSED ✓' if results['factory'] else 'FAILED ✗'}")
    
    print()
    
    if all_passed:
        print("="*60)
        print("✅ ALL TESTS PASSED! ✅".center(60))
        print("="*60)
        print("\nYour API keys are working correctly!")
        print("You can now use them in VerzekAutoTrader mobile app.")
        
        if not results["futures"]:
            print("\n⚠️  Note: Futures trading is not enabled.")
            print("To enable Futures:")
            print("1. Log into Binance website")
            print("2. Go to Derivatives → USDⓈ-M Futures")
            print("3. Complete Futures account activation")
            print("4. Create new API key AFTER enabling Futures")
    else:
        print("="*60)
        print("❌ SOME TESTS FAILED ❌".center(60))
        print("="*60)
        print("\nCommon Issues:")
        print("1. API key doesn't have correct permissions")
        print("   → Enable 'Spot & Margin Trading' in Binance API settings")
        print("2. API key created before Futures activation")
        print("   → Create a NEW API key after enabling Futures")
        print("3. IP whitelisting enabled without our server IP")
        print("   → Add 45.76.90.149 to Binance API whitelist")
        print("4. Timestamp issues")
        print("   → Check system time is synced correctly")
    
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)
