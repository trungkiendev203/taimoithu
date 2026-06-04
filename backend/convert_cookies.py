import json

def convert_json_to_netscape(json_path, netscape_path):
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            cookies = json.load(f)
            
        with open(netscape_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n\n")
            for c in cookies:
                domain = c.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                
                expiration = c.get('expirationDate')
                if expiration is None:
                    expiration = c.get('expires', 0)
                expiration = int(expiration) if expiration else 0
                
                name = c.get('name', '')
                value = c.get('value', '')
                
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == '__main__':
    json_path = r"e:\taimoithu\backend\backend\cookies.txt"
    netscape_path = r"e:\taimoithu\backend\backend\cookies_converted.txt"
    if convert_json_to_netscape(json_path, netscape_path):
        print("Successfully converted cookies to Netscape format.")
    else:
        print("Failed to convert cookies.")
