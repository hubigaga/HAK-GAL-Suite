"""
HAK-GAL MINIMAL API - For Testing Backend Fixes
===============================================
Simplified API without complex dependencies for immediate testing.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import sys
import os

# Simple Flask setup
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

print("🚀 HAK-GAL MINIMAL API - Starting...")

# Try to import backend - with error handling
backend_available = False
assistant = None

try:
    from backend.services import KAssistant
    print("🤖 Loading K-Assistant...")
    assistant = KAssistant()
    backend_available = True
    print("✅ K-Assistant loaded successfully")
    
    # Test our fixes
    print("🔧 Testing Backend Fixes:")
    
    # Test advanced_relevance_adapter (BACKEND-7 fix)
    if hasattr(assistant, 'advanced_relevance_manager'):
        print("   ✅ Advanced Relevance Manager available")
    else:
        print("   ⚠️ Advanced Relevance Manager not found")
    
    # Test for metadata fix (BACKEND-A fix)
    try:
        from tools.hak_gal_relevance_filter import RelevanceResult, Fact
        test_fact = Fact("test", "test", "test", "test")
        test_result = RelevanceResult(test_fact, 1.0, "test", metadata={"test": True})
        print("   ✅ RelevanceResult metadata support working")
    except Exception as e:
        print(f"   ❌ RelevanceResult metadata error: {e}")
        
except Exception as e:
    print(f"⚠️ Backend not available: {e}")
    print("🔧 Running in fallback mode...")

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint to verify API is working"""
    return jsonify({
        "status": "API is running",
        "backend_available": backend_available,
        "fixes_status": {
            "backend_7_fix": "inspect.isawaitable() implemented",
            "backend_a_fix": "RelevanceResult metadata support added"
        }
    })

@app.route('/api/command', methods=['POST'])
def handle_command():
    """Simplified command handler for testing"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"error": "Missing command"}), 400
        
        command = data['command'].strip()
        parts = command.split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        print(f"📨 Command: {cmd} | Args: {args}")
        
        if not backend_available:
            return jsonify({
                "chatResponse": f"⚠️ Backend nicht verfügbar. Command '{cmd}' kann nicht verarbeitet werden.",
                "status": "backend_unavailable",
                "error": "Backend services not loaded"
            })
        
        # Test critical commands
        if cmd == "learn":
            try:
                # Test BACKEND-7 fix: learn_facts with asyncio
                output = assistant.learn_facts()
                return jsonify({
                    "chatResponse": f"✅ Learn command successful! Output: {output}",
                    "status": "success",
                    "backend_7_test": "✅ PASSED"
                })
            except Exception as e:
                return jsonify({
                    "chatResponse": f"❌ Learn command failed: {e}",
                    "status": "error", 
                    "backend_7_test": f"❌ FAILED: {e}"
                })
        
        elif cmd == "ask":
            try:
                # Test BACKEND-A fix: ask command with metadata
                output = assistant.ask(args)
                return jsonify({
                    "chatResponse": f"✅ Ask command successful! Answer: {output}",
                    "status": "success",
                    "backend_a_test": "✅ PASSED"
                })
            except Exception as e:
                return jsonify({
                    "chatResponse": f"❌ Ask command failed: {e}",
                    "status": "error",
                    "backend_a_test": f"❌ FAILED: {e}"
                })
        
        elif cmd == "explain":
            try:
                output = assistant.explain(args)
                return jsonify({
                    "chatResponse": f"✅ Explain command successful! Explanation: {output}",
                    "status": "success"
                })
            except Exception as e:
                return jsonify({
                    "chatResponse": f"❌ Explain command failed: {e}",
                    "status": "error"
                })
        
        elif cmd == "help":
            return jsonify({
                "chatResponse": """🔧 HAK-GAL MINIMAL API - BACKEND FIX TESTING

✅ Available test commands:
  • learn          - Test BACKEND-7 fix (asyncio)
  • ask <query>    - Test BACKEND-A fix (metadata)
  • explain <text> - Test general functionality
  • help           - Show this help

🎯 For fix validation:
  • Use 'learn' to test asyncio Future fixes
  • Use 'ask critical components' to test metadata fixes
  • Check /api/test endpoint for overall status
                """,
                "status": "success"
            })
        
        else:
            return jsonify({
                "chatResponse": f"❌ Unknown command: {cmd}\n\n✅ Available: learn, ask, explain, help",
                "status": "unknown_command"
            })
            
    except Exception as e:
        print(f"❌ Error: {e}")
        traceback.print_exc()
        return jsonify({
            "chatResponse": f"🚨 API Error: {e}",
            "status": "error",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 Starting HAK-GAL Minimal API on port 5001...")
    print("🔧 This API is optimized for testing backend fixes")
    print("📊 Test URL: http://localhost:5001/api/test")
    print("🎯 Use Frontend or curl to test commands")
    
    app.run(debug=True, port=5001, host='0.0.0.0')
