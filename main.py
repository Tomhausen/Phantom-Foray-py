@namespace
class SpriteKind:
    melee = SpriteKind.create()
    xp = SpriteKind.create()

# setup
scene.set_tile_map_level(assets.tilemap("level"))

# sprites
witch = sprites.create(assets.image("witch"), SpriteKind.player)
controller.move_sprite(witch)
anim = assets.animation("walking")
characterAnimations.loop_frames(witch, anim, 100, characterAnimations.rule(Predicate.MOVING))
scene.camera_follow_sprite(witch)
melee_attack = sprites.create(image.create(16, 16), SpriteKind.melee)
melee_attack.scale = 2
# gh3
aura = sprites.create(image.create(16, 16), SpriteKind.melee)
sprites.set_data_number(aura, "angle", 0)
# /gh3

# bars
health_bar = statusbars.create(60, 4, StatusBarKind.Health)
health_bar.left = 0
health_bar.top = 0
xp_bar = statusbars.create(160, 4, StatusBarKind.magic)
xp_bar.bottom = 120
xp_bar.value = 0

# variables
last_vx = 100

# game properties
attack_damage = 20
cooldown = 2000
movement_speed = 100
enemy_health = 5
enemy_damage = 10
enemies_spawn = 2
magnet_active = False

# menu
menu_upgrades = [
    miniMenu.create_menu_item("hp"),
    miniMenu.create_menu_item("attack damage"),
    miniMenu.create_menu_item("cooldown"),
    miniMenu.create_menu_item("ranged attack"),
    miniMenu.create_menu_item("movement speed"),
    miniMenu.create_menu_item("damage range"),
# gh3
    miniMenu.create_menu_item("aura"),
# /gh3
# bh 3.1
    miniMenu.create_menu_item("dual attack")
# /bh 3.1
]

def remove_upgrade_from_list(item_text):
    for item in menu_upgrades:
        text = miniMenu.get_menu_item_property(item, MenuItemProperty.Text)
        if text == item_text:
            menu_upgrades.remove_element(item)

def open_level_up_menu():
    upgrades = []
    while len(upgrades) < 3:
        upgrade = menu_upgrades._pick_random()
        if upgrade in upgrades:
            continue
        upgrades.append(upgrade)
    upgrade_menu = miniMenu.createMenuFromArrayAndPauseGame(upgrades)
    upgrade_menu.set_flag(SpriteFlag.RELATIVE_TO_CAMERA, True)
    upgrade_menu.on_button_pressed(controller.A, select_upgrade)
# bh 2.1
    level_up_message = textsprite.create("LEVEL UP", 1, 15)
    level_up_message.set_max_font_height(10)
    level_up_message.set_position(80, 20)
    level_up_message.set_border(3, 1)
    effects.confetti.start_screen_effect()
# /bh 2.1

def select_upgrade(selection, selectionIndex):
    global attack_damage, cooldown, movement_speed
    if selection == "attack damage":
        attack_damage += 10
    elif selection == "hp":
        health_bar.max += 10
        health_bar.value += 10
    elif selection == "cooldown":
        cooldown *= 0.95
        cooldown = Math.constrain(cooldown, 500, 5000)
    elif selection == "ranged attack":
        remove_upgrade_from_list("ranged attack")
        ranged_attack_loop()
    elif selection == "movement speed":
        movement_speed += 10
        controller.move_sprite(witch, movement_speed, movement_speed)
    elif selection == "damage range":
        melee_attack.scale += 0.2
# gh3
    elif selection == "aura":
        remove_upgrade_from_list("aura")
        aura.set_image(assets.image("aura"))
# /gh3
# bh 3.2
    elif selection == "dual attack":
        remove_upgrade_from_list("dual attack")
# /bh 3.2
    sprites.all_of_kind(SpriteKind.mini_menu)[0].destroy()
# bh 2.2
    sprites.all_of_kind(SpriteKind.text)[0].destroy()
    effects.confetti.end_screen_effect()
# /bh 2.2

def make_damage_number(damage: number, damaged_sprite: Sprite):
    number_sprite = textsprite.create(str(damage), 0, 15)
    number_sprite.set_position(damaged_sprite.x, damaged_sprite.y)
    number_sprite.vy = -5
    number_sprite.lifespan = 1500

def turn_off_magnet():
    global magnet_active
    magnet_active = False

def spawn_xp(source: Sprite):
    global magnet_active
    if randint(1, 10) == 1:
        magnet_active = True
        witch.start_effect(effects.halo, 5000)
        timer.after(5000, turn_off_magnet)
    xp = sprites.create(assets.image("jewel"), SpriteKind.xp)
    xp.set_position(source.x, source.y)
    xp.x += randint(-10, 10)
    xp.y += randint(-10, 10)
    xp.scale = 0.75
    xp.lifespan = 10000

def damage_enemy(enemy, proj):
    damage = randint(attack_damage * 0.75, attack_damage * 1.25) // 1
    sprites.change_data_number_by(enemy, "hp", -damage)
    make_damage_number(damage, enemy)
    if sprites.read_data_number(enemy, "hp") < 1:
        enemy.destroy()
        info.change_score_by(100)
        spawn_xp(enemy)
# bh 1.1
        if randint(1, 10) == 1:
            heart = sprites.create(assets.image("heart"), SpriteKind.food)
            heart.set_position(enemy.x, enemy.y)
# /bh 1.1
    pause(500)
sprites.on_overlap(SpriteKind.enemy, SpriteKind.melee, damage_enemy)

# bh 1.2
def collect_heart(player, heart):
    health_bar.value += health_bar.max / 2
    heart.destroy()
sprites.on_overlap(SpriteKind.player, SpriteKind.food, collect_heart)
# /bh 1.2

def collect_xp(player, xp):
    xp_bar.value += 10
    if xp_bar.value == 100:
        xp_bar.value = 0
        open_level_up_menu()
    xp.destroy()
sprites.on_overlap(SpriteKind.player, SpriteKind.xp, collect_xp)

def proj_hit_enemy(enemy, proj):
    proj.destroy()
    damage_enemy(enemy, proj)
sprites.on_overlap(SpriteKind.enemy, SpriteKind.projectile, proj_hit_enemy)

def damage_player(player, enemy):
    health_bar.value -= 10
    if health_bar.value < 1:
        game.over(False)
    pause(500)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy, damage_player)

def ranged_attack_loop():
    proj = sprites.create(assets.image("proj"), SpriteKind.projectile)
    proj.set_position(witch.x, witch.y)
    proj.lifespan = 5000
    enemies = sprites.all_of_kind(SpriteKind.enemy)
    target = spriteutils.sort_list_of_sprites_by_distance_from(witch, enemies)[0]
    angle = spriteutils.angle_from(witch, target)
    spriteutils.set_velocity_at_angle(proj, angle, 200)
    timer.after(cooldown, ranged_attack_loop)

# bh 3.3
def dual_attack_loop():
    animation.run_image_animation(melee_attack, assets.animation("fireball both"), 100, False)
    timer.after(cooldown, dual_attack_loop)
# /bh 3.3

def base_attack_loop():
#bh 3.4
    for item in menu_upgrades:
        text = miniMenu.get_menu_item_property(item, MenuItemProperty.Text)
        if text == "dual attack":
            timer.after(cooldown, dual_attack_loop)
            return
# /bh 3.4
    if last_vx > 0:
        animation.run_image_animation(melee_attack, assets.animation("fireball right"), 100, False)
    else:
        animation.run_image_animation(melee_attack, assets.animation("fireball left"), 100, False)
    timer.after(cooldown, base_attack_loop)
timer.after(cooldown, base_attack_loop)

def difficulty_curve():
    global enemy_health, enemy_damage, enemies_spawn
    enemy_health += 10
    enemy_damage += 10
    enemies_spawn += 1
game.on_update_interval(20000, difficulty_curve)

def spawn_loop():
    if len(sprites.all_of_kind(SpriteKind.enemy)) < 50:
        for i in range(enemies_spawn):
            enemy = sprites.create(assets.image("ghost"), SpriteKind.enemy)
            tilesAdvanced.place_on_random_tile_off_screen(enemy, assets.tile("dirt"))
            enemy.follow(witch, 20, 50)
            sprites.set_data_number(enemy, "hp", randint(enemy_health * 0.75, enemy_health * 1.25))
game.on_update_interval(1000, spawn_loop)

def ghost_direction():
    for ghost in sprites.all_of_kind(SpriteKind.enemy):
        if ghost.vx > 0:
            ghost.set_image(assets.image("ghost right"))
        else:
            ghost.set_image(assets.image("ghost left"))

def pull_in_xp():
    for xp in sprites.all_of_kind(SpriteKind.xp):
        if spriteutils.distance_between(xp, witch) < 100 and magnet_active:
            xp.follow(witch, 200)

# gh3
def aura_turn():
    sprites.change_data_number_by(aura, "angle", 5)
    angle = sprites.read_data_number(aura, "angle")
    angle = spriteutils.degrees_to_radians(angle)
    spriteutils.place_angle_from(aura, angle, 20, witch)
# /gh3 

def tick():
    global last_vx
    if Math.abs(witch.vx) != 0:
        last_vx = witch.vx
    melee_attack.set_position(witch.x, witch.y)
    ghost_direction()
    pull_in_xp()
# gh3
    aura_turn()
# /gh3
game.on_update(tick)
