import pygame
import random
import math

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()

# ======== ESTADO DO JOGO ========
estado_jogo = "NORMAL"   # NORMAL → BOSS_INCOMING → BOSS → WIN


# CLASSE BASE
class Entidade(pygame.sprite.Sprite):
    def __init__(self, x, y, velocidade):
        super().__init__()
        self.velocidade = velocidade
        self.image = pygame.Surface((40, 40))
        self.rect = self.image.get_rect(center=(x, y))

    def mover(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy


# JOGADOR
class Jogador(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 5)
        self.image.fill((0, 255, 0))  # verde
        self.vida = 5

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

        self.rect.x = max(0, min(self.rect.x, LARGURA - 40))
        self.rect.y = max(0, min(self.rect.y, ALTURA - 40))


# TIRO (DO JOGADOR)
class Tiro(Entidade):
    def __init__(self, x, y):
        super().__init__(x, y, 10)
        self.image.fill((255, 255, 0))  # amarelo

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
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))  # vermelho

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO ZigueZague
class RoboZigueZague(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=3)
        self.direcao = 1

    def atualizar_posicao(self):
        self.rect.y += self.velocidade
        self.rect.x += self.direcao * 3

        if self.rect.x <= 0 or self.rect.x >= LARGURA - 40:
            self.direcao *= -1

    def update(self):
        self.atualizar_posicao()
        if self.rect.y > ALTURA:
            self.kill()


# ROBO Caçador
class RoboCacador(Robo):
    def __init__(self, x, y, velocidade=3, jitter=0.6, usar_jitter=True):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 100, 0))  # laranja
        self.jitter = jitter
        self.usar_jitter = usar_jitter

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


class RoboCircular(Robo):
    def __init__(self, x, y, raio, v_descida,v_angular):
        super().__init__(x, y, velocidade=3)
        self.center_x = x
        self.center_y = y
        self.raio = raio
        self.v_descida = v_descida
        self.v_angular = v_angular
        self.angulo = 0


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

#BOSS
class Boss(Robo):
    def __init__(self, x, y):
        super().__init__(x, y, velocidade=2)
        self.image = pygame.Surface((120, 120))
        self.image.fill((0, 0, 150))
        self.rect = self.image.get_rect(center=(x, y))

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
        super().__init__(x, y, 5)
        self.image.fill((0, 0, 255))

    def update(self):
        self.rect.y += self.velocidade
        if self.rect.top > ALTURA:
            self.kill()


# POWERUPS
class PowerUp(RoboZigueZague):
    def __init__(self, x, y, tipo):
        super().__init__(x, y)

        self.tipo = tipo
        self.velocidade = 6

        if tipo == "vida":
            self.image.fill((0, 0, 255))
        elif tipo == "velocidade":
            self.image.fill((163, 73, 14))
        elif tipo == "tirotriplo":
            self.image.fill((255, 141, 161))


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

rodando = True
while rodando:
    clock.tick(FPS)

    # TIRO DO JOGADOR
    keys = pygame.key.get_pressed()
    delay_tiro += 0.2
    if delay_tiro >= 4:
                if keys[pygame.K_SPACE]:
                    if tempo_tirotriplo > 0:
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
        if spawn_timer > 40:
            if random.random() < 0.15:
                robo = RoboCacador(random.randint(40, LARGURA - 40), -40, velocidade=2)

            elif random.random() < 0.3:
                robo = RoboCircular(x=random.randint(40, LARGURA - 40),y=-40,raio=random.randint(20, 60),v_descida=2,v_angular=random.uniform(3, 6))
            else:
                robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)
            todos_sprites.add(robo)
            inimigos.add(robo)
            spawn_timer = 0

        if random.random() < 0.005:
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

    hits = pygame.sprite.groupcollide(inimigos, tiros, True, True)
    pontos += len(hits)

    if chefao:
        tiros_acertaram = pygame.sprite.spritecollide(chefao, tiros, True)
        chefao.vida -= len(tiros_acertaram)

    if pygame.sprite.spritecollide(jogador, tiros_chefao, True):
        jogador.vida -= 1
        if jogador.vida <= 0:
            print("GAME OVER")
            rodando = False

    if pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1
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
    TELA.fill((20, 20, 20))
    todos_sprites.draw(TELA)

    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida} | Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

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
