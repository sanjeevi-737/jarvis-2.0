import sys
import asyncio

from src.config import Config
from src.engine.jarvis import Jarvis


def main() -> None:
    errors = Config.validate()
    if errors:
        for err in errors:
            print(f"[!] Config error: {err}")
        sys.exit(1)

    if "--daemon" in sys.argv:
        import threading
        import pystray
        from PIL import Image, ImageDraw

        def create_image():
            img = Image.new("RGB", (64, 64), (10, 10, 15))
            dc = ImageDraw.Draw(img)
            dc.ellipse((6, 6, 58, 58), fill=(30, 27, 50))
            dc.ellipse((10, 10, 54, 54), fill=(167, 139, 250))
            return img

        jarvis = Jarvis()

        def run_jarvis():
            asyncio.run(jarvis.start())

        t = threading.Thread(target=run_jarvis, daemon=True)
        t.start()

        def on_quit(icon, item):
            icon.stop()
            jarvis._running = False

        icon = pystray.Icon("JARVIS", create_image(), "JARVIS PRIME", menu=pystray.Menu(pystray.MenuItem("Quit", on_quit)))
        icon.run()
    else:
        asyncio.run(Jarvis().start())


if __name__ == "__main__":
    main()
