# Checkpoint: Empty Dict Serialization Fix

**Date**: 2026-03-17
**Priority**: P2
**Status**: Fixed

## Problem

`SQLiteTaskLogStore.save()` used truthy checks when serializing `input_data`/`output_data`, causing empty dictionaries `{}` to be saved as `None` after round-trip.

## Root Cause

```python
# Before (buggy)
input_data_json = json.dumps(entry.input_data) if entry.input_data else None
```

Python's empty dict `{}` is falsy, so `if entry.input_data` evaluated to `False`, storing `None`.

## Fix

Changed to explicit `is not None` checks in two locations:

1. **`save()` method** (lines 126-127):
   ```python
   input_data_json = json.dumps(entry.input_data, ensure_ascii=False) if entry.input_data is not None else None
   output_data_json = json.dumps(entry.output_data, ensure_ascii=False) if entry.output_data is not None else None
   ```

2. **`_row_to_entry()` method** (lines 311-312):
   ```python
   input_data=json.loads(row[4]) if row[4] is not None else None,
   output_data=json.loads(row[5]) if row[5] is not None else None,
   ```

## Tests Added

Two new tests in `tests/runtime_logging/test_sqlite_store.py`:

- `test_empty_dict_round_trip`: Verifies `{}` is preserved as `{}`
- `test_none_vs_empty_dict_distinction`: Confirms `None` and `{}` remain distinct

## Verification

```
22 tests passed in 2.33s
```

## Files Changed

- `src/runtime_logging/sqlite_store.py` (2 edits)
- `tests/runtime_logging/test_sqlite_store.py` (2 new tests)