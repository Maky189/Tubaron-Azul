# Relatório Técnico — Cabo Verde: Mundial 2026

**Projeto:** Jogo de futebol 2D ao vivo (arcade, vista de cima)
**Tema:** A seleção de Cabo Verde (os "Tubarões Azuis") no Mundial de 2026
**Tecnologia:** Python 3.12 + pygame 2.6
**Arquitetura:** Motor genérico reutilizável + jogo orientado a objetos
**Data:** Junho de 2026

---

## 1. Objetivo

O objetivo foi criar um **jogo de futebol jogável ao vivo** — ao estilo *FIFA* /
*Sensible Soccer* em vista de cima — à volta de um feito histórico: **Cabo Verde**
(os "Tubarões Azuis") no **Mundial de 2026**. O jogador controla a seleção em
tempo real (mover, passar, rematar, desarmar) contra um adversário comandado pelo
**computador**, marca golos, e percorre uma **caminhada de seis fases** de
dificuldade crescente: **Espanha**, Bélgica, Países Baixos, Inglaterra, França e o
**Brasil na final**. Vencer avança de fase; perder ou empatar elimina. Toda a
identidade visual é em **branco e azul** de Cabo Verde e a interface está em
português.

> Nota de evolução: o projeto começou como um *dungeon-crawler* ao estilo Persona,
> passou por um RPG de futebol por salas, e foi depois **completamente
> reformulado** neste jogo de futebol ao vivo. O código antigo de combate por
> turnos e exploração foi removido.

---

## 2. Arquitetura geral

O código está dividido em dois pacotes de topo independentes:

- **`engine/`** — genérico e reutilizável. Não conhece nada sobre futebol. Contém
  o ciclo principal e a janela (`app.py`), a pilha de cenas (`scene/`), a câmara
  (`rendering/camera.py`), os utilitários de desenho (`rendering/draw.py`), o
  input, o áudio, o carregamento de recursos e a matemática vetorial 2D (`Vec2`).
- **`game/`** — o jogo em si: a simulação do jogo de futebol, o modelo de domínio
  (o estado guardável), o conteúdo (equipas, paleta, fontes, música) e as cenas de
  interface.

O `main.py` é a única peça que liga os dois: cria a aplicação do motor, instancia
os serviços do jogo (gravação, recordes) e arranca na cena de título.

A separação **lógica vs interface** pedida está garantida em dois níveis: `engine`
vs `game`, e dentro do jogo, a simulação (`game/match/`, que **nunca desenha**) vs
as cenas e os *renderers* (`game/scenes/`, `game/visual/`).

---

## 3. A simulação do jogo (núcleo)

O coração do projeto é a classe **`Match`** (`game/match/match.py`). É **lógica
pura**: a cada frame, `Update(dt, MatchInput)` aplica o input humano ao jogador
ativo da equipa, corre a IA de todos os outros, integra a física da bola, resolve
colisões e deteta golos. Mantém o resultado, o relógio e uma pequena **máquina de
estados**: `pontapé de saída → em jogo → golo → (recomeço) → … → fim`.

Peças de apoio:

- **`game/match/entities.py`** — `Player` e `Ball`, simples dados mutáveis
  (posição, velocidade, orientação, temporizadores). Nenhum comportamento aqui.
- **`game/match/pitch.py`** — geometria do campo em pixels de mundo. O campo é um
  retângulo; a bola **ressalta nas linhas laterais exceto dentro das balizas**, uma
  regra de arcade que dispensa lançamentos e cantos.
- **`game/match/ai.py`** — decisões dos jogadores que o humano não controla
  (guarda-redes a cobrir o ângulo e a ler o remate, portador da bola, apoio,
  pressão, defesa) e a decisão de ação com bola (rematar / passar / aliviar). O
  atributo `ai_skill` de cada equipa escala a velocidade, o alcance de remate e a
  qualidade do guarda-redes — por isso a caminhada **fica genuinamente mais
  difícil** a cada fase.

A **posse** é resolvida pelo jogador mais perto da bola, com uma vantagem de
"aderência" para quem já a tem e um curto período de bloqueio após cada pontapé; o
desarme é emergente (um defesa que ganha o lado da baliza, ou o **avanço** do
humano na tecla de desarme, fica mais perto e rouba a bola). O **jogador ativo** é
escolhido automaticamente como o jogador de Cabo Verde mais perto da bola.

Na baliza está o **Vozinha**, o muro: um guarda-redes propositadamente
**imbatível**. A cada frame, o `Match._TeleportSuperKeeper` **teletransporta-o**
instantaneamente para o ponto onde qualquer remato cruza a linha de golo e recolhe
qualquer bola dentro da sua área (incluindo um drible perdido de um colega — é assim
que se evitam os autogolos), com um alcance de defesa enorme. O resultado é que Cabo
Verde **não sofre golos** em jogo corrido — toda a pressão recai sobre marcar do
outro lado.

O jogo arranca ainda numa **abertura cinematográfica** curta e saltável
(`game/scenes/cinematic_scene.py`): uma linha temporal de segmentos (estática de TV,
o logótipo dos Tubarões, o capitão, o Vozinha invencível, uma passagem pelo relvado e
o cartão de título) com *scanlines* e *vignette*, ao som do tema do IShowSpeed.

**Controlos:** mover (setas / WASD), sprint (Shift), rematar (Espaço/K), passar
(Z/J), desarmar (X/L), pausa (Esc).

---

## 4. Cumprimento dos requisitos

### 4.1 Programação orientada a objetos

- **Mínimo de 4 classes** — há muitas: `Match`, `Player`, `Ball`, `TeamDef`,
  `GameState`, `RecordBook`/`RecordEntry`, `SaveManager`, e toda a hierarquia de
  cenas, além das classes do motor (`Application`, `AssetManager`, `AudioManager`,
  `InputManager`, `SceneStack`, `Camera`, `Vec2`).
- **Construtores (`__init__`)** — todas as classes os têm.
- **Encapsulamento** — o estado é exposto por métodos com verbo ou `@property`. O
  `Camera`, o `AssetManager` e os serviços guardam estado privado (prefixo `_`); o
  `GameState` só altera o seu progresso por `RecordMatch(...)`.
- **Herança** — todas as cenas herdam de `Scene` → `GameScene`
  (`TitleScene`, `TournamentScene`, `MatchScene`, `ResultsScene`,
  `TournamentEndScene`, `PauseScene`, `RecordsScene`).
- **Polimorfismo** — cada cena redefine `OnEnter`/`HandleEvent`/`Update`/`Render`
  e o motor trata-as de forma uniforme pela interface comum de `Scene`; a IA
  resolve o mesmo passo (`DecideMovement`) com comportamentos distintos por papel.
- **Método especial (`__str__`)** — implementado em `Vec2` e `RecordEntry`.
- **Tratamento de exceções** — exceções próprias (`SaveError`, `AssetError`)
  lançadas e apanhadas onde fazem sentido (gravar/ler um ficheiro corrompido,
  carregar um asset em falta); o carregamento de um jogo guardado inválido recai
  graciosamente num jogo novo.

### 4.2 Requisitos gerais

- **Interface gráfica funcional** — pygame, janela 960×540, com cenas de título,
  caminhada do Mundial, jogo ao vivo, resultado, fim de torneio, pausa e recordes.
- **Listas e dicionários** — a lista de jogadores e a fila de transições de cena;
  o `SpriteFactory` guarda equipas em dicionário; as equipas e a formação são
  estruturas de dados em `game/data/teams.py`.
- **Persistência em ficheiros** — `persistence/save_manager.py` grava o progresso
  da caminhada em JSON (gravação atómica via ficheiro temporário). O próprio
  `GameState` sabe serializar-se (`CaptureSnapshot`/`ApplySnapshot`).
- **Sistema de recordes** — `persistence/records.py` mantém o top-8 de pontuações
  em disco, ordenado, tolerante a ficheiros em falta ou corrompidos. A pontuação é
  `vitórias×200 + golos_marcados×25 − golos_sofridos×10`.
- **Menus gráficos** — widget reutilizável `scenes/menu.py` (painéis inclinados em
  branco/azul) usado no título e na pausa.
- **Múltiplos níveis de jogo** — o Mundial é uma sequência de **seis fases**
  (Espanha → … → Brasil), com dificuldade crescente até à **grande final**. A cena
  `TournamentScene` mostra a estrada, as fases já vencidas e o próximo adversário.

---

## 5. Direção de arte

- **Sprites dos jogadores** — três poses base em pixel-art fornecidas pelo autor
  (jogador parado, jogador a rematar, guarda-redes em voo). O
  `tools/process_players.py` limpa o fundo branco com um *flood-fill* a partir das
  margens (preservando as meias, os atacadores e a bola brancos), recorta e
  redimensiona. **Cada outra seleção é gerada por recoloração** em tempo de
  carregamento (`game/visual/soccer_art.py`): o azul do equipamento é trocado pela
  cor da equipa, preservando o sombreado, e o guarda-redes amarelo pela cor de
  guarda-redes da equipa.
- **O relvado e os símbolos** são gerados por código
  (`tools/generate_assets.py`): relvado com riscas de corte, balizas com rede, a
  bola, e aproximações da **bandeira de Cabo Verde** e do **emblema-tubarão**.
- **Tipografia** — fontes *Anton* e *Barlow Condensed* (Google Fonts, licença
  OFL), com suporte para os acentos do português.
- **Renderização do jogo** — o `MatchScene` desenha o relvado sob a câmara que
  segue a bola, as balizas, as sombras, os jogadores ordenados por profundidade, a
  bola com altura (remates em arco) e sombra, o marcador (resultado, siglas,
  minuto) e os cartões de "GOLO!" / "PONTAPÉ DE SAÍDA" com um *flash* no golo.

---

## 6. Música

Cada cena tem a sua faixa, trocada nas transições (ficheiros `.ogg` em
`assets/audio/`):

| Cena | Faixa |
|---|---|
| Abertura cinematográfica | IShowSpeed — *World Cup (Champions)* |
| Menus e resultados | *We Are One (Ole Ola)* — canção oficial do Mundial 2014 |
| Jogo ao vivo | LA MC — *Malcriado (Ninguém, Ninguém, Ninguém)* |

A troca acontece via `AudioManager.PlayMusic`, que mantém uma faixa a tocar quando
já está em curso (`get_busy()`) e degrada para silêncio em máquinas sem áudio
(incluindo os testes *headless*). As faixas são material de terceiros usado apenas
neste trabalho académico (ver `assets/audio/CREDITS.md`).

---

## 7. Decisões de design relevantes

- **Simulação pura, separada do desenho.** O `Match` não conhece pygame de
  desenho; isto torna-o testável sem janela e mantém a interface isolada nas cenas.
- **Transições deferidas de cena.** A `SceneStack` aplica push/pop/replace só no
  fim do frame, evitando corromper a iteração quando uma cena pede uma transição a
  meio do seu próprio `Update`.
- **Jogador ativo com IA de reserva.** Quando o humano não dá direção, o jogador
  ativo é conduzido pela sua própria IA, para a equipa nunca ficar paralisada.
- **Dificuldade por dados.** A força de cada seleção é um único número (`ai_skill`)
  que escala velocidade, remate e guarda-redes — afinar o equilíbrio é editar
  `game/data/teams.py`.

---

## 8. Como executar e testar

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python main.py                 # jogar
python tests/test_smoke.py     # teste ponta-a-ponta (headless)
python tools/process_players.py    # reconstruir os sprites dos jogadores
python tools/generate_assets.py    # regenerar a arte procedural
```

O `tests/test_smoke.py` valida, sem abrir janela: a simulação de um jogo completo
até ao apito final, que um atacante ativo consegue marcar à seleção mais fácil, um
ciclo de gravar/ler o progresso em disco com um recorde, e a navegação real pela
pilha de cenas (abertura → título → caminhada → jogo → resultado, incluindo a pausa).

---

## 9. Conclusão

O projeto entrega um **jogo de futebol jogável ao vivo** contra o computador, com
marcação de golos, uma caminhada de seis fases com dificuldade crescente,
persistência do progresso, recordes e uma identidade visual coerente em branco e
azul de Cabo Verde. A arquitetura separa claramente motor de jogo e lógica de
interface, e está preparada para crescer: novas seleções e equilíbrio resumem-se a
editar dados em `game/data/`, sem tocar no motor.
