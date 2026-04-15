import os
import base64
import subprocess
import tempfile
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["https://alexgf004-maker.github.io"])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

@app.route('/convert', methods=['POST'])
def convert():
    try:
        data = request.get_json(force=True)
        if not data or 'docx_base64' not in data:
            return jsonify({'error': 'Falta docx_base64'}), 400
        docx_bytes = base64.b64decode(data['docx_base64'])
        with tempfile.TemporaryDirectory() as tmpdir:
            docx_path = os.path.join(tmpdir, 'despacho.docx')
            pdf_path  = os.path.join(tmpdir, 'despacho.pdf')
            with open(docx_path, 'wb') as f:
                f.write(docx_bytes)
            result = subprocess.run([
                'libreoffice', '--headless', '--norestore',
                '--convert-to', 'pdf',
                '--outdir', tmpdir, docx_path
            ], capture_output=True, text=True, timeout=45,
               env={**os.environ, 'HOME': tmpdir})
            if result.returncode != 0:
                return jsonify({'error': f'Conversión fallida: {result.stderr}'}), 500
            if not os.path.exists(pdf_path):
                return jsonify({'error': 'PDF no generado'}), 500
            with open(pdf_path, 'rb') as f:
                pdf_b64 = base64.b64encode(f.read()).decode('utf-8')
        return jsonify({'pdf_base64': pdf_b64})
    except subprocess.TimeoutExpired:
        return jsonify({'error': 'Timeout'}), 504
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
