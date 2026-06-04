import sys
import os

def export_cookies():
    # We must use the venv's python to ensure rookiepy is available
    # Or import it directly
    try:
        import rookiepy
    except ImportError:
        print("Installing rookiepy in virtualenv...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "rookiepy"])
        import rookiepy

    print("====================================================")
    print("   AUTO-EXTRACT DOUYIN COOKIES FROM YOUR BROWSER    ")
    print("====================================================")
    
    cookies = []
    
    # Try Chrome
    try:
        print("Extracting from Google Chrome...")
        cookies = rookiepy.chrome(["douyin.com"])
        print(f"-> Found {len(cookies)} cookies.")
    except Exception as e:
        print(f"-> Chrome extract failed: {e}")
        print("   (Note: Chrome v130+ requires running this command prompt as Administrator!)")

    # If Chrome failed or returned nothing, try Edge
    if not cookies:
        try:
            print("\nExtracting from Microsoft Edge...")
            cookies = rookiepy.edge(["douyin.com"])
            print(f"-> Found {len(cookies)} cookies.")
        except Exception as e:
            print(f"-> Edge extract failed: {e}")
            print("   (Note: Edge v130+ requires running this command prompt as Administrator!)")

    if not cookies:
        print("\n[ERROR] No cookies could be extracted from Chrome or Edge.")
        print("Please make sure:")
        print("1. You have visited douyin.com in Chrome or Edge.")
        print("2. You run this terminal/command prompt as ADMINISTRATOR (Right click cmd/powershell -> Run as Administrator).")
        return False

    # Check for ttwid and sessionid
    has_ttwid = any(c.get('name') == 'ttwid' for c in cookies)
    has_session = any(c.get('name') == 'sessionid' for c in cookies)
    print(f"\nCookie validation:")
    print(f"- Has 'ttwid' cookie: {'YES (Good)' if has_ttwid else 'NO'}")
    print(f"- Has 'sessionid' cookie: {'YES (Logged in)' if has_session else 'NO (Guest)'}")

    # Save to cookies_converted.txt in backend/backend/
    dest_dir = r"e:\taimoithu\backend\backend"
    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, "cookies_converted.txt")
    
    try:
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n\n")
            for c in cookies:
                domain = c.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                expiration = int(c.get('expires', 0)) if c.get('expires') is not None else 0
                name = c.get('name', '')
                value = c.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")
        
        # Also copy to cookies.txt to override
        with open(os.path.join(dest_dir, "cookies.txt"), 'w', encoding='utf-8') as f:
            f.write("# Netscape HTTP Cookie File\n\n")
            for c in cookies:
                domain = c.get('domain', '')
                flag = "TRUE" if domain.startswith('.') else "FALSE"
                path = c.get('path', '/')
                secure = "TRUE" if c.get('secure', False) else "FALSE"
                expiration = int(c.get('expires', 0)) if c.get('expires') is not None else 0
                name = c.get('name', '')
                value = c.get('value', '')
                f.write(f"{domain}\t{flag}\t{path}\t{secure}\t{expiration}\t{name}\t{value}\n")

        print(f"\n[SUCCESS] Saved verified cookies to: {dest_path}")
        print("The backend in Docker should pick this up automatically via mounted volume.")
        return True
    except Exception as e:
        print(f"\n[ERROR] Failed to save cookies file: {e}")
        return False

if __name__ == "__main__":
    export_cookies()
