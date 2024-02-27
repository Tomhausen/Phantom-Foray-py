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
let enemy_health = 5
let enemy_damage = 10
let enemies_spawn = 2
//  menu
let menu_upgrades = [miniMenu.createMenuItem("hp"), miniMenu.createMenuItem("attack damage"), miniMenu.createMenuItem("cooldown")]
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
        
        if (selection == "attack damage") {
            attack_damage += 10
        } else if (selection == "hp") {
            health_bar.max += 10
            health_bar.value += 10
        } else if (selection == "cooldown") {
            cooldown *= 0.95
            cooldown = Math.constrain(cooldown, 500, 5000)
        }
        
        sprites.allOfKind(SpriteKind.MiniMenu)[0].destroy()
    })
}

sprites.onOverlap(SpriteKind.Enemy, SpriteKind.melee, function damage_enemy(enemy: Sprite, proj: Sprite) {
    let damage = Math.idiv(randint(attack_damage * 0.75, attack_damage * 1.25), 1)
    sprites.changeDataNumberBy(enemy, "hp", -damage)
    if (sprites.readDataNumber(enemy, "hp") < 1) {
        enemy.destroy()
        info.changeScoreBy(100)
        xp_bar.value += 10
        if (xp_bar.value == 100) {
            xp_bar.value = 0
            open_level_up_menu()
        }
        
    }
    
})
sprites.onOverlap(SpriteKind.Player, SpriteKind.Enemy, function damage_player(player: Sprite, enemy: Sprite) {
    health_bar.value -= 10
    if (health_bar.value < 1) {
        game.over(false)
    }
    
    pause(500)
})
function base_attack_loop() {
    if (last_vx > 0) {
        animation.runImageAnimation(melee_attack, assets.animation`fireball right`, 100, false)
    } else {
        animation.runImageAnimation(melee_attack, assets.animation`fireball left`, 100, false)
    }
    
    timer.after(cooldown, base_attack_loop)
}

timer.after(cooldown, base_attack_loop)
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
