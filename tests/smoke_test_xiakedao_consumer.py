"""Smoke test for Xiakedao consumer seam in real request path"""
import sys
import os
from pathlib import Path

# Set the xiakedao consumer root (Linux path)
os.environ['XIAGEDAO_CONSUMER_ROOT'] = '/root/.openclaw/workspace/huidu/cang/publish/current/consumers/xiakedao'

# Add xiakedao to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.assembly import get_asset_bridge, validate_consumer_config
from src.adapters.asset_bridge import AssetKind

# Test 1: Validate consumer config
is_valid, msg = validate_consumer_config()
print(f'Consumer config valid: {is_valid}')
print(f'Message: {msg}')

# Test 2: Get asset bridge
try:
    bridge = get_asset_bridge()
    print(f'\nAsset bridge created successfully')
    print(f'Consumer root: {bridge.config.consumer_root}')
    
    # Test 3: List consumer assets
    consumer_assets = bridge.list_assets(AssetKind.CONSUMER)
    print(f'Consumer assets count: {len(consumer_assets)}')
    
    # Test 4: Check L2 directory
    has_l2 = False
    l2_files = []
    if bridge.config.consumer_root:
        l2_path = bridge.config.consumer_root / "l2"
        if l2_path.exists():
            has_l2 = True
            l2_files = [f.name for f in l2_path.rglob("*.json")][:10]
    
    print(f'has_l2: {has_l2}')
    print(f'l2_files: {l2_files[:5]}')
    
except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()

# Test 5: Test candidate release
print('\n--- Testing candidate release ---')
os.environ['XIAGEDAO_CONSUMER_ROOT'] = '/root/.openclaw/workspace/huidu/cang/publish/releases/REL-20260315-002/consumers/xiakedao'

# Reset the singleton
from src.assembly import reset_asset_bridge
reset_asset_bridge()

try:
    bridge_candidate = get_asset_bridge()
    print(f'Candidate consumer root: {bridge_candidate.config.consumer_root}')
    
    if bridge_candidate.config.consumer_root:
        l2_path = bridge_candidate.config.consumer_root / "l2"
        has_l2_candidate = l2_path.exists()
        print(f'Candidate has_l2: {has_l2_candidate}')
except Exception as e:
    print(f'Candidate error: {e}')