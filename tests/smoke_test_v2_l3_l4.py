"""Smoke test for V2 external_resolver L3/L4 reading"""
import sys
from pathlib import Path

# Add V2 to path
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
facts = resolver.resolve_facts({'product_id': 'lecanemab'})

# Check for L3 facts
l3_facts = [f for f in facts if 'l3' in str(f.lineage.get('source_file', ''))]
l4_facts = [f for f in facts if 'l4' in str(f.lineage.get('source_file', ''))]

has_l3 = len(l3_facts) > 0
has_l4 = len(l4_facts) > 0

print(f'Total facts: {len(facts)}')
print(f'L3 facts: {len(l3_facts)}')
print(f'L4 facts: {len(l4_facts)}')
print(f'has_l3: {has_l3}')
print(f'has_l4: {has_l4}')

# Check L3 source files
l3_files = set()
for f in facts:
    src = f.lineage.get('source_file', '')
    if 'l3' in src:
        l3_files.add(Path(src).parent.name)

print(f'L3 directories: {sorted(l3_files)}')

# Check L4 source files
l4_files = set()
for f in facts:
    src = f.lineage.get('source_file', '')
    if 'l4' in src:
        l4_files.add(Path(src).parent.name)

print(f'L4 directories: {sorted(l4_files)}')

# Success criteria
if has_l3 and has_l4:
    print('\n✅ V2 external_resolver can read L3 and L4 content')
else:
    print('\n❌ V2 external_resolver cannot read L3/L4 content')
    sys.exit(1)