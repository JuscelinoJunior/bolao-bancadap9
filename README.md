# Bolão da Copa

Aplicação local de bolão para Copa com persistência em SQLite. Permite criar conta com `username` e `código único`, fazer palpites e conferir ranking.

## O que é o código único?

O código único é a senha secreta do seu cadastro. Ele é usado junto com o `username` para entrar no bolão. Cada pessoa escolhe seu próprio código quando cria a conta.

## Como usar

1. Abra um terminal na pasta deste projeto.
2. Execute `python3 server.py`.
3. Abra `http://localhost:8000` no navegador.
4. Use "Criar conta" para registrar `username` e a `senha do bolão` (única para o bolão).
5. Faça login com o mesmo `username` e a `senha do bolão`.
6. Escolha vitória, empate ou derrota nos jogos abertos.
7. Jogos já iniciados ficam bloqueados e não aceitam mais palpites.
8. Veja o ranking com pontuação somando 1 ponto por acerto.

## Sobre
- O bolão é apenas vitória, empate ou derrota.
- Cada acerto vale 1 ponto.
- O login funciona com `username` + `senha do bolão` (senha universal do bolão).
- Os dados são guardados localmente em `bolao.db` usando SQLite.
- O servidor serve a interface e a API para manter os dados persistidos.
