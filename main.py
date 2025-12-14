import pygame
import random
import math
import os
import sys

try:
    import cv2
    OPENCV_OK = True
except Exception:
    OPENCV_OK = False

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Power Rangers: Robot Defense")

FPS = 60
clock = pygame.time.Clock()

SPRITES_DIR = 'sprites'
AUDIOS_DIR = 'audios'

if not os.path.exists(SPRITES_DIR):
    os.makedirs(SPRITES_DIR)
if not os.path.exists(AUDIOS_DIR):
    os.makedirs(AUDIOS_DIR)
    print(f"ATENÇÃO: Criada pasta '{AUDIOS_DIR}'. Coloque seus arquivos de áudio lá.")

pygame.mixer.init()
audios = {}
music_status = True

def carregar_audio(nome_arquivo, tipo="sfx"):
    caminho_completo = os.path.join(AUDIOS_DIR, nome_arquivo)
    try:
        if tipo == "sfx":
            audio = pygame.mixer.Sound(caminho_completo)
        else:
            audio = caminho_completo
        return audio
    except pygame.error as e:
        print(f"AVISO: Não foi possível carregar o áudio '{nome_arquivo}'. Erro: {e}")
        return None

def carregar_todos_audios():
    global audios

    audios['chegada_chefao'] = carregar_audio('chegada_chefao.wav', 'sfx')
    audios['clique_botao'] = carregar_audio('clique_botao.wav', 'sfx')
    audios['game_over'] = carregar_audio('game_over.wav', 'sfx')
    audios['morte_chefao'] = carregar_audio('morte_chefao.wav', 'sfx')
    audios['perca_easter_egg'] = carregar_audio('perca_easter_egg.wav', 'sfx')
    audios['power_up'] = carregar_audio('power_up.wav', 'sfx')
    audios['tiro'] = carregar_audio('tiro.wav', 'sfx')
    audios['transformacao_easter_egg'] = carregar_audio('transformacao_easter_egg.wav', 'sfx')
    
    audios['trilha_jogo'] = carregar_audio('trilha_sonora_1.mp3', 'musica') # Trilha normal
    audios['trilha_boss'] = carregar_audio('trilha_sonora_3.mp3', 'musica') # Trilha do chefão

def play_sfx(key):
    global music_status
    if music_status and audios.get(key) and isinstance(audios[key], pygame.mixer.Sound):
        audios[key].play()

def play_music(key, loops=-1):
    global music_status
    caminho = audios.get(key)
    if music_status and caminho and isinstance(caminho, str) and os.path.exists(caminho):
        try:
            pygame.mixer.music.load(caminho)
            pygame.mixer.music.play(loops)
        except pygame.error as e:
            print(f"Erro ao tocar música {key}: {e}")
        
def stop_music():
    pygame.mixer.music.stop()

carregar_todos_audios()

def tocar_video_intro(caminho_video):
    if not OPENCV_OK:
        print("OpenCV não está disponível — pulando intro.")
        return

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

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (LARGURA, ALTURA), interpolation=cv2.INTER_LINEAR)

        surface = pygame.image.frombuffer(frame.tobytes(), (LARGURA, ALTURA), 'RGB')

        TELA.blit(surface, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                cap.release()
                return
            if event.type == pygame.QUIT:
                cap.release()
                pygame.quit()
                sys.exit()

        clock.tick(int(fps_video))

    cap.release()

def carregar_fundo(caminho):
    try:
        img = pygame.image.load(caminho).convert()
        return pygame.transform.scale(img, (LARGURA, ALTURA))
    except Exception:
        print(f"Não foi possível carregar fundo {caminho}, usando fallback colorido.")
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill((20, 20, 20))
        return s

fundo = carregar_fundo(os.path.join(SPRITES_DIR, 'fundo.png'))

def carregar_sprite(nome_arquivo, cor_fallback=(0, 0, 0), largura=40, altura=40):
    largura_target, altura_target = largura, altura
    
    if 'power_' in nome_arquivo:
        largura_target, altura_target = 40, 40
    elif nome_arquivo == 'jogador.png':
        largura_target, altura_target = 60, 60
    elif nome_arquivo == 'tiro.png':
        largura_target, altura_target = 12, 24
    elif nome_arquivo == 'boss.png':
        largura_target, altura_target = 150, 150
    elif nome_arquivo == 'boss_tiro.png':
        largura_target, altura_target = 25, 35
    elif nome_arquivo == 'Botaopause.jpg':
        largura_target, altura_target = 60, 60
    
    if nome_arquivo == 'Pause.jpg':
        try:
            imagem = pygame.image.load(os.path.join(SPRITES_DIR, nome_arquivo)).convert_alpha()
            
            MAX_W = 400
            w_original, h_original = imagem.get_size()
            
            if w_original > MAX_W:
                ratio = MAX_W / w_original
                nova_w = MAX_W
                nova_h = int(h_original * ratio)
                imagem = pygame.transform.scale(imagem, (nova_w, nova_h))
            
            return imagem
        except Exception:
            print(f"ATENÇÃO: Não foi possível carregar a sprite {nome_arquivo}. Gerando fallback.")
            surface = pygame.Surface((400, 150), pygame.SRCALPHA)
            surface.fill((0, 0, 150))
            return surface

    caminho_completo = os.path.join(SPRITES_DIR, nome_arquivo)
    try:
        imagem = pygame.image.load(caminho_completo).convert_alpha()
        imagem = pygame.transform.scale(imagem, (largura_target, altura_target))
        return imagem
    except Exception:
        print(f"ATENÇÃO: Não foi possível carregar a sprite {caminho_completo}. Gerando fallback.")
        surface = pygame.Surface((largura_target, altura_target), pygame.SRCALPHA)
        if nome_arquivo == 'Botaopause.jpg':
             pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
             pygame.draw.line(surface, (0, 0, 0), (largura//3, altura//4), (largura//3, altura*3//4), 5)
             pygame.draw.line(surface, (0, 0, 0), (largura*2//3, altura//4), (largura*2//3, altura*3//4), 5)
        else:
             surface.fill(cor_fallback)
        return surface
    
tela_inicial_path = os.path.join(SPRITES_DIR, 'tela_inicial.png')
try:
    if os.path.exists(tela_inicial_path):
        tela_inicial_img = pygame.image.load(tela_inicial_path).convert_alpha()
        tela_inicial_img = pygame.transform.scale(tela_inicial_img, (LARGURA, ALTURA))
    else:
        raise FileNotFoundError
except Exception:
    def gerar_tela_inicial_fallback():
        s = pygame.Surface((LARGURA, ALTURA))
        s.fill((20, 160, 100))
        font_t = pygame.font.SysFont(None, 80)
        font_s = pygame.font.SysFont(None, 36)
        titulo = font_t.render("POWER RANGERS", True, (255, 215, 0))
        subt = font_t.render("ROBOT DEFENSE", True, (255, 255, 255))
        instru = font_s.render("Clique em PLAY ou pressione ENTER", True, (230, 230, 230))
        s.blit(titulo, (LARGURA//2 - titulo.get_width()//2, 120))
        s.blit(subt, (LARGURA//2 - subt.get_width()//2, 200))
        s.blit(instru, (LARGURA//2 - instru.get_width()//2, 360))
        return s
    tela_inicial_img = gerar_tela_inicial_fallback()
    print("sprites/tela_inicial.png não encontrado — será usado fallback gerado.")

botao_largura = 80
botao_espacamento = 30
total_largura = 2 * botao_largura + botao_espacamento
x_inicial = LARGURA//2 - total_largura//2

botao_play = pygame.Rect(x_inicial, 420, botao_largura, botao_largura)
botao_profile = pygame.Rect(x_inicial + botao_largura + botao_espacamento, 420, botao_largura, botao_largura)

def desenhar_hover(surface, rect):
    overlay = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    overlay.fill((255,255,255,30))
    surface.blit(overlay, (rect.x, rect.y))

def tela_inicial():
    global estado_jogo
    stop_music()
    while True:
        mouse_pos = pygame.mouse.get_pos()
        TELA.blit(tela_inicial_img, (0,0))

        if botao_play.collidepoint(mouse_pos):
            desenhar_hover(TELA, botao_play)
        if botao_profile.collidepoint(mouse_pos):
            desenhar_hover(TELA, botao_profile)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    play_sfx('clique_botao')
                    estado_jogo = "COUNTDOWN"
                    return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                if botao_play.collidepoint(x, y):
                    play_sfx('clique_botao')
                    estado_jogo = "COUNTDOWN"
                    return
                if botao_profile.collidepoint(x, y):
                    play_sfx('clique_botao')
                    abrir_perfil()

        clock.tick(FPS)

def abrir_perfil():
    try:
        img = pygame.image.load(os.path.join(SPRITES_DIR, "Agradecimentos (1).png")).convert()
        img = pygame.transform.scale(img, (LARGURA, ALTURA))
    except Exception:
        img = TELA.copy()
        img.fill((50, 50, 50))
        font = pygame.font.SysFont(None, 60)
        text = font.render("Perfil/Agradecimentos (Placeholder)", True, (255, 255, 255))
        img.blit(text, (LARGURA//2 - text.get_width()//2, ALTURA//2 - text.get_height()//2))

    rect_voltar = pygame.Rect(40, ALTURA - 120, 80, 80)

    rodando = True
    while rodando:
        TELA.blit(img, (0, 0))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if rect_voltar.collidepoint(event.pos):
                    return
        clock.tick(FPS)

def reset_game_state():
    global todos_sprites, inimigos, tiros, powerups, tiros_chefao, explosoes, chefao, pontos, cacador_ja_conhecido, jogador, spawn_timer, delay_tiro, tempo_velocidade, tempo_tirotriplo
    
    todos_sprites.empty(); inimigos.empty(); tiros.empty(); powerups.empty(); tiros_chefao.empty(); explosoes.empty();
    
    jogador = Jogador(LARGURA // 2, ALTURA - 60)
    todos_sprites.add(jogador)
    
    pontos = 0
    chefao = None
    cacador_ja_conhecido = False
    spawn_timer = 0
    delay_tiro = 0
    tempo_velocidade = 0
    tempo_tirotriplo = 0


def contagem_regressiva():
    global estado_jogo
    
    reset_game_state()
    
    fonte = pygame.font.SysFont(None, 200, bold=True)
    contagem_inicial = 5
    tempo_inicio = pygame.time.get_ticks()
    ultimo_numero_tocado = contagem_inicial + 1

    while True:
        tempo_decorrido = pygame.time.get_ticks() - tempo_inicio
        tempo_restante_seg = contagem_inicial - (tempo_decorrido // 1000)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        if tempo_restante_seg < 1:
            play_music('trilha_jogo')
            estado_jogo = "NORMAL"
            return

        TELA.blit(fundo, (0, 0))
        
        if tempo_restante_seg < ultimo_numero_tocado:
             play_sfx('contagem')
             ultimo_numero_tocado = tempo_restante_seg
        
        texto = fonte.render(str(tempo_restante_seg), True, (255, 255, 255))
        sombra = fonte.render(str(tempo_restante_seg), True, (0, 0, 0))
        
        TELA.blit(sombra, (LARGURA // 2 - sombra.get_width() // 2 + 3, ALTURA // 2 - sombra.get_height() // 2 + 3))
        TELA.blit(texto, (LARGURA // 2 - texto.get_width() // 2, ALTURA // 2 - texto.get_height() // 2))

        pygame.display.flip()
        clock.tick(FPS)


def tela_game_over(pontos_finais):
    global estado_jogo
    
    stop_music()
    play_sfx('game_over')
    
    TELA.blit(fundo, (0, 0))
    overlay = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    TELA.blit(overlay, (0, 0))

    font_titulo = pygame.font.SysFont(None, 120, bold=True)
    font_sub = pygame.font.SysFont(None, 40)
    
    titulo = font_titulo.render("GAME OVER", True, (255, 0, 0))
    score_text = font_sub.render(f"Pontuação Final: {pontos_finais}", True, (255, 255, 255))
    instrucao = font_sub.render("Pressione ENTER para Recomeçar ou ESC para Menu", True, (150, 150, 150))
    
    TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, ALTURA // 3))
    TELA.blit(score_text, (LARGURA // 2 - score_text.get_width() // 2, ALTURA // 2))
    TELA.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, ALTURA * 2 // 3))
    
    pygame.display.flip()

    while estado_jogo == "GAME_OVER":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    estado_jogo = "COUNTDOWN"
                    return
                if event.key == pygame.K_ESCAPE:
                    reset_game_state()
                    estado_jogo = "MENU"
                    return
        clock.tick(FPS)

sprites = {
    'jogador': carregar_sprite('jogador.png', cor_fallback=(0, 255, 0), largura=60, altura=60),
    'tiro': carregar_sprite('tiro.png', cor_fallback=(255, 255, 0), largura=12, altura=24),
    'robo_zigue': carregar_sprite('robo_zigue.png', cor_fallback=(255, 0, 0), largura=50, altura=50),
    'robo_cacador': carregar_sprite('robo_cacador.png', cor_fallback=(255, 100, 0), largura=50, altura=50),
    'robo_lento': carregar_sprite('robo_lento.png', cor_fallback=(100, 0, 255), largura=50, altura=50),
    'robo_rapido': carregar_sprite('robo_rapido.png', cor_fallback=(0, 100, 255), largura=50, altura=50),
    'robo_ciclico': carregar_sprite('robo_ciclico.png', cor_fallback=(255, 0, 100), largura=50, altura=50),
    'robo_saltador': carregar_sprite('robo_saltador.png', cor_fallback=(150, 0, 150), largura=50, altura=50),
    'power_vida': carregar_sprite('power_vida.png', cor_fallback=(0, 0, 255), largura=40, altura=40),
    'power_velocidade': carregar_sprite('power_velocidade.png', cor_fallback=(163, 73, 14), largura=40, altura=40),
    'power_tirotriplo': carregar_sprite('power_tirotriplo.png', cor_fallback=(255, 141, 161), largura=40, altura=40),
    'boss': carregar_sprite('boss.png', cor_fallback=(0, 0, 150), largura=150, altura=150),
    'boss_tiro': carregar_sprite('boss_tiro.png', cor_fallback=(0, 0, 255), largura=25, altura=35),
    'explosao': carregar_sprite('tentativa.png', cor_fallback=(255, 255, 255), largura=274, altura=384),
    'pause_button_sprite': carregar_sprite('Botaopause.jpg', cor_fallback=(0, 0, 0), largura=60, altura=60),
    'menu_pause_fundo': carregar_sprite('Pause.jpg', cor_fallback=(0, 0, 100))  
}

class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade, image_key):
        super().__init__()
        self.velocidade = velocidade
        self.image = sprites[image_key]
        self.rect = self.image.get_rect(center=(x, y))

class Jogador(Entidade):
    def __init__(self, x, y):
        self.velocidade_original = 5
        super().__init__(x, y, self.velocidade_original, 'jogador')

        self.vida = 5
        self.transformado = False
        self.cacador_desabilitado = False
        self.delay_transformacao = 0

    def ativar_transformacao(self):
        if not self.transformado:
            self.transformado = True

    def desativar_transformacao(self):
        if self.transformado:
            self.transformado = False

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
        super().__init__(x, y, velocidade=8, image_key='tiro')
    def update(self):
        self.rect.y -= self.velocidade
        if self.rect.y < 0:
            self.kill()

class TiroDiagonal(Entidade):
    def __init__(self, x, y, direcao):
        super().__init__(x, y, velocidade=8, image_key='tiro')
        self.direcao = direcao
    def update(self):
        self.rect.y -= self.velocidade
        self.rect.x += self.velocidade * 0.5 * self.direcao
        if self.rect.y < 0 or self.rect.x < 0 or self.rect.x > LARGURA:
            self.kill()

class RoboZigueZague(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3, image_key='robo_zigue')
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA: self.kill()

class RoboCacador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, image_key='robo_cacador')
    def update(self):
        # Robo caçador persegue o jogador; não deve ler teclas do jogador
        if 'jogador' in globals() and jogador is not None:
            dx = jogador.rect.centerx - self.rect.centerx
            dy = jogador.rect.centery - self.rect.centery
            distancia = math.hypot(dx, dy)
            if distancia != 0:
                nx = dx / distancia
                ny = dy / distancia
                self.rect.x += int(nx * self.velocidade)
                self.rect.y += int(ny * self.velocidade)
        else:
            # fallback: desce lentamente
            self.rect.y += self.velocidade

        # manter dentro da tela
        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width))
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.rect.height))
        if self.rect.top > ALTURA:
            self.kill()

class RoboLento(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1, image_key='robo_lento')
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA: self.kill()

class RoboRapido(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=5, image_key='robo_rapido')
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA: self.kill()

class RoboCircular(Entidade):
    def __init__(self, x, y, raio, v_descida, v_angular):
        super().__init__(x, y, velocidade=v_descida, image_key='robo_ciclico')
        # centro guarda o ponto central do movimento circular (desce ao longo do tempo)
        self.centro_x = float(self.rect.centerx)
        self.centro_y = float(self.rect.centery)
        self.angulo = random.uniform(0, 360)
        self.raio = raio
        self.v_angular = v_angular

    def update(self):
        # avança o centro verticalmente (descida)
        self.centro_y += self.velocidade

        # avança o ângulo e calcula posição circular em torno do centro
        self.angulo += self.v_angular
        rad = math.radians(self.angulo)
        self.rect.centerx = int(self.centro_x + self.raio * math.cos(rad))
        self.rect.centery = int(self.centro_y + self.raio * math.sin(rad))

        # se o centro mais o raio passou da tela, remove
        if self.rect.top > ALTURA or (self.centro_y - self.raio) > ALTURA:
            self.kill()

class RoboPulante(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2, image_key='robo_saltador')
        # centro do movimento (desce ao longo do tempo)
        self.centro_x = float(self.rect.centerx)
        self.centro_y = float(self.rect.centery)
        # parâmetros do salto (comportamento tipo canguru)
        self.jump_offset = 0.0
        self.jump_v = 0.0
        self.gravity = 0.8
        self.jump_strength_range = (8.0, 12.0)
        self.next_jump_timer = random.randint(20, 60)
        self.next_jump_timer = self.next_jump_timer

    def update(self):
        # desce continuamente
        self.centro_y += self.velocidade

        # timer para iniciar o próximo salto
        self.next_jump_timer -= 1
        if self.next_jump_timer <= 0 and self.jump_v == 0.0:
            self.jump_v = -random.uniform(*self.jump_strength_range)
            self.next_jump_timer = random.randint(30, 80)

        # física simples do salto (velocidade + gravidade)
        if self.jump_v != 0.0:
            self.jump_v += self.gravity
            self.jump_offset += self.jump_v
            # quando volta ao nível da base, "aterra"
            if self.jump_offset > 0:
                self.jump_offset = 0.0
                self.jump_v = 0.0

        # (sem invulnerabilidade aérea — morre como os outros inimigos)

        # aplicar posição final
        self.rect.centerx = int(self.centro_x)
        self.rect.centery = int(self.centro_y + self.jump_offset)

        # remoção quando sair da tela
        if self.rect.top > ALTURA or (self.centro_y -  self.rect.height) > ALTURA:
            self.kill()

class Boss(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=1, image_key='boss')
        self.vida = 100
        self.delay_tiro = 0  
    def update(self):
        self.rect.x += self.velocidade
        if self.rect.left < 0 or self.rect.right > LARGURA:
            self.velocidade *= -1

class BossTiro(Entidade):
    def __init__(self, x, y, jogador_pos):
        super().__init__(x, y, velocidade=5, image_key='boss_tiro')
        
        dx = jogador_pos[0] - x
        dy = jogador_pos[1] - y
        distancia = math.sqrt(dx**2 + dy**2)
        
        if distancia > 0:
            self.dx = dx / distancia
            self.dy = dy / distancia
        else:
            self.dx = 0
            self.dy = 1 
            
    def update(self):
        self.rect.x += self.dx * self.velocidade
        self.rect.y += self.dy * self.velocidade
        
        if self.rect.top > ALTURA or self.rect.bottom < 0 or self.rect.left > LARGURA or self.rect.right < 0:
            self.kill()

class PowerUp(Entidade):
    def __init__(self, x, y, tipo):
        self.tipo = tipo
        key_map = {"vida": "power_vida", "velocidade": "power_velocidade", "tirotriplo": "power_tirotriplo"}
        super().__init__(x, y, velocidade=2, image_key=key_map.get(tipo, 'power_vida'))
    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA: self.kill()

class Explosao(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frames = [pygame.transform.scale(sprites['explosao'], (80, 80))]
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

cacador_transformacao = None
cacador_ja_conhecido = False

estado_jogo = "MENU"

pause_rect = sprites['pause_button_sprite'].get_rect(topright=(LARGURA - 10, 10))

def menu_pausa():
    global estado_jogo, music_status
    
    fundo_pausa = TELA.copy()
    menu_img = sprites['menu_pause_fundo']
    menu_rect = menu_img.get_rect(center=(LARGURA // 2, ALTURA // 2))

    menu_w = menu_img.get_width()
    menu_h = menu_img.get_height()
    col_w = menu_w // 3 

    rect_play = pygame.Rect(menu_rect.left, menu_rect.top, col_w, menu_h)
    rect_musica = pygame.Rect(menu_rect.left + col_w, menu_rect.top, col_w, menu_h) 
    rect_sair = pygame.Rect(menu_rect.left + 2 * col_w, menu_rect.top, col_w, menu_h)
    
    stop_music()
    
    while estado_jogo == "PAUSED":
        
        TELA.blit(fundo_pausa, (0, 0))
        TELA.blit(menu_img, menu_rect)
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "NORMAL" if chefao is None else "BOSS"
                if music_status:
                    play_music('trilha_boss' if chefao else 'trilha_jogo')
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                
                if rect_play.collidepoint(x, y):
                    play_sfx('clique_botao')
                    estado_jogo = "NORMAL" if chefao is None else "BOSS"
                    if music_status:
                        play_music('trilha_boss' if chefao else 'trilha_jogo')
                    return
                
                elif rect_musica.collidepoint(x, y):
                    play_sfx('clique_botao')
                    music_status = not music_status
                    print(f"Música: {'Ligada' if music_status else 'Desligada'}")

                elif rect_sair.collidepoint(x, y):
                    play_sfx('clique_botao')
                    reset_game_state()
                    estado_jogo = "MENU"
                    return

        clock.tick(FPS)

intro_video = "lv_0_20251208094527.mp4"
if OPENCV_OK and os.path.exists(intro_video):
    try:
        tocar_video_intro(intro_video)
    except Exception as e:
        print("Falha ao reproduzir intro:", e)
else:
    print("Cutscene pulada (OpenCV ausente ou arquivo não existe).")

rodando = True
while rodando:
    clock.tick(FPS)

    if estado_jogo == "MENU":
        tela_inicial()
        continue
    
    if estado_jogo == "COUNTDOWN":
        contagem_regressiva()
        continue

    if estado_jogo == "GAME_OVER":
        tela_game_over(pontos)
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if estado_jogo in ["NORMAL", "BOSS"]:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                estado_jogo = "PAUSED"
            
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pause_rect.collidepoint(event.pos):
                    play_sfx('clique_botao')
                    estado_jogo = "PAUSED"

        if estado_jogo == "WIN":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                reset_game_state()
                estado_jogo = "COUNTDOWN"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                reset_game_state()
                estado_jogo = "MENU"

    if estado_jogo in ["NORMAL", "BOSS", "BOSS_INCOMING"]:
        keys = pygame.key.get_pressed()
        delay_tiro += 0.2
        if keys[pygame.K_SPACE]:
            delay_tiro_ajustado = 2 if jogador.transformado else 4
            if delay_tiro >= delay_tiro_ajustado:
                play_sfx('tiro')
                if tempo_tirotriplo > 0 or jogador.transformado:
                    t1 = Tiro(jogador.rect.centerx, jogador.rect.y)
                    t2 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, -1)
                    t3 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, 1)
                    for t in (t1, t2, t3):
                        todos_sprites.add(t); tiros.add(t)
                else:
                    t = Tiro(jogador.rect.centerx, jogador.rect.y)
                    todos_sprites.add(t); tiros.add(t)
                delay_tiro = 0

        if pontos >= 50 and estado_jogo == "NORMAL":
            estado_jogo = "BOSS_INCOMING"
            play_sfx('chegada_chefao')
            play_music('trilha_boss')
            aviso_timer = FPS * 2

        if estado_jogo == "BOSS_INCOMING":
            aviso_timer -= 1
            if aviso_timer <= 0:
                estado_jogo = "BOSS"
                chefao = Boss(LARGURA // 2, 120)
                todos_sprites.add(chefao)

        if estado_jogo == "BOSS":
            if chefao:
                chefao.delay_tiro += 1
                
                if chefao.delay_tiro >= 45: 
                    
                    if (chefao.delay_tiro % 10) == 0 and chefao.delay_tiro <= 65:
                        t = BossTiro(chefao.rect.centerx, chefao.rect.bottom + 5, jogador.rect.center)
                        tiros_chefao.add(t); todos_sprites.add(t)

                    if chefao.delay_tiro >= 70:
                        chefao.delay_tiro = 0 

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

            if random.random() < 0.005 and not jogador.transformado:
                tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                r = PowerUp(random.randint(40, LARGURA - 40), -40, tipo)
                todos_sprites.add(r)
                powerups.add(r)

        for p in pygame.sprite.spritecollide(jogador, powerups, True):
            play_sfx('power_up')
            if p.tipo == "vida":
                jogador.vida += 1
            elif p.tipo == "velocidade":
                jogador.velocidade = 10
                tempo_velocidade = FPS * 5
            elif p.tipo == "tirotriplo":
                tempo_tirotriplo = FPS * 5

        # tratar colisões entre inimigos e tiros
        # não remover tiros automaticamente: usamos invulnerabilidade aérea para pulantes
        colisoes = pygame.sprite.groupcollide(inimigos, tiros, False, False)
        for inimigo, lista_tiros in colisoes.items():
            # se inimigo estiver invulnerável (ex.: pulando), ignorar colisão e deixar tiros seguirem
            if getattr(inimigo, 'invulneravel', False):
                continue

            dano = len(lista_tiros)

            # remover os tiros que acertaram, pois agora vamos processar o impacto
            for t in lista_tiros:
                t.kill()

            # inimigos com atributo 'vida' recebem dano progressivo
            if hasattr(inimigo, 'vida'):
                inimigo.vida -= dano
                if inimigo.vida <= 0:
                    explos = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
                    explosoes.add(explos); todos_sprites.add(explos)
                    pontos += 1
                    if random.random() < 0.10:
                        tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                        p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                        powerups.add(p); todos_sprites.add(p)
                    inimigo.kill()

            else:
                # comportamento para inimigos sem 'vida'
                if jogador.transformado:
                    # jogador transformado precisa acertar 2 tiros para matar inimigos comuns
                    if dano >= 2:
                        explos = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
                        explosoes.add(explos); todos_sprites.add(explos)
                        pontos += 1
                        if random.random() < 0.10:
                            tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                            p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                            powerups.add(p); todos_sprites.add(p)
                        inimigo.kill()
                else:
                    explos = Explosao(inimigo.rect.centerx, inimigo.rect.centery)
                    explosoes.add(explos); todos_sprites.add(explos)
                    pontos += dano
                    if random.random() < 0.10:
                        tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                        p = PowerUp(inimigo.rect.centerx, inimigo.rect.centery, tipo)
                        powerups.add(p); todos_sprites.add(p)
                    inimigo.kill()

        if chefao:
            tiros_acertaram = pygame.sprite.spritecollide(chefao, tiros, True)
            
            for tiro in tiros_acertaram:
                chefao.vida -= 1

                if random.random() < 0.10: 
                    tipo = random.choice(["vida", "velocidade", "tirotriplo"])
                    p = PowerUp(chefao.rect.centerx, chefao.rect.centery, tipo)
                    powerups.add(p); todos_sprites.add(p)
                    
            if chefao.vida <= 0:
                chefao.kill()
                chefao = None
                estado_jogo = "WIN"
                play_sfx('morte_chefao')
                stop_music()
                pontos += 50

        colisao_cacador = pygame.sprite.spritecollide(jogador, inimigos, False)
        for inimigo in list(colisao_cacador):
            if isinstance(inimigo, RoboCacador) and not jogador.transformado:
                play_sfx('transformacao_easter_egg')
                jogador.ativar_transformacao()
                inimigo.kill()
                cacador_ja_conhecido = True
            elif isinstance(inimigo, RoboCacador) and jogador.transformado:
                inimigo.kill()

        if pygame.sprite.spritecollide(jogador, tiros_chefao, True):
            jogador.vida -= 1
            if jogador.transformado:
                play_sfx('perca_easter_egg')
                jogador.desativar_transformacao()
                cacador_ja_conhecido = False
            if jogador.vida <= 0:
                estado_jogo = "GAME_OVER"
        
        colisao_inimigos = pygame.sprite.spritecollide(jogador, inimigos, True)
        for inimigo in colisao_inimigos:
            if not isinstance(inimigo, RoboCacador):
                jogador.vida -= 1
                if jogador.transformado:
                    play_sfx('perca_easter_egg')
                    jogador.desativar_transformacao()
                    cacador_ja_conhecido = False
                if jogador.vida <= 0:
                    estado_jogo = "GAME_OVER"

        if tempo_velocidade > 0:
            tempo_velocidade -= 1
            if tempo_velocidade == 0:
                jogador.velocidade = jogador.velocidade_original
        
        if tempo_tirotriplo > 0:
            tempo_tirotriplo -= 1
            
        todos_sprites.update()
        tiros_chefao.update()
        explosoes.update()

    if estado_jogo in ["NORMAL", "BOSS", "BOSS_INCOMING"]:
        if jogador.transformado:
            fundo_mod = fundo.copy()
            overlay = pygame.Surface((LARGURA, ALTURA))
            overlay.fill((0, 40, 40))
            overlay.set_alpha(120)
            fundo_mod.blit(overlay, (0, 0))
            TELA.blit(fundo_mod, (0, 0))
        else:
            TELA.blit(fundo, (0, 0))

        todos_sprites.draw(TELA)
        explosoes.draw(TELA)

        TELA.blit(sprites['pause_button_sprite'], pause_rect)

        if estado_jogo == "BOSS_INCOMING":
            cor_aviso = (255, 0, 0) 
            
            if (aviso_timer // 10) % 2 == 0:
                 cor_aviso = (255, 255, 0) 
            
            font_aviso = pygame.font.SysFont(None, 100, bold=True)
            texto_principal = "BOSS CHEGANDO!" 
            
            sombra_aviso = font_aviso.render(texto_principal, True, (0, 0, 0))
            TELA.blit(sombra_aviso, (LARGURA // 2 - sombra_aviso.get_width() // 2 + 3, ALTURA // 2 - 40 + 3))
            
            texto_aviso = font_aviso.render(texto_principal, True, cor_aviso)
            TELA.blit(texto_aviso, (LARGURA // 2 - texto_aviso.get_width() // 2, ALTURA // 2 - 40))

        if estado_jogo == "BOSS" and chefao:
            barra_w = 300  
            barra_h = 20    
            barra_x = LARGURA // 2 - barra_w // 2 
            barra_y = 10
            
            pygame.draw.rect(TELA, (0, 0, 0), (barra_x, barra_y, barra_w, barra_h))
            pygame.draw.rect(TELA, (255, 0, 0), (barra_x, barra_y, barra_w, barra_h), 3) 
            
            vida_atual_w = int((chefao.vida / 100) * barra_w)
            
            cor_vida = (0, 255, 0) 
            if chefao.vida < 50:
                 cor_vida = (255, 255, 0) 
            if chefao.vida < 20:
                 cor_vida = (255, 0, 0) 
                 
            pygame.draw.rect(TELA, cor_vida, (barra_x, barra_y, vida_atual_w, barra_h))
            
            font_boss = pygame.font.SysFont(None, 24, bold=True)
            texto_vida = font_boss.render(f"BOSS (HP: {chefao.vida})", True, (255, 255, 255))
            TELA.blit(texto_vida, (LARGURA // 2 - texto_vida.get_width() // 2, barra_y + 3))

        font = pygame.font.SysFont(None, 30)
        texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}", True, (255, 255, 255))
        TELA.blit(texto, (10, 10))
        
    elif estado_jogo == "PAUSED":
        menu_pausa()

    elif estado_jogo == "WIN":
        TELA.blit(fundo, (0, 0))
        
        font_titulo = pygame.font.SysFont(None, 120, bold=True)
        font_sub = pygame.font.SysFont(None, 40)
        titulo = font_titulo.render("VITÓRIA!", True, (0, 255, 0))
        score_text = font_sub.render(f"Pontuação Total: {pontos}", True, (255, 255, 255))
        instrucao = font_sub.render("Pressione ENTER para Recomeçar ou ESC para Menu", True, (150, 150, 150))
        
        TELA.blit(titulo, (LARGURA // 2 - titulo.get_width() // 2, ALTURA // 3))
        TELA.blit(score_text, (LARGURA // 2 - score_text.get_width() // 2, ALTURA // 2))
        TELA.blit(instrucao, (LARGURA // 2 - instrucao.get_width() // 2, ALTURA * 2 // 3))
        
    
    pygame.display.flip()

pygame.quit()
sys.exit()
