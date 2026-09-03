const $ = id => document.getElementById(id);
const base = () => $('baseUrl').value.replace(/\/+$/, '');

let devToken = null;
let apiKey = null;

async function call(path, options = {}) {
  const res = await fetch(base() + path, options);
  const text = await res.text();
  let body;
  try { body = JSON.parse(text); } catch { body = text; }
  return { status: res.status, ok: res.ok, body };
}

function show(id, obj) {
  $(id).textContent = typeof obj === 'string' ? obj : JSON.stringify(obj, null, 2);
}

async function devRegister() {
  const r = await call('/developers/registration', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      email: $('devRegEmail').value,
      plain_password: $('devRegPass').value
    })
  });
  show('devRegOut', { status: r.status, body: r.body });
}

async function devLogin() {
  const params = new URLSearchParams();
  params.set('username', $('devLoginEmail').value);
  params.set('password', $('devLoginPass').value);

  const r = await call('/developers/dev-login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString()
  });
  show('devLoginOut', { status: r.status, body: r.body });

  if (r.ok && r.body.access_token) {
    devToken = r.body.access_token;
    $('devTokenShown').textContent = devToken.slice(0, 24) + '...';
  }
}

async function createProject() {
  if (!devToken) {
    show('projOut', 'Log in as a developer first (step 2)');
    return;
  }
  const r = await call('/developers/projects/new_project', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + devToken
    },
    body: JSON.stringify({ project_name: $('projName').value })
  });
  show('projOut', { status: r.status, body: r.body });

  if (r.ok && r.body.API) {
    apiKey = r.body.API;
    $('apiKeyShown').textContent = apiKey;
    $('euApiKey').value = apiKey;
    $('euLoginApiKey').value = apiKey;
    if (r.body.project_id) $('listProjectId').value = r.body.project_id;
  }
}

async function listUsers() {
  if (!devToken) {
    show('listOut', 'Log in as a developer first (step 2)');
    return;
  }
  const pid = $('listProjectId').value;
  const r = await call(`/developers/projects/users?project_id=${encodeURIComponent(pid)}`, {
    headers: { 'Authorization': 'Bearer ' + devToken }
  });
  show('listOut', { status: r.status, body: r.body });
}

async function euRegister() {
  const key = $('euApiKey').value || apiKey;
  if (!key) {
    show('euRegOut', 'Create a project first to get an API key (step 3)');
    return;
  }
  const r = await call('/end-user/new-user', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'API-key': key },
    body: JSON.stringify({
      email: $('euRegEmail').value,
      name: $('euRegName').value,
      plain_password: $('euRegPass').value
    })
  });
  show('euRegOut', { status: r.status, body: r.body });
}

async function euLogin() {
  const key = $('euLoginApiKey').value || apiKey;
  if (!key) {
    show('euLoginOut', 'Create a project first to get an API key (step 3)');
    return;
  }
  const params = new URLSearchParams();
  params.set('username', $('euLoginEmail').value);
  params.set('password', $('euLoginPass').value);

  const r = await call('/end-user/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded', 'API-key': key },
    body: params.toString()
  });
  show('euLoginOut', { status: r.status, body: r.body });
}

async function rawRequest() {
  const headers = {};
  const key = $('rawApiKey').value.trim();
  const bearer = $('rawBearer').value.trim();
  const bodyText = $('rawBody').value.trim();

  if (key) headers['API-key'] = key;
  if (bearer) headers['Authorization'] = 'Bearer ' + bearer;

  let body;
  if (bodyText) {
    headers['Content-Type'] = 'application/json';
    body = bodyText;
  }

  const r = await call($('rawPath').value, {
    method: $('rawMethod').value.toUpperCase(),
    headers,
    body
  });
  show('rawOut', { status: r.status, body: r.body });
}
