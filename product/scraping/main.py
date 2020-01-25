from bottle import run

import app

if __name__ == "__main__":
    run(host='localhost', port=8080, reloader=True, debug=True)