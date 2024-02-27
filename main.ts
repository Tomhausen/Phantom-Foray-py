namespace SpriteKind {
    export const melee = SpriteKind.create()
}

//  setup
scene.setTileMapLevel(assets.tilemap`level`)
//  sprites
let witch = sprites.create(assets.image`witch`, SpriteKind.Player)
controller.moveSprite(witch)
scene.cameraFollowSprite(witch)
let melee_attack = sprites.create(image.create(16, 16), SpriteKind.melee)
melee_attack.scale = 2
//  bars
let health_bar = statusbars.create(60, 4, StatusBarKind.Health)
health_bar.left = 0
health_bar.top = 0
let xp_bar = statusbars.create(160, 4, StatusBarKind.Magic)
xp_bar.bottom = 120
xp_bar.value = 0
//  variables
let last_vx = 100
//  game properties
let attack_damage = 10
let cooldown = 2000
//  b1.1
let movement_speed = 100
//  /b1.1
let enemy_health = 5
let enemy_damage = 10
let enemies_spawn = 2
//  menu
let menu_upgrades = [miniMenu.createMenuItem("hp"), miniMenu.createMenuItem("attack damage"), miniMenu.createMenuItem("cooldown"), miniMenu.createMenuItem("ranged attack"), miniMenu.createMenuItem("movement speed")]
//  gh1
//  /gh1
//  b1.1
//  /b1.1
//  gh1
function remove_upgrade_from_list(item_text: string) {
    let text: any;
    for (let item of menu_upgrades) {
        text = miniMenu.getMenuItemProperty(item, MenuItemProperty.Text)
        if (text == item_text) {
            menu_upgrades.removeElement(item)
        }
        
    }
}

//  /gh1
function open_level_up_menu() {
    let upgrade: miniMenu.MenuItem;
    let upgrades = []
    while (upgrades.length < 3) {
        upgrade = menu_upgrades._pickRandom()
        if (upgrades.indexOf(upgrade) >= 0) {
            continue
        }
        
        upgrades.push(upgrade)
    }
    let upgrade_menu = miniMenu.createMenuFromArrayAndPauseGame(upgrades)
    upgrade_menu.setFlag(SpriteFlag.RelativeToCamera, true)
    upgrade_menu.onButtonPressed(controller.A, function select_upgrade(selection: string, selectionIndex: number) {
        
        //  b 1.2
        if (selection == "attack damage") {
            attack_damage += 10
        } else if (selection == "hp") {
            health_bar.max += 10
            health_bar.value += 10
        } else if (selection == "cooldown") {
            cooldown *= 0.95
            cooldown = Math.constrain(cooldown, 500, 5000)
        } else if (selection == "ranged attack") {
            //  gh1
            remove_upgrade_from_list("ranged attack")
            ranged_attack_loop()
        } else if (selection == "movement speed") {
            //  /gh1
            //  b1.1
            movement_speed += 10
            controller.moveSprite(witch, movement_speed, movement_speed)
        }
        
        //  /b1.1
        sprites.allOfKind(SpriteKind.MiniMenu)[0].destroy()
    })
}

//  b1.2
function make_damage_number(damage: number, damaged_sprite: Sprite) {
    let number_sprite = textsprite.create("" + damage, 0, 15)
    number_sprite.setPosition(damaged_sprite.x, damaged_sprite.y)
    number_sprite.vy = -5
    pause(1500)
    number_sprite.destroy()
}

//  /b1.2
function damage_enemy(enemy: Sprite, proj: Sprite) {
    let damage = Math.idiv(randint(attack_damage * 0.75, attack_damage * 1.25), 1)
    sprites.changeDataNumberBy(enemy, "hp", -damage)
    //  b1.2
    make_damage_number(damage, enemy)
    //  /b1.2
    if (sprites.readDataNumber(enemy, "hp") < 1) {
        enemy.destroy()
        info.changeScoreBy(100)
        xp_bar.value += 10
        if (xp_bar.value == 100) {
            xp_bar.value = 0
            open_level_up_menu()
        }
        
    }
    
}

sprites.onOverlap(SpriteKind.Enemy, SpriteKind.melee, damage_enemy)
//  gh1
sprites.onOverlap(SpriteKind.Enemy, SpriteKind.Projectile, function proj_hit_enemy(enemy: Sprite, proj: Sprite) {
    damage_enemy(enemy, proj)
    proj.destroy()
})
//  /gh1
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, function damage_player(player: Sprite, enemy: Sprite) {
    health_bar.value -= 10
    if (health_bar.value < 1) {
        game.over(false)
    }
    
    pause(500)
})
//  gh1
function ranged_attack_loop() {
    let proj = sprites.create(assets.image`proj`, SpriteKind.Projectile)
    proj.setPosition(witch.x, witch.y)
    proj.lifespan = 5000
    let enemies = sprites.allOfKind(SpriteKind.Enemy)
    let target = spriteutils.sortListOfSpritesByDistanceFrom(witch, enemies)[0]
    let angle = spriteutils.angleFrom(witch, target)
    spriteutils.setVelocityAtAngle(proj, angle, 200)
    timer.after(cooldown, ranged_attack_loop)
}

//  /gh1
function base_attack_loop() {
    if (last_vx > 0) {
        animation.runImageAnimation(melee_attack, assets.animation`fireball right`, 100, false)
    } else {
        animation.runImageAnimation(melee_attack, assets.animation`fireball left`, 100, false)
    }
    
    timer.after(cooldown, base_attack_loop)
}

timer.after(cooldown, base_attack_loop)
//  b1.3
game.onUpdateInterval(20000, function difficulty_curve() {
    
    enemy_health += 10
    enemy_damage += 10
    enemies_spawn += 1
})
//  /b1.3
game.onUpdateInterval(1000, function spawn_loop() {
    let enemy: Sprite;
    if (sprites.allOfKind(SpriteKind.Enemy).length < 50) {
        for (let i = 0; i < enemies_spawn; i++) {
            enemy = sprites.create(assets.image`ghost`, SpriteKind.Enemy)
            tilesAdvanced.placeOnRandomTileOffScreen(enemy, assets.tile`dirt`)
            enemy.follow(witch, 20, 50)
            sprites.setDataNumber(enemy, "hp", randint(enemy_health * 0.75, enemy_health * 1.25))
        }
    }
    
})
game.onUpdate(function tick() {
    
    if (Math.abs(witch.vx) != 0) {
        last_vx = witch.vx
    }
    
    melee_attack.setPosition(witch.x, witch.y)
})
