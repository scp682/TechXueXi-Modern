"""Audit tracked/index content before publishing. Never print secret values."""
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = re.compile(
    r'^(SourcePackages/(user|chrome)/|\.runtime/|\.venv/|\.playwright-cli/|output/)|'
    r'(^|/)(__pycache__/|\.env(?:\.|$)|cookies\.json$|qrcode\.png$)|'
    r'\.(db|sqlite3?|log|pyc|pem|key)$', re.I)
SECRET_PATTERNS = [
    r'github_pat_[A-Za-z0-9_]{20,}', r'gh[pousr]_[A-Za-z0-9]{20,}',
    r'AKIA[A-Z0-9]{16}', r'-----BEGIN [A-Z ]*PRIVATE KEY-----',
    r'\bsk-[A-Za-z0-9_-]{24,}', r'\b[0-9]{8,}:[A-Za-z0-9_-]{30,}']


def git(*args):
    return subprocess.check_output(['git', *args], cwd=str(ROOT))


def audit():
    files = git('ls-files', '-z').decode('utf-8').split('\0')
    files = [name for name in files if name]
    issues = []
    total = 0
    for name in files:
        if FORBIDDEN.search(name):
            issues.append((name, 'private/local file path'))
            continue
        content = git('show', ':' + name)
        total += len(content)
        if b'\0' in content[:8192]:
            continue
        text = content.decode('utf-8', errors='replace')
        if any(re.search(pattern, text) for pattern in SECRET_PATTERNS):
            issues.append((name, 'possible credential pattern; value hidden'))
    for name, reason in issues:
        print('BLOCKED:', name, '-', reason)
    print('Audited {} tracked files, {} bytes; {} finding(s).'.format(
        len(files), total, len(issues)))
    return not issues


if __name__ == '__main__':
    sys.exit(0 if audit() else 1)
