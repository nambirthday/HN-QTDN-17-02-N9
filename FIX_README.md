# Odoo Module Fixes - README

## Summary of Changes

All critical errors in your three Odoo modules have been fixed:

### ✅ Fixed Issues

#### 1. SQL Constraint Indentation (3 files - CRITICAL)
- **nhan_su/models/don_vi.py** - Line 28-34
- **nhan_su/models/chuc_vu.py** - Line 11-16  
- **nhan_su/models/chung_chi_bang_cap.py** - Line 39-45

**Problem**: Incorrect indentation (4 spaces instead of 8)
**Result**: Module loading would fail with IndentationError

#### 2. Missing Method Implementation (CRITICAL)
- **quan_ly_du_an/models/giai_doan_du_an.py** - Line 71-93

**Problem**: Fields `tong_cong_viec` and `tien_do` referenced `_compute_thong_ke()` method that didn't exist
**Solution**: Implemented the method to calculate:
- `tong_cong_viec`: Total tasks in the project stage
- `tien_do`: Progress percentage (completed tasks / total tasks * 100)

#### 3. Circular Search Logic (MEDIUM)
- **quan_ly_cong_viec/models/nhan_vien.py** - Line 26-48

**Problem**: `_search_kpi()` used circular reference `[('kpi', operator, value)]`
**Solution**: Implemented proper search that:
- Filters employees by computed KPI values
- Supports all comparison operators (=, !=, <, >, <=, >=)

---

## How to Apply the Fixes

### Option 1: Quick Database Reset (Recommended)

1. **Run the database fix utility**:
   ```bash
   python3 fix_database.py
   ```
   This will:
   - Drop the problematic `base_registry_signaling` sequence
   - Show connection status
   - Ready Odoo for restart

2. **Start Odoo with module updates**:
   ```bash
   python3 odoo-bin.py -c odoo.conf -u all
   ```

### Option 2: Manual Database Cleanup

If you prefer to handle the database directly:

```bash
# Connect to PostgreSQL
psql -U odoo -d data

# Drop the problematic sequence
DROP SEQUENCE IF EXISTS base_registry_signaling CASCADE;

# Exit psql
\q
```

Then restart Odoo:
```bash
python3 odoo-bin.py -c odoo.conf -u all
```

### Option 3: Complete Database Reset

If the above doesn't work, you can completely reset the database:

```bash
# Drop the entire database
dropdb -U odoo data

# Create a fresh database
createdb -U odoo data

# Run Odoo to initialize
python3 odoo-bin.py -c odoo.conf --init=base,nhan_su,quan_ly_du_an,quan_ly_cong_viec
```

---

## Verification Checklist

After applying the fixes:

- [ ] Python modules load without syntax errors
- [ ] Database sequence issue is resolved
- [ ] Odoo starts successfully on http://localhost:8069
- [ ] All three modules can be accessed from the menu
- [ ] No red errors in the terminal output
- [ ] Forms for don_vi, chuc_vu, chung_chi_bang_cap load correctly
- [ ] giai_doan_du_an stages show progress calculation
- [ ] Employee KPI searches work properly

---

## Module Dependency Tree

```
├── nhan_su (Quản Lý Nhân Sự)
│   └── depends: base
│
├── quan_ly_du_an (Quản Lý Dự Án)
│   ├── depends: base
│   └── depends: nhan_su
│
└── quan_ly_cong_viec (Quản Lý Công Việc)
    ├── depends: base
    ├── depends: nhan_su
    └── depends: quan_ly_du_an
```

---

## Technical Details

### Fixed Compute Method
The `_compute_thong_ke()` method in `giai_doan_du_an.py` now:
1. Counts total tasks in the stage: `cong_viec.search_count([('giai_doan_id', '=', rec.id)])`
2. Counts completed tasks: `cong_viec.search_count([...with trang_thai='hoan_thanh'])`
3. Calculates progress: `completed / total * 100` (returns 0 if no tasks)

### Fixed Search Method
The `_search_kpi()` method in `quan_ly_cong_viec/nhan_vien.py` now:
1. Retrieves all employees
2. Calculates their individual KPI values
3. Matches against the provided operator and value
4. Returns properly formatted search domain: `[('id', 'in', matched_ids)]`

---

## Support & Troubleshooting

**Error**: `psycopg2.errors.DuplicateTable: relation "base_registry_signaling" already exists`
- **Solution**: Run `python3 fix_database.py` to drop the sequence

**Error**: `AttributeError: "_compute_thong_ke" method not found`
- **Status**: ✓ FIXED - Method now implemented

**Error**: Indentation or syntax errors in module loading
- **Status**: ✓ FIXED - All SQL constraints properly indented

**Module won't load**:
1. Check terminal output for specific error
2. Run: `python3 odoo-bin.py -c odoo.conf --validate-only all`
3. If issues persist, try Option 3 (Complete Database Reset)

---

**Date Fixed**: 2026-06-23
**Modified Files**: 5
**Issues Resolved**: 5 (3 CRITICAL, 1 CRITICAL, 1 MEDIUM)
