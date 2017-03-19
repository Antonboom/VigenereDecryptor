import json

from flask import (
    Flask,
    request,
    render_template
)
from flask import Response

from core import Vigenere


app = Flask(__name__, template_folder='templates', static_folder='static', static_url_path='/static')


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', **{})


@app.route('/vigenere', methods=['POST'])
def vigenere():
    SOLUTIONS_COUNT_LIMIT = 1000

    vig = Vigenere()

    key = request.form.get('key')
    encrypt_text = request.form.get('encrypt_text')

    gramm_repeats_min_count = int(request.form.get('gramm_repeats') or 2)
    symbol_repeats_min_count = int(request.form.get('symbol_repeats') or 2)
    key_length = int(request.form.get('key_length') or 0)

    if key and encrypt_text:
        solution = vig.decrypt(encrypt_text, key)

        if len(solution['keys']) >= SOLUTIONS_COUNT_LIMIT:
            solution = {'error': 'Solutions count > {}'.format(SOLUTIONS_COUNT_LIMIT)}

    elif encrypt_text:
        solution = vig.vigenering(
            encrypt_text=encrypt_text,
            gramm_repeats_min_count=gramm_repeats_min_count,
            symbol_repeats_min_count=symbol_repeats_min_count,
            key_length=key_length
        )

        if len(solution['keys']) >= SOLUTIONS_COUNT_LIMIT:
            solution = {'error': 'Solutions count > {}'.format(SOLUTIONS_COUNT_LIMIT)}

    else:
        solution = {'error': 'Invalid params'}

    return Response(json.dumps(solution), content_type='application/json')


if __name__ == "__main__":
    app.run(debug=True)
