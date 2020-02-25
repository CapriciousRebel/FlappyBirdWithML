import pygame
import neat
import time
import random
import os


pygame.font.init()

WINDOW_WIDTH = 500
WINDOW_HEIGHT = 800

STAT_FONT = pygame.font.SysFont("comicsans", 50)

# Loading all the sprites
bird_sprites = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
                pygame.transform.scale2x(pygame.image.load(
                    os.path.join("imgs", "bird2.png"))),
                pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

pipe_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "pipe.png")))

background_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "bg.png")))

base_sprite = pygame.transform.scale2x(
    pygame.image.load(os.path.join("imgs", "base.png")))


class Bird:
    images = bird_sprites           # This is the list of sprites of the bird
    max_angular_displacement = 25   # This is the maximum outward rotation of the bird
    # This is the angular velocity at which the bird rotates
    angular_velocity = 20
    # Time in seconds for which each bird is displayed.
    animation_time = 5

    def __init__(self, x, y):
        '''Initializing the bird's attributes'''

        #### Physics variables ####
        self.x = x                   # top-left anchor point of the bird
        self.y = y                   # top-right anchor point of the bird
        self.angular_displacement = 0
        self.velocity = 0            # velocity of the bird
        self.height = self.y         # ~ The height of the bird
        self.tick_count = 0          # current tick of the bird, basically time

        #### Rendering Variables ####
        self.img_count = 0           # The current image id which is being shown for the bird
        self.image = self.images[0]  # The current image of the bird

    def jump(self):                 # The jump method for the bird

        # Resetting the tick_count to zero everytime the jump method is called
        self.tick_count = 0
        self.velocity = -10.5
        self.height = self.y

    def move(self):
        # Tick count works like time
        self.tick_count += 1

        # We call the move() function on every frame, and it updates the position of the bird, giving it a parabolic trajectory
        # The following equation gives the parabolic physics
        displacement = (self.velocity)*(self.tick_count) + \
            1.5*((self.tick_count)**2)

        # The terminal velocoty for the bird
        if displacement >= 16:
            displacement = 16

        # Fine tuning to make it look better
        if displacement < 0:
            displacement -= 2

        self.y += displacement

        # if we are moving upward or if we are above the jump height position
        if displacement < 0 or self.y < self.height + 50:
            # rotate the bird directly to maxrotation
            if self.angular_displacement < self.max_angular_displacement:
                self.angular_displacement = self.max_angular_displacement
        # if the bird is falling down then the bird must slowly approach to a 90-degree rotation(nose-dive)
        else:
            if self.angular_displacement > -90:
                self.angular_displacement -= self.angular_velocity

    def draw(self, win):
        # This variable keeps a track of the no. of times the bird was drawn to the window
        self.img_count += 1

        # Bird animation
        if self.img_count < self.animation_time:
            self.image = self.images[0]
        elif self.img_count < self.animation_time*2:
            self.image = self.images[1]
        elif self.img_count < self.animation_time*3:
            self.image = self.images[2]
        elif self.img_count < self.animation_time*4:
            self.image = self.images[1]
        elif self.img_count == self.animation_time*4 + 1:
            self.image = self.images[0]
            self.img_count = 0

        # Nose dive
        if self.angular_displacement <= -80:
            self.image = self.images[1]
            # setting the image count to 10 so that it looks natural after the nose dive is done
            self.img_count = self.animation_time*2

        # Logic to rotate the image
        rotated_image = pygame.transform.rotate(
            self.image, self.angular_displacement)
        new_rect = rotated_image.get_rect(
            center=self.image.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, new_rect.topleft)

    # For pixel perfect collision
    def get_mask(self):
        return pygame.mask.from_surface(self.image)


class Pipe:
    GAP = 200
    velocity = 5

    def __init__(self, x):

        #### The physics variables ####
        self.x = x
        self.height = 0
        self.gap = 100

        #### The Rendering variables ####
        self.top = 0            # Tracking where the top of pipe will be drawn
        self.bottom = 0         # Tracking where the bottom of pipe will be drawn

        self.top_pipe = pygame.transform.flip(pipe_sprite, False, True)
        self.bottom_pipe = pipe_sprite

        #### The logic variables ####
        self.passed = False

        #### everytime a pipe is created, we must create a height for it ####
        self.set_height()

    def set_height(self):
        '''set the height randomly for the pipe'''
        self.height = random.randrange(50, 450)
        self.top = self.height - self.top_pipe.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        '''move the pipe behind'''
        self.x -= self.velocity

    def draw(self, win):
        '''draw the pipe to the window'''
        win.blit(self.top_pipe, (self.x, self.top))
        win.blit(self.bottom_pipe, (self.x, self.bottom))

    def collide(self, bird):
        '''pixel perfect collisions using masks'''
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.top_pipe)
        bottom_mask = pygame.mask.from_surface(self.bottom_pipe)

        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        bottom_overlap = bird_mask.overlap(bottom_mask, bottom_offset)
        top_overlap = bird_mask.overlap(top_mask, top_offset)

        if top_overlap or bottom_overlap:
            return True

        return False


class Base:
    #### Physics variables ####
    velocity = 5

    #### Rendering variables ####
    width = base_sprite.get_width()
    image = base_sprite

    def __init__(self, y):

        self.y = y              # The y-postion of the base
        self.x1 = 0             # The x-postion of the first image
        self.x2 = self.width    # The x-postion of the second image

    def move(self):
        ''' move the bases to make it look like its continous'''
        self.x1 -= self.velocity
        self.x2 -= self.velocity

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    def draw(self, win):
        '''render the images on the screen'''
        win.blit(self.image, (self.x1, self.y))
        win.blit(self.image, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, collideText):
    win.blit(background_sprite, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    for bird in birds:
        bird.draw(win)

    base.draw(win)

    
    text = STAT_FONT.render("Score : " + str(score), 1, (255, 255, 255))
    win.blit(text, (WINDOW_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Collision : " + collideText, 1, (255, 255, 255))
    win.blit(text, (WINDOW_WIDTH - 200 - text.get_width(), 10))

    pygame.display.update()


def main(genomes, config):

    nets = []
    ge = []
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)

        birds.append(Bird(230, 350))

        g.fitness = 0
        ge.append(g)

    base = Base(730)
    pipes = [Pipe(600)]

    win = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    score = 0

    run = True

    while run:

        clock.tick(30)
        collideText = "False"

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

#            if event.type == pygame.KEYDOWN:
#               if event.key == pygame.K_SPACE:
#                   bird.jump()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].top_pipe.get_width():
                pipe_ind = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            bird.move()
            ge[x].fitness += 0.1

            output = nets[x].activate((bird.y, abs(
                bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.jump()

        #### Pipe genration logic ####
        add_pipe = False
        remove_pipes = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    # If a bird collides with a pipe, then it must lose some of its fitness so that it is not favoured as much as a bird that didnt hit the pipe at the same level
                    ge[x].fitness -= 1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.top_pipe.get_width() < 0:
                remove_pipes.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            # When a bird crosses a pipe, it gets a bonus fitness of +5 as an encouragement for it to pass through the pipes
            # Here we dont need to loop through all the birds since only those birds who make it through the pipes will be alive in the genome
            for g in ge:
                g.fitness += 5

            pipes.append(Pipe(600))

        for remove_pipe in remove_pipes:
            pipes.remove(remove_pipe)

        # bottom collision
        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() >= 730 or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        base.move()
        draw_window(win, birds, pipes, base, score, collideText)


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path)

    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
