"""Stable vector objects. Schema is read from the course's frozen source."""
import json
import os
from pathlib import Path
from manimlib import *

COURSE = Path(__file__).resolve().parents[2]
SCHEMA = json.loads((COURSE / '素材/来源/whisper-mcp/transcribe_audio.schema.json').read_text())
FONT = os.getenv('AI_IO_FONT', 'PingFang SC')
BLUE_IO, GREEN_IO, GOLD_IO, CYAN_IO = '#49A8EF', '#69C991', '#EBC75B', '#63D5DB'
INK = '#D7DBDF'
PARAMS = {'file_path': '/audio/meeting.wav', 'model': 'large', 'language': 'zh', 'output_format': 'timestamps'}


def label(value, size=28, color=INK):
    return Text(value, font=FONT, font_size=size).set_color(color)


def brackets(width, height, color=INK):
    left = VMobject().set_points_as_corners([
        [-width/2+.16, height/2, 0], [-width/2, height/2, 0],
        [-width/2, -height/2, 0], [-width/2+.16, -height/2, 0]])
    right = left.copy().rotate(PI, about_point=ORIGIN)
    return VGroup(left, right).set_stroke(color, 2)


def outline(content, color=INK, buff=.18):
    return RoundedRectangle(width=content.get_width()+2*buff,
                            height=content.get_height()+2*buff,
                            corner_radius=.12).set_stroke(color,2.5).set_fill(BLACK,0).move_to(content)


def enclosed(content, color=INK, buff=.18):
    return VGroup(content, outline(content,color,buff))


def dim_model(mob):
    # Dim the surface colors, not opacity: rear layers must remain occluded.
    mob[0].set_fill('#24282D',1).set_stroke('#727A83',1.8)
    mob[1].set_color('#858D95')
    return mob


def bars(color=INK, n=3, width=.65):
    return VGroup(*[Line(LEFT*width/2, RIGHT*(width/2-.07*(i%2)), color=color, stroke_width=3)
                    for i in range(n)]).arrange(DOWN, buff=.12)


def source_icon(kind):
    if kind == 0:
        return label('”', 76, BLUE_IO).set_height(.55)
    if kind == 1:
        return bars(GREEN_IO)
    if kind == 2:
        return VGroup(Line(LEFT*.3, RIGHT*.3), Line(DOWN*.3, UP*.3)).set_stroke(INK, 3)
    long = RoundedRectangle(width=.78, height=.18, corner_radius=.08).set_stroke(GOLD_IO, 2)
    short = VGroup(*[Circle(radius=.08).set_stroke(GOLD_IO, 2) for _ in range(3)]).arrange(RIGHT, buff=.08)
    return VGroup(long, short.next_to(long, DOWN, buff=.10))


class InputGroup(VGroup):
    """Both full and thumbnail states retain each semantic component."""
    def __init__(self, updated=False, compact=False):
        super().__init__()
        self.updated = updated
        names = ['用户', '系统指令', '环境', '工具定义']
        self.rows = VGroup(*[VGroup(source_icon(i), label(name, 27).move_to([1.55, 0, 0]))
                              for i, name in enumerate(names)]).arrange(DOWN, buff=.24, aligned_edge=LEFT)
        if updated:
            self.rows.add(record(False).set_width(2.8),record(True).set_width(2.8))
            self.rows.arrange(DOWN,buff=.2,aligned_edge=LEFT)
        self.add(self.rows)
        self.frame = brackets(self.rows.get_width()+.55,self.rows.get_height()+.45).move_to(self.rows)
        self.add(self.frame)
        self.move_to(ORIGIN)
        if compact and updated:
            for index,row in enumerate(self.rows[:4]):
                row.remove(row[1])
                row[0].set_width(.34).move_to([-.75+index*.5,.62,0])
            for row,text,color,y in [(self.rows[4],'请求记录',GOLD_IO,.02),
                                      (self.rows[5],'工具结果',CYAN_IO,-.59)]:
                compact_body=VGroup(bars(color,2,.32),label(text,21,color)).arrange(RIGHT,buff=.18)
                box=outline(compact_body,color,.11)
                point=Dot(box.get_right(),radius=.055).set_color(color)
                row.become(VGroup(compact_body,box,point).move_to([0,y,0]))
            self.frame.become(brackets(2.5,2.0).move_to([0,0,0]))
            self.move_to(ORIGIN)
        elif compact:
            for row in self.rows:
                row.remove(row[1])
            icons=VGroup(*[row[0] for row in self.rows]).arrange(DOWN,buff=.15)
            self.frame.become(brackets(1.15,icons.get_height()+.4).move_to(icons))
            self.move_to(ORIGIN).set_height(1.3)


def model():
    layers = VGroup()
    for y in [-.24, 0, .24]:
        layers.add(Polygon([-0.7,y,0], [0,y+.38,0], [.7,y,0], [0,y-.38,0],
                           fill_color='#42474D', fill_opacity=1, stroke_color=INK, stroke_width=1.8))
    return VGroup(layers, label('语言模型', 25).next_to(layers, DOWN, buff=.22))


def program():
    circle = Circle(radius=.46).set_stroke(BLUE_IO, 3)
    return VGroup(circle, label('程序', 25, BLUE_IO))


def tool():
    body=RoundedRectangle(width=2,height=.8,corner_radius=.18).set_stroke(INK,2.5)
    ports=VGroup(body,*[Circle(radius=.1).set_fill(BLACK,1).set_stroke(INK,2.5).move_to([x,0,0]) for x in [-1,1]])
    ticks=VGroup(*[Line([x,-.23,0],[x,.23,0],color='#6C8899') for x in np.linspace(-.65,.65,7)])
    return VGroup(ports,ticks,label('转写工具',23).move_to([0,-.76,0]))


def wave():
    heights = [.12,.24,.43,.65,.35,.2,.12,.3,.52,.37,.23,.15,.31,.2,.1]
    lines = VGroup(*[Line([i*.12,-h/2,0],[i*.12,h/2,0]) for i,h in enumerate(heights)]).set_stroke(INK,2)
    lines.move_to(ORIGIN)
    return VGroup(lines, label('本地录音',23).next_to(lines, DOWN, buff=.2))


def record(result=False):
    color=CYAN_IO if result else GOLD_IO
    lines=bars(color,2,.95)
    title=label('工具结果' if result else '请求记录',25,color).next_to(lines,UP,buff=.14)
    body=VGroup(lines,title)
    if not result:
        body.add(label(SCHEMA['name'],22,color).next_to(lines,DOWN,buff=.12))
    frame=RoundedRectangle(width=2.8,height=body.get_height()+.3,corner_radius=.12).set_stroke(color,2.5).move_to(body)
    point=Dot(frame.get_right(),radius=.075).set_color(color)
    # Stable slots: body (title at body[1]), boundary, pairing point.
    return VGroup(body,frame,point)


def answer():
    page=VMobject().set_points_as_corners([[-.95,-1.05,0],[-.95,1.05,0],
          [.58,1.05,0],[.95,.68,0],[.95,-1.05,0],[-.95,-1.05,0]])
    fold=VMobject().set_points_as_corners([[.58,1.05,0],[.58,.68,0],[.95,.68,0]])
    title=label('会议纪要',25).move_to([0,.55,0])
    lines=bars(INK,4,1.25).move_to([0,-.25,0])
    return VGroup(page.set_stroke(INK,2.5),fold.set_stroke(INK,2.5),title,lines)


def arrow(start, end, color=INK):
    return Arrow(start, end, buff=.12, fill_color=color, thickness=2)
