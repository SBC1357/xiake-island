"""Smoke test for V2 external_resolver l2 reading"""
import sys
from pathlib import Path

# Add paths
# NOTE: V2 system is deprecated. These tests are kept for reference but will not work on Linux.
# V2 path was: D:\汇度编辑部1\写作知识库\medical_kb_system_v2
v2_path = Path('/root/.openclaw/workspace/huidu/V2medical-kb-system')
sys.path.insert(0, str(v2_path))

from engine.evidence.external_resolver import ExternalResolver
from engine.config.knowledge_source import KnowledgeSourceConfig

# Test with current release
config = KnowledgeSourceConfig(knowledge_root=Path('/root/.openclaw/workspace/huidu/cang'))
resolver = ExternalResolver(config=config)

# Resolve facts
facts = resolver.resolve_facts({'product_id': 'test'})

# Check for L2 facts
l2_facts = [f for f in facts if 'l2' in str(f.lineage.get('source_file', ''))]
has_l2 = len(l2_facts) > 0

print(f'Total facts: {len(facts)}')
print(f'L2 facts: {len(l2_facts)}')
print(f'has_l2: {has_l2}')

# Show some L2 file names
l2_files = set()
for f in facts:
    src = f.lineage.get('source_file', '')
    if 'l2' in src:
        l2_files.add(Path(src).name)

print(f'L2 files found: {sorted(l2_files)[:5]}')

# Test with candidate release
print("\n--- Testing candidate release ---")
config_candidate = KnowledgeSourceConfig(
    knowledge_root=Path('/root/.openclaw/workspace/huidu/cang'),
    release_id='REL-20260315-002'
)
try:
    resolver_candidate = ExternalResolver(config=config_candidate)
    facts_candidate = resolver_candidate.resolve_facts({'product_id': 'test'})
    l2_facts_candidate = [f for f in facts_candidate if 'l2' in str(f.lineage.get('source_file', ''))]
    print(f'Candidate release facts: {len(facts_candidate)}')
    print(f'Candidate L2 facts: {len(l2_facts_candidate)}')
    print(f'Candidate has_l2: {len(l2_facts_candidate) > 0}')
except Exception as e:
    print(f'Candidate release error: {e}')