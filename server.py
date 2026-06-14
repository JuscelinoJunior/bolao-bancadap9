import json
import os
import secrets
import sqlite3
from datetime import datetime, timezone, timedelta

BRT = timezone(timedelta(hours=-3))
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

DB_FILENAME = os.environ.get('DB_PATH', 'bolao.db')
PORT = int(os.environ.get('PORT', 8000))

_db_dir = os.path.dirname(DB_FILENAME)
if _db_dir:
    os.makedirs(_db_dir, exist_ok=True)
# senha universal do bolão (altere aqui para sua senha)
POOL_CODE = 'CrvgP9@2026!'

MATCHES = [
    {'id': 1, 'group': 'Grupo A', 'home': 'México', 'away': 'África do Sul', 'date': '2026-06-11T16:00:00', 'result': {'home': 2, 'away': 0}},
    {'id': 2, 'group': 'Grupo A', 'home': 'Coreia do Sul', 'away': 'República Tcheca', 'date': '2026-06-11T23:00:00', 'result': {'home': 2, 'away': 1}},
    {'id': 3, 'group': 'Grupo B', 'home': 'Canadá', 'away': 'Bósnia', 'date': '2026-06-12T16:00:00', 'result': {'home': 1, 'away': 1}},
    {'id': 4, 'group': 'Grupo D', 'home': 'Estados Unidos', 'away': 'Paraguai', 'date': '2026-06-12T22:00:00', 'result': {'home': 4, 'away': 1}},
    {'id': 5, 'group': 'Grupo B', 'home': 'Catar', 'away': 'Suíça', 'date': '2026-06-13T16:00:00', 'result': {'home': 1, 'away': 1}},
    {'id': 6, 'group': 'Grupo C', 'home': 'Brasil', 'away': 'Marrocos', 'date': '2026-06-13T19:00:00', 'result': {'home': 1, 'away': 1}},
    {'id': 7, 'group': 'Grupo C', 'home': 'Haiti', 'away': 'Escócia', 'date': '2026-06-13T22:00:00', 'result': {'home': 0, 'away': 1}},
    {'id': 8, 'group': 'Grupo D', 'home': 'Austrália', 'away': 'Turquia', 'date': '2026-06-14T01:00:00', 'result': {'home': 2, 'away': 0}},
    {'id': 9, 'group': 'Grupo E', 'home': 'Alemanha', 'away': 'Curaçao', 'date': '2026-06-14T14:00:00', 'result': {'home': 7, 'away': 1}},
    {'id': 10, 'group': 'Grupo F', 'home': 'Holanda', 'away': 'Japão', 'date': '2026-06-14T17:00:00', 'result': {'home': 2, 'away': 2}},
    {'id': 11, 'group': 'Grupo E', 'home': 'Costa do Marfim', 'away': 'Equador', 'date': '2026-06-14T20:00:00', 'result': None},
    {'id': 12, 'group': 'Grupo F', 'home': 'Suécia', 'away': 'Tunísia', 'date': '2026-06-14T23:00:00', 'result': None},
    {'id': 13, 'group': 'Grupo H', 'home': 'Espanha', 'away': 'Cabo Verde', 'date': '2026-06-15T13:00:00', 'result': None},
    {'id': 14, 'group': 'Grupo G', 'home': 'Bélgica', 'away': 'Egito', 'date': '2026-06-15T16:00:00', 'result': None},
    {'id': 15, 'group': 'Grupo H', 'home': 'Arábia Saudita', 'away': 'Uruguai', 'date': '2026-06-15T19:00:00', 'result': None},
    {'id': 16, 'group': 'Grupo G', 'home': 'Irã', 'away': 'Nova Zelândia', 'date': '2026-06-15T22:00:00', 'result': None},
    {'id': 17, 'group': 'Grupo I', 'home': 'França', 'away': 'Senegal', 'date': '2026-06-16T16:00:00', 'result': None},
    {'id': 18, 'group': 'Grupo I', 'home': 'Iraque', 'away': 'Noruega', 'date': '2026-06-16T19:00:00', 'result': None},
    {'id': 19, 'group': 'Grupo J', 'home': 'Argentina', 'away': 'Argélia', 'date': '2026-06-16T22:00:00', 'result': None},
    {'id': 20, 'group': 'Grupo J', 'home': 'Áustria', 'away': 'Jordânia', 'date': '2026-06-17T01:00:00', 'result': None},
    {'id': 21, 'group': 'Grupo K', 'home': 'Portugal', 'away': 'RD Congo', 'date': '2026-06-17T14:00:00', 'result': None},
    {'id': 22, 'group': 'Grupo L', 'home': 'Inglaterra', 'away': 'Croácia', 'date': '2026-06-17T17:00:00', 'result': None},
    {'id': 23, 'group': 'Grupo L', 'home': 'Gana', 'away': 'Panamá', 'date': '2026-06-17T20:00:00', 'result': None},
    {'id': 24, 'group': 'Grupo K', 'home': 'Uzbequistão', 'away': 'Colômbia', 'date': '2026-06-17T23:00:00', 'result': None},
    # Rodada 2
    {'id': 25, 'group': 'Grupo A', 'home': 'República Tcheca', 'away': 'África do Sul', 'date': '2026-06-18T13:00:00', 'result': None},
    {'id': 26, 'group': 'Grupo B', 'home': 'Suíça', 'away': 'Bósnia', 'date': '2026-06-18T16:00:00', 'result': None},
    {'id': 27, 'group': 'Grupo B', 'home': 'Canadá', 'away': 'Catar', 'date': '2026-06-18T19:00:00', 'result': None},
    {'id': 28, 'group': 'Grupo A', 'home': 'México', 'away': 'Coreia do Sul', 'date': '2026-06-18T22:00:00', 'result': None},
    {'id': 29, 'group': 'Grupo D', 'home': 'Estados Unidos', 'away': 'Austrália', 'date': '2026-06-19T16:00:00', 'result': None},
    {'id': 30, 'group': 'Grupo C', 'home': 'Escócia', 'away': 'Marrocos', 'date': '2026-06-19T19:00:00', 'result': None},
    {'id': 31, 'group': 'Grupo C', 'home': 'Brasil', 'away': 'Haiti', 'date': '2026-06-19T21:30:00', 'result': None},
    {'id': 32, 'group': 'Grupo D', 'home': 'Turquia', 'away': 'Paraguai', 'date': '2026-06-20T00:00:00', 'result': None},
    {'id': 33, 'group': 'Grupo F', 'home': 'Holanda', 'away': 'Suécia', 'date': '2026-06-20T14:00:00', 'result': None},
    {'id': 34, 'group': 'Grupo E', 'home': 'Alemanha', 'away': 'Costa do Marfim', 'date': '2026-06-20T17:00:00', 'result': None},
    {'id': 35, 'group': 'Grupo E', 'home': 'Equador', 'away': 'Curaçao', 'date': '2026-06-20T21:00:00', 'result': None},
    {'id': 36, 'group': 'Grupo F', 'home': 'Tunísia', 'away': 'Japão', 'date': '2026-06-21T01:00:00', 'result': None},
    {'id': 37, 'group': 'Grupo H', 'home': 'Espanha', 'away': 'Arábia Saudita', 'date': '2026-06-21T13:00:00', 'result': None},
    {'id': 38, 'group': 'Grupo G', 'home': 'Bélgica', 'away': 'Irã', 'date': '2026-06-21T16:00:00', 'result': None},
    {'id': 39, 'group': 'Grupo H', 'home': 'Uruguai', 'away': 'Cabo Verde', 'date': '2026-06-21T19:00:00', 'result': None},
    {'id': 40, 'group': 'Grupo G', 'home': 'Nova Zelândia', 'away': 'Egito', 'date': '2026-06-21T22:00:00', 'result': None},
    {'id': 41, 'group': 'Grupo J', 'home': 'Argentina', 'away': 'Áustria', 'date': '2026-06-22T14:00:00', 'result': None},
    {'id': 42, 'group': 'Grupo I', 'home': 'França', 'away': 'Iraque', 'date': '2026-06-22T18:00:00', 'result': None},
    {'id': 43, 'group': 'Grupo I', 'home': 'Noruega', 'away': 'Senegal', 'date': '2026-06-22T21:00:00', 'result': None},
    {'id': 44, 'group': 'Grupo J', 'home': 'Jordânia', 'away': 'Argélia', 'date': '2026-06-23T00:00:00', 'result': None},
    {'id': 45, 'group': 'Grupo K', 'home': 'Portugal', 'away': 'Uzbequistão', 'date': '2026-06-23T14:00:00', 'result': None},
    {'id': 46, 'group': 'Grupo L', 'home': 'Inglaterra', 'away': 'Gana', 'date': '2026-06-23T17:00:00', 'result': None},
    {'id': 47, 'group': 'Grupo L', 'home': 'Panamá', 'away': 'Croácia', 'date': '2026-06-23T20:00:00', 'result': None},
    {'id': 48, 'group': 'Grupo K', 'home': 'Colômbia', 'away': 'RD Congo', 'date': '2026-06-23T23:00:00', 'result': None},
    # Rodada 3
    {'id': 49, 'group': 'Grupo B', 'home': 'Suíça', 'away': 'Canadá', 'date': '2026-06-24T16:00:00', 'result': None},
    {'id': 50, 'group': 'Grupo B', 'home': 'Bósnia', 'away': 'Catar', 'date': '2026-06-24T16:00:00', 'result': None},
    {'id': 51, 'group': 'Grupo C', 'home': 'Marrocos', 'away': 'Haiti', 'date': '2026-06-24T19:00:00', 'result': None},
    {'id': 52, 'group': 'Grupo C', 'home': 'Escócia', 'away': 'Brasil', 'date': '2026-06-24T19:00:00', 'result': None},
    {'id': 53, 'group': 'Grupo A', 'home': 'África do Sul', 'away': 'Coreia do Sul', 'date': '2026-06-24T22:00:00', 'result': None},
    {'id': 54, 'group': 'Grupo A', 'home': 'República Tcheca', 'away': 'México', 'date': '2026-06-24T22:00:00', 'result': None},
    {'id': 55, 'group': 'Grupo E', 'home': 'Equador', 'away': 'Alemanha', 'date': '2026-06-25T17:00:00', 'result': None},
    {'id': 56, 'group': 'Grupo E', 'home': 'Curaçao', 'away': 'Costa do Marfim', 'date': '2026-06-25T17:00:00', 'result': None},
    {'id': 57, 'group': 'Grupo F', 'home': 'Tunísia', 'away': 'Holanda', 'date': '2026-06-25T20:00:00', 'result': None},
    {'id': 58, 'group': 'Grupo F', 'home': 'Japão', 'away': 'Suécia', 'date': '2026-06-25T20:00:00', 'result': None},
    {'id': 59, 'group': 'Grupo D', 'home': 'Turquia', 'away': 'Estados Unidos', 'date': '2026-06-25T23:00:00', 'result': None},
    {'id': 60, 'group': 'Grupo D', 'home': 'Paraguai', 'away': 'Austrália', 'date': '2026-06-25T23:00:00', 'result': None},
    {'id': 61, 'group': 'Grupo I', 'home': 'Senegal', 'away': 'Iraque', 'date': '2026-06-26T16:00:00', 'result': None},
    {'id': 62, 'group': 'Grupo I', 'home': 'Noruega', 'away': 'França', 'date': '2026-06-26T16:00:00', 'result': None},
    {'id': 63, 'group': 'Grupo H', 'home': 'Cabo Verde', 'away': 'Arábia Saudita', 'date': '2026-06-26T21:00:00', 'result': None},
    {'id': 64, 'group': 'Grupo H', 'home': 'Uruguai', 'away': 'Espanha', 'date': '2026-06-26T21:00:00', 'result': None},
    {'id': 65, 'group': 'Grupo G', 'home': 'Egito', 'away': 'Irã', 'date': '2026-06-27T00:00:00', 'result': None},
    {'id': 66, 'group': 'Grupo G', 'home': 'Nova Zelândia', 'away': 'Bélgica', 'date': '2026-06-27T00:00:00', 'result': None},
    {'id': 67, 'group': 'Grupo L', 'home': 'Croácia', 'away': 'Gana', 'date': '2026-06-27T18:00:00', 'result': None},
    {'id': 68, 'group': 'Grupo L', 'home': 'Panamá', 'away': 'Inglaterra', 'date': '2026-06-27T18:00:00', 'result': None},
    {'id': 69, 'group': 'Grupo K', 'home': 'RD Congo', 'away': 'Uzbequistão', 'date': '2026-06-27T20:30:00', 'result': None},
    {'id': 70, 'group': 'Grupo K', 'home': 'Colômbia', 'away': 'Portugal', 'date': '2026-06-27T20:30:00', 'result': None},
    {'id': 71, 'group': 'Grupo J', 'home': 'Jordânia', 'away': 'Argentina', 'date': '2026-06-27T23:00:00', 'result': None},
    {'id': 72, 'group': 'Grupo J', 'home': 'Argélia', 'away': 'Áustria', 'date': '2026-06-27T23:00:00', 'result': None},
]


def init_db():
    connection = sqlite3.connect(DB_FILENAME)
    cursor = connection.cursor()
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS users (
             id INTEGER PRIMARY KEY,
             username TEXT UNIQUE NOT NULL,
             code TEXT NOT NULL,
             created_at TEXT NOT NULL
           )'''
    )
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS predictions (
             id INTEGER PRIMARY KEY,
             user_id INTEGER NOT NULL,
             match_id INTEGER NOT NULL,
             choice TEXT NOT NULL,
             UNIQUE(user_id, match_id),
             FOREIGN KEY(user_id) REFERENCES users(id)
           )'''
    )
    # migração: adiciona coluna token se ainda não existir
    try:
        cursor.execute('ALTER TABLE users ADD COLUMN token TEXT')
    except sqlite3.OperationalError:
        pass
    connection.commit()
    connection.close()


def get_db_connection():
    return sqlite3.connect(DB_FILENAME)


def json_response(handler, data, status=200):
    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json; charset=utf-8')
    handler.send_header('Content-Length', str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def parse_request_body(handler):
    length = int(handler.headers.get('Content-Length', 0))
    if length == 0:
        return {}
    body = handler.rfile.read(length)
    return json.loads(body.decode('utf-8'))


def lower_username(username):
    return username.strip().lower()


def get_match_by_id(match_id):
    for match in MATCHES:
        if match['id'] == match_id:
            return match
    return None


def match_winner(result):
    if result['home'] > result['away']:
        return 'home'
    if result['home'] < result['away']:
        return 'away'
    return 'draw'


def match_status(match):
    now = datetime.now(BRT).replace(tzinfo=None)
    start = datetime.fromisoformat(match['date'])
    if match['result'] is not None and now >= start:
        return 'done'
    if now >= start:
        return 'closed'
    return 'upcoming'


def calculate_ranking():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT id, username FROM users')
    users = cursor.fetchall()
    ranking = []

    for user_id, username in users:
        cursor.execute('SELECT match_id, choice FROM predictions WHERE user_id = ?', (user_id,))
        predictions = cursor.fetchall()
        score = 0
        for match_id, choice in predictions:
            match = get_match_by_id(match_id)
            if not match or match['result'] is None:
                continue
            if match_winner(match['result']) == choice:
                score += 1
        ranking.append({'username': username, 'points': score})

    connection.close()
    ranking.sort(key=lambda entry: (-entry['points'], entry['username'].lower()))
    return ranking


class BolaoHandler(SimpleHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/'):
            return self.handle_api_get(parsed)
        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith('/api/'):
            return self.handle_api_post(parsed)
        self.send_error(404, 'Not Found')

    def handle_api_get(self, parsed):
        if parsed.path == '/api/matches':
            json_response(self, {'matches': MATCHES})
            return

        if parsed.path == '/api/predictions':
            params = parse_qs(parsed.query)
            username = params.get('username', [''])[0].strip()
            if not username:
                return json_response(self, {'error': 'Username é obrigatório.'}, status=400)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE lower(username) = ?', (lower_username(username),))
            user = cursor.fetchone()
            if not user:
                connection.close()
                return json_response(self, {'error': 'Usuário não encontrado.'}, status=404)

            user_id = user[0]
            cursor.execute('SELECT match_id, choice FROM predictions WHERE user_id = ?', (user_id,))
            predictions = [{'matchId': row[0], 'choice': row[1]} for row in cursor.fetchall()]
            connection.close()
            json_response(self, {'predictions': predictions})
            return

        if parsed.path == '/api/ranking':
            json_response(self, {'ranking': calculate_ranking()})
            return

        self.send_error(404, 'API endpoint não encontrado')

    def handle_api_post(self, parsed):
        if parsed.path == '/api/register':
            try:
                data = parse_request_body(self)
            except json.JSONDecodeError:
                return json_response(self, {'error': 'JSON inválido.'}, status=400)

            username = data.get('username', '').strip()
            code = data.get('code', '').strip()
            if not username or not code:
                return json_response(self, {'error': 'Preencha username e senha do bolão.'}, status=400)
            if code != POOL_CODE:
                return json_response(self, {'error': 'Senha do bolão inválida.'}, status=401)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE lower(username) = ?', (lower_username(username),))
            if cursor.fetchone():
                connection.close()
                return json_response(self, {'error': 'Username já existe.'}, status=400)

            token = secrets.token_hex(32)
            cursor.execute(
                'INSERT INTO users (username, code, created_at, token) VALUES (?, ?, ?, ?)',
                (username, code, datetime.utcnow().isoformat(), token)
            )
            connection.commit()
            connection.close()
            json_response(self, {'message': 'Conta criada com sucesso.', 'username': username, 'token': token})
            return

        if parsed.path == '/api/login':
            try:
                data = parse_request_body(self)
            except json.JSONDecodeError:
                return json_response(self, {'error': 'JSON inválido.'}, status=400)

            username = data.get('username', '').strip()
            code = data.get('code', '').strip()
            if not username or not code:
                return json_response(self, {'error': 'Preencha username e senha do bolão.'}, status=400)
            if code != POOL_CODE:
                return json_response(self, {'error': 'Senha do bolão inválida.'}, status=401)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE lower(username) = ?', (lower_username(username),))
            user = cursor.fetchone()
            if not user:
                connection.close()
                return json_response(self, {'error': 'Usuário não encontrado.'}, status=401)

            token = secrets.token_hex(32)
            cursor.execute('UPDATE users SET token = ? WHERE id = ?', (token, user[0]))
            connection.commit()
            connection.close()
            json_response(self, {'message': 'Login bem sucedido.', 'username': username, 'token': token})
            return

        if parsed.path == '/api/prediction':
            try:
                data = parse_request_body(self)
            except json.JSONDecodeError:
                return json_response(self, {'error': 'JSON inválido.'}, status=400)

            username = data.get('username', '').strip()
            token = data.get('token', '').strip()
            match_id = data.get('matchId')
            choice = data.get('choice', '').strip()
            if not username or not token or not match_id or choice not in ('home', 'draw', 'away'):
                return json_response(self, {'error': 'Dados de palpite inválidos.'}, status=400)

            match = get_match_by_id(int(match_id))
            if not match:
                return json_response(self, {'error': 'Jogo não encontrado.'}, status=404)
            if match_status(match) != 'upcoming':
                return json_response(self, {'error': 'Palpites encerrados para esse jogo.'}, status=400)

            connection = get_db_connection()
            cursor = connection.cursor()
            cursor.execute('SELECT id FROM users WHERE lower(username) = ? AND token = ?', (lower_username(username), token))
            user = cursor.fetchone()
            if not user:
                connection.close()
                return json_response(self, {'error': 'Sessão inválida. Faça login novamente.'}, status=401)

            user_id = user[0]
            cursor.execute(
                'INSERT OR REPLACE INTO predictions (user_id, match_id, choice) VALUES (?, ?, ?)',
                (user_id, match['id'], choice)
            )
            connection.commit()
            connection.close()
            json_response(self, {'message': 'Palpite registrado com sucesso.'})
            return

        self.send_error(404, 'API endpoint não encontrado')

    def send_error(self, code, message=None, explain=None):
        if self.path.startswith('/api/'):
            json_response(self, {'error': message or self.responses.get(code, ('',))[0]}, status=code)
        else:
            super().send_error(code, message, explain)


if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    init_db()
    server = ThreadingHTTPServer(('0.0.0.0', PORT), BolaoHandler)
    print(f'Servidor iniciado em http://localhost:{PORT}')
    server.serve_forever()
