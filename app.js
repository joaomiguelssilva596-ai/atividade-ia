/**
 * TaskFlow — Gerenciador de Tarefas
 * Stack: HTML + Tailwind CDN + JavaScript Vanilla
 * Persistência: localStorage (simula db.json com "users" e "todos")
 */

// ──────────────────────────────────────────
// HELPERS DE PERSISTÊNCIA (localStorage)
// ──────────────────────────────────────────

/** Retorna o array de usuários salvo no localStorage. */
function getUsuarios() {
  return JSON.parse(localStorage.getItem('users') || '[]');
}

/** Salva o array de usuários no localStorage. */
function salvarUsuarios(users) {
  localStorage.setItem('users', JSON.stringify(users));
}

/** Retorna o array de tarefas salvo no localStorage. */
function getTodos() {
  return JSON.parse(localStorage.getItem('todos') || '[]');
}

/** Salva o array de tarefas no localStorage. */
function salvarTodos(todos) {
  localStorage.setItem('todos', JSON.stringify(todos));
}

/** Retorna o usuário atualmente logado (ou null). */
function getUsuarioAtual() {
  return JSON.parse(localStorage.getItem('currentUser') || 'null');
}

/** Define o usuário logado no localStorage. */
function setUsuarioAtual(user) {
  localStorage.setItem('currentUser', JSON.stringify(user));
}

/** Remove o usuário logado do localStorage. */
function removerUsuarioAtual() {
  localStorage.removeItem('currentUser');
}


// ──────────────────────────────────────────
// NAVEGAÇÃO ENTRE TELAS
// ──────────────────────────────────────────

/**
 * Esconde todas as telas e exibe apenas a selecionada.
 * @param {string} idTela - ID do elemento a exibir.
 */
function mostrarTela(idTela) {
  const telas = ['tela-login', 'tela-cadastro', 'tela-painel'];
  telas.forEach(id => {
    const el = document.getElementById(id);
    if (id === idTela) {
      el.classList.remove('hidden');
      el.classList.add('flex');
    } else {
      el.classList.add('hidden');
      el.classList.remove('flex');
    }
  });
}

/**
 * Exibe uma mensagem de erro em um elemento específico.
 * @param {string} idElemento - ID do parágrafo de erro.
 * @param {string} mensagem - Texto a exibir.
 */
function exibirErro(idElemento, mensagem) {
  const el = document.getElementById(idElemento);
  if (el) el.textContent = mensagem;
}

/** Limpa a mensagem de erro de um elemento. */
function limparErro(idElemento) {
  exibirErro(idElemento, '');
}


// ──────────────────────────────────────────
// AUTENTICAÇÃO — LOGIN
// ──────────────────────────────────────────

/** Valida credenciais e efetua login do usuário. */
function fazerLogin() {
  // Captura os valores dos campos
  const email = document.getElementById('login-email').value.trim();
  const senha  = document.getElementById('login-senha').value;

  limparErro('login-erro');

  // Validação: campos obrigatórios
  if (!email || !senha) {
    exibirErro('login-erro', 'Preencha e-mail e senha.');
    return;
  }

  // Busca usuário pelo e-mail
  const usuarios = getUsuarios();
  const usuario  = usuarios.find(u => u.email === email);

  // Verifica se o e-mail existe e a senha confere
  if (!usuario || usuario.senha !== senha) {
    exibirErro('login-erro', 'E-mail ou senha incorretos.');
    return;
  }

  // Login bem-sucedido: salva sessão e vai para o painel
  setUsuarioAtual(usuario);
  abrirPainel();
}


// ──────────────────────────────────────────
// AUTENTICAÇÃO — CADASTRO
// ──────────────────────────────────────────

/** Valida dados e cria novo usuário. */
function fazerCadastro() {
  const nome  = document.getElementById('cad-nome').value.trim();
  const email = document.getElementById('cad-email').value.trim();
  const senha = document.getElementById('cad-senha').value;

  limparErro('cad-erro');

  // Validação: todos os campos obrigatórios
  if (!nome || !email || !senha) {
    exibirErro('cad-erro', 'Preencha todos os campos.');
    return;
  }

  // Validação: senha mínima
  if (senha.length < 6) {
    exibirErro('cad-erro', 'A senha deve ter pelo menos 6 caracteres.');
    return;
  }

  const usuarios = getUsuarios();

  // Verifica se o e-mail já está cadastrado
  if (usuarios.find(u => u.email === email)) {
    exibirErro('cad-erro', 'Este e-mail já está cadastrado.');
    return;
  }

  // Cria e salva o novo usuário
  const novoUsuario = { nome, email, senha };
  usuarios.push(novoUsuario);
  salvarUsuarios(usuarios);

  // Faz login automático após cadastro
  setUsuarioAtual(novoUsuario);
  abrirPainel();
}


// ──────────────────────────────────────────
// LOGOUT
// ──────────────────────────────────────────

/** Remove a sessão e volta para a tela de login. */
function fazerLogout() {
  removerUsuarioAtual();
  // Limpa os campos de login para segurança
  document.getElementById('login-email').value = '';
  document.getElementById('login-senha').value = '';
  mostrarTela('tela-login');
}


// ──────────────────────────────────────────
// PAINEL — ABERTURA E RENDERIZAÇÃO
// ──────────────────────────────────────────

/** Abre o painel do usuário logado. */
function abrirPainel() {
  const usuario = getUsuarioAtual();
  if (!usuario) {
    mostrarTela('tela-login');
    return;
  }

  // Exibe o nome do usuário no header
  document.getElementById('usuario-nome').textContent = usuario.nome;

  // Limpa o formulário de tarefa
  document.getElementById('task-titulo').value    = '';
  document.getElementById('task-tipo').value      = 'trabalho';
  document.getElementById('task-descricao').value = '';
  limparErro('task-erro');

  mostrarTela('tela-painel');
  renderizarTarefas();
}

/**
 * Renderiza a lista de tarefas do usuário logado.
 * Tarefas concluídas aparecem ao final.
 */
function renderizarTarefas() {
  const usuario   = getUsuarioAtual();
  const container = document.getElementById('lista-tarefas');

  if (!usuario) return;

  // Filtra tarefas do usuário atual
  const todos = getTodos().filter(t => t.userId === usuario.email);

  // Ordena: pendentes primeiro, concluídas depois
  const pendentes  = todos.filter(t => !t.done);
  const concluidas = todos.filter(t =>  t.done);
  const ordenadas  = [...pendentes, ...concluidas];

  // Caso vazio
  if (ordenadas.length === 0) {
    container.innerHTML = `
      <div class="text-center text-slate-600 py-12">
        <p class="text-3xl mb-3">📋</p>
        <p class="text-sm">Nenhuma tarefa cadastrada ainda.</p>
      </div>
    `;
    return;
  }

  // Mapa de badges por tipo
  const badgeClasses = {
    trabalho: 'badge-trabalho',
    pessoal:  'badge-pessoal',
    estudos:  'badge-estudos',
  };
  const badgeLabels = {
    trabalho: '💼 Trabalho',
    pessoal:  '🎯 Pessoal',
    estudos:  '📚 Estudos',
  };

  // Gera o HTML de cada card
  container.innerHTML = ordenadas.map(tarefa => `
    <div class="task-card ${tarefa.done ? 'done' : ''}" id="card-${tarefa.id}">
      <div class="flex items-start justify-between gap-3">
        <div class="flex-1 min-w-0">
          <p class="task-title text-white font-medium text-sm leading-snug">${escapeHtml(tarefa.titulo)}</p>
          ${tarefa.descricao
            ? `<p class="text-slate-500 text-xs mt-1 leading-relaxed">${escapeHtml(tarefa.descricao)}</p>`
            : ''}
        </div>
        <span class="badge ${badgeClasses[tarefa.tipo] || ''} shrink-0">
          ${badgeLabels[tarefa.tipo] || tarefa.tipo}
        </span>
      </div>
      <div class="flex items-center justify-between mt-3">
        <span class="text-xs text-slate-600">${tarefa.done ? '✅ Concluída' : '⏳ Pendente'}</span>
        ${!tarefa.done
          ? `<button class="btn-outline text-xs py-1 px-3" onclick="concluirTarefa('${tarefa.id}')">Concluir</button>`
          : ''}
      </div>
    </div>
  `).join('');
}


// ──────────────────────────────────────────
// TAREFAS — CRIAR
// ──────────────────────────────────────────

/** Valida o formulário e adiciona uma nova tarefa ao localStorage. */
function adicionarTarefa() {
  const titulo    = document.getElementById('task-titulo').value.trim();
  const tipo      = document.getElementById('task-tipo').value;
  const descricao = document.getElementById('task-descricao').value.trim();
  const usuario   = getUsuarioAtual();

  limparErro('task-erro');

  // Validação: título obrigatório (evita tarefas sem nome)
  if (!titulo) {
    exibirErro('task-erro', 'O título da tarefa é obrigatório.');
    return;
  }

  if (!usuario) return;

  // Cria o objeto da tarefa
  const novaTarefa = {
    id:         Date.now().toString(),  // identificador único via timestamp
    userId:     usuario.email,          // víncula ao usuário logado
    titulo,
    tipo,
    descricao,
    done:       false,                  // inicia como pendente
  };

  // Salva no localStorage
  const todos = getTodos();
  todos.push(novaTarefa);
  salvarTodos(todos);

  // Limpa o formulário após adicionar
  document.getElementById('task-titulo').value    = '';
  document.getElementById('task-tipo').value      = 'trabalho';
  document.getElementById('task-descricao').value = '';

  // Atualiza a listagem
  renderizarTarefas();
}


// ──────────────────────────────────────────
// TAREFAS — CONCLUIR
// ──────────────────────────────────────────

/**
 * Marca uma tarefa como concluída pelo ID.
 * Aplica texto riscado e opacidade reduzida no card.
 * @param {string} id - ID da tarefa.
 */
function concluirTarefa(id) {
  const todos = getTodos();

  // Encontra e atualiza o status da tarefa
  const tarefa = todos.find(t => t.id === id);
  if (tarefa) {
    tarefa.done = true;
    salvarTodos(todos);
    renderizarTarefas();  // re-renderiza para mover ao final da lista
  }
}


// ──────────────────────────────────────────
// UTILITÁRIO — ESCAPE DE HTML
// ──────────────────────────────────────────

/**
 * Escapa caracteres especiais para prevenir XSS.
 * @param {string} texto - Texto bruto.
 * @returns {string} Texto seguro para inserção no DOM.
 */
function escapeHtml(texto) {
  if (!texto) return '';
  return texto
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}


// ──────────────────────────────────────────
// INICIALIZAÇÃO — VERIFICA SESSÃO ATIVA
// ──────────────────────────────────────────

/**
 * Ao carregar a página, verifica se há um usuário logado no localStorage.
 * Se sim, abre o painel diretamente; caso contrário, exibe o login.
 * Corrige o problema de desconexão ao recarregar a página.
 */
(function init() {
  const usuarioAtual = getUsuarioAtual();
  if (usuarioAtual) {
    abrirPainel();
  } else {
    mostrarTela('tela-login');
  }
})();
