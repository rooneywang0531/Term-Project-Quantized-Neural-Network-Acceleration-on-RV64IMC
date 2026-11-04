#!/usr/bin/env python3
"""Install checksum-pinned Linux amd64 cross binaries locally, without sudo."""
import hashlib,json,platform,subprocess,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    if platform.system()!='Linux' or platform.machine() not in ('x86_64','amd64'):
        raise SystemExit('Pinned binary path supports Linux x86_64; use --platform linux/amd64 Docker on other hosts.')
    lock=json.loads((ROOT/'tools.lock.json').read_text());cache=ROOT/'.deps/downloads';dest=ROOT/'.tools/cross'
    cache.mkdir(parents=True,exist_ok=True);dest.mkdir(parents=True,exist_ok=True)
    for item in lock['linux_amd64_toolchain_packages']:
        p=cache/item['file']
        if not p.exists():urllib.request.urlretrieve(item['url'],p)
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256'],'Wrong toolchain checksum '+p.name
        subprocess.run(['dpkg-deb','-x',str(p),str(dest)],check=True)
    print('Pinned cross compiler installed locally:',dest/'usr/bin/riscv64-unknown-elf-gcc')
if __name__=='__main__':main()
