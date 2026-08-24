from flask import Flask, render_template, Response
import time
import os

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
            # Go to the end of the file to stream new real-time transactions
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                # Ensure the line is a valid JSON transaction before sending
                if line.startswith("{"):
                    yield f"data: {line}\n\n"

    return Response(generate(), mimetype='text/event-stream')

if __name__ == '__main__':
  
    print(" FinGraph Live Dashboard Server is Running!")
   
    print(" 1. Make sure simulator.py is running in another terminal")
    print(" 2. Open this link in your browser: http://127.0.0.1:5000")

    app.run(debug=True, threaded=True, port=5000)
