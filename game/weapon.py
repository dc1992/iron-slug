# Weapon definitions.
# ammo=-1 means unlimited.
# max_range=0 means unlimited range; >0 = max px the bullet travels before dying.
# spread = max random vertical offset applied per bullet (0 = straight).

WEAPONS: dict[str, dict] = {
    'pistol': dict(
        label     = 'PISTOL',
        damage    = 10,
        cooldown  = 12,
        ammo      = -1,
        speed     = 12,
        color     = (255, 220,   0),
        max_range = 0,
        spread    = 0,
    ),
    'ak47': dict(
        label     = 'AK-47',
        damage    = 25,
        cooldown  = 7,
        ammo      = 30,
        speed     = 15,
        color     = (180, 220, 255),
        max_range = 0,
        spread    = 0,
    ),
    'flamethrower': dict(
        label     = 'FLAMER',
        damage    = 15,
        cooldown  = 4,
        ammo      = 60,
        speed     = 6,
        color     = (255, 100,  20),
        max_range = 120,
        spread    = 3,          # random vy ±3 per bullet
    ),
}
