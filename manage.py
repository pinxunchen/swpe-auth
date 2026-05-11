"""
SWPE 授權名單管理工具
用法:
  python manage.py generate     - 從 users.json 產生加密檔案
  python manage.py push         - 產生 + 推送到 GitHub
  python manage.py add 名稱 類型 ID 到期日  - 新增用戶
  python manage.py remove 名稱  - 移除用戶
  python manage.py list         - 列出所有用戶
"""
import base64, hashlib, os, json, sys, datetime, subprocess
from Crypto.Cipher import AES

# ============================================================
# 加密密碼（從 SWPE.exe 逆向取得）
# ============================================================
PWD2 = '4mwD4<A)5JTb>=EpPH&iDUw6V<1*,/9%I[tK@GS9pBcKi#=S'  # 外層
PWD3 = '9#e7L%*.+B4U1VM&z%f>fl@;qn+ci6zp'                    # 內層

USERS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.json')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Reliable')
OUTPUT_FILE = os.path.join(OUTPUT_DIR, 'Reversible')

def encrypt_ag_a(plaintext: str, password: str) -> str:
    """AES-CBC 加密: Key=SHA256(password), IV=random, 結果=Base64(IV+encrypted)"""
    key = hashlib.sha256(password.encode('utf-8')).digest()
    iv = os.urandom(16)
    data = plaintext.encode('utf-8')
    pad_len = 16 - (len(data) % 16)
    data += bytes([pad_len] * pad_len)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(data)
    return base64.b64encode(iv + encrypted).decode('ascii')

def decrypt_ag_a(encrypted_b64: str, password: str) -> str:
    """AES-CBC 解密"""
    try:
        cipher_data = base64.b64decode(encrypted_b64)
        iv = cipher_data[:16]
        enc = cipher_data[16:]
        key = hashlib.sha256(password.encode('utf-8')).digest()
        cipher = AES.new(key, AES.MODE_CBC, iv)
        dec = cipher.decrypt(enc)
        pad = dec[-1]
        if pad <= 16:
            dec = dec[:-pad]
        return dec.decode('utf-8')
    except:
        return None

def date_to_ticks(date_str):
    """日期字串 (YYYY-MM-DD) 轉 .NET DateTime ticks"""
    parts = date_str.split('-')
    dt = datetime.datetime(int(parts[0]), int(parts[1]), int(parts[2]), 23, 59, 59)
    epoch = datetime.datetime(1, 1, 1)
    delta = dt - epoch
    return int(delta.total_seconds() * 10000000)

def ticks_to_date(ticks):
    """ticks 轉可讀日期"""
    dt = datetime.datetime(1, 1, 1) + datetime.timedelta(microseconds=ticks // 10)
    return dt.strftime('%Y-%m-%d')

def load_users():
    """讀取 users.json"""
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(data):
    """儲存 users.json"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def generate():
    """從 users.json 產生加密的 Reversible 檔案"""
    data = load_users()
    settings = data['settings']
    users = data['users']
    
    lines = []
    
    # 第一行（標頭）
    permanent = date_to_ticks(settings['key_114615_expire'])
    key225_expire = date_to_ticks(settings['key_225783_expire'])
    
    h0 = settings['header_field_0']  # 保留原始值
    h1 = encrypt_ag_a(settings['default_permission'], PWD3)
    h2 = encrypt_ag_a(f"114615={permanent},225783={key225_expire}", PWD3)
    lines.append(f"{h0},{h1},{h2}")
    
    # 用戶行
    for user in users:
        expire_ticks = date_to_ticks(user['expire'])
        permanent_ticks = date_to_ticks("2099-12-31")
        
        # SWPE expects ID at index 1 or 2
        fields = [
            encrypt_ag_a(user['type'], PWD3), # 0: Type
            encrypt_ag_a(str(user['id']), PWD3), # 1: ID (MATCH THIS!)
            encrypt_ag_a(user['name'], PWD3), # 2: Name
            encrypt_ag_a("_skip_", PWD3),     # 3: Skip
            encrypt_ag_a("_skip_", PWD3),     # 4: Skip
            encrypt_ag_a(str(expire_ticks), PWD3), # 5: Expire
            encrypt_ag_a(settings['default_permission'], PWD3), # 6: Permission
            encrypt_ag_a(f"114615={permanent_ticks},225783={expire_ticks}", PWD3), # 7: VIP
        ]
        lines.append(",".join(fields))
    
    # 組合 + 外層加密
    plaintext = "\n".join(lines)
    encrypted = encrypt_ag_a(plaintext, PWD2)
    
    # 儲存
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(encrypted)
    
    # 驗證
    verify = decrypt_ag_a(encrypted, PWD2)
    if verify == plaintext:
        print(f"  [OK] 加密驗證通過")
    else:
        print(f"  [ERROR] 加密驗證失敗!")
        return False
    
    print(f"  [OK] 已產生: {OUTPUT_FILE}")
    print(f"  [OK] 共 {len(users)} 位用戶")
    return True

def push():
    """產生 + git push"""
    print("=" * 50)
    print("Step 1: 產生加密檔案")
    print("=" * 50)
    if not generate():
        return
    
    print()
    print("=" * 50)
    print("Step 2: 推送到 GitHub")
    print("=" * 50)
    
    repo_dir = os.path.dirname(os.path.abspath(__file__))
    
    cmds = [
        ['git', 'add', '.'],
        ['git', 'commit', '-m', f'Update auth list - {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}'],
        ['git', 'push'],
    ]
    
    for cmd in cmds:
        print(f"  > {' '.join(cmd)}")
        result = subprocess.run(cmd, cwd=repo_dir, capture_output=True, text=True)
        if result.returncode != 0:
            if 'nothing to commit' in result.stdout:
                print("  [OK] 沒有變更需要推送")
                return
            print(f"  [ERROR] {result.stderr}")
            return
        print(f"  [OK]")
    
    print()
    print("  推送完成!")

def add_user(name, user_type, user_id, expire):
    """新增用戶"""
    data = load_users()
    
    # 檢查是否已存在
    for u in data['users']:
        if u['name'] == name:
            print(f"  [ERROR] 用戶 '{name}' 已存在!")
            return
    
    data['users'].append({
        'name': name,
        'type': user_type,
        'id': int(user_id),
        'expire': expire,
    })
    
    save_users(data)
    print(f"  [OK] 已新增用戶: {name} (ID:{user_id}, 到期:{expire})")

def remove_user(name):
    """移除用戶"""
    data = load_users()
    original_count = len(data['users'])
    data['users'] = [u for u in data['users'] if u['name'] != name]
    
    if len(data['users']) == original_count:
        print(f"  [ERROR] 找不到用戶: {name}")
        return
    
    save_users(data)
    print(f"  [OK] 已移除用戶: {name}")

def list_users():
    """列出所有用戶"""
    data = load_users()
    now = datetime.datetime.now()
    
    print(f"{'序號':<4} {'名稱':<16} {'類型':<14} {'ID':<10} {'到期日':<14} {'狀態'}")
    print("-" * 70)
    
    for i, u in enumerate(data['users'], 1):
        exp = datetime.datetime.strptime(u['expire'], '%Y-%m-%d')
        status = "有效" if exp > now else "已過期"
        print(f"  {i:<4} {u['name']:<14} {u['type']:<14} {u['id']:<10} {u['expire']:<14} {status}")
    
    print(f"\n共 {len(data['users'])} 位用戶")

# ============================================================
# 主程式
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'generate':
        generate()
    elif cmd == 'push':
        push()
    elif cmd == 'add':
        if len(sys.argv) < 6:
            print("用法: python manage.py add 名稱 類型 ID 到期日")
            print("範例: python manage.py add 新用戶 New::137 999001 2030-12-31")
            sys.exit(1)
        add_user(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif cmd == 'remove':
        if len(sys.argv) < 3:
            print("用法: python manage.py remove 名稱")
            sys.exit(1)
        remove_user(sys.argv[2])
    elif cmd == 'list':
        list_users()
    else:
        print(f"未知指令: {cmd}")
        print(__doc__)
