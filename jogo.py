"""
Jogo no Estilo Atari — Nave vs Asteroides
Desenvolvido com Python e pygame
"""

import pygame
import random
import sys

# ──────────────────────────────────────────
# INICIALIZAÇÃO DO PYGAME
# ──────────────────────────────────────────
pygame.init()

# Configurações da janela
LARGURA = 800
ALTURA = 600
tela = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Jogo Atari — Nave vs Asteroides")

# ──────────────────────────────────────────
# CORES
# ──────────────────────────────────────────
PRETO      = (0,   0,   0)
BRANCO     = (255, 255, 255)
AMARELO    = (255, 255, 0)
VERMELHO   = (220, 50,  50)
LARANJA    = (255, 140, 0)
CINZA      = (160, 160, 160)
AZUL_CLARO = (100, 200, 255)
VERDE      = (50,  220, 100)

# ──────────────────────────────────────────
# FONTE
# ──────────────────────────────────────────
fonte_hud    = pygame.font.SysFont("monospace", 24, bold=True)
fonte_titulo = pygame.font.SysFont("monospace", 52, bold=True)
fonte_media  = pygame.font.SysFont("monospace", 32, bold=True)
fonte_small  = pygame.font.SysFont("monospace", 20)

# ──────────────────────────────────────────
# RELÓGIO (controla FPS)
# ──────────────────────────────────────────
relogio = pygame.time.Clock()
FPS = 60


# ══════════════════════════════════════════
# CLASSE — NAVE DO JOGADOR
# ══════════════════════════════════════════
class Nave:
    def __init__(self):
        # Posição inicial: centro-baixo da tela
        self.largura = 48
        self.altura  = 36
        self.x = LARGURA // 2 - self.largura // 2
        self.y = ALTURA - self.altura - 20
        self.velocidade = 6
        # Tempo de recarga do tiro (em frames)
        self.recarga    = 0
        self.recarga_max = 15

    def mover(self, teclas):
        """Move a nave com as setas esquerda/direita, mantendo dentro da tela."""
        if teclas[pygame.K_LEFT] and self.x > 0:
            self.x -= self.velocidade
        if teclas[pygame.K_RIGHT] and self.x < LARGURA - self.largura:
            self.x += self.velocidade

    def atirar(self, teclas, projéteis):
        """Cria um projétil se espaço for pressionado e recarga estiver pronta."""
        self.recarga -= 1
        if teclas[pygame.K_SPACE] and self.recarga <= 0:
            cx = self.x + self.largura // 2
            projéteis.append(Projetil(cx, self.y))
            self.recarga = self.recarga_max

    def desenhar(self, superficie):
        """Desenha a nave como um triângulo/foguete estilizado."""
        # Corpo principal
        pontos = [
            (self.x + self.largura // 2, self.y),            # topo
            (self.x,                     self.y + self.altura), # base esquerda
            (self.x + self.largura,      self.y + self.altura), # base direita
        ]
        pygame.draw.polygon(superficie, AZUL_CLARO, pontos)
        # Cabine central
        pygame.draw.circle(
            superficie, BRANCO,
            (self.x + self.largura // 2, self.y + self.altura // 2), 6
        )
        # Chama do motor
        chama = [
            (self.x + 12,                self.y + self.altura),
            (self.x + self.largura - 12, self.y + self.altura),
            (self.x + self.largura // 2, self.y + self.altura + 14),
        ]
        pygame.draw.polygon(superficie, LARANJA, chama)

    @property
    def rect(self):
        """Retorna o retângulo de colisão da nave."""
        return pygame.Rect(self.x + 6, self.y + 6, self.largura - 12, self.altura - 6)


# ══════════════════════════════════════════
# CLASSE — PROJÉTIL
# ══════════════════════════════════════════
class Projetil:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocidade = 10
        self.raio = 4

    def atualizar(self):
        """Move o projétil para cima."""
        self.y -= self.velocidade

    def fora_da_tela(self):
        """Retorna True se o projétil saiu pelo topo."""
        return self.y < -self.raio

    def desenhar(self, superficie):
        """Desenha o projétil como uma elipse luminosa."""
        pygame.draw.ellipse(
            superficie, AMARELO,
            (self.x - self.raio, self.y - self.raio * 2,
             self.raio * 2, self.raio * 4)
        )

    @property
    def rect(self):
        return pygame.Rect(self.x - self.raio, self.y - self.raio, self.raio * 2, self.raio * 2)


# ══════════════════════════════════════════
# CLASSE — ASTEROIDE
# ══════════════════════════════════════════
class Asteroide:
    def __init__(self, velocidade_base):
        # Tamanho aleatório entre 22 e 44 px
        self.raio = random.randint(22, 44)
        self.x    = random.randint(self.raio, LARGURA - self.raio)
        self.y    = -self.raio
        # Velocidade levemente variável em torno da base
        self.velocidade = velocidade_base + random.uniform(-0.5, 0.5)
        # Forma irregular: pontos ao redor do círculo com variação
        self.pontos = self._gerar_pontos()

    def _gerar_pontos(self):
        """Gera um polígono irregular para simular a aparência de um asteroide."""
        import math
        pts = []
        num = 10
        for i in range(num):
            angulo = (2 * math.pi / num) * i
            r = self.raio * random.uniform(0.7, 1.0)
            pts.append((
                self.x + r * math.cos(angulo),
                self.y + r * math.sin(angulo),
            ))
        return pts

    def atualizar(self):
        """Move o asteroide para baixo e atualiza os pontos do polígono."""
        self.y += self.velocidade
        self.pontos = self._gerar_pontos_atual()

    def _gerar_pontos_atual(self):
        """Versão atualizada dos pontos na posição atual (sem re-randomizar forma)."""
        import math
        pts = []
        num = len(self.pontos)
        raios_rel = []  # guarda proporções originais
        for _ in range(num):
            raios_rel.append(random.uniform(0.7, 1.0))
        for i in range(num):
            angulo = (2 * math.pi / num) * i
            r = self.raio * raios_rel[i]
            pts.append((
                self.x + r * math.cos(angulo),
                self.y + r * math.sin(angulo),
            ))
        return pts

    def chegou_ao_fundo(self):
        """Retorna True se o asteroide saiu pela parte de baixo da tela."""
        return self.y - self.raio > ALTURA

    def desenhar(self, superficie):
        """Desenha o asteroide como um polígono acinzentado."""
        if len(self.pontos) >= 3:
            pygame.draw.polygon(superficie, CINZA, self.pontos)
            pygame.draw.polygon(superficie, BRANCO, self.pontos, 1)

    @property
    def rect(self):
        return pygame.Rect(
            self.x - self.raio * 0.8,
            self.y - self.raio * 0.8,
            self.raio * 1.6,
            self.raio * 1.6,
        )


# ══════════════════════════════════════════
# CLASSE — PARTÍCULA DE EXPLOSÃO
# ══════════════════════════════════════════
class Particula:
    def __init__(self, x, y):
        self.x  = x
        self.y  = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-4, 0)
        self.vida     = random.randint(15, 30)
        self.vida_max = self.vida
        self.cor = random.choice([LARANJA, AMARELO, VERMELHO, BRANCO])
        self.raio = random.randint(2, 5)

    def atualizar(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2   # gravidade suave
        self.vida -= 1

    def vivo(self):
        return self.vida > 0

    def desenhar(self, superficie):
        alpha = max(0, int(255 * self.vida / self.vida_max))
        cor = (*self.cor[:3], alpha)
        pygame.draw.circle(superficie, self.cor[:3], (int(self.x), int(self.y)), self.raio)


# ══════════════════════════════════════════
# FUNÇÃO — DESENHAR HUD (pontuação, nível)
# ══════════════════════════════════════════
def desenhar_hud(superficie, pontuacao, nivel):
    # Pontuação
    txt = fonte_hud.render(f"PONTOS: {pontuacao}", True, BRANCO)
    superficie.blit(txt, (14, 10))
    # Nível
    txt2 = fonte_hud.render(f"NÍVEL: {nivel}", True, AMARELO)
    superficie.blit(txt2, (14, 38))


# ══════════════════════════════════════════
# FUNÇÃO — TELA DE GAME OVER
# ══════════════════════════════════════════
def tela_game_over(superficie, pontuacao):
    """Exibe a tela de game over com pontuação final e opções de reinício ou saída."""
    superficie.fill(PRETO)

    # Título
    titulo = fonte_titulo.render("GAME OVER", True, VERMELHO)
    superficie.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, 160))

    # Pontuação final
    pts = fonte_media.render(f"Pontuação Final: {pontuacao}", True, AMARELO)
    superficie.blit(pts, (LARGURA // 2 - pts.get_width() // 2, 260))

    # Instruções
    reiniciar = fonte_small.render("Pressione  R  para reiniciar", True, VERDE)
    sair      = fonte_small.render("Pressione  Q  para sair", True, CINZA)
    superficie.blit(reiniciar, (LARGURA // 2 - reiniciar.get_width() // 2, 340))
    superficie.blit(sair,      (LARGURA // 2 - sair.get_width() // 2, 376))

    pygame.display.flip()

    # Aguarda decisão do jogador
    while True:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_r:
                    return True   # reiniciar
                if evento.key == pygame.K_q:
                    pygame.quit()
                    sys.exit()


# ══════════════════════════════════════════
# FUNÇÃO — LOOP PRINCIPAL DO JOGO
# ══════════════════════════════════════════
def jogar():
    """Executa uma sessão completa do jogo e retorna quando o jogador morre."""

    # Instâncias e listas de objetos
    nave       = Nave()
    projeteis  = []
    asteroides = []
    particulas = []

    # Controle de pontuação e dificuldade
    pontuacao       = 0
    nivel           = 1
    velocidade_base = 2.0   # velocidade inicial dos asteroides

    # Temporizador de spawn de asteroides (em frames)
    intervalo_spawn = 80
    contador_spawn  = 0

    # ── Geração de estrelas de fundo ──
    estrelas = [
        (random.randint(0, LARGURA), random.randint(0, ALTURA), random.randint(1, 3))
        for _ in range(120)
    ]

    rodando = True

    while rodando:
        relogio.tick(FPS)

        # ── Eventos ──
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # ── Teclas pressionadas ──
        teclas = pygame.key.get_pressed()
        nave.mover(teclas)
        nave.atirar(teclas, projeteis)

        # ── Atualizar projéteis ──
        for p in projeteis:
            p.atualizar()
        projeteis = [p for p in projeteis if not p.fora_da_tela()]

        # ── Spawn de asteroides ──
        contador_spawn += 1
        if contador_spawn >= intervalo_spawn:
            asteroides.append(Asteroide(velocidade_base))
            contador_spawn = 0

        # ── Atualizar asteroides ──
        for a in asteroides:
            a.atualizar()

        # ── Verificar colisão: projétil × asteroide ──
        projeteis_vivos   = []
        asteroides_vivos  = []
        acertados         = set()

        for a_idx, a in enumerate(asteroides):
            atingido = False
            for p_idx, p in enumerate(projeteis):
                if p_idx not in []:  # reservado para futura lógica
                    pass
                if a.rect.colliderect(p.rect) and a_idx not in acertados:
                    acertados.add(a_idx)
                    atingido = True
                    pontuacao += 10
                    # Gerar explosão de partículas
                    for _ in range(18):
                        particulas.append(Particula(a.x, a.y))
                    break
            if not atingido:
                asteroides_vivos.append(a)

        # Remove projéteis que acertaram algum asteroide
        projeteis_limpos = []
        for p in projeteis:
            colidiu = False
            for a_idx, a in enumerate(asteroides):
                if a_idx in acertados and a.rect.colliderect(p.rect):
                    colidiu = True
                    break
            if not colidiu:
                projeteis_limpos.append(p)

        projeteis  = projeteis_limpos
        asteroides = asteroides_vivos

        # ── Verificar asteroides que chegaram ao fundo ──
        for a in asteroides:
            if a.chegou_ao_fundo():
                rodando = False
                break

        # ── Verificar colisão: nave × asteroide ──
        for a in asteroides:
            if nave.rect.colliderect(a.rect):
                rodando = False
                break

        # ── Atualizar nível e dificuldade ──
        novo_nivel = pontuacao // 50 + 1
        if novo_nivel != nivel:
            nivel           = novo_nivel
            velocidade_base = 2.0 + (nivel - 1) * 0.6
            intervalo_spawn = max(30, 80 - (nivel - 1) * 8)

        # ── Atualizar partículas ──
        for part in particulas:
            part.atualizar()
        particulas = [part for part in particulas if part.vivo()]

        # ══ DESENHO ══════════════════════════════
        tela.fill(PRETO)

        # Estrelas de fundo
        for (ex, ey, er) in estrelas:
            pygame.draw.circle(tela, BRANCO, (ex, ey), er)

        # Objetos do jogo
        nave.desenhar(tela)
        for p in projeteis:
            p.desenhar(tela)
        for a in asteroides:
            a.desenhar(tela)
        for part in particulas:
            part.desenhar(tela)

        # HUD
        desenhar_hud(tela, pontuacao, nivel)

        pygame.display.flip()

    return pontuacao   # retorna pontuação final para a tela de game over


# ══════════════════════════════════════════
# PONTO DE ENTRADA
# ══════════════════════════════════════════
if __name__ == "__main__":
    while True:
        pontuacao_final = jogar()
        reiniciar = tela_game_over(tela, pontuacao_final)
        if not reiniciar:
            break
