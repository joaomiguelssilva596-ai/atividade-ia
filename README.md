# 🚀 Jogo Atari — Nave vs Asteroides

Jogo 2D no estilo Atari desenvolvido com **Python** e **pygame**.

## Como Jogar

| Tecla | Ação |
|-------|------|
| ← → | Mover a nave |
| `Espaço` | Atirar |
| `R` | Reiniciar (na tela de Game Over) |
| `Q` | Sair (na tela de Game Over) |

## Mecânicas

- Asteroides surgem no topo e descem com velocidade crescente
- Cada acerto vale **10 pontos**
- A cada **50 pontos** o nível sobe e o jogo fica mais difícil
- O jogo termina se um asteroide atingir a nave ou chegar ao fundo

## Como Executar

```bash
pip install -r requirements.txt
python jogo.py
```

## Estrutura do Projeto

```
jogo-atari/
├── jogo.py           # Código principal do jogo
├── requirements.txt  # Dependência: pygame
└── README.md         # Este arquivo
```
