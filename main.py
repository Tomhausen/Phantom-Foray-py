@namespace
class SpriteKind:
    melee = SpriteKind.create()

# setup
scene.set_tile_map_level(assets.tilemap("level"))

# sprites
witch = sprites.create(assets.image("witch"), SpriteKind.player)
controller.move_sprite(witch)
scene.camera_follow_sprite(witch)
melee_attack = sprites.create(image.create(16, 16), SpriteKind.melee)
melee_attack.scale = 2

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
attack_damage = 10
cooldown = 2000
enemy_health = 5
enemy_damage = 10
enemies_spawn = 2

# menu
menu_upgrades = [
    miniMenu.create_menu_item("hp"), 
    miniMenu.create_menu_item("attack damage"),
    miniMenu.create_menu_item("cooldown"),
]

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

def select_upgrade(selection, selectionIndex):
    global attack_damage, cooldown
    if selection == "attack damage":
        attack_damage += 10
    elif selection == "hp":
        health_bar.max += 10
        health_bar.value += 10
    elif selection == "cooldown":
        cooldown *= 0.95
        cooldown = Math.constrain(cooldown, 500, 5000)
    sprites.all_of_kind(SpriteKind.mini_menu)[0].destroy()

def damage_enemy(enemy, proj):
    damage = randint(attack_damage * 0.75, attack_damage * 1.25) // 1
    sprites.change_data_number_by(enemy, "hp", -damage)
    if sprites.read_data_number(enemy, "hp") < 1:
        enemy.destroy()
        info.change_score_by(100)
        xp_bar.value += 10
        if xp_bar.value == 100:
            xp_bar.value = 0
            open_level_up_menu()
sprites.on_overlap(SpriteKind.enemy, SpriteKind.melee, damage_enemy)

def damage_player(player, enemy):
    health_bar.value -= 10
    if health_bar.value < 1:
        game.over(False)
    pause(500)
sprites.on_overlap(SpriteKind.player, SpriteKind.enemy, damage_player)

def base_attack_loop():
    if last_vx > 0:
        animation.run_image_animation(melee_attack, assets.animation("fireball right"), 100, False)
    else:
        animation.run_image_animation(melee_attack, assets.animation("fireball left"), 100, False)
    timer.after(cooldown, base_attack_loop)
timer.after(cooldown, base_attack_loop)

def spawn_loop():
    if len(sprites.all_of_kind(SpriteKind.enemy)) < 50:
        for i in range(enemies_spawn):
            enemy = sprites.create(assets.image("ghost"), SpriteKind.enemy)
            tilesAdvanced.place_on_random_tile_off_screen(enemy, assets.tile("dirt"))
            enemy.follow(witch, 20, 50)
            sprites.set_data_number(enemy, "hp", randint(enemy_health * 0.75, enemy_health * 1.25))
game.on_update_interval(1000, spawn_loop)

def tick():
    global last_vx
    if Math.abs(witch.vx) != 0:
        last_vx = witch.vx
    melee_attack.set_position(witch.x, witch.y)
game.on_update(tick)
