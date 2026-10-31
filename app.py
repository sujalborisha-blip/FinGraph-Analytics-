import os
import sys
from pathlib import Path

# --- Streamlit Cloud Auto-Forwarder ---
# If Streamlit Cloud runs app.py instead of streamlit_app.py,
# automatically execute streamlit_app.py so the dashboard loads seamlessly!
def _check_streamlit():
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx() is not None
    except Exception:
        return False

if _check_streamlit():
    st_app_file = Path(__file__).resolve().parent / "streamlit_app.py"
    if st_app_file.exists():
        with open(st_app_file, "r", encoding="utf-8") as f:
            code = compile(f.read(), str(st_app_file), "exec")
            exec(code, globals())
else:
    from flask import Flask, render_template, Response
    import time

    app = Flask(__name__)
    LOG_FILE = "transactions.log"

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/stream')
    def stream():
        def generate():
            if not os.path.exists(LOG_FILE):
                yield "data: {\"error\": \"Log file not found\"}\n\n"
                return
                
            with open(LOG_FILE, "r") as f:
                f.seek(0, os.SEEK_END)
                while True:
                    line = f.readline()
                    if not line:
                        time.sleep(0.5)
                        continue
                    if line.startswith("{"):
                        yield f"data: {line}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    if __name__ == '__main__':
        print(" FinGraph Live Dashboard Server is Running!")
        print(" 1. Make sure simulator.py is running in another terminal")
        print(" 2. Open this link in your browser: http://127.0.0.1:5000")
        app.run(debug=False, threaded=True, port=5000)
