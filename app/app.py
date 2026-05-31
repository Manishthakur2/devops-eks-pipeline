from flask import Flask, jsonify

app = Flask(__name__)

todos = []

@app.route('/')
def home():
    return jsonify({
        "message": "Welcome to DevOps Todo API",
        "version": "1.0.0"
    })

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy"
    })

@app.route('/todos', methods=['GET'])
def get_todos():
    return jsonify(todos)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
