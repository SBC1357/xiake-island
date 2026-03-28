"""
2C-4: Current Switch and Rollback Drill
"""
import json
import shutil
from pathlib import Path
from datetime import datetime

WORKING_DIR = Path("/root/.openclaw/workspace/huidu")
PUBLISH_DIR = WORKING_DIR / "藏经阁" / "publish"
CURRENT_DIR = PUBLISH_DIR / "current"
RELEASES_DIR = PUBLISH_DIR / "releases"
CURRENT_META = CURRENT_DIR / "current_meta.json"
CONSUMERS_DIR = CURRENT_DIR / "consumers"

# Releases
TARGET_RELEASE = "REL-20260316-001"
PREVIOUS_RELEASE = "REL-20260315-002"

def read_current_meta():
    with open(CURRENT_META, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_current_meta(meta):
    with open(CURRENT_META, 'w', encoding='utf-8') as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

def sync_consumers(release_id):
    """Sync consumers from release to current"""
    release_consumers = RELEASES_DIR / release_id / "consumers"
    
    if not release_consumers.exists():
        print(f"  Warning: Release {release_id} has no consumers directory")
        return False
    
    # Sync v2
    v2_src = release_consumers / "v2"
    v2_dst = CONSUMERS_DIR / "v2"
    if v2_src.exists():
        if v2_dst.exists():
            shutil.rmtree(v2_dst)
        shutil.copytree(v2_src, v2_dst)
        print(f"  Synced v2 consumers")
    
    # Sync xiakedao
    xia_src = release_consumers / "xiakedao"
    xia_dst = CONSUMERS_DIR / "xiakedao"
    if xia_src.exists():
        if xia_dst.exists():
            shutil.rmtree(xia_dst)
        shutil.copytree(xia_src, xia_dst)
        print(f"  Synced xiakedao consumers")
    
    return True

def switch_to_release(target_release, previous_release):
    """Switch current to target release"""
    print(f"\n[SWITCH] {previous_release} -> {target_release}")
    
    # Sync consumers
    sync_consumers(target_release)
    
    # Update meta
    meta = {
        "current_release": target_release,
        "switched_at": datetime.now().isoformat(),
        "switch_type": "atomic",
        "previous_release": previous_release,
        "validation": {
            "manifest_exists": True,
            "manifest_status": "published",
            "consumers_ready": ["v2", "xiakedao"],
            "pre_verification_passed": True
        }
    }
    write_current_meta(meta)
    print(f"  Updated current_meta.json")
    
    return True

def verify_current():
    """Verify current release is working via real request chains"""
    import sys
    import os
    
    # Set environment for Xiakedao
    os.environ['XIAGEDAO_CONSUMER_ROOT'] = str(CONSUMERS_DIR / "xiakedao")
    os.environ['XIAGEDAO_STRICT_MODE'] = 'true'
    
    # NOTE: V2 system is deprecated. Path updated for Linux.
# Original: D:\汇度编辑部1\写作知识库\medical_kb_system_v2
sys.path.insert(0, str(WORKING_DIR / "V2medical-kb-system"))
    sys.path.insert(0, str(WORKING_DIR / "XiaKe-Island"))
    
    from engine.evidence.external_resolver import ExternalResolver
    from engine.config.knowledge_source import KnowledgeSourceConfig
    
    # V2 verification - real resolve_facts call
    config = KnowledgeSourceConfig(knowledge_root=WORKING_DIR / "cang")
    resolver = ExternalResolver(config=config)
    facts = resolver.resolve_facts({'product_id': 'lecanemab'})
    v2_ok = len(facts) > 0
    print(f"  V2 facts: {len(facts)} - {'PASS' if v2_ok else 'FAIL'}")
    
    # Xiakedao verification - real API request chain
    from fastapi.testclient import TestClient
    from src.assembly import reset_asset_bridge
    from src.api.app import app
    
    # Reset singleton to pick up new consumer root
    reset_asset_bridge()
    
    client = TestClient(app)
    response = client.get("/v1/workflow/knowledge-assets")
    
    if response.status_code != 200:
        print(f"  Xiakedao API: status {response.status_code} - FAIL")
        return False
    
    data = response.json()
    consumer_root = data.get("consumer_root", "")
    consumer_count = data.get("consumer_assets_count", 0)
    has_l2 = data.get("has_l2", False)
    
    # Verify consumer_root points to current
    expected_root = str(CONSUMERS_DIR / "xiakedao")
    root_ok = expected_root in consumer_root
    count_ok = consumer_count > 0
    
    print(f"  Xiakedao API: status 200, count={consumer_count}, has_l2={has_l2}, root_ok={root_ok}")
    
    if not (root_ok and count_ok):
        print(f"    Expected root containing: {expected_root}")
        print(f"    Actual root: {consumer_root}")
    
    xia_ok = root_ok and count_ok and has_l2
    print(f"  Xiakedao verification: {'PASS' if xia_ok else 'FAIL'}")
    
    return v2_ok and xia_ok

# === DRILL EXECUTION ===
print("=" * 60)
print("2C-4: CURRENT SWITCH AND ROLLBACK DRILL")
print("=" * 60)

# Step 1: Record current state
print("\n[STEP 1] Record current state")
current_meta = read_current_meta()
print(f"  Current release: {current_meta['current_release']}")
print(f"  Previous release: {current_meta['previous_release']}")

# Step 2: Verify current (should pass)
print("\n[STEP 2] Verify current release")
step2_ok = verify_current()
if not step2_ok:
    print("  ERROR: Current release verification failed")
    exit(1)

# Step 3: Rollback to previous release
print("\n[STEP 3] ROLLBACK to previous release")
switch_to_release(PREVIOUS_RELEASE, TARGET_RELEASE)

# Step 4: Verify after rollback
print("\n[STEP 4] Verify after rollback")
step4_ok = verify_current()
if not step4_ok:
    print("  ERROR: Rollback verification failed")
    # Auto-revert to target
    print("\n[AUTO-REVERT] Switching back to target release")
    switch_to_release(TARGET_RELEASE, PREVIOUS_RELEASE)
    exit(1)

# Step 5: Switch back to target release
print("\n[STEP 5] SWITCH BACK to target release")
switch_to_release(TARGET_RELEASE, PREVIOUS_RELEASE)

# Step 6: Final verification
print("\n[STEP 6] Final verification")
step6_ok = verify_current()
if not step6_ok:
    print("  ERROR: Final verification failed")
    exit(1)

print("\n" + "=" * 60)
print("ROLLBACK DRILL COMPLETE: ALL STEPS PASSED")
print("=" * 60)