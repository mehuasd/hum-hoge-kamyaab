"""Flask server for code transpiler - FIXED with CORS"""
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import traceback

from core.transpiler import Transpiler
from core.ir import IRProgram

app = Flask(__name__, static_folder='static', template_folder='templates')

# ⭐ CRITICAL: Enable CORS for API requests
CORS(app, resources={r"/api/*": {"origins": "*"}})

transpiler = Transpiler()

@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """Serve static files"""
    return send_from_directory('static', filename)

@app.route('/api/transpile', methods=['POST', 'OPTIONS'])
def transpile():
    """API endpoint for transpilation - FIXED"""
    
    # Handle CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        print("DEBUG: Received transpile request")
        
        data = request.get_json()
        print(f"DEBUG: Request data: {data}")
        
        source_code = data.get('code', '')
        source_language = data.get('source_language', 'python')
        target_languages = data.get('target_languages', ['python', 'c', 'cpp', 'java'])
        
        print(f"DEBUG: Source lang: {source_language}, Targets: {target_languages}")
        
        if not source_code:
            return jsonify({'error': 'No source code provided'}), 400
        
        results = {}
        for target_lang in target_languages:
            try:
                print(f"DEBUG: Transpiling to {target_lang}")
                
                result = transpiler.transpile(
                    source_code, 
                    source_language, 
                    target_lang
                )
                results[target_lang] = {
                    'code': result,
                    'success': True,
                    'error': None
                }
                print(f"DEBUG: Success for {target_lang}")
                
            except Exception as e:
                print(f"DEBUG: Error for {target_lang}: {str(e)}")
                print(traceback.format_exc())
                
                results[target_lang] = {
                    'code': '',
                    'success': False,
                    'error': str(e)
                }
        
        print(f"DEBUG: Returning results: {results}")
        return jsonify(results), 200
    
    except Exception as e:
        print(f"DEBUG: Outer exception: {str(e)}")
        print(traceback.format_exc())
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/languages', methods=['GET'])
def get_languages():
    """Get available languages"""
    return jsonify({
        'languages': ['python', 'c', 'cpp', 'java'],
        'support': {
            'python': ['c', 'cpp', 'java'],
            'c': ['python', 'cpp', 'java'],
            'cpp': ['python', 'c', 'java'],
            'java': ['python', 'c', 'cpp']
        }
    })

@app.route('/api/samples', methods=['GET'])
def get_samples():
    """Get sample code"""
    samples = {
        'python': '''# Python: Print with variables
print("Hello, World!")
x = 5
y = 10
print(x + y)
for i in range(0, 4):
    print(i)''',
        'c': '''#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    int x = 5;
    int y = 10;
    printf("%d\\n", x + y);
    for(int i = 0; i < 4; i++) {
        printf("%d\\n", i);
    }
    return 0;
}''',
        'cpp': '''#include <iostream>
using namespace std;

int main() {
    cout << "Hello, World!" << endl;
    int x = 5;
    int y = 10;
    cout << x + y << endl;
    for(int i = 0; i < 4; i++) {
        cout << i << endl;
    }
    return 0;
}''',
        'java': '''public class Main {
    public static void main(String[] args) {
        System.out.println("Hello, World!");
        int x = 5;
        int y = 10;
        System.out.println(x + y);
        for(int i = 0; i < 4; i++) {
            System.out.println(i);
        }
    }
}'''
    }
    return jsonify(samples)

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    print(f"Server error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📍 Access at http://localhost:5000")
    print("⚠️  Press Ctrl+C to stop")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=5000,
        use_reloader=True
    )
