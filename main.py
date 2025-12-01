import pygame
import random

pygame.init()

LARGURA = 800
ALTURA = 600
TELA = pygame.display.set_mode((LARGURA, ALTURA))
pygame.display.set_caption("Robot Defense - Template")

FPS = 60
clock = pygame.time.Clock()


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

        # limites de tela
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


# ROBO BASE
class Robo(Entidade):
    def __init__(self, x, y, velocidade):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 0, 0))  # vermelho

    def atualizar_posicao(self):
        raise NotImplementedError


# ROBO EXEMPLO — ZigueZague
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

class RoboCacador(Robo):
    def __init__(self, x, y, velocidade=3, jitter=0.6, usar_jitter=True):
        super().__init__(x, y, velocidade)
        self.image.fill((255, 100, 0))  # laranja
        self.jitter = jitter
        self.usar_jitter = usar_jitter

    def atualizar_posicao(self):
        # posição alvo (jogador global)
        tx = jogador.rect.centerx
        ty = jogador.rect.centery
        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery

        # distância sem usar math.hypot (evita import extra)
        dist = (dx*dx + dy*dy) ** 0.5
        if dist == 0:
            return

        nx = dx / dist
        ny = dy / dist

        # acelera um pouco quando perto para comportamento mais agressivo
        speed = self.velocidade + (1 if dist < 180 else 0)

        # jitter opcional: pequena variação aleatória para parecer "impreciso"
        jx = random.uniform(-self.jitter, self.jitter) if self.usar_jitter else 0
        jy = random.uniform(-self.jitter, self.jitter) if self.usar_jitter else 0

        # aplicar movimento (usar int/round para não acumular float no rect)
        self.rect.x += int(nx * speed + jx)
        self.rect.y += int(ny * speed + jy)

    def update(self):
        self.atualizar_posicao()
        # remover se sair muito da tela
        if (self.rect.top > ALTURA + 200 or self.rect.bottom < -200 or
                self.rect.left < -200 or self.rect.right > LARGURA + 200):
            self.kill()

class Vida_extra(RoboZigueZague):
  def __init__(self, x, y):
      super().__init__(x, y)
      self.velocidade = 6
      self.image.fill((0,0,255))
  def atualizar_posicao(self):
      return super().atualizar_posicao()
  def update(self):
      return super().update()      

todos_sprites = pygame.sprite.Group()
inimigos = pygame.sprite.Group()
tiros = pygame.sprite.Group()
vida_extra = pygame.sprite.Group()

jogador = Jogador(LARGURA // 2, ALTURA - 60)
todos_sprites.add(jogador)

pontos = 0
spawn_timer = 0
spawn_timer_vida = 0
rodando = True
while rodando:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            rodando = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                tiro = Tiro(jogador.rect.centerx, jogador.rect.y)
                todos_sprites.add(tiro)
                tiros.add(tiro)

    # timer de entrada dos inimigos
    spawn_timer += 1
    if spawn_timer > 40:
        if random.random() < 0.15:
            robo = RoboCacador(random.randint(40, LARGURA - 40), -40, velocidade=2)
        else:
            robo = RoboZigueZague(random.randint(40, LARGURA - 40), -40)
        todos_sprites.add(robo)
        inimigos.add(robo)
        spawn_timer = 0
   
   #controla a entrada das vidas extras     
    spawn_timer_vida += 1
    if spawn_timer_vida > 1000:
        robo = Vida_extra(random.randint(40, LARGURA - 40), -40)
        todos_sprites.add(robo)
        vida_extra.add(robo)
        spawn_timer_vida = 0

    #colisão vida_extra x jogador
    if pygame.sprite.spritecollide(jogador, vida_extra, True):
            jogador.vida += 1
    # colisão tiro x robô
    colisao = pygame.sprite.groupcollide(inimigos, tiros, True, True)
    pontos += len(colisao)

    # colisão robô x jogador
    if pygame.sprite.spritecollide(jogador, inimigos, True):
        jogador.vida -= 1
        if jogador.vida <= 0:
            print("GAME OVER!")
            rodando = False

    # atualizar
    todos_sprites.update()

    # desenhar
    TELA.fill((20, 20, 20))
    todos_sprites.draw(TELA)

    #Painel de pontos e vida
    font = pygame.font.SysFont(None, 30)
    texto = font.render(f"Vida: {jogador.vida}  |  Pontos: {pontos}", True, (255, 255, 255))
    TELA.blit(texto, (10, 10))

    pygame.display.flip()

pygame.quit()