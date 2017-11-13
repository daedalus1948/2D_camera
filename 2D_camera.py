# this code implements a simple 2d camera system
# an alpha version of Animation buffer event pump is also implemented
# use mouse buttons for locking and directing the movement of locked objects, mouse wheel to zoom
# 'wasd' is currently hardcoded for camera movement (will be changed later)
# change camera mode with 'm' - after that, mouse controls and camera behave differently
# move static classes to their own modules (and remove the classes there)
# (animations) consider writing class specific attribute setters and attribute guards (eg. forbid an attribute to become negative)

import pygame
import random
import math

# static
class Game:

    colors = {'black': (0, 0, 0), 'red': (255, 0, 0), 'yellow': (255, 255, 0), 'white': (255, 255, 255), 'violet': (148, 0, 211)}
    FPS = 30
    FPS_clock = None
    (width, height) = (600, 600)
    screen = None
    font = None

    data = []  # all game objects reside in this structure
    running = False

    def init():  # mutates the state of Game class object variables

        pygame.init()  # important
        Game.FPS_clock = pygame.time.Clock()
        Game.screen = pygame.display.set_mode((Game.width, Game.height))
        Game.font = pygame.font.Font(None, 15)
        Camera.init_modes()  # init camera modes after all classes and functions are initialized

    def handle_events():  # method handles user input via combination of polling (key.get_pressed()) and event loop (event.get)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                Controls.follow_mouse()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # left click
                    Controls.move_to_mouseclick()
                if event.button == 3:  # right click
                    Camera.mode_routine()  # changes based on the current mode
                if event.button == 4:  # scroll up
                    Camera.set_zoom(1)
                if event.button == 5:  # scroll down
                    Camera.set_zoom(-1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    Controls.quit()  # quit game, end program
                if event.key == pygame.K_w:
                    Controls.up()
                if event.key == pygame.K_a:
                    Controls.left()
                if event.key == pygame.K_s:
                    Controls.down()
                if event.key == pygame.K_d:
                    Controls.right()
                if event.key == pygame.K_c:
                    Controls.grow()
                if event.key == pygame.K_m:
                    Camera.change_mode()

        if pygame.key.get_pressed()[pygame.K_i]:
            Camera.move("up")
        if pygame.key.get_pressed()[pygame.K_k]:
            Camera.move("down")
        if pygame.key.get_pressed()[pygame.K_j]:
            Camera.move("left")
        if pygame.key.get_pressed()[pygame.K_l]:
            Camera.move("right")

    def start():
        Game.running = True

    def stop():
        Game.running = False

    def loop():

        Game.start()
        Game.spawn_stuff(10)

        while Game.running:

            Game.handle_events()
            Game.logic()

            pygame.Surface.fill(Game.screen, Game.colors['black'])
            Camera.draw()

            pygame.display.update()

            Game.FPS_clock.tick(Game.FPS)

    def remove_object(thing):  # routine to remove all object references
        Game.data.remove(thing)
        Camera.update_default()  # reverting to default, need to update
        Camera.target = Camera.default
        Controls.current = Controls.default

    def test_collision(one, two):  # return True or False if supplied targets collide

        dx = (one.x-two.x)
        dy = (one.y-two.y)
        combined_radius = one.radius + two.radius
        distance = math.sqrt(dx*dx + dy*dy)  # pythagorean theorem

        if distance < combined_radius:  # circles overlap and collide
            return True
        elif distance > combined_radius:  # circles do not overlap or collide
            return False

    def collision():  # revise this function later

        for first in Game.data:
            for second in Game.data:
                if first != second:  # dont collide with yourself
                    if Game.test_collision(first, second):  # if there is a collision
                         if first._id != 765 and second._id != 765:
                            # emit event (future revision)
                            if first.radius > second.radius:
                                first.devour(second)
                                Game.remove_object(second)
                                break
                            else:
                                second.devour(first)
                                Game.remove_object(first)
                                break

    def process_animations_per_frame():
        for animation in Animation._buffer:
            # zero guard
            # check if the following class attribute state update would result in negative number
            # consider creating a specific set attribute for each classes along with their specific guards
            # in order to not pollute this function code
            if animation[4] == True and getattr(animation[0], animation[1]) + animation[2] < 0:
                    setattr(animation[0], animation[1], 0.001) # 0.001 an adhoc default minimal value
            else:  # process animation in a standard way
                setattr(animation[0], animation[1], getattr(animation[0], animation[1])+animation[2])

            animation[3] -= 1  # count down a frame because it has been processed
            if animation[3] <= 0:
                Animation._buffer.remove(animation)

    def move():  # rework this later
        for thing in Game.data:
            if thing.dx != 0 or thing.dy != 0:
                thing.check_if_at_final_xy()
                thing.move()

    def grow():
        for thing in Game.data:
            thing.radius += 1

    def shrink():
        for thing in Game.data:
            thing.radius -= 1

    def spawn_object(x, y):
        Circle(999, x, y, Game.colors['red'], 2, 0)

    def spawn_stuff(amount):
        for x in range(1, amount):
            rnd = random.randint
            Circle(x, rnd(20, 580), rnd(20, 580), Game.colors['yellow'], rnd(5, 10), 1)

    def enemy_AI(target):
        for thing in Game.data:
            if thing._id != target._id:
                if thing.radius > target.radius:  # pursue
                    thing.set_new_dx_dy(target.x, target.y)
                elif thing.radius < target.radius:  # flee
                    # make the enemy run to the opposite direction from you (shortest path - line)
                    abs_x = target.x - thing.x
                    abs_y = target.y - thing.y
                    opposite_x = thing.x - abs_x
                    opposite_y = thing.y - abs_y
                    thing.set_new_dx_dy(opposite_x, opposite_y)

    def logic():
        Game.enemy_AI(Controls.current)
        Game.move()
        Game.process_animations_per_frame()
        Game.collision()


class Circle:

    def __init__(self, _id, x, y, color, radius, speed):
        self._id = _id
        self.x = x
        self.y = y
        self.dx = 0
        self.dy = 0
        self.color = color
        self.radius = radius
        self.speed = speed
        self.final_x = 0
        self.final_y = 0
        Game.data.append(self)  # consider making a Game function creating Circle objects instead of this

    def move(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed

    def accelerate(self, dx,dy):
        self.dx = dx
        self.dy = dy

    def set_speed(self, value):
        self.speed = value

    # these 4 methods are for turning/aiming/shooting/rotation - consider making them even simpler
    def calc_rads_angle(self, source_x, source_y, target_x, target_y):  # calculate the turn angle to target in radians (you just rotate, no movement)
        adjacent = source_x - target_x
        opposite = source_y - target_y
        arctan = math.atan2(opposite, adjacent)
        return arctan

    # code based on unit circle visualisation
    def calc_next_position(self, radians):  # use the rotation radians
        new_dx = -math.cos(radians)  # cos_of_x == x axis dx (times speed later on)
        new_dy = -math.sin(radians)  # sin_of_y == y axis dy (times speed later on)
        return [new_dx, new_dy]

    def get_new_dx_dy(self, target_x, target_y):
        return self.calc_next_position(self.calc_rads_angle(self.x, self.y, target_x, target_y))

    def set_new_dx_dy(self, target_x, target_y):
        [dx, dy] = self.get_new_dx_dy(target_x, target_y)
        self.dx = dx
        self.dy = dy

    def move_to_location(self, destination_x, destination_y):
        self.final_x = destination_x
        self.final_y = destination_y
        self.set_new_dx_dy(self.final_x, self.final_y)

    def stop(self):
        self.dx = 0
        self.dy = 0

    def check_if_at_final_xy(self):  # move to mouseclick location
        if self.x < self.final_x + 1 and self.x > self.final_x - 1:
            if self.y < self.final_y + 1 and self.y > self.final_y - 1:
                self.stop()

    # ACTIONS
    def devour(self, target):
        self.grow(target.radius)

    def grow(self, value):  # requires, animation
        Animation.create_animation(self, "radius", value, seconds=1)


class Animation:

    _buffer = []  # [animation_object, time]

    def create_animation(thing, attribute_to_change, value, seconds, below_zero_guard=False):  # side-effect sets/modifies _buffer (appends new animation)
        # if the below zero guard is set to True, the attribute will not ever go below zero
        total_frames = Game.FPS * seconds
        change_value_per_frame = value / total_frames
        new_animation = [thing, attribute_to_change, change_value_per_frame, total_frames, below_zero_guard]
        Animation._buffer.append(new_animation)

# static
class Camera:

    zoom = 1
    width = 600
    height = 600
    center = [width//2, height//2]  # center is hardcoded, consider rewriting for different camera modes
    mode = 0
    modes = None
    default = Circle(765, 100,300, Game.colors['white'], 2, 0) # the camera dummy object does not move since its speed is ZERO !!!!!
    target = default  # This reference gets handled by the Game.remove_object function

    def init_modes():
        Camera.modes = {0: [Camera.unlock, Camera.lock, Controls.switch_controls],
                        1: [Controls.switch_controls]}

    def change_mode():  # calls all functions based on the mode number
        Camera.mode = (Camera.mode + 1) % len(Camera.modes)  # cycler

    def mode_routine():  # calls all functions based on the mode number
        Camera.update_default()
        clicked_object = Camera.get_object_at_mouse_coords()
        for func in Camera.modes[Camera.mode]:  # all functions take one paramater - circle object (interface)
            func(clicked_object)

    def get_object_at_mouse_coords():
        realx, realy = Camera.mouse_coords()
        for thing in Game.data:
            if thing.x < realx + thing.radius and thing.x > realx - thing.radius:
                if thing.y < realy + thing.radius and thing.y > realy - thing.radius:
                    return thing
        else:
            return Camera.default

    def lock(target):
        Camera.target = target
        Camera.target.color = Game.colors['violet']

    def unlock(*args):  # parameter not needed, dummy
        Camera.target.color = Game.colors['yellow']
        Camera.target = Camera.default

    def update_default():  # update default camera object with the current locked object coordinates
        Camera.default.x = Camera.target.x
        Camera.default.y = Camera.target.y

    def move(direction):
        if direction == "left":
            Camera.target.x -= 20
        if direction == "right":
            Camera.target.x += 20
        if direction == "up":
            Camera.target.y -= 20
        if direction == "down":
            Camera.target.y += 20

    def set_zoom(magnitude):
        Animation.create_animation(Camera, "zoom", magnitude, seconds=3, below_zero_guard=True)

    def draw():

        for thing in Game.data:

            thing_dist_x = int( (Camera.target.x - thing.x) * Camera.zoom )  # calculate the distance between points and apply zoom if needed
            thing_dist_y = int( (Camera.target.y - thing.y) * Camera.zoom )  # calculate the real distance between points and apply zoom aswell

            thing_rel_x = int(Camera.center[0] - thing_dist_x)  # calculate how far from the relative center should the object be drawn
            thing_rel_y = int(Camera.center[1] - thing_dist_y)  # calculate how far from the relative center should the object be drawn
            thing_radius = int(thing.radius)

            thing_radius_zoomed = int(thing_radius * Camera.zoom)

            pygame.draw.circle(Game.screen, thing.color, (thing_rel_x, thing_rel_y), thing_radius_zoomed)
            Camera.draw_coords(thing, thing_rel_x, thing_rel_y, 20, Game.colors['red'])

    def draw_coords(thing, visual_x, visual_y, z, color):  # GUI visulation
        coords=Game.font.render(str(int(thing.x))+":"+str(int(thing.y)), 1, color)
        Game.screen.blit(coords, (visual_x, visual_y-z))

    def mouse_coords():  # mouse position is the opposite since you don't know the real mouse coordinates
        # you only get the relative mouse coordinates based on the pixels present in the window

        mousex, mousey = pygame.mouse.get_pos()

        mousex_from_centerx = int( (Camera.center[0] - mousex) // Camera.zoom )
        mousey_from_centery = int( (Camera.center[1] - mousey) // Camera.zoom )

        real_mousex = Camera.target.x - mousex_from_centerx
        real_mousey = Camera.target.y - mousey_from_centery

        return [real_mousex, real_mousey]


class Mouse:

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.radius = 1

# static
class Controls:

    default = Camera.default
    current = default  # This reference gets handled by the Game.remove_object function

    def acquire_current(thing):
        Controls.current = thing

    def switch_controls(target):
        Controls.acquire_current(target)

    def follow_mouse():  # Mouse Class - ONLY NEED IS HERE - consider refactoring
        mouse_object = Mouse(*Camera.mouse_coords())  # unpack a tuple argument of (x, y) and supply to the constructor
        # since you dont have to work with real coordinates, you can calculate the angle directly from the camera view
        if not Game.test_collision(Controls.current, mouse_object): # test if controlled object is in collision
            Controls.current.set_new_dx_dy(mouse_object.x, mouse_object.y)  # no collision (mouse is not above the object), follow mouse
        else:
            Controls.current.stop()  # collision - stop (mouse is above the object)

    def move_to_mouseclick():
        # as opposed to here because you need real coordinates to spawn an object AND to move the player there
        mousex, mousey = Camera.mouse_coords()
        Controls.current.move_to_location(mousex, mousey)
        Game.spawn_object(mousex, mousey)

    def quit():
        Game.stop()

    def left():
        Controls.current.accelerate(-1, 0)

    def right():
        Controls.current.accelerate(1, 0)

    def up():
        Controls.current.accelerate(0, -1)

    def down():
        Controls.current.accelerate(0, 1)

    def grow():
        Controls.current.grow(10)


if __name__ == '__main__':
    Game.init()
    Game.loop()
