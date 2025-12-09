# main.py — jogo completo com intro em vídeo (OpenCV) e fundo restaurado
import pygame
import random
import math
import os
import cv2
import numpy as np

pygame.init()

# -----------------------
# CONFIGURAÇÕES BÁSICAS
# -----------------------
LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()

SPRITES_DIR = 'sprites/'

# -----------------------
# FUNÇÃO PARA TOCAR VÍDEO (OpenCV)
# -----------------------
def tocar_video_intro(caminho_video):
    """Reproduz vídeo usando OpenCV e permite pular com qualquer tecla."""
    if not os.path.exists(caminho_video):
        print(f"Intro: arquivo {caminho_video} não encontrado, pulando intro.")
        return

    cap = cv2.VideoCapture(caminho_video)
    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    fps_video = cap.get(cv2.CAP_PROP_FPS) or 30.0
    fps_video = max(15.0, float(fps_video))

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Converte BGR -> RGB e redimensiona
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (LARGURA, ALTURA), interpolation=cv2.INTER_LINEAR)

        # Cria surface diretamente (sem rotacionar)
        surface = pygame.image.frombuffer(frame.tobytes(), (LARGURA, ALTURA), 'RGB')

        TELA.blit(surface, (0, 0))
        pygame.display.flip()

        # Eventos: pular com qualquer tecla ou fechar
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.QUIT:
                cap.release()
                return

        clock.tick(int(fps_video))

    cap.release()

# chama a intro (arquivo deve estar na mesma pasta)
tocar_video_intro("lv_0_20251208094527.mp4")


# -----------------------
# CARREGAMENTO DO FUNDO
# -----------------------
def carregar_fundo(caminho):
    try:
        img = pygame.image.load(caminho).convert()
        return pygame.transform.scale(img, (LARGURA, ALTURA))
    except Exception:
        print(f"Não foi possível carregar fundo {caminho}, usando fallback colorido.")
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill((20, 20, 20))
        return s

# caminho padrão: sprites/fundo.png
fundo = carregar_fundo(os.path.join(SPRITES_DIR, 'fundo.png'))


# -----------------------
# FUNÇÃO DE CARREGAMENTO DE SPRITES
# -----------------------
def carregar_sprite(nome_arquivo, cor_fallback=(0, 0, 0), largura=40, altura=40):
    if 'power_' in nome_arquivo:
        largura, altura = 40, 40
    elif nome_arquivo == 'jogador.png':
        largura, altura = 60, 60
    elif nome_arquivo == 'tiro.png':
        largura, altura = 12, 24
    elif nome_arquivo == 'boss.png':
        largura, altura = 150, 150
    elif nome_arquivo == 'boss_tiro.png':
        largura, altura = 25, 35
    else:
        largura, altura = 50, 50

    caminho_completo = os.path.join(SPRITES_DIR, nome_arquivo)
    try:
        imagem = pygame.image.load(caminho_completo).convert_alpha()
        imagem = pygame.transform.scale(imagem, (largura, altura))
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"ATENÇÃO: Não foi possível carregar a sprite {caminho_completo}. Gerando fallback.")
        surface = pygame.Surface((largura, altura)).convert_alpha()
        surface.fill(cor_fallback)
        return surface


# -----------------------
# SPRITES PRINCIPAIS
# -----------------------
sprites = {
    'jogador': carregar_sprite('jogador.png', cor_fallback=(0, 255, 0)),
    'tiro': carregar_sprite('tiro.png', cor_fallback=(255, 255, 0)),
    'robo_zigue': carregar_sprite('robo_zigue.png', cor_fallback=(255, 0, 0)),
    'robo_cacador': carregar_sprite('robo_cacador.png', cor_fallback=(255, 100, 0)),
    'robo_lento': carregar_sprite('robo_lento.png', cor_fallback=(100, 0, 255)),
    'robo_rapido': carregar_sprite('robo_rapido.png', cor_fallback=(0, 100, 255)),
    'robo_ciclico': carregar_sprite('robo_ciclico.png', cor_fallback=(255, 0, 100)),
    'robo_saltador': carregar_sprite('robo_saltador.png', cor_fallback=(150, 0, 150)),
    'power_vida': carregar_sprite('power_vida.png', cor_fallback=(0, 0, 255)),
    'power_velocidade': carregar_sprite('power_velocidade.png', cor_fallback=(163, 73, 14)),
    'power_tirotriplo': carregar_sprite('power_tirotriplo.png', cor_fallback=(255, 141, 161)),
    'boss': carregar_sprite('boss.png', cor_fallback=(0, 0, 150)),
    'boss_tiro': carregar_sprite('boss_tiro.png', cor_fallback=(0, 0, 255)),
    'explosao': carregar_sprite('tentativa.png', cor_fallback=(255, 255, 255), largura=274, altura=384),
}


# -----------------------
# ANIMAÇÃO DE EXPLOSÃO
# -----------------------
explosao_frames = []
sheet = sprites['explosao']
cols, rows = 1, 1
fw = sheet.get_width() // cols
fh = sheet.get_height() // rows
for i in range(rows):
    for j in range(cols):
        frame = sheet.subsurface((j * fw, i * fh, fw, fh))
        frame = pygame.transform.scale(frame, (80, 80))
        explosao_frames.append(frame)


class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = explosao_frames
        self.frame_index = 0
        self.image = self.frames[self.frame_index]
        self.rect = self.image.get_rect(center=(x, y))
        self.counter = 0

    def update(self):
        self.counter += 1
        if self.counter >= 15:
            self.counter = 0
            self.frame_index += 1
            if self.frame_index >= len(self.frames):
                self.kill()
            else:
                self.image = self.frames[self.frame_index]


# -----------------------
# CLASSES DO JOGO
# -----------------------
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade, image_key):
        super().__init__()
        self.velocidade = velocidade
        self.image = sprites[image_key]
        self.rect = self.image.get_rect(center=(x, y))


class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 'jogador')
        self.vida = 5
        self.transformado = False
        self.tamanho_original = (60, 60)
        self.velocidade_original = 5
        self.cacador_desabilitado = False

    def ativar_transformacao(self):
        self.transformado = True
        novo_tamanho = (int(60 * 1.3), int(60 * 1.3))
        self.image = pygame.transform.scale(sprites['jogador'], novo_tamanho)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.velocidade = 6.5

    def desativar_transformacao(self):
        self.transformado = False
        self.image = pygame.transform.scale(sprites['jogador'], self.tamanho_original)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.velocidade = self.velocidade_original
        self.cacador_desabilitado = True

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.velocidade
        if keys[pygame.K_s]:
            self.rect.y += self.velocidade
        if keys[pygame.K_a]:
            self.rect.x -= self.velocidade
        if keys[pygame.K_d]:
            self.rect.x += self.velocidade

        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.rect.height))


class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10, 'tiro')

    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()


class TiroDiagonal(Tiro):
    def __init__(self, x, y, direcao_x):
        super().__init__(x, y)
        self.direcao_x = direcao_x
        self.velocidade_x = 4

    def update(self):
        self.rect.y -= self.velocidade
        self.rect.x += self.direcao_x * self.velocidade_x
        if self.rect.y < 0 or self.rect.x < 0 or self.rect.x > LARGURA:
            self.kill()


# ----- Robôs -----
class Robo(Entidade):
    def atualizar_posicao(self):
        raise NotImplementedError


class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, image_key='robo_zigue')
        self.direcao = 1
        self.vida = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3
        if self.rect.x <= 0 or self.rect.x >= LARGURA - self.rect.width:
            self.direcao *= -1

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()


class RoboCiclico(RoboZigueZague):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = sprites['robo_ciclico']
        self.vida = 1


class RoboLento(RoboZigueZague):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = sprites['robo_lento']
        self.vida = 1


class RoboRapido(RoboZigueZague):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.image = sprites['robo_rapido']
        self.vida = 1


class RoboCacador(Robo):
    def __init__(self, x, y, velocidade=2, jitter=0.6, usar_jitter=True):
        super().__init__(x, y, velocidade, image_key='robo_cacador')
        self.jitter = jitter
        self.usar_jitter = usar_jitter
        self.easter_egg = False
        self.vida = 1

    def atualizar_posicao(self):
        tx = jogador.rect.centerx
        ty = jogador.rect.centery
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = math.hypot(dx, dy)
        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist
        speed = self.velocidade + (1 if dist < 180 else 0)

        jx = random.uniform(-self.jitter, self.jitter) if self.usar_jitter else 0
        jy = random.uniform(-self.jitter, self.jitter) if self.usar_jitter else 0

        self.rect.x += int(nx * speed + jx)
        self.rect.y += int(ny * speed + jy)

    def update(self):
        self.atualizar_posicao()
        if (self.rect.top > ALTURA + 200 or self.rect.bottom < -200 or
                self.rect.left < -200 or self.rect.right > LARGURA + 200):
            self.kill()


class RoboCircular(Robo):
    def __init__(self, x, y, raio, v_descida, v_angular):
        super().__init__(x, y, velocidade=1, image_key='robo_ciclico')
        self.center_x = x
        self.center_y = y
        self.raio = raio
        self.v_descida = v_descida
        self.v_angular = v_angular
        self.angulo = 0
        self.vida = 1

    def atualizar_posicao(self):
        self.angulo += self.v_angular
        if self.angulo > 360:
            self.angulo -= 360
        angulo_rad = math.radians(self.angulo)
        self.center_y += self.v_descida
        self.rect.x = int(self.center_x + self.raio * math.cos(angulo_rad))
        self.rect.y = int(self.center_y + self.raio * math.sin(angulo_rad))

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()


class RoboPulante(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, image_key='robo_saltador')
        self.cooldown_pulo = random.randint(40, 80)
        self.timer = 0
        self.forca_pulo = random.randint(-80, -40)
        self.vida = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.timer += 1
        if self.timer >= self.cooldown_pulo:
            self.rect.y += self.forca_pulo
            self.timer = 0
            self.cooldown_pulo = random.randint(40, 80)

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()


class Boss(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, image_key='boss')
        self.vida = 100
        self.mov_direcao = 1
        self.atirar_timer = 0

    def atualizar_posicao(self):
        self.rect.x += self.mov_direcao * 3
        if self.rect.left <= 0 or self.rect.right >= LARGURA:
            self.mov_direcao *= -1

    def atirar(self):
        tiro = BossTiro(self.rect.centerx, self.rect.bottom)
        todos_sprites.add(tiro)
        tiros_chefao.add(tiro)

    def update(self):
        global estado_jogo
        if estado_jogo != "BOSS":
            return
        self.atualizar_posicao()
        self.atirar_timer += 1
        if self.atirar_timer >= 40:
            self.atirar()
            self.atirar_timer = 0
        if self.vida <= 0:
            estado_jogo = "WIN"
            self.kill()


class BossTiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 'boss_tiro')

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA:
            self.kill()


# PowerUp — versão correta
class PowerUp(RoboZigueZague):
    def __init__(self, x, y, tipo):
        sprite_map = {
            "vida": 'power_vida',
            "velocidade": 'power_velocidade',
            "tirotriplo": 'power_tirotriplo',
        }
        super().__init__(x, y)
        key = sprite_map[tipo]
        self.image = sprites[key]
        self.rect = self.image.get_rect(center=(x, y))
        self.tipo = tipo
        self.velocidade = 3
        self.direcao = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 2
        if self.rect.x <= 0 or self.rect.x >= LARGURA - self.rect.width:
            self.direcao *= -1

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()


# Classe auxiliar (enemies com vida extra)
class RoboComVida(Robo):
    def __init__(self, x, y, velocidade, image_key, vida=1):
        super().__init__(x, y, velocidade, image_key)
        self.vida = vida


# -----------------------
# GRUPOS E VARIÁVEIS INICIAIS
# -----------------------
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
powerups = pygame.sprite.Group()
tiros_chefao = pygame.sprite.Group()
explosoes = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

chefao = None
pontos = 0
spawn_timer = 0
tempo_velocidade = 0
tempo_tirotriplo = 0
delay_tiro = 0

# Easter egg flags
cacador_transformacao = None
cacador_ja_conhecido = False

estado_jogo = "NORMAL"
aviso_timer = 0

# -----------------------
# LOOP PRINCIPAL
# -----------------------
rodando = True
while rodando:
    clock.tick(FPS)

    # TIRO DO JOGADOR
    keys = pygame.key.get_pressed()
    delay_tiro += 0.2
    if delay_tiro >= 4:
        if keys[pygame.K_SPACE]:
            delay_tiro_ajustado = 2 if jogador.transformado else 4
            if delay_tiro >= delay_tiro_ajustado:
                if tempo_tirotriplo > 0:
                    t1 = Tiro(jogador.rect.centerx, jogador.rect.y)
                    t2 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, -1)
                    t3 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, 1)
                    for t in (t1, t2, t3):
                        todos_sprites.add(t); tiros.add(t)
                elif jogador.transformado:
                    t1 = Tiro(jogador.rect.centerx, jogador.rect.y)
                    t2 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, -1)
                    t3 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, 1)
                    for t in (t1, t2, t3):
                        todos_sprites.add(t); tiros.add(t)
                else:
                    t = Tiro(jogador.rect.centerx, jogador.rect.y)
                    todos_sprites.add(t); tiros.add(t)
                delay_tiro = 0

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        # Reiniciar após WIN
        if estado_jogo == "WIN":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                pontos = 0
                jogador.vida = 5
                jogador.rect.center = (LARGURA // 2, ALTURA - 60)
                if jogador.transformado:
                    jogador.desativar_transformacao()
                cacador_ja_conhecido = False
                jogador.cacador_desabilitado = False
                for grp in (inimigos, tiros, powerups, tiros_chefao, explosoes):
                    for s in grp.copy():
                        s.kill()
                chefao = None
                estado_jogo = "NORMAL"

    # CHEFÃO incoming
    if pontos >= 50 and estado_jogo == "NORMAL":
        estado_jogo = "BOSS_INCOMING"
        aviso_timer = FPS * 2

    if estado_jogo == "BOSS_INCOMING":
        aviso_timer -= 1
        if aviso_timer <= 0:
            estado_jogo = "BOSS"
            chefao = Boss(LARGURA // 2, 120)
            todos_sprites.add(chefao)

    # SPAWN (NORMAL)
    if estado_jogo == "NORMAL":
        spawn_timer += 1
        if spawn_timer > 60:
            rand = random.random()
            x_pos = random.randint(50, LARGURA - 50)

            if rand < 0.15 and not jogador.transformado and not jogador.cacador_desabilitado:
                robo = RoboCacador(x_pos, -50)
            elif rand < 0.30:
                robo = RoboCircular(x_pos, -50, raio=random.randint(20, 60), v_descida=1, v_angular=random.uniform(3, 6))
            elif rand < 0.45:
                robo = RoboPulante(x_pos, -50)
            elif rand < 0.60:
                robo = RoboRapido(x_pos, -50)
            elif rand < 0.75:
                robo = RoboLento(x_pos, -50)
            else:
                robo = RoboZigueZague(x_pos, -50)

            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        # powerups spawn probabilístico (não quando transformado)
        if random.random() < 0.005 and not jogador.transformado:
            tipo = random.choice(["vida", "velocidade", "tirotriplo"])
            r = PowerUp(random.randint(40, LARGURA - 40), -40, tipo)
            todos_sprites.add(r)
            powerups.add(r)

    # coleta powerups
    for p in pygame.sprite.spritecollide(jogador, powerups, True):
        if p.tipo == "vida":
            jogador.vida += 1
        elif p.tipo == "velocidade":
            jogador.velocidade = 10
            tempo_velocidade = FPS * 5
        elif p.tipo == "tirotriplo":
            tempo_tirotriplo = FPS * 5

    # colisões: inimigos x tiros -> explosão + drops
    acertos = pygame.sprite.groupcollide(inimigos, tiros, True, True)
    for inimigo in acertos:
        explos = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
        explosoes.add(explos); todos_sprites.add(explos)
        pontos += 1
        # chance de drop ao morrer (10%)
        if random.random() < 0.10:
            tipo = random.choice(["vida", "velocidade", "tirotriplo"])
            p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
            powerups.add(p); todos_sprites.add(p)

    # hits (quando jogador transformado causa necessidade de mais tiros)
    hits = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    for inimigo, lista_tiros in hits.items():
        dano = len(lista_tiros)
        if jogador.transformado:
            if hasattr(inimigo, 'vida'):
                inimigo.vida -= dano
                if inimigo.vida <= 0:
                    inimigo.kill(); pontos += 1
                    if random.random() < 0.10:
                        tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                        p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                        powerups.add(p); todos_sprites.add(p)
            else:
                if dano >= 2:
                    inimigo.kill(); pontos += 1
                    if random.random() < 0.10:
                        tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                        p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                        powerups.add(p); todos_sprites.add(p)
        else:
            # modo normal: 1 tiro mata
            inimigo.kill(); pontos += len(lista_tiros)
            if random.random() < 0.10:
                tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                powerups.add(p); todos_sprites.add(p)

    # dano no chefao
    if chefao:
        tiros_acertaram = pygame.sprite.spritecollide(chefao, tiros, True)
        chefao.vida -= len(tiros_acertaram)

    # colisão especial: caçador ativa transformação
    colisao_cacador = pygame.sprite.spritecollide(jogador, inimigos, False)
    for inimigo in list(colisao_cacador):
        if isinstance(inimigo, RoboCacador) and not jogador.transformado:
            jogador.ativar_transformacao()
            inimigo.kill()
            cacador_ja_conhecido = True
        elif isinstance(inimigo, RoboCacador) and jogador.transformado:
            inimigo.kill()

    # tiros do chefao atingem jogador
    if pygame.sprite.spritecollide(jogador, tiros_chefao, True):
        jogador.vida -= 1
        if jogador.transformado:
            jogador.desativar_transformacao()
            cacador_ja_conhecido = False
        if jogador.vida <= 0:
            print("GAME OVER")
            rodando = False

    # colisão com inimigos normais (já removemos caçador acima)
    colisao_inimigos = pygame.sprite.spritecollide(jogador, inimigos, True)
    for inimigo in colisao_inimigos:
        if not isinstance(inimigo, RoboCacador):
            jogador.vida -= 1
            if jogador.transformado:
                jogador.desativar_transformacao()
                cacador_ja_conhecido = False
            if jogador.vida <= 0:
                print("GAME OVER")
                rodando = False

    # timers
    if tempo_velocidade > 0:
        tempo_velocidade -= 1
        if tempo_velocidade == 0:
            jogador.velocidade = jogador.velocidade_original

    if tempo_tirotriplo > 0:
        tempo_tirotriplo -= 1

    todos_sprites.update()
    tiros_chefao.update()
    explosoes.update()

    # DESENHO DO FUNDO (com efeito quando transformado)
    if jogador.transformado:
        fundo_mod = fundo.copy()
        overlay = pygame.Surface((LARGURA, ALTURA))
        overlay.fill((0, 40, 40))
        overlay.set_alpha(120)
        fundo_mod.blit(overlay, (0, 0))
        TELA.blit(fundo_mod, (0, 0))
    else:
        TELA.blit(fundo, (0, 0))

    # Desenha sprites e explosões
    todos_sprites.draw(TELA)
    explosoes.draw(TELA)

    # HUD
    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    if jogador.transformado:
        status_text = font.render("TRANSFORMADO!", True, (0, 255, 255))
        TELA.blit(status_text, (LARGURA - 220, 10))

    # HUD do chefe
    if estado_jogo == "BOSS" and chefao:
        vida_pct = max(0, chefao.vida) / 100
        HUD_LARGURA = 300
        HUD_X = (LARGURA - HUD_LARGURA) // 2
        pygame.draw.rect(TELA, (60, 0, 0), (HUD_X, 20, HUD_LARGURA, 12))
        pygame.draw.rect(TELA, (0, 255, 0), (HUD_X, 20, int(HUD_LARGURA * vida_pct), 12))

    if estado_jogo == "BOSS_INCOMING":
        text = font.render("CHEFÃO SE APROXIMANDO!", True, (255, 0, 0))
        TELA.blit(text, (LARGURA // 2 - 150, ALTURA // 2))

    if estado_jogo == "WIN":
        win_text = font.render("VOCÊ VENCEU! PRESSIONE ENTER PARA REINICIAR", True, (255, 255, 0))
        TELA.blit(win_text, (100, ALTURA // 2))

    pygame.display.flip()

pygame.quit()
