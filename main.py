import pygame
import random
import math 
import os

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()

# FUNÇÃO DE CARREGAMENTO DE SPRITE E DIMENSÕES AJUSTADAS
def carregar_sprite(nome_arquivo, cor_fallback=(0, 0, 0), largura=40, altura=40):
    
    # TAMANHOS DE SPRITE AJUSTADOS
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
    else: # Todos os robôs inimigos 
        largura, altura = 50, 50 
    
    # Define o caminho completo
    caminho_completo = 'sprites/' + nome_arquivo 
    
    try:
        imagem = pygame.image.load(caminho_completo).convert_alpha()
        imagem = pygame.transform.scale(imagem, (largura, altura))
        return imagem
    except (pygame.error, FileNotFoundError):
        print(f"ATENÇÃO: Não foi possível carregar a sprite {caminho_completo}. Gerando quadrado.")
        surface = pygame.Surface((largura, altura))
        if 'robo_ciclico' in nome_arquivo:
            cor_fallback = (255, 0, 100)
        elif 'robo_saltador' in nome_arquivo:
            cor_fallback = (150, 0, 150)
        
        surface.fill(cor_fallback)
        surface.set_colorkey((0,0,0)) 
        return surface.convert_alpha()

# CARREGAMENTO GLOBAL DE SPRITES
sprites = {
    'jogador': carregar_sprite('jogador.png', cor_fallback=(0, 255, 0)),
    'tiro': carregar_sprite('tiro.png', cor_fallback=(255, 255, 0)), 
    'robo_zigue': carregar_sprite('robo_zigue.png', cor_fallback=(255, 0, 0)),
    'robo_cacador': carregar_sprite('robo_cacador.png', cor_fallback=(255, 100, 0)),
    'robo_lento': carregar_sprite('robo_lento.png', cor_fallback=(100, 0, 255)), 
    'robo_rapido': carregar_sprite('robo_rapido.png', cor_fallback=(0, 100, 255)), 
    # Cores personalizadas para fallback
    'robo_ciclico': carregar_sprite('robo_ciclico.png', cor_fallback=(255, 0, 100)),
    'robo_saltador': carregar_sprite('robo_saltador.png', cor_fallback=(150, 0, 150)), 
    
    'power_vida': carregar_sprite('power_vida.png', cor_fallback=(0, 0, 255)),
    'power_velocidade': carregar_sprite('power_velocidade.png', cor_fallback=(163, 73, 14)),
    'power_tirotriplo': carregar_sprite('power_tirotriplo.png', cor_fallback=(255, 141, 161)),
    'boss': carregar_sprite('boss.png', cor_fallback=(0, 0, 150)), 
    'boss_tiro': carregar_sprite('boss_tiro.png', cor_fallback=(0, 0, 255)), 
}

# ESTADO DO JOGO
estado_jogo = "NORMAL"


# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade, image_key):
        super().__init__()
        self.velocidade = velocidade
        self.image = sprites[image_key] 
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5, 'jogador') 
        self.vida = 5
        self.transformado = False
        self.tamanho_original = (60, 60)
        self.velocidade_original = 5
        self.cacador_desabilitado = False  # Controla se caçador pode aparecer

    def ativar_transformacao(self):
        """Ativa o modo transformado (Easter Egg do Caçador)"""
        self.transformado = True
        # Aumenta o tamanho um pouco
        novo_tamanho = (int(60 * 1.3), int(60 * 1.3))
        self.image = pygame.transform.scale(sprites['jogador'], novo_tamanho)
        self.rect = self.image.get_rect(center=self.rect.center)
        # Aumenta velocidade (balanceado)
        self.velocidade = 6.5

    def desativar_transformacao(self):
        """Desativa o modo transformado"""
        self.transformado = False
        self.image = pygame.transform.scale(sprites['jogador'], self.tamanho_original)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.velocidade = self.velocidade_original
        self.cacador_desabilitado = True  # Caçador não spawna mais após transformação

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.mover(0, -self.velocidade)
        if keys[pygame.K_s]:
            self.mover(0, self.velocidade)
        if keys[pygame.K_a]:
            self.mover(-self.velocidade, 0)
        if keys[pygame.K_d]:
            self.mover(self.velocidade, 0)

        self.rect.x = max(0, min(self.rect.x, LARGURA - self.rect.width)) 
        self.rect.y = max(0, min(self.rect.y, ALTURA - self.rect.height)) 


# TIRO (DO JOGADOR)
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


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade, image_key):
        super().__init__(x, y, velocidade, image_key) 

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO ZigueZague
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

# Variações do Robo ZigueZague
class RoboCiclico(RoboZigueZague): 
    def __init__(self, x, y):
        super(RoboZigueZague, self).__init__(x, y, velocidade=2, image_key='robo_ciclico') 
        self.direcao = 1
        self.vida = 1

class RoboLento(RoboZigueZague): 
    def __init__(self, x, y):
        super(RoboZigueZague, self).__init__(x, y, velocidade=1, image_key='robo_lento') 
        self.direcao = 1
        self.vida = 1

class RoboRapido(RoboZigueZague): 
    def __init__(self, x, y):
        super(RoboZigueZague, self).__init__(x, y, velocidade=4, image_key='robo_rapido') 
        self.direcao = 1
        self.vida = 1 

# ROBO Caçador
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
        dist = (dx*dx + dy*dy) ** 0.5
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


# ROBO CIRCULAR
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
        # Descida contínua
        self.rect.y += self.velocidade 
        self.timer += 1

        # Lógica de pulo
        if self.timer >= self.cooldown_pulo:
            self.rect.y += self.forca_pulo
            self.timer = 0
            self.cooldown_pulo = random.randint(40, 80)

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()

#BOSS
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


# POWERUPS
class PowerUp(RoboZigueZague):
    def __init__(self, x, y, tipo):
        
        sprite_map = {
            "vida": 'power_vida',
            "velocidade": 'power_velocidade',
            "tirotriplo": 'power_tirotriplo',
        }

        super(RoboZigueZague, self).__init__(x, y, velocidade=3, image_key=sprite_map[tipo]) 

        self.tipo = tipo
        self.velocidade = 3
        self.direcao = 1 


# GRUPOS
todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
powerups = pygame.sprite.Group()
tiros_chefao = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

chefao = None
pontos = 0
spawn_timer = 0
tempo_velocidade = 0
tempo_tirotriplo = 0
delay_tiro = 0

# Variáveis para o easter egg
caçador_transformacao = None  # Referência ao caçador especial
caçador_jaConhecido = False   # Flag para evitar múltiplos caçadores especiais

rodando = True
while rodando:
    clock.tick(FPS)

    # TIRO DO JOGADOR
    keys = pygame.key.get_pressed()
    delay_tiro += 0.2
    if delay_tiro >= 4:
        if keys[pygame.K_SPACE]:
            # Reduz delay de tiro quando transformado
            delay_tiro_ajustado = 2 if jogador.transformado else 4
            if delay_tiro >= delay_tiro_ajustado:
                if tempo_tirotriplo > 0:
                    t1 = Tiro(jogador.rect.centerx, jogador.rect.y)
                    t2 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, -1)
                    t3 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, 1)
                    for t in (t1, t2, t3):
                        todos_sprites.add(t)
                        tiros.add(t)
                elif jogador.transformado:
                    # Tiro triplo quando transformado
                    t1 = Tiro(jogador.rect.centerx, jogador.rect.y)
                    t2 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, -1)
                    t3 = TiroDiagonal(jogador.rect.centerx, jogador.rect.y, 1)
                    for t in (t1, t2, t3):
                        todos_sprites.add(t)
                        tiros.add(t)
                else:
                    t = Tiro(jogador.rect.centerx, jogador.rect.y)
                    todos_sprites.add(t)
                    tiros.add(t)
                delay_tiro = 0
                
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        # REINICIAR APÓS VITÓRIA
        if estado_jogo == "WIN":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:

                pontos = 0
                jogador.vida = 5
                jogador.rect.center = (LARGURA // 2, ALTURA - 60)
                
                # Reverter transformação ao reiniciar
                if jogador.transformado:
                    jogador.desativar_transformacao()
                caçador_jaConhecido = False
                jogador.cacador_desabilitado = False  # Reseta para próximo jogo

                # limpar tudo menos o jogador
                for grp in (inimigos, tiros, powerups, tiros_chefao, todos_sprites):
                    for s in grp.copy():
                        if not isinstance(s, Jogador):
                            s.kill()

                chefao = None
                estado_jogo = "NORMAL"

    #Lógica da chegada do CHEFÃO
    if pontos >= 50 and estado_jogo == "NORMAL":
        estado_jogo = "BOSS_INCOMING"
        aviso_timer = FPS * 2 

    if estado_jogo == "BOSS_INCOMING":
        aviso_timer -= 1
        if aviso_timer <= 0:
            estado_jogo = "BOSS"
            chefao = Boss(LARGURA // 2, 120)
            todos_sprites.add(chefao)

    # Spawn de inimigos APENAS no modo NORMAL
    if estado_jogo == "NORMAL":
        spawn_timer += 1
        if spawn_timer > 60: 
            rand = random.random()
            x_pos = random.randint(50, LARGURA - 50) 
            
            if rand < 0.15 and not jogador.transformado and not jogador.cacador_desabilitado:
                # Caçador NÃO spawna quando transformado ou após ser usado
                robo = RoboCacador(x_pos, -50)
            elif rand < 0.30:
                robo = RoboCircular(
                    x=x_pos, 
                    y=-50,
                    raio=random.randint(20, 60),
                    v_descida=1, 
                    v_angular=random.uniform(3, 6)
                )
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

        # Power-ups NÃO spawnam quando transformado
        if random.random() < 0.005 and not jogador.transformado:
            tipo = random.choice(["vida", "velocidade", "tirotriplo"])
            r = PowerUp(random.randint(40, LARGURA - 40), -40, tipo)
            todos_sprites.add(r)
            powerups.add(r)

    # colisão powerup
    for p in pygame.sprite.spritecollide(jogador, powerups, True):
        if p.tipo == "vida":
            jogador.vida += 1
        elif p.tipo == "velocidade":
            jogador.velocidade = 10
            tempo_velocidade = FPS * 5
        elif p.tipo == "tirotriplo":
            tempo_tirotriplo = FPS * 5

    hits = pygame.sprite.groupcollide(inimigos, tiros, False, True)
    for inimigo, lista_tiros in hits.items():
        # Se transformado, inimigos precisam de 2 tiros
        dano = len(lista_tiros)
        if jogador.transformado:
            if hasattr(inimigo, 'vida'):
                inimigo.vida -= dano
                if inimigo.vida <= 0:
                    inimigo.kill()
                    pontos += 1
            else:
                # Inimigos sem vida (normais) precisam de 2 tiros quando transformado
                if dano >= 2:
                    inimigo.kill()
                    pontos += 1
        else:
            # Modo normal: 1 tiro mata
            inimigo.kill()
            pontos += len(lista_tiros)

    if chefao:
        tiros_acertaram = pygame.sprite.spritecollide(chefao, tiros, True)
        chefao.vida -= len(tiros_acertaram)

    # COLISÃO ESPECIAL: Caçador (Easter Egg)
    colisao_cacador = pygame.sprite.spritecollide(jogador, inimigos, False)
    for inimigo in colisao_cacador:
        if isinstance(inimigo, RoboCacador) and not jogador.transformado:
            # Ativa transformação!
            jogador.ativar_transformacao()
            inimigo.kill()
            # Muda as cores de fundo
            cor_fundo_alterada = True
        elif isinstance(inimigo, RoboCacador) and jogador.transformado:
            # Se já está transformado, apenas mata o caçador normalmente
            inimigo.kill()

    # Tiros do chefão acertam o jogador
    if pygame.sprite.spritecollide(jogador, tiros_chefao, True):
        jogador.vida -= 1
        # Reverte transformação ao tomar dano
        if jogador.transformado:
            jogador.desativar_transformacao()
            caçador_jaConhecido = False
        if jogador.vida <= 0:
            print("GAME OVER")
            rodando = False

    # Colisão com inimigos normais (exceto caçador que já foi tratado)
    colisao_inimigos = pygame.sprite.spritecollide(jogador, inimigos, True)
    for inimigo in colisao_inimigos:
        if not isinstance(inimigo, RoboCacador):  # Caçador já foi tratado acima
            jogador.vida -= 1
            # Reverte transformação ao tomar dano
            if jogador.transformado:
                jogador.desativar_transformacao()
                caçador_jaConhecido = False
            if jogador.vida <= 0:
                print("GAME OVER")
                rodando = False

    if tempo_velocidade > 0:
        tempo_velocidade -= 1
        if tempo_velocidade == 0:
            jogador.velocidade = 5

    if tempo_tirotriplo > 0:
        tempo_tirotriplo -= 1

    todos_sprites.update()
    tiros_chefao.update()

    # DESENHO
    # Altera cor de fundo quando transformado
    cor_fundo = (0, 20, 20) if jogador.transformado else (20, 20, 20)
    TELA.fill(cor_fundo)
    todos_sprites.draw(TELA)

    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))
    
    # Exibe status de transformação
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

# Classe para controlar dano em inimigos
class RoboComVida(Robo):
    def __init__(self, x, y, velocidade, image_key, vida=1):
        super().__init__(x, y, velocidade, image_key)
        self.vida = vida
