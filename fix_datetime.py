#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Fix datetime imports and usage in server.py"""

import re

# Read the file
with open('server.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix 1: Remove the duplicate import line
content = content.replace(
    'from datetime import datetime, timedelta\nimport json\nimport os\nimport logging\nimport shutil\nfrom datetime import datetime as dt_now\nimport re',
    'from datetime import datetime, timedelta\nimport json\nimport os\nimport logging\nimport shutil\nimport re'
)

# Fix 2: Replace all dt_now usages in Column defaults
content = re.sub(r'default=dt_now', 'default=datetime.utcnow', content)
content = re.sub(r'onupdate=dt_now', 'onupdate=datetime.utcnow', content)

# Fix 3: Replace dt_now.now() with datetime.now()
content = re.sub(r'dt_now\.now\(\)', 'datetime.now()', content)

# Fix 4: Replace dt_now.utcnow() with datetime.utcnow()
content = re.sub(r'dt_now\.utcnow\(\)', 'datetime.utcnow()', content)

# Fix 5: Handle remaining dt_now references (like 'dt_now,')
content = re.sub(r'\bdt_now\b', 'datetime.utcnow()', content)

# Write back
with open('server.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed datetime references in server.py")
