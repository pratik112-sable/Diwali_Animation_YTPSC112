"""DIWALI • Festival of Light
Install: python -m pip install pygame
Run:     python diwali_animation_ultimate.py
Optional: python diwali_animation_ultimate.py --name "Your Name" --quality high
All artwork is generated in code. No images, fonts or audio downloads required.
"""
import argparse
import math
import random
import time
from pathlib import Path
import pygame

W, H = 1280, 800
TAU = math.tau
GOLD = (255, 199, 104)
PALETTE = [(255, 185, 70), (255, 91, 145), (94, 220, 255),
           (192, 125, 255), (112, 255, 191), (255, 235, 170)]

def clamp(x, a=0, b=1):
    return max(a, min(b, x))

def blend(a, b, t):
    return tuple(int(x + (y-x)*clamp(t)) for x, y in zip(a, b))

def polar(x, y, r, a):
    return (x + math.cos(a)*r, y + math.sin(a)*r)

def ip(p):
    return tuple(round(v) for v in p)

def text(surface, font, message, color, pos, center=True):
    img = font.render(message, True, color)
    rect = img.get_rect(center=ip(pos)) if center else img.get_rect(topleft=ip(pos))
    surface.blit(img, rect)
    return rect

class Studio:
    def __init__(self, name='', quality='high'):
        pygame.init()
        pygame.display.set_caption('DIWALI | Festival of Light')
        self.window = pygame.display.set_mode((W, H), pygame.RESIZABLE)
        self.scene = pygame.Surface((W, H))
        self.light = pygame.Surface((W, H))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont('georgia,dejavuserif', 100, bold=True)
        self.serif = pygame.font.SysFont('georgia,dejavuserif', 25)
        self.small = pygame.font.SysFont('verdana,dejavusans', 14)
        self.tiny = pygame.font.SysFont('verdana,dejavusans', 11)
        self.name = name.strip()[:42]
        self.high = quality == 'high'
        self.cap = 1800 if self.high else 700
        self.glows = {}
        self.stars = [(random.uniform(35,W-35), random.uniform(55,510),
                       random.uniform(.7,2), random.random()*TAU) for _ in range(125)]
        self.lanterns = [(random.uniform(0,W), random.uniform(150,650),
                          random.uniform(.35,.85), random.random()*TAU) for _ in range(12)]
        self.particles, self.rockets = [], []
        self.t = 0
        self.paused = False
        self.auto = True
        self.fullscreen = False
        self.help = True
        self.running = True
        self.next_launch = .4
        self.finale_until = 0
        self.toast = ''
        self.toast_until = 0
        self.viewport = pygame.Rect(0,0,W,H)
        self.background = self.build_background()
        self.rangoli = self.build_rangoli()

    def glow(self, pos, radius, color, strength=1):
        radius = max(2, int(radius))
        key = (radius, color)
        if key not in self.glows:
            surf = pygame.Surface((radius*2+2, radius*2+2))
            for r in range(radius, 0, -2):
                falloff = (1-r/radius)**2
                c = tuple(int(v*falloff*.65) for v in color)
                pygame.draw.circle(surf, c, (radius+1,radius+1), r)
            self.glows[key] = surf
        image = self.glows[key]
        if strength < .98:
            image = image.copy()
            image.fill((int(255*clamp(strength)),)*3, special_flags=pygame.BLEND_RGB_MULT)
        self.light.blit(image, (int(pos[0]-radius-1), int(pos[1]-radius-1)),
                        special_flags=pygame.BLEND_RGB_ADD)

    def build_background(self):
        s = pygame.Surface((W,H))
        for y in range(H):
            c = blend((5,8,27), (32,12,43), y/H)
            if y>560:
                c = blend(c, (12,9,24), (y-560)/240)
            pygame.draw.line(s,c,(0,y),(W,y))
        rng = random.Random(41)
        for x in range(-10,W,30):
            h = rng.randint(20,95)
            pygame.draw.rect(s,(13,14,34),(x,564-h,32,h))
            if rng.random()<.35:
                pygame.draw.polygon(s,(13,14,34),[(x-3,564-h),(x+16,540-h),(x+35,564-h)])
            for wy in range(574-h,550,15):
                if rng.random()<.4:
                    pygame.draw.rect(s,(77,49,46),(x+10,wy,3,5))
        pygame.draw.line(s,(90,53,54),(0,565),(W,565))
        pygame.draw.rect(s,(94,66,65),(23,23,W-46,H-46),1,border_radius=12)
        pygame.draw.rect(s,(48,37,55),(30,30,W-60,H-60),1,border_radius=9)
        for x,sign in [(45,1),(W-45,-1)]:
            for y,sy in [(45,1),(H-45,-1)]:
                pygame.draw.lines(s,GOLD,False,[(x,y+28*sy),(x,y),(x+28*sign,y)],2)
                pygame.draw.circle(s,GOLD,(x+9*sign,y+9*sy),2)
        return s

    def build_rangoli(self):
        s = pygame.Surface((440,440),pygame.SRCALPHA)
        cx=cy=220
        for radius, n, color, offset in [(186,24,(242,146,65),0),
                (151,16,(229,68,126),.1),(110,16,(248,188,75),0),
                (72,12,(106,214,203),.2),(38,8,(255,218,145),0)]:
            for j in range(n):
                a=j*TAU/n+offset
                pts=[]
                for k in range(41):
                    u=k/40
                    r=radius*(.28+.72*math.sin(math.pi*u))
                    angle=a+(u-.5)*TAU/n*.88
                    pts.append(ip(polar(cx,cy,r,angle)))
                pygame.draw.polygon(s,(*color,175),pts)
                pygame.draw.lines(s,(*GOLD,220),True,pts,1)
            pygame.draw.circle(s,(*color,180),(cx,cy),radius,1)
        for j in range(64):
            a=j*TAU/64
            pygame.draw.circle(s,(*GOLD,220),ip(polar(cx,cy,201,a)),2 if j%2 else 3)
        pygame.draw.circle(s,(255,218,145),(cx,cy),12)
        pygame.draw.circle(s,(220,74,124),(cx,cy),7)
        return s

    def launch(self, target=None):
        # Launch from near the bottom and keep the flight mostly vertical,
        # with a little sideways drift so the sky fills naturally.
        start_x = random.uniform(105, W-105)
        if target is None:
            target_x = clamp(start_x + random.uniform(-115, 115), 90, W-90)
            target = (target_x, random.uniform(105, 420))
        self.rockets.append([start_x, H-112, target[0], target[1],
                             random.choice(PALETTE),
                             random.choice(['peony', 'ring', 'willow', 'heart'])])

    def explode(self,x,y,color,kind):
        count = (95 if self.high else 48)
        for i in range(count):
            a=TAU*i/count+random.uniform(-.025,.025)
            speed=random.uniform(95,210)
            if kind=='ring':
                speed=random.uniform(175,190)
            vx,vy=math.cos(a)*speed,math.sin(a)*speed
            if kind=='heart':
                vx=12*16*math.sin(a)**3
                vy=-12*(13*math.cos(a)-5*math.cos(2*a)-2*math.cos(3*a)-math.cos(4*a))
            life=random.uniform(1.1,2.1) if kind!='willow' else random.uniform(2,3.2)
            self.particles.append([x,y,vx,vy,life,life,color,kind=='willow'])
        self.particles=self.particles[-self.cap:]

    def update(self, dt):
        self.t+=dt
        if self.auto and self.t>=4.8 and self.t>=self.next_launch:
            self.launch()
            # Frequent but staggered launches create a continuous fireworks show.
            self.next_launch=self.t+random.uniform(.32,.62)
        if self.t<self.finale_until and random.random()<dt*13:
            self.launch()
        for r in self.rockets[:]:
            dx,dy=r[2]-r[0],r[3]-r[1]
            dist=math.hypot(dx,dy)
            speed=520
            if dist<speed*dt:
                self.explode(r[2],r[3],r[4],r[5])
                self.rockets.remove(r)
            else:
                r[0]+=dx/dist*speed*dt
                r[1]+=dy/dist*speed*dt
                # Short-lived sparks fall behind the rising rocket as a bright trail.
                trail_life=random.uniform(.22,.42)
                self.particles.append([r[0], r[1], random.uniform(-20,20),
                                       random.uniform(35,85), trail_life, trail_life,
                                       r[4], False])
        for p in self.particles:
            p[0]+=p[2]*dt
            p[1]+=p[3]*dt
            drag=math.exp(-(1.0 if p[7] else .48)*dt)
            p[2]*=drag
            p[3]=p[3]*drag+(38 if p[7] else 65)*dt
            p[4]-=dt
        self.particles=[p for p in self.particles if p[4]>0][-self.cap:]

    def draw_lights(self):
        for segment in range(4):
            x0=45+segment*(W-90)/4
            width=(W-90)/4
            points=[(x0+u*width,52+43*math.sin(math.pi*u)) for u in [i/40 for i in range(41)]]
            pygame.draw.lines(self.scene,(98,73,71),False,points,2)
            for j in range(7):
                u=(j+.5)/7
                x,y=x0+u*width,52+43*math.sin(math.pi*u)
                col=PALETTE[(segment*7+j)%len(PALETTE)]
                pulse=.65+.35*math.sin(self.t*2.2+j*.7+segment)
                pygame.draw.line(self.scene,(138,101,72),(x,y),(x,y+9),2)
                self.glow((x,y+14),26,col,pulse)
                pygame.draw.ellipse(self.scene,blend((70,40,40),col,pulse),(x-4,y+8,8,12))
                pygame.draw.circle(self.scene,(255,246,213),ip((x-1,y+11)),1)

    def draw_lanterns(self):
        for x,y,scale,phase in self.lanterns:
            yy=135+(y-self.t*14*scale-135)%440
            xx=x+math.sin(self.t*.6+phase)*15
            width,height=22*scale,33*scale
            self.glow((xx,yy),32,(255,123,45),.65)
            pts=[(xx-width/2,yy-height/2),(xx+width/2,yy-height/2),
                 (xx+width*.38,yy+height/2),(xx-width*.38,yy+height/2)]
            pygame.draw.polygon(self.scene,(156,74,45),pts)
            pygame.draw.lines(self.scene,(248,171,82),True,pts,1)
            pygame.draw.line(self.scene,(221,131,65),(xx,yy-height/2),(xx,yy+height/2))
            pygame.draw.ellipse(self.scene,(255,218,117),(xx-3,yy+height*.2,6,6))

    def draw_diya(self,x,y,scale,phase):
        flicker=math.sin(self.t*9+phase)*.07+math.sin(self.t*17+phase)*.03
        self.glow((x,y-24*scale),int(88*scale),(255,119,35),.85+flicker)
        self.glow((x,y+20*scale),int(65*scale),(186,66,25),.45)
        bowl=[(x-37*scale,y),(x+37*scale,y),(x+26*scale,y+24*scale),
              (x,y+32*scale),(x-26*scale,y+24*scale)]
        pygame.draw.polygon(self.scene,(130,46,38),bowl)
        pygame.draw.lines(self.scene,(226,133,62),False,bowl[1:],2)
        pygame.draw.ellipse(self.scene,(242,170,67),(x-37*scale,y-6*scale,74*scale,12*scale))
        pygame.draw.ellipse(self.scene,(83,36,38),(x-29*scale,y-3*scale,58*scale,7*scale))
        for j in range(5):
            pygame.draw.circle(self.scene,GOLD,ip((x+(j-2)*10*scale,y+(18-abs(j-2)*2)*scale)),max(1,int(2*scale)))
        pygame.draw.line(self.scene,(56,27,30),(x,y),(x+2,y-10*scale),3)
        sway=math.sin(self.t*5+phase)*4*scale
        for width,height,color in [(11,46,(255,115,29)),(7,34,(255,196,64)),(3.5,22,(255,247,194))]:
            pts=[]
            for i in range(25):
                u=i/24
                xx=width*scale*math.sin(math.pi*u)**.8
                yy=y-5*scale-u*height*scale*(1+flicker)
                pts.append((x+xx+sway*u*u,yy))
            for i in range(24,-1,-1):
                u=i/24
                pts.append((x-width*scale*math.sin(math.pi*u)**.8+sway*u*u,
                            y-5*scale-u*height*scale*(1+flicker)))
            pygame.draw.polygon(self.scene,color,pts)

    @staticmethod
    def ease_reveal(value):
        value = clamp(value)
        return value * value * (3 - 2 * value)

    def reveal(self, start, duration=1.2):
        return self.ease_reveal((self.t - start) / duration)

    def draw_layer(self, callback, alpha):
        """Render one scene layer separately so it can fade in smoothly."""
        if alpha <= 0:
            return
        original_scene, original_light = self.scene, self.light
        layer = pygame.Surface((W, H), pygame.SRCALPHA)
        glow_layer = pygame.Surface((W, H), pygame.SRCALPHA)
        self.scene, self.light = layer, glow_layer
        try:
            callback()
        finally:
            self.scene, self.light = original_scene, original_light
        layer.blit(glow_layer, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        layer.set_alpha(int(255 * clamp(alpha)))
        original_scene.blit(layer, (0, 0))

    def draw(self):
        self.scene.blit(self.background, (0, 0))
        self.light.fill((0, 0, 0))

        def stars():
            for x, y, r, phase in self.stars:
                bright = .35 + .65 * (.5 + .5 * math.sin(self.t * 1.4 + phase))
                pygame.draw.circle(self.scene, blend((35, 32, 61), (233, 227, 208), bright),
                                   ip((x, y)), max(1, int(r)))
                if r > 1.7:
                    self.glow((x, y), 10, (125, 151, 211), bright * .5)

        def festive_lights():
            self.draw_lights()

        def lanterns():
            self.draw_lanterns()

        def fireworks():
            for rocket in self.rockets:
                # Bright rocket head and a small flame glow beneath it.
                self.glow(rocket[:2], 25, rocket[4], .95)
                self.glow((rocket[0], rocket[1] + 10), 12, (255, 157, 65), .9)
                pygame.draw.line(self.scene, rocket[4], ip(rocket[:2]),
                                 ip((rocket[0], rocket[1] + 19)), 3)
                pygame.draw.circle(self.scene, (255, 250, 224), ip(rocket[:2]), 3)
            for particle in self.particles:
                fade = clamp(particle[4] / min(.8, particle[5]))
                color = blend((0, 0, 0), particle[6], fade)
                tail = (particle[0] - particle[2] * .026,
                        particle[1] - particle[3] * .026)
                pygame.draw.line(self.light, color, ip(tail), ip(particle[:2]), 2)
                if self.high and particle[4] > .6 and int(particle[0] + particle[1]) % 7 == 0:
                    self.glow(particle[:2], 12, particle[6], fade * .65)

        def floor_decor():
            self.glow((W / 2, 650), 210, (95, 35, 30), .6)
            size = 1 + .008 * math.sin(self.t * 1.2)
            mandala = pygame.transform.smoothscale(
                self.rangoli, (int(440 * size), int(440 * size * .43)))
            self.scene.blit(mandala, mandala.get_rect(center=(640, 658)))

        def diyas():
            positions = [(110, 675, .9), (250, 702, 1), (390, 726, .85),
                         (890, 726, .85), (1030, 702, 1), (1170, 675, .9)]
            for i, (x, y, scale) in enumerate(positions):
                self.draw_diya(x, y, scale, i * 1.7)
            self.draw_diya(640, 677, 1.18, 4)

        def heading():
            text(self.scene, self.small, 'T H E   F E S T I V A L   O F   L I G H T S',
                 GOLD, (640, 188))

        def title():
            text(self.scene, self.font, 'Happy Diwali', (35, 15, 35), (643, 286))
            text(self.scene, self.font, 'Happy Diwali',
                 blend(GOLD, (255, 235, 178), .5 + .5 * math.sin(self.t)), (640, 280))

        def message():
            text(self.scene, self.serif, 'May your world shine a little brighter.',
                 (224, 204, 190), (640, 360))
            pygame.draw.line(self.scene, (143, 101, 72), (470, 402), (600, 402))
            pygame.draw.line(self.scene, (143, 101, 72), (680, 402), (810, 402))
            pygame.draw.polygon(self.scene, GOLD,
                                [(640, 395), (647, 402), (640, 409), (633, 402)])
            if self.name:
                text(self.scene, self.serif, 'With love, ' + self.name, GOLD, (640, 445))
            else:
                text(self.scene, self.small,
                     'L I G H T   •   L O V E   •   N E W   B E G I N N I N G S',
                     (190, 159, 151), (640, 445))

        # A slow cinematic build: each visual family gets its own entrance.
        self.draw_layer(stars, self.reveal(.2, 1.8))
        self.draw_layer(festive_lights, self.reveal(1.3, 1.7))
        self.draw_layer(lanterns, self.reveal(2.5, 1.8))
        self.draw_layer(floor_decor, self.reveal(3.4, 1.8))
        self.draw_layer(diyas, self.reveal(4.0, 2.0))
        self.draw_layer(fireworks, self.reveal(5.0, 1.8))
        self.draw_layer(heading, self.reveal(4.7, 1.3))
        self.draw_layer(title, self.reveal(5.4, 1.7))
        self.draw_layer(message, self.reveal(6.2, 1.6))

        if self.help and self.t > 7.0:
            text(self.scene, self.tiny,
                 'CLICK  fireworks     SPACE  grand finale     P  pause     A  autoplay     F  fullscreen     S  snapshot     H  hide controls',
                 (182, 159, 154), (640, 765))
        if self.paused:
            text(self.scene, self.small, 'PAUSED', (255, 228, 169), (640, 118))
        if time.monotonic() < self.toast_until:
            text(self.scene, self.small, self.toast, (255, 228, 169), (640, 490))
        self.present()

    def present(self):
        ww,wh=self.window.get_size()
        ratio=min(ww/W,wh/H)
        size=(max(1,int(W*ratio)),max(1,int(H*ratio)))
        self.viewport=pygame.Rect((ww-size[0])//2,(wh-size[1])//2,*size)
        self.window.fill((3,4,12))
        image=pygame.transform.smoothscale(self.scene,size) if size!=(W,H) else self.scene
        self.window.blit(image,self.viewport)
        pygame.display.flip()

    def events(self):
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                self.running=False
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if self.viewport.collidepoint(event.pos):
                    x=(event.pos[0]-self.viewport.x)*W/self.viewport.width
                    y=(event.pos[1]-self.viewport.y)*H/self.viewport.height
                    self.explode(x,y,random.choice(PALETTE),random.choice(['heart','ring','peony','willow']))
            elif event.type==pygame.KEYDOWN:
                k=event.key
                if k==pygame.K_ESCAPE:
                    self.running=False
                elif k==pygame.K_p:
                    self.paused=not self.paused
                elif k==pygame.K_a:
                    self.auto=not self.auto
                elif k==pygame.K_h:
                    self.help=not self.help
                elif k==pygame.K_SPACE:
                    self.finale_until=self.t+5
                    for _ in range(3):
                        self.launch()
                elif k==pygame.K_f:
                    self.fullscreen=not self.fullscreen
                    flags=pygame.FULLSCREEN if self.fullscreen else pygame.RESIZABLE
                    self.window=pygame.display.set_mode((0,0) if self.fullscreen else (W,H),flags)
                elif k==pygame.K_s:
                    try:
                        folder=Path.cwd()/'diwali_snapshots'
                        folder.mkdir(exist_ok=True)
                        path=folder/('diwali_'+time.strftime('%Y%m%d_%H%M%S')+'_'+str(time.time_ns()%1000000)+'.png')
                        pygame.image.save(self.scene,str(path))
                        self.toast='Snapshot saved to diwali_snapshots'
                    except (OSError,pygame.error) as exc:
                        self.toast='Snapshot failed: '+str(exc)[:65]
                    self.toast_until=time.monotonic()+3

    def run(self):
        try:
            while self.running:
                dt=min(self.clock.tick(60)/1000,.05)
                self.events()
                if not self.paused:
                    self.update(dt)
                self.draw()
        finally:
            pygame.quit()

def main():
    parser=argparse.ArgumentParser(description='An interactive, procedurally drawn Diwali celebration.')
    parser.add_argument('--name',default='',help='Personal greeting signature')
    parser.add_argument('--quality',choices=['high','low'],default='high',help='Use low on slower machines')
    args=parser.parse_args()
    Studio(args.name,args.quality).run()

if __name__=='__main__':
    main()