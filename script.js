const TEAM_FLAGS = {
  'México': '🇲🇽', 'África do Sul': '🇿🇦', 'Coreia do Sul': '🇰🇷',
  'República Tcheca': '🇨🇿', 'Canadá': '🇨🇦', 'Bósnia': '🇧🇦',
  'Estados Unidos': '🇺🇸', 'Paraguai': '🇵🇾', 'Catar': '🇶🇦',
  'Suíça': '🇨🇭', 'Brasil': '🇧🇷', 'Marrocos': '🇲🇦',
  'Haiti': '🇭🇹', 'Escócia': '🏴󠁧󠁢󠁳󠁣󠁴󠁿', 'Austrália': '🇦🇺',
  'Turquia': '🇹🇷', 'Alemanha': '🇩🇪', 'Curaçao': '🇨🇼',
  'Holanda': '🇳🇱', 'Japão': '🇯🇵', 'Costa do Marfim': '🇨🇮',
  'Equador': '🇪🇨', 'Suécia': '🇸🇪', 'Tunísia': '🇹🇳',
  'Bélgica': '🇧🇪', 'Egito': '🇪🇬', 'Irã': '🇮🇷',
  'Nova Zelândia': '🇳🇿', 'Espanha': '🇪🇸', 'Cabo Verde': '🇨🇻',
  'Arábia Saudita': '🇸🇦', 'Uruguai': '🇺🇾', 'França': '🇫🇷',
  'Senegal': '🇸🇳', 'Iraque': '🇮🇶', 'Noruega': '🇳🇴',
  'Argentina': '🇦🇷', 'Argélia': '🇩🇿', 'Áustria': '🇦🇹',
  'Jordânia': '🇯🇴', 'Portugal': '🇵🇹', 'RD Congo': '🇨🇩',
  'Uzbequistão': '🇺🇿', 'Colômbia': '🇨🇴', 'Inglaterra': '🏴󠁧󠁢󠁥󠁮󠁧󠁿',
  'Croácia': '🇭🇷', 'Gana': '🇬🇭', 'Panamá': '🇵🇦'
};

const registerForm = document.getElementById('registerForm');
const loginForm = document.getElementById('loginForm');
const authMessage = document.getElementById('authMessage');
const registerMessage = document.getElementById('registerMessage');
const dashboard = document.getElementById('dashboard');
const loginCard = document.getElementById('loginCard');
const userLabel = document.getElementById('userLabel');
const matchesList = document.getElementById('matchesList');
const rankingBody = document.getElementById('rankingBody');
const logoutBtn = document.getElementById('logoutBtn');
const registerModal = document.getElementById('registerModal');
const openRegisterModalBtn = document.getElementById('openRegisterModalBtn');
const closeModalBtn = document.getElementById('closeModalBtn');
const rankingModal = document.getElementById('rankingModal');
const openRankingModalBtn = document.getElementById('openRankingModalBtn');
const closeRankingModalBtn = document.getElementById('closeRankingModalBtn');
const rankingModalBody = document.getElementById('rankingModalBody');

let currentFilter = 'all';

let rankingRefreshInterval = null;

// ── API ──────────────────────────────────────────────────────────────────────

function apiFetch(path, options = {}) {
  const init = { headers: { 'Content-Type': 'application/json' }, ...options };
  if (init.body && typeof init.body !== 'string') {
    init.body = JSON.stringify(init.body);
  }
  return fetch(path, init).then(async response => {
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(payload.error || 'Erro ao conectar com o servidor.');
    return payload;
  });
}

// ── SESSION ──────────────────────────────────────────────────────────────────

function getSessionUser()  { return localStorage.getItem('bolao_current_user'); }
function getSessionToken() { return localStorage.getItem('bolao_token'); }
function setSession(u, t)  { localStorage.setItem('bolao_current_user', u); localStorage.setItem('bolao_token', t); }
function clearSession()    { localStorage.removeItem('bolao_current_user'); localStorage.removeItem('bolao_token'); }

// ── TOAST ────────────────────────────────────────────────────────────────────

function showToast(message, type = 'success') {
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);
  setTimeout(() => {
    toast.classList.add('out');
    toast.addEventListener('animationend', () => toast.remove(), { once: true });
  }, 3500);
}

function showMessage(message, isError = true) {
  authMessage.textContent = message;
  authMessage.style.color = isError ? '#fca5a5' : '#a5f3fc';
}

// ── HELPERS ──────────────────────────────────────────────────────────────────

// Horários do GE estão em Brasília (UTC-3); força o offset para evitar
// que o browser interprete como UTC e feche palpites 3h antes do jogo.
function parseBRT(dateString) {
  return new Date(dateString + '-03:00');
}

function formatDate(dateString) {
  return parseBRT(dateString).toLocaleString('pt-BR', {
    weekday: 'short', day: '2-digit', month: 'short',
    hour: '2-digit', minute: '2-digit'
  });
}

function getMatchStatus(match) {
  const now = new Date();
  const start = parseBRT(match.date);
  if (match.result && now >= start) return { type: 'done', label: 'Finalizado' };
  if (now >= start) return { type: 'closed', label: 'Encerrado' };
  return { type: 'upcoming', label: 'Aberto' };
}

function getMatchWinner(result) {
  if (result.home > result.away) return 'home';
  if (result.home < result.away) return 'away';
  return 'draw';
}

function flag(teamName) {
  return TEAM_FLAGS[teamName] || '🏳';
}

// ── MATCH CARD ───────────────────────────────────────────────────────────────

function createMatchCard(match, currentUser, predictions) {
  const existing = predictions.find(p => p.matchId === match.id);
  const status = getMatchStatus(match);
  const homeFlag = flag(match.home);
  const awayFlag = flag(match.away);
  const winner = (status.type === 'done' && match.result) ? getMatchWinner(match.result) : null;

  const card = document.createElement('div');
  card.className = 'match-card';
  card.dataset.hasPrediction = existing ? 'true' : 'false';
  card.dataset.isDone = (status.type === 'done') ? 'true' : 'false';
  card.dataset.isOpen = (status.type === 'upcoming') ? 'true' : 'false';

  // Top row: group badge + status pill
  const top = document.createElement('div');
  top.className = 'match-card-top';

  const groupBadge = document.createElement('span');
  groupBadge.className = 'match-group-badge';
  groupBadge.textContent = match.group;

  const pill = document.createElement('span');
  pill.className = `status-pill status-${status.type}`;
  pill.textContent = status.label;

  top.append(groupBadge, pill);

  // Teams row
  const teams = document.createElement('div');
  teams.className = 'match-teams';

  const homeTeam = makeTeam(homeFlag, match.home, 'home');
  const awayTeam = makeTeam(awayFlag, match.away, 'away');

  const center = document.createElement('div');
  center.className = 'match-center';

  if (winner !== null && match.result) {
    const score = document.createElement('span');
    score.className = 'match-score-display';
    score.textContent = `${match.result.home} — ${match.result.away}`;
    center.appendChild(score);
  } else {
    const vs = document.createElement('span');
    vs.className = 'match-vs';
    vs.textContent = '×';
    center.appendChild(vs);
  }

  teams.append(homeTeam, center, awayTeam);

  // Date
  const dateEl = document.createElement('div');
  dateEl.className = 'match-date';
  dateEl.textContent = formatDate(match.date);

  // Vote buttons
  const voteRow = document.createElement('div');
  voteRow.className = 'vote-row';

  const choices = [
    { label: `${homeFlag} ${match.home}`, value: 'home' },
    { label: '🤝 Empate', value: 'draw' },
    { label: `${awayFlag} ${match.away}`, value: 'away' }
  ];

  choices.forEach(choice => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'vote-btn';
    btn.textContent = choice.label;

    const isSelected = existing && existing.choice === choice.value;
    if (isSelected) btn.classList.add('active');

    if (winner !== null && isSelected) {
      btn.classList.add(winner === choice.value ? 'correct' : 'incorrect');
    }

    if (status.type !== 'upcoming') {
      btn.disabled = true;
    } else {
      btn.addEventListener('click', async () => {
        try {
          await apiFetch('/api/prediction', {
            method: 'POST',
            body: { username: currentUser, token: getSessionToken(), matchId: match.id, choice: choice.value }
          });
          showToast('Palpite registrado!', 'success');
          await renderDashboard(currentUser);
        } catch (error) {
          showToast(error.message, 'error');
        }
      });
    }

    voteRow.appendChild(btn);
  });

  if (status.type === 'done' && existing) {
    const feedback = document.createElement('div');
    const hit = winner === existing.choice;
    feedback.className = `match-feedback ${hit ? 'feedback-hit' : 'feedback-miss'}`;
    feedback.textContent = hit ? '✓ Acertou!' : '✗ Errou.';
    card.append(top, teams, dateEl, voteRow, feedback);
  } else {
    card.append(top, teams, dateEl, voteRow);
  }
  return card;
}

function makeTeam(flagEmoji, name, side) {
  const div = document.createElement('div');
  div.className = `team ${side}`;

  const f = document.createElement('span');
  f.className = 'team-flag';
  f.textContent = flagEmoji;

  const n = document.createElement('span');
  n.className = 'team-name';
  n.textContent = name;

  div.append(f, n);
  return div;
}

// ── RENDER MATCHES ───────────────────────────────────────────────────────────

function renderMatchesList(matches, currentUser, predictions) {
  matchesList.innerHTML = '';

  const groups = {};
  matches.forEach(match => {
    if (!groups[match.group]) groups[match.group] = [];
    groups[match.group].push(match);
  });

  let first = true;
  Object.entries(groups).forEach(([groupName, groupMatches]) => {
    const header = document.createElement('div');
    header.className = 'group-header';
    if (first) { header.style.marginTop = '0'; first = false; }
    header.textContent = groupName;
    matchesList.appendChild(header);

    groupMatches.forEach(match => {
      matchesList.appendChild(createMatchCard(match, currentUser, predictions));
    });
  });
}

// ── RENDER RANKING ───────────────────────────────────────────────────────────

function buildRankingRows(ranking, currentUser) {
  const rows = [];
  if (ranking.length === 0) {
    const row = document.createElement('tr');
    const cell = document.createElement('td');
    cell.colSpan = 3;
    cell.className = 'empty-row';
    cell.textContent = 'Nenhum participante ainda.';
    row.appendChild(cell);
    return [row];
  }
  ranking.forEach((entry, index) => {
    const pos = index + 1;
    const row = document.createElement('tr');
    if (pos === 1) row.classList.add('rank-gold');
    else if (pos === 2) row.classList.add('rank-silver');
    else if (pos === 3) row.classList.add('rank-bronze');
    if (pos > 3) row.classList.add('rank-extra');
    if (entry.username.toLowerCase() === currentUser.toLowerCase()) row.classList.add('rank-current');

    const posCell = document.createElement('td');
    posCell.textContent = pos === 1 ? '🥇' : pos === 2 ? '🥈' : pos === 3 ? '🥉' : pos;
    const nameCell = document.createElement('td');
    nameCell.textContent = entry.username;
    const ptsCell = document.createElement('td');
    ptsCell.textContent = entry.points;

    row.append(posCell, nameCell, ptsCell);
    rows.push(row);
  });
  return rows;
}

function renderRankingTable(ranking, currentUser) {
  rankingBody.innerHTML = '';
  rankingModalBody.innerHTML = '';
  buildRankingRows(ranking, currentUser).forEach(row => {
    rankingBody.appendChild(row.cloneNode(true));
    rankingModalBody.appendChild(row.cloneNode(true));
  });
}

// ── DASHBOARD ────────────────────────────────────────────────────────────────

async function renderDashboard(username) {
  userLabel.textContent = username;
  document.getElementById('userAvatar').textContent = username.charAt(0).toUpperCase();
  dashboard.classList.remove('hidden');

  const [matchesData, predictionsData, rankingData] = await Promise.all([
    apiFetch('/api/matches'),
    apiFetch(`/api/predictions?username=${encodeURIComponent(username)}`),
    apiFetch('/api/ranking')
  ]);

  const sorted = [...matchesData.matches].sort((a, b) => new Date(a.date) - new Date(b.date));
  const predictions = predictionsData.predictions;

  // Calculate user stats
  let points = 0;
  predictions.forEach(p => {
    const m = sorted.find(x => x.id === p.matchId);
    if (m && m.result && getMatchStatus(m).type === 'done') {
      if (getMatchWinner(m.result) === p.choice) points++;
    }
  });

  document.getElementById('userPointsChip').textContent =
    `${points} ${points === 1 ? 'ponto' : 'pontos'}`;
  document.getElementById('userPredictionsChip').textContent =
    `${predictions.length} ${predictions.length === 1 ? 'palpite' : 'palpites'}`;

  renderMatchesList(sorted, username, predictions);
  applyMatchFilter();
  renderRankingTable(rankingData.ranking, username);
}

// ── RANKING AUTO-REFRESH ──────────────────────────────────────────────────────

async function refreshRankingOnly(username) {
  try {
    const data = await apiFetch('/api/ranking');
    renderRankingTable(data.ranking, username);
  } catch (_) {}
}

// ── MODAL ────────────────────────────────────────────────────────────────────

function openModal() {
  registerForm.reset();
  registerMessage.textContent = '';
  registerModal.classList.remove('hidden');
  document.getElementById('registerUsername').focus();
}

function closeModal() {
  registerModal.classList.add('hidden');
}

openRegisterModalBtn.addEventListener('click', openModal);
closeModalBtn.addEventListener('click', closeModal);
registerModal.addEventListener('click', e => { if (e.target === registerModal) closeModal(); });

openRankingModalBtn.addEventListener('click', () => {
  rankingModal.classList.remove('hidden');
});
closeRankingModalBtn.addEventListener('click', () => {
  rankingModal.classList.add('hidden');
});
rankingModal.addEventListener('click', e => { if (e.target === rankingModal) rankingModal.classList.add('hidden'); });

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    closeModal();
    rankingModal.classList.add('hidden');
  }
});

// ── FILTRO DE JOGOS ──────────────────────────────────────────────────────────

document.querySelectorAll('.filter-chip').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-chip').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    currentFilter = btn.dataset.filter;
    applyMatchFilter();
  });
});

function applyMatchFilter() {
  document.querySelectorAll('.match-card').forEach(card => {
    const hasPrediction = card.dataset.hasPrediction === 'true';
    const isDone = card.dataset.isDone === 'true';
    const isOpen = card.dataset.isOpen === 'true';
    let visible = true;
    if (currentFilter === 'pending') visible = !hasPrediction && isOpen;
    else if (currentFilter === 'open') visible = isOpen;
    else if (currentFilter === 'done') visible = isDone;
    card.style.display = visible ? '' : 'none';
  });

  // mostra/oculta cabeçalhos de grupo que ficaram sem jogos visíveis
  document.querySelectorAll('.group-header').forEach(header => {
    let next = header.nextElementSibling;
    let hasVisible = false;
    while (next && !next.classList.contains('group-header')) {
      if (next.style.display !== 'none') { hasVisible = true; break; }
      next = next.nextElementSibling;
    }
    header.style.display = hasVisible ? '' : 'none';
  });
}

// ── LOGOUT ───────────────────────────────────────────────────────────────────

function logout() {
  clearSession();
  if (rankingRefreshInterval) { clearInterval(rankingRefreshInterval); rankingRefreshInterval = null; }
  dashboard.classList.add('hidden');
  loginCard.classList.remove('hidden');
  showMessage('Você foi desconectado. Faça login novamente.', false);
}

logoutBtn.addEventListener('click', logout);

// ── REGISTER ─────────────────────────────────────────────────────────────────

registerForm.addEventListener('submit', async event => {
  event.preventDefault();
  const username = document.getElementById('registerUsername').value.trim();
  const code = document.getElementById('registerCode').value.trim();

  if (!username || !code) {
    showMessage('Preencha username e a senha do bolão.', true);
    return;
  }

  try {
    const res = await apiFetch('/api/register', { method: 'POST', body: { username, code } });
    setSession(username, res.token);
    closeModal();
    authMessage.textContent = '';
    loginCard.classList.add('hidden');
    await renderDashboard(username);
    rankingRefreshInterval = setInterval(() => refreshRankingOnly(username), 30000);
    showToast(`Bem-vindo, ${username}!`, 'success');
  } catch (error) {
    registerMessage.textContent = error.message;
    registerMessage.style.color = '#fca5a5';
  }
});

// ── LOGIN ─────────────────────────────────────────────────────────────────────

loginForm.addEventListener('submit', async event => {
  event.preventDefault();
  const username = document.getElementById('loginUsername').value.trim();
  const code = document.getElementById('loginCode').value.trim();

  if (!username || !code) {
    showMessage('Informe username e a senha do bolão para entrar.', true);
    return;
  }

  try {
    const res = await apiFetch('/api/login', { method: 'POST', body: { username, code } });
    setSession(username, res.token);
    authMessage.textContent = '';
    loginCard.classList.add('hidden');
    await renderDashboard(username);
    rankingRefreshInterval = setInterval(() => refreshRankingOnly(username), 30000);
  } catch (error) {
    showMessage(error.message, true);
  }
});

// ── INIT ──────────────────────────────────────────────────────────────────────

window.addEventListener('load', async () => {
  const currentUser = getSessionUser();
  const currentToken = getSessionToken();
  if (currentUser && currentToken) {
    try {
      loginCard.classList.add('hidden');
      await renderDashboard(currentUser);
      rankingRefreshInterval = setInterval(() => refreshRankingOnly(currentUser), 30000);
    } catch (error) {
      logout();
    }
  } else if (currentUser && !currentToken) {
    clearSession();
  }
});
