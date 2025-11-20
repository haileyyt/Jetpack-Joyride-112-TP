def checkBossCollision(app):
    character = (
        app.char.x, 
        app.char.y, 
        app.char.width,
        app.char.height
        )
    if app.boss.state == 'laserAttack' and app.laser.lasers != None:
        x0, y0, x1, y1 = app.laser.lasers
        if lineHitsCharLaser((x0, y0, x1, y1), character):
            return True

    if app.boss.state == 'lightningAttack' and app.lightning.segments != []:
        for segment in app.lightning.segments:
            if lineHitsCharLightning(segment, character):
                return True

    if app.boss.state == 'chargeAttack':
        bossHitBox = (
            app.boss.cx - app.boss.width / 2,
            app.boss.cy - app.boss.height / 2 + 60,
            app.boss.width,
            app.boss.height-60
            )
        if rectsOverlap(character, bossHitBox):
            return True
    return False

def rectsOverlap(r1, r2):
    cx1, cy1, width1, height1 = r1
    cx2, cy2, width2, height2 = r2
    return (cx1 < cx2 + width2 and cx1 + width1 > cx2 and
            cy1 < cy2 + height2 and cy1 + height1 > cy2)

#referenced this website to figure out projections for line circle collision
#https://www.jeffreythompson.org/collision-detection/line-circle.php

def lineHitsCharLaser(line, hitBox):
    x0, y0, x1, y1 = line
    cx, cy, width, height = hitBox
    centerx = cx + width / 2
    centery = cy + height / 2
    dx = x1 - x0
    dy = y1 - y0
    if dx == dy == 0:
        return False
    t = ((centerx - x0) * dx + (centery - y0) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    closestX = x0 + t * dx
    closestY = y0 + t * dy
    distSq = (closestX - centerx)**2 + (closestY - centery)**2
    beamWidth = 25
    radius = height / 2
    effectiveRadius = radius + beamWidth/2
    return distSq <= effectiveRadius**2

def lineHitsCharLightning(line, hitBox):
    x0, y0, x1, y1 = line
    cx, cy, width, height = hitBox
    centerx = cx + width / 2
    centery = cy + height / 2
    dx = x1 - x0
    dy = y1 - y0
    if dx == dy == 0:
        return False
    t = ((centerx - x0) * dx + (centery - y0) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))
    closestX = x0 + t * dx
    closestY = y0 + t * dy
    distSq = (closestX - centerx)**2 + (closestY - centery)**2
    beamWidth = 10
    radius = height/2
    effectiveRadius = radius + beamWidth/2
    return distSq <= effectiveRadius**2
