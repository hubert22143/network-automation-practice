from flask import Flask , request , jsonify

app = Flask(__name__)

@app.route('/api',methods = ['GET'])
@app.route('/api/', methods=['GET'])
def hello():
    return jsonify({'message': 'Your Flask Api response'})
if __name__ == '__main__':
    app.run(debug=True)