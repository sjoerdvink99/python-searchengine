import op
from flask import Flask, request, render_template


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET'])
def result():
    if request.method == 'GET':
        query = request.args['query']
        queries = query.split()
        context = op.artikelInformatie(queries)
    return render_template('result.html', context=[context], query=[query])


if __name__ == '__main__':
    app.run(debug=True)