import sys, pygame, random, time, math
from enum import Enum
import json, os
from datetime import datetime
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Window
WIDTH, HEIGHT = 900, 800
# Colors
CYAN = (0,255,255)
MED_CYAN = (0,180,180)
LIGHT_CYAN = (180,255,255)
BG_COLOR = (15,25,35)
WHITE = (255,255,255)
BLACK = (0,0,0)
YELLOW = (255,255,0)
BLUE = (0,0,255)
MAGENTA = (255,0,255)

# Game States
class GameState(Enum):
    MENU = 1
    SUBMENU_SNAKE = 2
    SUBMENU_TETRIS = 3
    SNAKE = 4
    TETRIS = 5
    GAME_OVER = 6
    PAUSE = 7
    LOAD_MENU_SNAKE = 8
    LOAD_MENU_TETRIS = 9
    DETAIL_SAVE_SNAKE = 10
    DETAIL_SAVE_TETRIS = 11

# Orbiting Morphing Button
class OrbitButton:
    def __init__(self, label, center, size, action, icon=None):
        self.label = label
        self.center = center
        self.size = size
        self.rect = pygame.Rect(0, 0, size[0], size[1])
        # static tablet position
        self.rect.center = self.center
        self.pos = self.rect.topleft
        self.action = action
        self.hovered = False
        self.icon = icon

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered = self.rect.collidepoint(mx, my)

    def draw(self, surf, font):
        # slot buttons: white background, black text, with icon
        if self.label.startswith("Slot"):
            pygame.draw.rect(surf, WHITE, self.rect, border_radius=self.size[1]//2)
            txt = font.render(self.label, True, BLACK)
            tw, th = txt.get_size()
            # draw icon if available
            if getattr(self, 'icon', None):
                icon_w, icon_h = self.icon.get_size()
                pad_x = 10
                icon_x = self.rect.x + pad_x
                icon_y = self.rect.centery - icon_h//2
                surf.blit(self.icon, (icon_x, icon_y))
                tx = icon_x + icon_w + pad_x
                ty = self.rect.centery - th//2
            else:
                tx = self.rect.centerx - tw//2
                ty = self.rect.centery - th//2
            surf.blit(txt, (tx, ty))
            return
        col = LIGHT_CYAN if self.hovered else MED_CYAN
        # dynamic icon button overrides static: draw uniform circle background then text
        if getattr(self, 'icon', None):
            text_surf = font.render(self.label, True, WHITE)
            tw, th = text_surf.get_size()
            iw, ih = self.icon.get_size()
            gap = 10
            pill_w, pill_h = self.size
            # fixed padding for icon circle
            pad_x = 20
            icon_bg_radius = pill_h // 2
            pill_rect = pygame.Rect(0, 0, pill_w, pill_h)
            pill_rect.center = self.center
            # update hit area
            self.rect = pill_rect
            self.pos = pill_rect.topleft
            # draw pill background
            pygame.draw.rect(surf, col, pill_rect, border_radius=icon_bg_radius)
            # draw icon circle background at constant padding from left
            bg_cx = pill_rect.x + pad_x + icon_bg_radius
            bg_cy = pill_rect.centery
            pygame.draw.circle(surf, col, (bg_cx, bg_cy), icon_bg_radius)
            # render icon and text
            surf.blit(self.icon, (bg_cx - iw//2, bg_cy - ih//2))
            # draw text: center only for pause menu labels, keep icon position
            if self.label in ("Continue", "Save & Quit", "Quit Without Saving"):
                tx = pill_rect.centerx - tw//2
                surf.blit(text_surf, (tx, pill_rect.centery - th//2))
            else:
                surf.blit(text_surf, (bg_cx + icon_bg_radius + gap, pill_rect.centery - th//2))
            return
        # draw rounded rectangle tablet
        pygame.draw.rect(surf, col, self.rect, border_radius=self.size[1]//2)
        # draw icon at left side
        icon_w, icon_h = 20, 20
        ix = self.pos[0] + 10
        iy = self.pos[1] + self.size[1]//2 - icon_h//2
        if "Snake" in self.label:
            for i in range(3):
                pygame.draw.rect(surf, MED_CYAN, (ix + i*(icon_w//3 + 2), iy, icon_w//3, icon_h//3))
        elif "Tetris" in self.label:
            # T-shaped tetromino
            bar_w, bar_h = icon_w*2//3, icon_h//4
            pygame.draw.rect(surf, LIGHT_CYAN, (ix + icon_w//6, iy, bar_w, bar_h))
            pygame.draw.rect(surf, LIGHT_CYAN, (ix + icon_w//2 - bar_h//2, iy + bar_h, bar_h*3, bar_h))
        elif "Save" in self.label:
            # floppy disk icon
            pygame.draw.rect(surf, YELLOW, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.rect(surf, WHITE, (ix + icon_w//4, iy + icon_h//4, icon_w//2, icon_h//2), 2)
        elif "Load" in self.label:
            # folder icon
            pygame.draw.rect(surf, BLUE, (ix, iy + icon_h//4, icon_w, icon_h*3//4), border_radius=3)
            pygame.draw.rect(surf, BLUE, (ix + icon_w//6, iy, icon_w//3, icon_h//4), border_radius=2)
        elif "New Game" in self.label:
            # new game icon
            pygame.draw.rect(surf, LIGHT_CYAN, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.rect(surf, WHITE, (ix + icon_w//4, iy + icon_h//4, icon_w//2, icon_h//2), 2)
        elif "Back" in self.label:
            # back icon
            pygame.draw.rect(surf, LIGHT_CYAN, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.polygon(surf, WHITE, [(ix + icon_w//2, iy + icon_h//4), (ix + icon_w//4, iy + icon_h*3//4), (ix + icon_w*3//4, iy + icon_h*3//4)])
        elif "Save & Quit" in self.label:
            # save and quit icon
            pygame.draw.rect(surf, YELLOW, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.polygon(surf, WHITE, [(ix + icon_w//2, iy + icon_h//4), (ix + icon_w//4, iy + icon_h*3//4), (ix + icon_w*3//4, iy + icon_h*3//4)])
            pygame.draw.rect(surf, WHITE, (ix + icon_w//4, iy + icon_h//4, icon_w//2, icon_h//2), 2)
        elif "Continue" in self.label:
            # continue icon
            pygame.draw.rect(surf, LIGHT_CYAN, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.polygon(surf, WHITE, [(ix + icon_w//2, iy + icon_h//4), (ix + icon_w//4, iy + icon_h*3//4), (ix + icon_w*3//4, iy + icon_h*3//4)])
        elif "Quit Without Saving" in self.label:
            # quit without saving icon
            pygame.draw.rect(surf, LIGHT_CYAN, (ix, iy, icon_w, icon_h), border_radius=3)
            pygame.draw.polygon(surf, WHITE, [(ix + icon_w//2, iy + icon_h//4), (ix + icon_w//4, iy + icon_h*3//4), (ix + icon_w*3//4, iy + icon_h*3//4)])
        # label
        text = font.render(self.label, True, WHITE)
        tr = text.get_rect(center=self.rect.center)
        surf.blit(text, tr)

    def handle_event(self, event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.hovered:
            self.action()

# Title
def draw_title(surf, font, icon, panel_rect, title_str="PMD742OMNI GAME HUB"):
    # dynamic title pill inside menu panel
    try:
        title_font = pygame.font.SysFont("consolas", 12)
    except:
        title_font = pygame.font.Font(None, 12)
    text_surf = title_font.render(title_str, True, WHITE)
    text_surf.set_alpha(200)
    icon_gap = 5
    icon_w, icon_h = (icon.get_width(), icon.get_height()) if icon else (0, 0)
    # compute group height
    group_h = text_surf.get_height() + (icon_h + icon_gap if icon else 0)
    # pill dimensions relative to panel with extra size
    margin_x, margin_y = 15, 20  # original side margins
    vpad = 12  # vertical padding inside pill
    delta_y = 30  # further increased downward shift for title pill
    # compute raw dimensions then reduce by 25%
    raw_w = panel_rect.width - margin_x*2
    raw_h = group_h + vpad*2
    pill_w = int(raw_w * 0.80)
    pill_h = int(raw_h * 0.80)
    pill_h += 20
    # center reduced pill inside original margins
    pill_x = panel_rect.x + margin_x + (raw_w - pill_w)//2
    pill_y = panel_rect.y + margin_y + (raw_h - pill_h)//2 + delta_y
    # draw pill with smoother edges
    pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
    smooth_rad = pill_h // 2
    pygame.draw.rect(pill, (255,255,255,120), pill.get_rect(), border_radius=smooth_rad)
    surf.blit(pill, (pill_x, pill_y))
    # center text inside pill
    text_rect = text_surf.get_rect(midtop=(pill_x + pill_w//2, pill_y + (pill_h - group_h)//2))
    surf.blit(text_surf, text_rect.topleft)
    # draw icon if available
    if icon:
        icon_rect = icon.get_rect(midtop=(pill_x + pill_w//2, text_rect.bottom + icon_gap))
        surf.blit(icon, icon_rect.topleft)

# Snake game
class SnakeGame:
    def __init__(self):
        self.cell=20; self.cols=WIDTH//self.cell; self.rows=HEIGHT//self.cell
        self.reset()
    def reset(self):
        self.snake=[(self.cols//2,self.rows//2)]
        self.dir=(1,0)
        self.spawn_food()
        self.powers=[]
        self.score=0
        self.active=None; self.end_time=0
        self.last_move=pygame.time.get_ticks(); self.move_delay=150
    def spawn_food(self):
        while True:
            p=(random.randrange(self.cols), random.randrange(self.rows))
            if p not in self.snake: break
        self.food=p
    def spawn_power(self):
        types=[("speed",YELLOW,0.5),("slow",BLUE,2),("inv",MAGENTA,1)]
        t=types[random.randrange(len(types))]
        while True:
            p=(random.randrange(self.cols), random.randrange(self.rows))
            if p!=self.food and p not in self.snake: break
        self.powers.append({"type":t[0],"pos":p,"color":t[1],"mult":t[2]})
    def update(self, events):
        now=pygame.time.get_ticks()
        for e in events:
            if e.type==pygame.KEYDOWN:
                if e.key in (pygame.K_UP,pygame.K_w): self.dir=(0,-1)
                if e.key in (pygame.K_DOWN,pygame.K_s): self.dir=(0,1)
                if e.key in (pygame.K_LEFT,pygame.K_a): self.dir=(-1,0)
                if e.key in (pygame.K_RIGHT,pygame.K_d): self.dir=(1,0)
        delay=self.move_delay
        if self.active in ("speed","slow"): delay=int(self.move_delay*self.powerspeed)
        if now-self.last_move>delay:
            self.last_move=now
            head=( (self.snake[0][0]+self.dir[0])%self.cols,
                   (self.snake[0][1]+self.dir[1])%self.rows)
            if head in self.snake and self.active!="inv": return ("Snake",self.score)
            self.snake.insert(0,head)
            if head==self.food:
                self.score+=1; self.spawn_food()
                if random.random()<0.2: self.spawn_power()
            else: self.snake.pop()
            for pu in self.powers:
                if head==pu["pos"]:
                    self.active=pu["type"]; self.powerspeed=pu["mult"]
                    self.end_time=now+7000
                    self.powers.remove(pu); break
        if self.active and now>self.end_time:
            self.active=None
        return None
    def draw(self,surf,font):
        surf.fill(BG_COLOR)
        pygame.draw.rect(surf, LIGHT_CYAN, (self.food[0]*self.cell,self.food[1]*self.cell,self.cell,self.cell))
        for pu in self.powers:
            pygame.draw.rect(surf,pu["color"],(pu["pos"][0]*self.cell,pu["pos"][1]*self.cell,self.cell,self.cell))
        for seg in self.snake:
            pygame.draw.rect(surf, MED_CYAN, (seg[0]*self.cell,seg[1]*self.cell,self.cell,self.cell))
        txt=font.render(f"Score: {self.score}",True,WHITE); surf.blit(txt,(5,5))
        if self.active:
            rem=(self.end_time-pygame.time.get_ticks())//1000
            txt2=font.render(f"{self.active}:{rem}",True,WHITE); surf.blit(txt2,(5,30))
    @classmethod
    def from_dict(cls,data):
        g = cls()
        g.snake = [tuple(pos) for pos in data['snake']]
        g.dir = tuple(data['dir'])
        g.food = tuple(data['food'])
        g.powers = [{'type':p['type'],'pos':tuple(p['pos']),'color':tuple(p['color']),'mult':p['mult']} for p in data['powers']]
        g.score = data['score']
        g.active = data['active']
        now = pygame.time.get_ticks()
        rem = data.get('remaining_ms',0)
        if g.active and rem>0:
            g.end_time = now + rem
            if g.active in ('speed','slow'):
                g.powerspeed = data.get('active_mult',1)
        else:
            g.active = None
            g.end_time = 0
        g.move_delay = data.get('move_delay',g.move_delay)
        g.last_move = now
        return g

# Tetris game
class TetrisGame:
    shapes={
        'I':[[(1,1,1,1)],[(1,),(1,),(1,),(1,)]],
        'O':[[(1,1),(1,1)]],
        'T':[[(0,1,0),(1,1,1)],[(1,0),(1,1),(1,0)],[(1,1,1),(0,1,0)],[(0,1),(1,1),(0,1)]],
        'S':[[(0,1,1),(1,1,0)],[(1,0),(1,1),(0,1)]],
        'Z':[[(1,1,0),(0,1,1)],[(0,1),(1,1),(1,0)]],
        'J':[[(1,0,0),(1,1,1)],[(1,1),(1,0),(1,0)],[(1,1,1),(1,0,0)],[(0,1),(0,1),(1,1)]],
        'L':[[(0,0,1),(1,1,1)],[(1,0),(1,0),(1,1)],[(1,1,1),(1,0,0)],[(1,1),(0,1),(0,1)]]
    }
    colors={'I':CYAN,'O':YELLOW,'T':LIGHT_CYAN,'S':BLUE,'Z':MAGENTA,'J':MED_CYAN,'L':WHITE}
    def __init__(self):
        self.cols=10; self.rows=20; self.cell=30
        self.grid=[[None for _ in range(self.cols)] for __ in range(self.rows)]
        self.score=0; self.level=1; self.lines=0; self.over=False
        self.new_piece()
        self.gravity_event=pygame.USEREVENT+1
        pygame.time.set_timer(self.gravity_event, max(50,500 - (self.level-1)*50))
    def new_piece(self):
        self.shape=random.choice(list(self.shapes.keys())); self.rot=0
        self.pattern=self.shapes[self.shape][self.rot]
        self.x=self.cols//2 - len(self.pattern[0])//2; self.y=0
        if self.collide(self.x,self.y,self.pattern): self.over=True
    def rotate(self):
        r=(self.rot+1)%len(self.shapes[self.shape])
        patt=self.shapes[self.shape][r]
        if not self.collide(self.x,self.y,patt): self.rot=r; self.pattern=patt
    def collide(self,x,y,patt):
        for i,row in enumerate(patt):
            for j,val in enumerate(row):
                if val:
                    if x+j<0 or x+j>=self.cols or y+i>=self.rows or (y+i>=0 and self.grid[y+i][x+j]):
                        return True
        return False
    def lock(self):
        for i,row in enumerate(self.pattern):
            for j,val in enumerate(row):
                if val and self.y+i>=0: self.grid[self.y+i][self.x+j]=self.colors[self.shape]
        newg=[]; cleared=0
        for row in self.grid:
            if None not in row: cleared+=1
            else: newg.append(row)
        for _ in range(cleared): newg.insert(0,[None]*self.cols)
        self.grid=newg; self.lines+=cleared; self.score+=cleared*100
        if self.lines//10+1>self.level:
            self.level+=1
            pygame.time.set_timer(self.gravity_event, max(50,500 - (self.level-1)*50))
        self.new_piece()
    def update(self, events):
        for e in events:
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_LEFT and not self.collide(self.x-1,self.y,self.pattern): self.x-=1
                if e.key==pygame.K_RIGHT and not self.collide(self.x+1,self.y,self.pattern): self.x+=1
                if e.key==pygame.K_DOWN and not self.collide(self.x,self.y+1,self.pattern): self.y+=1
                if e.key in (pygame.K_UP,pygame.K_w): self.rotate()
            if e.type==self.gravity_event:
                if not self.collide(self.x,self.y+1,self.pattern): self.y+=1
                else: self.lock()
        if getattr(self,"over",False): return ("Tetris",self.score)
        return None
    def draw(self,surf,font):
        surf.fill(BG_COLOR)
        offx=WIDTH//2 - self.cols*self.cell//2; offy=HEIGHT//2 - self.rows*self.cell//2
        for i,row in enumerate(self.grid):
            for j,color in enumerate(row):
                if color: pygame.draw.rect(surf,color,(offx+j*self.cell,offy+i*self.cell,self.cell,self.cell))
        for i,row in enumerate(self.pattern):
            for j,val in enumerate(row):
                if val and self.y+i>=0:
                    pygame.draw.rect(surf,self.colors[self.shape],(offx+(self.x+j)*self.cell,offy+(self.y+i)*self.cell,self.cell,self.cell))
        txt=font.render(f"Score:{self.score}",True,WHITE); surf.blit(txt,(5,5))
        txt2=font.render(f"Lvl:{self.level}",True,WHITE); surf.blit(txt2,(5,30))
    @classmethod
    def from_dict(cls,data):
        g = cls()
        g.grid = [[tuple(cell) if cell else None for cell in row] for row in data['grid']]
        g.score = data['score']
        g.level = data['level']
        g.lines = data['lines']
        pygame.time.set_timer(g.gravity_event, max(50,500-(g.level-1)*50))
        g.shape = data['shape']
        g.rot = data['rot']
        g.pattern = g.shapes[g.shape][g.rot]
        g.x = data['x']
        g.y = data['y']
        g.over = False
        return g

# Game Over Screen
class GameOverScreen:
    def __init__(self, game, score): self.game=game; self.score=score
    def draw(self,surf,font):
        surf.fill(BG_COLOR)
        t1=font.render("Game Over",True,WHITE)
        t2=font.render(f"{self.game} Score: {self.score}",True,WHITE)
        t3=font.render("Click to return to Menu",True,WHITE)
        surf.blit(t1,(WIDTH//2-t1.get_width()//2,HEIGHT//3))
        surf.blit(t2,(WIDTH//2-t2.get_width()//2,HEIGHT//2))
        surf.blit(t3,(WIDTH//2-t3.get_width()//2,HEIGHT*2//3))

# Main Hub
class GameHub:
    def __init__(self):
        pygame.display.set_caption("PMD742OMNI HUB")
        self.screen=pygame.display.set_mode((WIDTH,HEIGHT))
        self.set_icon()
        try: self.font=pygame.font.SysFont("consolas",24)
        except: self.font=pygame.font.Font(None,24)
        self.state=GameState.MENU
        # load snake button icon
        try:
            raw = pygame.image.load(os.path.join('icons','snake.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.snake_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.snake_icon = None
        # load tetris button icon
        try:
            raw = pygame.image.load(os.path.join('icons','tetris.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.tetris_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.tetris_icon = None
        # load save button icon
        try:
            raw = pygame.image.load(os.path.join('icons','save game.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.save_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.save_icon = None
        # load Load Progress button icon
        try:
            raw = pygame.image.load(os.path.join('icons','load game.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.load_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.load_icon = None
        # load New Game button icon
        try:
            raw = pygame.image.load(os.path.join('icons','new game.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.new_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.new_icon = None
        # load Back button icon
        try:
            raw = pygame.image.load(os.path.join('icons','back.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.back_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.back_icon = None
        # load Save & Quit button icon
        try:
            raw = pygame.image.load(os.path.join('icons','Save & Quit.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.save_quit_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.save_quit_icon = None
        # load Continue button icon
        try:
            raw = pygame.image.load(os.path.join('icons','Continue.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.continue_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.continue_icon = None
        # load info pill icons
        try:
            raw = pygame.image.load(os.path.join('icons','title.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.title_pill_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.title_pill_icon = None
        try:
            raw = pygame.image.load(os.path.join('icons','Date & Time.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.datetime_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.datetime_icon = None
        # load slot button icon
        try:
            raw = pygame.image.load(os.path.join(BASE_DIR, 'icons','Slot.png')).convert_alpha()
            h = self.font.get_height()
            w = raw.get_width() * h // raw.get_height()
            self.slot_icon = pygame.transform.smoothscale(raw, (w, h))
        except:
            self.slot_icon = None
        # unify icon sizes to Save Progress icon dimensions
        if self.save_icon:
            size = self.save_icon.get_size()
            if self.snake_icon:
                self.snake_icon = pygame.transform.smoothscale(self.snake_icon, size)
            if self.tetris_icon:
                self.tetris_icon = pygame.transform.smoothscale(self.tetris_icon, size)
            if getattr(self, 'load_icon', None):
                self.load_icon = pygame.transform.smoothscale(self.load_icon, size)
            if getattr(self, 'new_icon', None):
                self.new_icon = pygame.transform.smoothscale(self.new_icon, size)
            if getattr(self, 'back_icon', None):
                self.back_icon = pygame.transform.smoothscale(self.back_icon, size)
            if getattr(self, 'save_quit_icon', None):
                self.save_quit_icon = pygame.transform.smoothscale(self.save_quit_icon, size)
            if getattr(self, 'continue_icon', None):
                self.continue_icon = pygame.transform.smoothscale(self.continue_icon, size)
            if getattr(self, 'title_pill_icon', None):
                self.title_pill_icon = pygame.transform.smoothscale(self.title_pill_icon, size)
            if getattr(self, 'datetime_icon', None):
                self.datetime_icon = pygame.transform.smoothscale(self.datetime_icon, size)
            if getattr(self, 'slot_icon', None):
                self.slot_icon = pygame.transform.smoothscale(self.slot_icon, size)
        # compute uniform width for buttons
        gap, pad_x = 10, 20
        snake_txt_w = self.font.render("Play Snake", True, WHITE).get_width()
        snake_icon_w = self.snake_icon.get_width() if self.snake_icon else 0
        calc_snake_w = snake_txt_w + snake_icon_w + gap + pad_x*2
        tetris_txt_w = self.font.render("Play Tetris", True, WHITE).get_width()
        tetris_icon_w = self.tetris_icon.get_width() if self.tetris_icon else 0
        calc_tetris_w = tetris_txt_w + tetris_icon_w + gap + pad_x*2
        save_txt_w = self.font.render("Save Progress", True, WHITE).get_width()
        save_icon_w = self.save_icon.get_width() if self.save_icon else 0
        calc_save_w = save_txt_w + save_icon_w + gap + pad_x*2
        load_txt_w = self.font.render("Load Progress", True, WHITE).get_width()
        load_icon_w = self.load_icon.get_width() if getattr(self, 'load_icon', None) else 0
        calc_load_w = load_txt_w + load_icon_w + gap + pad_x*2
        new_txt_w = self.font.render("Start New Game", True, WHITE).get_width()
        new_icon_w = self.new_icon.get_width() if getattr(self, 'new_icon', None) else 0
        calc_new_w = new_txt_w + new_icon_w + gap + pad_x*2
        back_txt_w = self.font.render("Back", True, WHITE).get_width()
        back_icon_w = self.back_icon.get_width() if getattr(self, 'back_icon', None) else 0
        calc_back_w = back_txt_w + back_icon_w + gap + pad_x*2
        unified_w = max(calc_snake_w, calc_tetris_w, calc_save_w, calc_load_w, calc_new_w, calc_back_w, 180)
        # dynamic pill height: icon/font height + vertical padding (min height 70)
        vpad = 16
        icon_h = self.save_icon.get_height() if getattr(self, 'save_icon', None) else self.font.get_height()
        unified_h = icon_h + vpad*2
        unified_h = max(unified_h, 70)
        unified_size = (unified_w + 105, unified_h)
        # keep button size for submenus
        self.btn_size = unified_size
        # load title icon under title
        try:
            self.title_icon = pygame.image.load(os.path.join('icons','game hub.png')).convert_alpha()
            self.title_icon = pygame.transform.smoothscale(self.title_icon, (50, 50))
        except:
            self.title_icon = None
        # Main menu: two game selectors
        cx = WIDTH//2
        mid_y = HEIGHT//2
        offset = unified_size[1] + 20
        self.buttons = [
            OrbitButton("Play Snake", (cx, mid_y - offset//2), unified_size, self.open_snake_menu, self.snake_icon),
            OrbitButton("Play Tetris", (cx, mid_y + offset//2), unified_size, self.open_tetris_menu, self.tetris_icon),
        ]
        self.scores = self.load_scores()
        self.over = None
        self.paused_state = None
        # setup absolute save directories
        os.makedirs(os.path.join(BASE_DIR,'saves','snake'), exist_ok=True)
        os.makedirs(os.path.join(BASE_DIR,'saves','tetris'), exist_ok=True)
        # migrate legacy single-slot saves into multi-slot folders
        for game in ('snake','tetris'):
            old = os.path.join(BASE_DIR, f"{game}_save.json")
            if os.path.exists(old):
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                dest = os.path.join(BASE_DIR, 'saves', game, f"autosave_{now}.json")
                os.rename(old, dest)
                print(f"[MIGRATE] moved {old} to {dest}")
        # migrate generic savegame.json into multi-slot folders
        oldg = os.path.join(BASE_DIR, "savegame.json")
        if os.path.exists(oldg):
            with open(oldg, "r") as _f:
                d = json.load(_f)
            game = d.get("game")
            if game in ('snake','tetris'):
                now = datetime.now().strftime("%Y%m%d_%H%M%S")
                destg = os.path.join(BASE_DIR, 'saves', game, f"savegame_{now}.json")
                os.rename(oldg, destg)
                print(f"[MIGRATE] moved generic savegame to {destg}")

    def set_icon(self):
        # load custom app icon, fallback to default GH
        try:
            raw = pygame.image.load(os.path.join('icons','app icon.png')).convert_alpha()
            surf = pygame.transform.smoothscale(raw, (32,32))
        except:
            surf = pygame.Surface((32,32))
            surf.fill(CYAN)
            try: f=pygame.font.SysFont("consolas",20)
            except: f=pygame.font.Font(None,20)
            txt = f.render("PH", True, BG_COLOR)
            surf.blit(txt, (8,5))
        pygame.display.set_icon(surf)

    def play_snake(self): self.game=SnakeGame(); self.state=GameState.SNAKE

    def play_tetris(self): self.game=TetrisGame(); self.state=GameState.TETRIS

    def load_scores(self, filename="scores.json"):
        if os.path.exists(filename):
            with open(filename, "r") as f:
                return json.load(f)
        return {"snake": [], "tetris": []}

    def save_scores(self, filename="scores.json"):
        with open(filename, "w") as f:
            json.dump(self.scores, f)

    def record_score(self, game, score):
        key = game.lower()
        if key in self.scores:
            self.scores[key].append(score)
        else:
            self.scores[key] = [score]
        self.save_scores()

    def save_progress(self, filename="savegame.json"):
        # determine which game to save: use paused_state when pausing
        state = self.paused_state or self.state
        if state == GameState.SNAKE:
            data = {"game": "snake", "data": {
                "snake": self.game.snake,
                "dir": self.game.dir,
                "food": self.game.food,
                "powers": self.game.powers,
                "score": self.game.score,
                "active": self.game.active,
                "remaining_ms": max(0, self.game.end_time - pygame.time.get_ticks()) if self.game.active else 0,
                "active_mult": getattr(self.game, "powerspeed", 1),
                "move_delay": self.game.move_delay
            }}
        elif state == GameState.TETRIS:
            data = {"game": "tetris", "data": {
                "grid": [[list(cell) if cell else None for cell in row] for row in self.game.grid],
                "score": self.game.score,
                "level": self.game.level,
                "lines": self.game.lines,
                "shape": self.game.shape,
                "rot": self.game.rot,
                "x": self.game.x,
                "y": self.game.y
            }}
        else:
            return
        with open(filename, "w") as f:
            json.dump(data, f)

    def load_progress(self, filename="savegame.json"):
        if not os.path.exists(filename):
            return
        with open(filename, "r") as f:
            data = json.load(f)
        if data.get("game") == "snake":
            self.game = SnakeGame.from_dict(data["data"])
            self.state = GameState.SNAKE
        elif data.get("game") == "tetris":
            self.game = TetrisGame.from_dict(data["data"])
            self.state = GameState.TETRIS

    # Game-specific save wrappers
    def save_snake_game(self):
        self.save_progress(os.path.join(BASE_DIR, "snake_save.json"))

    def save_tetris_game(self):
        self.save_progress(os.path.join(BASE_DIR, "tetris_save.json"))

    # Submenu navigation
    def open_snake_menu(self):
        unified_size = self.btn_size
        cx = WIDTH//2; mid_y = HEIGHT//2; offset_y = unified_size[1] + 20
        self.buttons = [
            OrbitButton("Start New Game", (cx, mid_y - offset_y), unified_size, self.start_snake,      self.new_icon),
            OrbitButton("Load Game",      (cx, mid_y),            unified_size, self.open_load_snake_menu,   self.load_icon),
            OrbitButton("Back",           (cx, mid_y + offset_y), unified_size, self.open_main_menu,    self.back_icon),
        ]
        self.state = GameState.SUBMENU_SNAKE

    def open_tetris_menu(self):
        unified_size = self.btn_size
        cx = WIDTH//2; mid_y = HEIGHT//2; offset_y = unified_size[1] + 20
        self.buttons = [
            OrbitButton("Start New Game", (cx, mid_y - offset_y), unified_size, self.start_tetris,      self.new_icon),
            OrbitButton("Load Game",      (cx, mid_y),            unified_size, self.open_load_tetris_menu,  self.load_icon),
            OrbitButton("Back",           (cx, mid_y + offset_y), unified_size, self.open_main_menu,    self.back_icon),
        ]
        self.state = GameState.SUBMENU_TETRIS

    def start_snake(self):
        self.game = SnakeGame(); self.state = GameState.SNAKE

    def start_tetris(self):
        self.game = TetrisGame(); self.state = GameState.TETRIS

    def open_main_menu(self):
        unified_size = self.btn_size
        cx = WIDTH//2
        mid_y = HEIGHT//2
        offset_y = unified_size[1] + 20
        self.buttons = [
            OrbitButton("Play Snake", (cx, mid_y - offset_y//2), unified_size, self.open_snake_menu,  self.snake_icon),
            OrbitButton("Play Tetris", (cx, mid_y + offset_y//2), unified_size, self.open_tetris_menu, self.tetris_icon),
        ]
        self.state = GameState.MENU

    def load_snake_game(self):
        self.load_progress(os.path.join(BASE_DIR, "snake_save.json"))

    def load_tetris_game(self):
        self.load_progress(os.path.join(BASE_DIR, "tetris_save.json"))

    def open_pause_menu(self):
        self.paused_state = self.state
        unified_size = self.btn_size
        pause_size = (unified_size[0] + 50, unified_size[1])
        cx = WIDTH//2; mid_y = HEIGHT//2; offset_y = unified_size[1] + 20
        self.buttons = [
            OrbitButton("Continue",            (cx, mid_y - offset_y),   pause_size, self.resume_game,               self.continue_icon),
            OrbitButton("Save & Quit",         (cx, mid_y),              pause_size, self.perform_save_quit,         self.save_quit_icon),
            OrbitButton("Quit Without Saving", (cx, mid_y + offset_y),   pause_size, self.perform_quit_without_saving, self.back_icon),
        ]
        self.state = GameState.PAUSE

    def resume_game(self):
        self.state = self.paused_state

    def perform_save_quit(self):
        # auto-save with timestamp + return to submenu
        now = datetime.now().strftime("%Y%m%d_%H%M%S")
        sub = 'snake' if self.paused_state==GameState.SNAKE else 'tetris'
        dir_path = os.path.join(BASE_DIR,'saves',sub)
        fname = f"save_{now}.json"
        full = os.path.join(dir_path,fname)
        self.save_progress(full)
        print(f"[SAVE] created {full}")
        if self.paused_state==GameState.SNAKE: self.open_snake_menu()
        else: self.open_tetris_menu()

    def perform_quit_without_saving(self):
        if self.paused_state==GameState.SNAKE: self.open_snake_menu()
        else: self.open_tetris_menu()

    # Multi-slot load menus
    def open_load_snake_menu(self):
        path = os.path.join(BASE_DIR, 'saves','snake')
        print(f"[DEBUG] open_load_snake_menu path: {path}")
        files = sorted(f for f in os.listdir(path) if f.endswith('.json'))
        print(f"[DEBUG] found save files: {files}")
        cx, mid_y = WIDTH//2, HEIGHT//2; offset_y = self.btn_size[1] + 20
        start_y = mid_y - ((len(files)-1)/2)*offset_y
        self.buttons = []
        for i, fname in enumerate(files):
            y = int(start_y + i*offset_y)
            label = f"Slot {i+1}"
            self.buttons.append(OrbitButton(label, (cx, y), self.btn_size,
                lambda f=fname, sn=i+1: self.open_detail_snake(f, sn), self.slot_icon))
        # back to game submenu
        self.buttons.append(OrbitButton("Back", (cx, int(start_y + len(files)*offset_y)), self.btn_size, lambda: self.open_snake_menu(), self.back_icon))
        self.state = GameState.LOAD_MENU_SNAKE
        self.slot_scroll = 0
        pygame.event.clear(pygame.MOUSEBUTTONDOWN)

    def open_load_tetris_menu(self):
        path = os.path.join(BASE_DIR, 'saves','tetris')
        print(f"[DEBUG] open_load_tetris_menu path: {path}")
        files = sorted(f for f in os.listdir(path) if f.endswith('.json'))
        print(f"[DEBUG] found save files: {files}")
        cx, mid_y = WIDTH//2, HEIGHT//2; offset_y = self.btn_size[1] + 20
        start_y = mid_y - ((len(files)-1)/2)*offset_y
        self.buttons = []
        for i, fname in enumerate(files):
            y = int(start_y + i*offset_y)
            label = f"Slot {i+1}"
            self.buttons.append(OrbitButton(label, (cx, y), self.btn_size,
                lambda f=fname, sn=i+1: self.open_detail_tetris(f, sn), self.slot_icon))
        self.buttons.append(OrbitButton("Back", (cx, int(start_y + len(files)*offset_y)), self.btn_size, lambda: self.open_tetris_menu(), self.back_icon))
        self.state = GameState.LOAD_MENU_TETRIS
        self.slot_scroll = 0
        pygame.event.clear(pygame.MOUSEBUTTONDOWN)

    def open_detail_snake(self, fname, slot_no):
        path = os.path.join(BASE_DIR, 'saves','snake', fname)
        name_no_ext = fname[:-5]
        timestamp = name_no_ext[-15:]
        title = name_no_ext[:-16] or 'save'
        self.detail_title = title
        self.detail_timestamp = timestamp
        self.detail_filepath = path
        self.detail_slot = slot_no
        cx, mid_y = WIDTH//2, HEIGHT//2; offset = self.btn_size[1] + 20
        self.detail_pill1_y = int(mid_y - 1.5*offset)
        self.detail_pill2_y = int(mid_y - 0.5*offset)
        y_load = int(mid_y + 0.5*offset); y_delete = int(mid_y + 1.5*offset); y_back = int(mid_y + 2.5*offset)
        self.buttons = [
            OrbitButton("Load Game",   (cx, y_load),   self.btn_size, lambda: self.load_progress(self.detail_filepath), self.load_icon),
            OrbitButton("Delete Slot", (cx, y_delete), self.btn_size, self.perform_delete_slot, None),
            OrbitButton("Back",        (cx, y_back),   self.btn_size, lambda: self.open_load_snake_menu(), self.back_icon),
        ]
        self.state = GameState.DETAIL_SAVE_SNAKE

    def open_detail_tetris(self, fname, slot_no):
        path = os.path.join(BASE_DIR, 'saves','tetris', fname)
        name_no_ext = fname[:-5]
        timestamp = name_no_ext[-15:]
        title = name_no_ext[:-16] or 'save'
        self.detail_title = title
        self.detail_timestamp = timestamp
        self.detail_filepath = path
        self.detail_slot = slot_no
        cx, mid_y = WIDTH//2, HEIGHT//2; offset = self.btn_size[1] + 20
        self.detail_pill1_y = int(mid_y - 1.5*offset)
        self.detail_pill2_y = int(mid_y - 0.5*offset)
        y_load = int(mid_y + 0.5*offset); y_delete = int(mid_y + 1.5*offset); y_back = int(mid_y + 2.5*offset)
        self.buttons = [
            OrbitButton("Load Game",   (cx, y_load),   self.btn_size, lambda: self.load_progress(self.detail_filepath), self.load_icon),
            OrbitButton("Delete Slot", (cx, y_delete), self.btn_size, self.perform_delete_slot, None),
            OrbitButton("Back",        (cx, y_back),   self.btn_size, lambda: self.open_load_tetris_menu(), self.back_icon),
        ]
        self.state = GameState.DETAIL_SAVE_TETRIS

    def perform_delete_slot(self):
        try:
            os.remove(self.detail_filepath)
            print(f"[DELETE] removed {self.detail_filepath}")
        except Exception as e:
            print(f"[ERROR] deleting slot: {e}")
        # return to the appropriate load menu
        if self.state == GameState.DETAIL_SAVE_SNAKE:
            self.open_load_snake_menu()
        else:
            self.open_load_tetris_menu()

    def run(self):
        """
        Main game loop for GameHub.

        This method implements the main game loop for GameHub, which is
        responsible for updating and drawing the current game state, as
        well as handling events and transitioning between different game
        states.

        The loop runs at a maximum of 60 frames per second, and it
        continuously checks for events (such as key presses or mouse
        clicks) and updates the game state accordingly.

        The game state is represented by an instance of the GameState
        enum, which can take on one of four values: MENU, SNAKE,
        TETRIS, or GAME_OVER. The game loop updates and draws the game
        state based on its current value.

        If the game state is MENU, the loop draws the main menu and
        checks for events that trigger transitions to other game states.

        If the game state is SNAKE or TETRIS, the loop updates and draws
        the current game and checks for events that trigger transitions
        to other game states (such as pausing or quitting the game).

        If the game state is GAME_OVER, the loop draws the game over
        screen and checks for events that trigger transitions back to
        the main menu.

        The loop runs until the user closes the game window, at which
        point it exits and the program terminates.
        """

        clock=pygame.time.Clock()
        while True:
            dt=clock.tick(60)/1000
            events=pygame.event.get()
            for e in events:
                if e.type==pygame.QUIT: pygame.quit(); sys.exit()
            if self.state==GameState.MENU:
                for b in self.buttons: b.update(dt)
                for e in events:
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                # panel background sized to buttons
                btn_w = max(b.size[0] for b in self.buttons)
                # add extra horizontal margins (40px each side)
                panel_w = btn_w + 70
                # dynamic panel height to enclose all buttons (min 85% screen height)
                btn_h = self.buttons[0].size[1]
                centers_y = [b.center[1] for b in self.buttons]
                extent = max(centers_y) - min(centers_y)
                margin_v = 20
                dynamic_h = extent + btn_h + margin_v*2
                panel_h = max(dynamic_h, int(HEIGHT * 0.85))
                panel_h - 70
                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                # smoother, more rounded corners
                radius = min(panel_w, panel_h) // 3
                pygame.draw.rect(panel, (*MED_CYAN, 50), panel.get_rect(), border_radius=radius)
                x = (WIDTH - panel_w)//2
                y = (HEIGHT - panel_h)//2
                self.screen.blit(panel, (x, y))
                # draw title with panel rect for dynamic sizing
                panel_rect = pygame.Rect(x, y, panel_w, panel_h)
                draw_title(self.screen,self.font,self.title_icon, panel_rect)
                for b in self.buttons: b.draw(self.screen, self.font)
            elif self.state==GameState.SUBMENU_SNAKE:
                # Snake submenu
                for b in self.buttons: b.update(dt)
                for e in events:
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                # draw panel background
                btn_w = max(b.size[0] for b in self.buttons)
                panel_w = btn_w + 70; btn_h = self.buttons[0].size[1]
                centers_y = [b.center[1] for b in self.buttons]
                dynamic_h = (max(centers_y)-min(centers_y)) + btn_h + 40
                panel_h = max(dynamic_h, int(HEIGHT*0.85))
                panel = pygame.Surface((panel_w,panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel, (*MED_CYAN,50), panel.get_rect(), border_radius=min(panel_w,panel_h)//3)
                x=(WIDTH-panel_w)//2; y=(HEIGHT-panel_h)//2
                self.screen.blit(panel,(x,y))
                draw_title(self.screen,self.font,self.snake_icon, pygame.Rect(x,y,panel_w,panel_h), "SNAKE")
                for b in self.buttons: b.draw(self.screen,self.font)
            elif self.state==GameState.SUBMENU_TETRIS:
                # Tetris submenu
                for b in self.buttons: b.update(dt)
                for e in events:
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                btn_w = max(b.size[0] for b in self.buttons)
                panel_w = btn_w + 70; btn_h = self.buttons[0].size[1]
                centers_y = [b.center[1] for b in self.buttons]
                dynamic_h = (max(centers_y)-min(centers_y)) + btn_h + 40
                panel_h = max(dynamic_h, int(HEIGHT*0.85))
                panel = pygame.Surface((panel_w,panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel, (*MED_CYAN,50), panel.get_rect(), border_radius=min(panel_w,panel_h)//3)
                x=(WIDTH-panel_w)//2; y=(HEIGHT-panel_h)//2
                self.screen.blit(panel,(x,y))
                draw_title(self.screen,self.font,self.tetris_icon, pygame.Rect(x,y,panel_w,panel_h), "TETRIS")
                for b in self.buttons: b.draw(self.screen,self.font)
            elif self.state==GameState.SNAKE:
                # pause/save in game
                for e in events:
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_p:
                        self.open_pause_menu()
                        break
                if self.state == GameState.SNAKE:
                    res=self.game.update(events)
                    self.game.draw(self.screen,self.font)
                    hint = self.font.render("Press P to Pause", True, WHITE)
                    self.screen.blit(hint, (WIDTH-hint.get_width()-10, HEIGHT-hint.get_height()-10))
                    if res:
                        g,s=res; self.record_score(g,s); self.over=GameOverScreen(g,s); self.state=GameState.GAME_OVER
            elif self.state==GameState.TETRIS:
                # pause/save in game
                for e in events:
                    if e.type==pygame.KEYDOWN and e.key==pygame.K_p:
                        self.open_pause_menu()
                        break
                if self.state == GameState.TETRIS:
                    res=self.game.update(events)
                    self.game.draw(self.screen,self.font)
                    hint = self.font.render("Press P to Pause", True, WHITE)
                    self.screen.blit(hint, (WIDTH-hint.get_width()-10, HEIGHT-hint.get_height()-10))
                    if res:
                        g,s=res; self.record_score(g,s); self.over=GameOverScreen(g,s); self.state=GameState.GAME_OVER
            elif self.state==GameState.PAUSE:
                for b in self.buttons: b.update(dt)
                for e in events:
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                for b in self.buttons: b.draw(self.screen,self.font)
            elif self.state==GameState.LOAD_MENU_SNAKE:
                # update and handle scroll events
                for b in self.buttons: b.update(dt)
                offset_y = self.btn_size[1] + 20
                scroll_step = offset_y
                panel_h = int(HEIGHT * 0.85)
                slot_area_h = offset_y * 3
                max_scroll = max(0, len(self.buttons)*offset_y - slot_area_h)
                for e in events:
                    if e.type==pygame.MOUSEBUTTONDOWN:
                        if e.button==4:
                            self.slot_scroll = max(self.slot_scroll - scroll_step, 0)
                        elif e.button==5:
                            self.slot_scroll = min(self.slot_scroll + scroll_step, max_scroll)
                    elif e.type==pygame.KEYDOWN:
                        if e.key==pygame.K_DOWN:
                            self.slot_scroll = min(self.slot_scroll + scroll_step, max_scroll)
                        elif e.key==pygame.K_UP:
                            self.slot_scroll = max(self.slot_scroll - scroll_step, 0)
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                # draw panel background
                btn_w = max(b.size[0] for b in self.buttons)
                panel_w = btn_w + 70
                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel, (*MED_CYAN,50), panel.get_rect(), border_radius=min(panel_w,panel_h)//3)
                panel_x = (WIDTH - panel_w)//2; panel_y = (HEIGHT - panel_h)//2
                self.screen.blit(panel, (panel_x, panel_y))
                # header pill "Slots"
                pill_w, pill_h = self.btn_size
                hdr_pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(hdr_pill, (0,0,0,150), hdr_pill.get_rect(), border_radius=pill_h//2)
                hdr_surf = self.font.render("Slots", True, WHITE)
                hdr_pill.blit(hdr_surf, ((pill_w - hdr_surf.get_width())//2, (pill_h - hdr_surf.get_height())//2))
                hdr_x = panel_x + (panel_w - pill_w)//2; hdr_y = panel_y + 80
                self.screen.blit(hdr_pill, (hdr_x, hdr_y))
                # draw scrollable buttons
                content_start_y = hdr_y + pill_h + 80
                prev_clip = self.screen.get_clip()
                clip_y = content_start_y - pill_h//2
                clip_h = slot_area_h + pill_h
                self.screen.set_clip(pygame.Rect(panel_x, clip_y, panel_w, clip_h))
                slot_buttons = self.buttons[:-1]
                back_btn = self.buttons[-1]
                first_visible = self.slot_scroll // offset_y
                slot_pad = 20
                total_slots_h = 3 * self.btn_size[1] + 2 * 20  # 3 slots, 2 gaps
                slot_area_y = content_start_y + (slot_area_h - total_slots_h)//2
                for i in range(3):
                    idx = first_visible + i
                    if idx >= len(slot_buttons): break
                    b = slot_buttons[idx]
                    y = slot_area_y + i * (self.btn_size[1] + slot_pad)
                    b.center = (panel_x + panel_w//2, y + self.btn_size[1]//2)
                    b.rect.center = b.center
                    b.pos = b.rect.topleft
                    b.draw(self.screen, self.font)
                self.screen.set_clip(prev_clip)
                # draw Back button always below slot area, never clipped
                back_gap = 40
                by = content_start_y + slot_area_h + back_gap
                back_btn.center = (panel_x + panel_w//2, by)
                back_btn.rect.center = back_btn.center
                back_btn.pos = back_btn.rect.topleft
                back_btn.draw(self.screen, self.font)
            elif self.state==GameState.LOAD_MENU_TETRIS:
                # update and handle scroll events
                for b in self.buttons: b.update(dt)
                offset_y = self.btn_size[1] + 20
                scroll_step = offset_y
                panel_h = int(HEIGHT * 0.85)
                slot_area_h = offset_y * 3
                max_scroll = max(0, len(self.buttons)*offset_y - slot_area_h)
                for e in events:
                    if e.type==pygame.MOUSEBUTTONDOWN:
                        if e.button==4:
                            self.slot_scroll = max(self.slot_scroll - scroll_step, 0)
                        elif e.button==5:
                            self.slot_scroll = min(self.slot_scroll + scroll_step, max_scroll)
                    elif e.type==pygame.KEYDOWN:
                        if e.key==pygame.K_DOWN:
                            self.slot_scroll = min(self.slot_scroll + scroll_step, max_scroll)
                        elif e.key==pygame.K_UP:
                            self.slot_scroll = max(self.slot_scroll - scroll_step, 0)
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                # draw panel background
                btn_w = max(b.size[0] for b in self.buttons)
                panel_w = btn_w + 70
                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel, (*MED_CYAN,50), panel.get_rect(), border_radius=min(panel_w,panel_h)//3)
                panel_x = (WIDTH - panel_w)//2; panel_y = (HEIGHT - panel_h)//2
                self.screen.blit(panel, (panel_x, panel_y))
                # header pill "Slots"
                pill_w, pill_h = self.btn_size
                hdr_pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(hdr_pill, (0,0,0,150), hdr_pill.get_rect(), border_radius=pill_h//2)
                hdr_surf = self.font.render("Slots", True, WHITE)
                hdr_pill.blit(hdr_surf, ((pill_w - hdr_surf.get_width())//2, (pill_h - hdr_surf.get_height())//2))
                hdr_x = panel_x + (panel_w - pill_w)//2; hdr_y = panel_y + 80
                self.screen.blit(hdr_pill, (hdr_x, hdr_y))
                # draw scrollable buttons
                content_start_y = hdr_y + pill_h + 80
                prev_clip = self.screen.get_clip()
                clip_y = content_start_y - pill_h//2
                clip_h = slot_area_h + pill_h
                self.screen.set_clip(pygame.Rect(panel_x, clip_y, panel_w, clip_h))
                slot_buttons = self.buttons[:-1]
                back_btn = self.buttons[-1]
                first_visible = self.slot_scroll // offset_y
                slot_pad = 20
                total_slots_h = 3 * self.btn_size[1] + 2 * 20  # 3 slots, 2 gaps
                slot_area_y = content_start_y + (slot_area_h - total_slots_h)//2
                for i in range(3):
                    idx = first_visible + i
                    if idx >= len(slot_buttons): break
                    b = slot_buttons[idx]
                    y = slot_area_y + i * (self.btn_size[1] + slot_pad)
                    b.center = (panel_x + panel_w//2, y + self.btn_size[1]//2)
                    b.rect.center = b.center
                    b.pos = b.rect.topleft
                    b.draw(self.screen, self.font)
                self.screen.set_clip(prev_clip)
                # draw Back button always below slot area, never clipped
                back_gap = 40
                by = content_start_y + slot_area_h + back_gap
                back_btn.center = (panel_x + panel_w//2, by)
                back_btn.rect.center = back_btn.center
                back_btn.pos = back_btn.rect.topleft
                back_btn.draw(self.screen, self.font)
            elif self.state in (GameState.DETAIL_SAVE_SNAKE, GameState.DETAIL_SAVE_TETRIS):
                # render detailed save view
                for b in self.buttons: b.update(dt)
                for e in events:  # handle back/load button clicks
                    for b in self.buttons: b.handle_event(e)
                self.screen.fill(BG_COLOR)
                # outer panel
                btn_w = max(b.size[0] for b in self.buttons)
                panel_w = btn_w + 70; panel_h = int(HEIGHT * 0.85) + 50
                panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
                pygame.draw.rect(panel, (*MED_CYAN,50), panel.get_rect(), border_radius=min(panel_w,panel_h)//3)
                x = (WIDTH-panel_w)//2; y = (HEIGHT-panel_h)//2
                pill_h = self.btn_size[1]
                panel_drop = pill_h // 2
                y += panel_drop
                self.screen.blit(panel, (x, y))
                # header pill for slot number instead of default title
                pill_w, pill_h = self.btn_size
                hdr_pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(hdr_pill, (0,0,0,150), hdr_pill.get_rect(), border_radius=pill_h//2)
                hdr_txt = f"Slot {self.detail_slot}"
                hdr_surf = self.font.render(hdr_txt, True, WHITE)
                hdr_pill.blit(hdr_surf, ((pill_w - hdr_surf.get_width())//2, (pill_h - hdr_surf.get_height())//2))
                hdr_x = x + (panel_w - pill_w)//2
                hdr_y = y + pill_h  # drop header pill by one pill height from panel top
                self.screen.blit(hdr_pill, (hdr_x, hdr_y))
                # inner cyan panel for info pills
                pill_w, pill_h = self.btn_size
                inner_pad = 10
                info_w = pill_w + inner_pad*2
                info_h = pill_h*2 + inner_pad*3
                info_panel = pygame.Surface((info_w, info_h), pygame.SRCALPHA)
                pygame.draw.rect(info_panel, (*CYAN,100), info_panel.get_rect(), border_radius=pill_h//2)
                ix = x + (panel_w - info_w)//2
                # position inner panel below header pill with consistent padding
                iy = hdr_y + pill_h + inner_pad
                self.screen.blit(info_panel, (ix, iy))
                # title pill
                pill = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(pill, (255,255,255,150), pill.get_rect(), border_radius=pill_h//2)
                pad_x = 20; gap = 10; icon_r = pill_h//2
                bg_x = pad_x + icon_r; bg_y = pill_h//2
                pygame.draw.circle(pill, (255,255,255,150), (bg_x, bg_y), icon_r)
                if self.title_pill_icon:
                    pill.blit(self.title_pill_icon, (bg_x - self.title_pill_icon.get_width()//2, bg_y - self.title_pill_icon.get_height()//2))
                txt = self.font.render(self.detail_title, True, (0,0,0))
                pill.blit(txt, (bg_x + icon_r + gap, bg_y - txt.get_height()//2))
                self.screen.blit(pill, (ix + inner_pad, iy + inner_pad))
                # datetime pill
                pill2 = pygame.Surface((pill_w, pill_h), pygame.SRCALPHA)
                pygame.draw.rect(pill2, (255,255,255,150), pill2.get_rect(), border_radius=pill_h//2)
                pygame.draw.circle(pill2, (255,255,255,150), (bg_x, bg_y), icon_r)
                if self.datetime_icon:
                    pill2.blit(self.datetime_icon, (bg_x - self.datetime_icon.get_width()//2, bg_y - self.datetime_icon.get_height()//2))
                txt2 = self.font.render(self.detail_timestamp, True, (0,0,0))
                pill2.blit(txt2, (bg_x + icon_r + gap, bg_y - txt2.get_height()//2))
                self.screen.blit(pill2, (ix + inner_pad, iy + inner_pad*2 + pill_h))
                # draw Load/Back buttons directly below inner panel using inner_pad spacing
                cx = WIDTH // 2
                y_load = iy + info_h + pill_h + inner_pad*2
                y_back = y_load + pill_h + inner_pad
                for b in self.buttons:
                    new_y = y_load if b.label == "Load Game" else y_back
                    b.center = (cx, new_y)
                    b.rect.center = b.center
                    b.pos = b.rect.topleft
                    b.draw(self.screen, self.font)
                pygame.display.flip()
                continue
            elif self.state==GameState.GAME_OVER:
                for e in events:
                    if e.type==pygame.MOUSEBUTTONDOWN: self.state=GameState.MENU
                self.over.draw(self.screen,self.font)
            pygame.display.flip()

if __name__=="__main__":
    pygame.init()
    GameHub().run()
