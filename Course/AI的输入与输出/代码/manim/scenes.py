"""Three main shots; end comparison belongs only to ReturnAnswer."""
import json
import os
from pathlib import Path
from manimlib import *
from objects import *


class FilmScene(Scene):
    def setup(self):
        super().setup()
        self.cues = []
        self.caption = None

    def cue(self, key, text):
        self.cues.append({'key': key, 'time': round(self.time, 3), 'text': text})
        new = label(text, 27).move_to([0,-3.35,0])
        if self.caption is None:
            self.add(new)
        else:
            self.remove(self.caption)
            self.add(new)
        self.caption = new

    def finish(self):
        output = os.getenv('AI_IO_CUES')
        if output:
            Path(output).mkdir(parents=True, exist_ok=True)
            (Path(output)/f'{type(self).__name__}.json').write_text(json.dumps(
                {'scene': type(self).__name__, 'duration': self.time, 'cues': self.cues},
                ensure_ascii=False, indent=2))

    def construct(self):
        self.build()
        self.finish()


class FirstInput(FilmScene):
    def build(self):
        # 01.1 User request, before application-provided context.
        self.cue('01.1', '教学示例：第一次提问')
        user = source_icon(0).scale(1.4).move_to([-4.7,1,0])
        sentence = label('把这段本地录音\n整理成会议纪要。', 38, BLUE_IO).move_to([.2,1,0])
        self.play(FadeIn(user), Write(sentence), run_time=1.8)
        self.wait(2)
        # 01.2–3 Compose the four separate sources.
        inputs = InputGroup().move_to([-4.6,.3,0])
        self.cue('01.2', '一句话之外，程序还可以组织其他输入')
        self.play(TransformFromCopy(user, inputs.rows[0]), FadeOut(sentence), FadeOut(user), run_time=1)
        self.play(ShowCreation(inputs.frame), LaggedStart(*[FadeIn(r) for r in inputs.rows[1:]], lag_ratio=.35), run_time=2)
        self.remove(*inputs.rows, inputs.frame)
        self.add(inputs)
        heading = label('首次输入',28).next_to(inputs, UP, buff=.3)
        self.play(FadeIn(heading), run_time=.5)
        self.wait(1.2)
        # 01.4–6 Expand local details, tethered to stable source icons.
        details = [('01.4', 0, '把这段本地录音\n整理成会议纪要。', BLUE_IO, '用户消息 · 教学示例'),
                   ('01.5', 1, '使用中文，\n依据取得的资料回答。', GREEN_IO, '系统指令 · 教学示例'),
                   ('01.6', 2, '录音位置\n/audio/meeting.wav', INK, '路径已经进入输入，录音内容还没有')]
        for key, index, text, color, caption in details:
            self.cue(key, caption)
            content = enclosed(label(text,34),color,.25).move_to([1.8,.65,0])
            tether = Line(inputs.rows[index].get_right()+RIGHT*.15, content.get_left()+LEFT*.25, color=color, stroke_width=1.3)
            self.play(TransformFromCopy(inputs.rows[index][0], content), ShowCreation(tether),run_time=1)
            extras = VGroup()
            if index == 2:
                w = wave().move_to([1.8,-1.55,0])
                link = Line(content.get_bottom()+DOWN*.1,w.get_top()+UP*.1,stroke_width=1)
                extras.add(w,link)
                self.play(FadeIn(extras),run_time=.6)
            self.wait(2.5)
            self.play(content.animate.scale(.05).move_to(inputs.rows[index][0]).set_opacity(0),FadeOut(tether),FadeOut(extras),run_time=.7)
            self.remove(content)
        # 01.7 Definition identity, then nested real Schema.
        self.cue('01.7', '工具定义：告诉模型可以请求什么操作')
        identity = VGroup(label('name: '+SCHEMA['name'],31,GOLD_IO),
                          label('description:',27),label('Transcribe an audio file\nusing Whisper.',27),
                          label('转写音频 · 原定义局部',25,GOLD_IO)).arrange(DOWN,aligned_edge=LEFT,buff=.22).move_to([1.6,.5,0])
        identity = enclosed(identity,GOLD_IO,.22)
        tether = Line(inputs.rows[3].get_right(),identity.get_left(),color=GOLD_IO,stroke_width=1.5)
        self.play(TransformFromCopy(inputs.rows[3][0],identity),ShowCreation(tether),run_time=1)
        self.wait(3)
        
        self.cue('01.8', 'inputSchema 描述参数结构（原定义局部）')
        name=label(SCHEMA['name'],29,GOLD_IO).move_to([1.7,2.65,0])
        root=label('inputSchema',27,GOLD_IO).move_to([.0,2.1,0])
        typ=label('type: object',26).move_to([.45,1.55,0])
        prop=label('properties',26,GOLD_IO).move_to([.35,1.03,0])
        fields=VGroup(*[enclosed(label(key,25,GOLD_IO),GOLD_IO,.12)
                        for key in SCHEMA['inputSchema']['properties']]).arrange(DOWN,aligned_edge=LEFT,buff=.13).move_to([2.65,-.35,0])
        parent=Line([-1.4,2.1,0],[-1.4,-2.5,0],color=GOLD_IO,stroke_width=1.6)
        branches=VGroup(Line([-1.4,1.55,0],[-.7,1.55,0]),Line([-1.4,1.03,0],[-.7,1.03,0])).set_stroke(GOLD_IO,1.6)
        field_bracket=brackets(5.5,2.7,GOLD_IO).move_to([3.15,-.3,0])
        self.play(ReplacementTransform(identity[0][0],name),FadeOut(VGroup(*identity[0][1:],identity[1])),
                  FadeIn(root),FadeIn(typ),FadeIn(prop),ShowCreation(parent),ShowCreation(branches),
                  FadeIn(fields),ShowCreation(field_bracket),run_time=1.3)
        self.remove(identity)
        self.add(name,root,typ,prop,parent,branches,fields,field_bracket)
        self.wait(1.5)
        self.cue('01.9','file_path 是字符串，表示文件路径')
        expanded=enclosed(label('file_path: {"type": "string"}',25,GOLD_IO),GOLD_IO,.15).move_to([3.2,fields[0].get_y(),0])
        self.play(Transform(fields[0],expanded),run_time=1.2)
        self.wait(2)
        self.cue('01.10','required 与 properties 同级；只有 file_path 必填')
        required=label('required: ["file_path"]',26,GOLD_IO).move_to([1.7,-2.3,0])
        branch=Line([-1.4,-2.3,0],required.get_left()+LEFT*.1,color=GOLD_IO,stroke_width=1.6)
        constraint=VMobject().set_points_as_corners([required.get_right()+RIGHT*.12,[6.2,-2.3,0],
                                                     [6.2,fields[0].get_y(),0],fields[0].get_right()]).set_stroke(GOLD_IO,2)
        self.play(FadeIn(required),ShowCreation(branch),ShowCreation(constraint),run_time=1)
        self.play(Indicate(fields[0],color=GOLD_IO),run_time=.8)
        self.wait(2)
        self.cue('01.11','另外三个参数为可选字符串')
        expanded_others=VGroup(*[enclosed(label(key+': {"type": "string"}',23,GOLD_IO),GOLD_IO,.12).move_to([3.2,row.get_y(),0])
                               for key,row in zip(list(SCHEMA['inputSchema']['properties'])[1:],fields[1:])])
        self.play(*[Transform(src,dst) for src,dst in zip(fields[1:],expanded_others)],run_time=1.2)
        optional=label('可选',23).move_to([-.35,-.7,0])
        self.play(FadeIn(optional),run_time=.4)
        self.wait(3)
        self.cue('01.12','首次输入：四种来源，边界保留')
        all_detail=VGroup(name,root,typ,prop,parent,branches,fields,field_bracket,required,branch,constraint,optional)
        self.play(all_detail.animate.scale(.02).move_to(inputs.rows[3][0]).set_opacity(0),FadeOut(tether),run_time=1)
        self.remove(all_detail)
        self.wait(1)
        self.remove(self.caption)
        self.caption = None
        self.play(FadeOut(heading),run_time=.4)


def execution_state():
    inputs = InputGroup(compact=True).move_to([-5.7,2.0,0])
    m = model().move_to([-4.55,.3,0])
    p = program().move_to([4.6,.45,0])
    t = tool().move_to([4.6,-1.85,0])
    req = record().move_to([1.4,.5,0])
    res = record(True).move_to([4.65,2.05,0])
    return inputs,m,p,t,req,res


class GenerateExecute(FilmScene):
    def build(self):
        # 02.1–2 First call with small context anchor.
        inputs = InputGroup().move_to([-4.6,.3,0])
        self.add(inputs)
        self.cue('02.1','程序把这次输入提供给语言模型')
        m = model().move_to([0,.3,0])
        self.play(FadeIn(m),run_time=.8)
        self.play(Transform(inputs,InputGroup(compact=True).move_to([-5.7,2,0])),m.animate.move_to([-4.55,.3,0]),run_time=1.2)
        flow = arrow(inputs.get_bottom(),m.get_top())
        self.play(GrowArrow(flow),run_time=.5)
        parcel = inputs.copy()
        self.add(parcel)
        self.play(parcel.animate.scale(.15).move_to(m).set_opacity(0),run_time=1)
        self.remove(parcel)
        # 02.3–7 Generate only a tool-call message, progressively.
        self.cue('02.3','模型正在生成消息；此时还没有读取录音')
        frame = brackets(7,3.7,GOLD_IO).move_to([1.1,.45,0])
        cursor = Line(UP*.16,DOWN*.16,color=GOLD_IO).move_to([-1.8,1.65,0])
        out = arrow(m.get_right(),frame.get_left(),GOLD_IO)
        self.play(ShowCreation(frame[0]),GrowArrow(out),FadeIn(cursor),run_time=.8)
        name = label(SCHEMA['name'],32,GOLD_IO).move_to([.45,1.65,0])
        self.cue('02.4','先生成工具名称')
        self.play(Write(name),cursor.animate.move_to([-1.8,.8,0]),run_time=1.4)
        rows = VGroup(*[label(json.dumps(k)+': '+json.dumps(v),27) for k,v in PARAMS.items()]).arrange(DOWN,aligned_edge=LEFT,buff=.28)
        rows.move_to([1.0,-.25,0])
        self.cue('02.5','再生成 file_path；路径仍然只是参数')
        self.play(Write(rows[0]),cursor.animate.move_to(rows[1].get_left()+LEFT*.2),run_time=1.6)
        self.wait(1.4)
        self.cue('02.6','假设参数：large、zh、timestamps')
        self.play(LaggedStart(*[Write(r) for r in rows[1:]],lag_ratio=.35),FadeOut(cursor),run_time=2.2)
        kind = enclosed(label('工具调用',27,GOLD_IO),GOLD_IO,.12).next_to(frame,UP,buff=.15)
        self.play(ShowCreation(frame[1]),run_time=.3)
        closed=RoundedRectangle(width=7,height=3.7,corner_radius=.15).set_stroke(GOLD_IO,2.5).move_to(frame)
        self.play(Transform(frame,VGroup(closed)),FadeIn(kind),run_time=.7)
        self.cue('02.7','完整的工具调用消息，是模型的一种输出')
        self.wait(2)
        # 02.8–10 Program receives and dispatches by message type.
        message = VGroup(frame,name,rows,kind)
        self.remove(frame,name,*rows,kind)
        self.add(message)
        self.cue('02.8','程序接收模型输出')
        p = program().move_to([4.6,.45,0])
        self.play(message.animate.scale(.65).move_to([.25,.6,0]),FadeIn(p),FadeOut(out),FadeOut(flow),Transform(m,dim_model(m.copy())),run_time=1)
        receive = arrow(message.get_right(),p.get_left(),GOLD_IO)
        self.play(GrowArrow(receive),run_time=.6)
        self.cue('02.9','程序识别消息类型，再选择执行分支')
        upper = VGroup(Line(p.get_top(),[5.3,1.7,0]),label('回答',24).move_to([5.5,2,0])).set_opacity(.35)
        lower = VGroup(Line(p.get_bottom(),[4.6,-.9,0],color=GOLD_IO),label('执行',24,GOLD_IO).move_to([5.35,-.65,0]))
        self.play(FadeIn(upper),ShowCreation(lower),Indicate(kind,color=GOLD_IO),run_time=.8)
        self.wait(1.5)
        self.cue('02.10','程序选择 transcribe_audio，传递参数')
        t = tool().move_to([4.6,-1.85,0])
        tool_name = label(SCHEMA['name'],22,GOLD_IO).next_to(t,DOWN,buff=.14)
        self.play(FadeIn(t),FadeIn(tool_name),run_time=.7)
        match=Line(name.get_bottom(),tool_name.get_left(),color=GOLD_IO,stroke_width=1.4)
        self.play(ShowCreation(match),Indicate(tool_name,color=GOLD_IO),run_time=.8)
        param_copy = rows.copy()
        self.add(param_copy)
        self.play(param_copy.animate.scale(.15).move_to(t).set_opacity(0),run_time=1.1)
        self.remove(param_copy)
        self.play(FadeOut(match),run_time=.3)
        # 02.11 Exactly one simulated read/execution.
        self.cue('02.11','程序触发执行后，工具才读取录音（模拟）')
        w = wave().move_to([-.7,-1.85,0])
        read = arrow(w.get_right(),t.get_left())
        self.play(FadeIn(w),GrowArrow(read),run_time=.6)
        sample = w[0].copy()
        self.add(sample)
        self.play(sample.animate.scale(.65).move_to(t[0]),run_time=1)
        scan = Line(DOWN*.3,UP*.3,color=CYAN_IO).move_to(t[0].get_left()+RIGHT*.2)
        self.play(ShowCreation(scan),run_time=.2)
        self.play(scan.animate.shift(RIGHT*1.6),run_time=1.4,rate_func=linear)
        self.play(FadeOut(scan),FadeOut(sample),FadeOut(w),FadeOut(read),run_time=.5)
        # 02.12 Result returns to the program; handoff state for shot 03.
        self.cue('02.12','工具返回结果，先交给程序')
        req = record().move_to([1.4,.5,0])
        res = record(True).move_to([4.65,2.05,0])
        self.play(ReplacementTransform(message,req),FadeOut(receive),FadeOut(upper),FadeOut(lower),FadeOut(tool_name),run_time=.7)
        # A bounded result emerges from the tool's output port and travels on the route.
        res.scale(.48).move_to([6.1,t[0].get_y(),0])
        route=VMobject().set_points_as_corners([res.get_center(),[6.1,res.get_y(),0],
                    [6.1,2.05,0],[4.65,2.05,0]])
        result_flow=route.copy().set_stroke(CYAN_IO,2)
        self.play(FadeIn(res),ShowCreation(result_flow),run_time=.6)
        self.play(MoveAlongPath(res,route),run_time=2.4,rate_func=smooth)
        self.play(res.animate.scale(1/.48),run_time=.6)
        self.play(FadeOut(result_flow),run_time=.3)
        self.wait(.7)



class ReturnAnswer(FilmScene):
    def build(self):
        # 03.1–3 Continue the returned result, without executing again.
        inputs,m,p,t,req,res = execution_state()
        dim_model(m)
        self.add(inputs,m,p,t,req,res)
        self.cue('03.1','程序收到返回的工具结果')
        receive = arrow(res.get_bottom(),p.get_top(),CYAN_IO)
        self.play(GrowArrow(receive),run_time=.6)
        self.play(res.animate.scale(.8).next_to(p,UP,buff=.18),run_time=1)
        self.play(Indicate(p,color=CYAN_IO),run_time=.6)
        self.play(FadeOut(receive),run_time=.3)
        self.cue('03.2','请求记录与工具结果都要保留')
        self.play(res.animate.scale(1/.8).move_to([1.4,-1.05,0]),run_time=1.2)
        self.wait(.8)
        # Pair the boundary-attached markers, rather than a line between text blocks.
        pair=VMobject().set_points_as_corners([req[2].get_center(),[3,.5,0],[3,-1.05,0],res[2].get_center()]).set_stroke(INK,2)
        self.cue('03.3','程序把工具结果对应到这次请求')
        self.play(ShowCreation(pair),Indicate(req[2]),Indicate(res[2]),run_time=1)
        self.wait(1.3)
        self.cue('03.4','程序组织下一次输入，保留每项内容的边界')
        updated=InputGroup(updated=True).set_height(4.8).move_to([-.4,.2,0])
        self.play(req.animate.set_width(2.6).move_to([3.4,-.1,0]),
                  res.animate.set_width(2.6).move_to([2.9,-1.55,0]),FadeOut(pair),
                  p.animate.move_to([4.6,1.5,0]),t.animate.scale(.65).move_to([5.25,-2.4,0]),run_time=1)
        t.set_stroke(color='#737D86')
        title=label('下一次输入',28).next_to(updated,UP,buff=.2)
        organize=arrow(p.get_left(),updated.frame.get_right())
        self.play(ShowCreation(updated.frame),FadeIn(title),GrowArrow(organize),run_time=.8)
        first_four=VGroup(*updated.rows[:4])
        self.play(TransformFromCopy(inputs.rows,first_four),run_time=1.3)
        self.wait(.7)
        for key,caption,source,target,color in [
            ('03.5','加入完整的请求记录',req,updated.rows[4],GOLD_IO),
            ('03.6','加入与请求对应的工具结果',res,updated.rows[5],CYAN_IO)]:
            self.cue(key,caption)
            transfer=arrow(source.get_left(),target.get_right(),color)
            self.play(GrowArrow(transfer),run_time=.4)
            # Same record structure retains body, border and pairing point in transit.
            self.play(TransformFromCopy(source,target),run_time=1.5)
            self.wait(.7)
            self.play(FadeOut(transfer),run_time=.3)
        self.remove(updated.frame,first_four,updated.rows[4],updated.rows[5])
        self.add(updated)
        self.cue('03.7','完整输入：原有信息、请求记录、工具结果')
        self.wait(1.8)
        self.second_call(updated,inputs,m,p,req,res,title,organize)
        self.comparison()

    def second_call(self,updated,inputs,m,p,req,res,title,organize):
        # 03.8–9 The SAME updated object shrinks; gold/cyan never disappear.
        self.cue('03.8','第 2 次调用：用户没有重新提问')
        self.play(FadeOut(inputs),FadeOut(title),FadeOut(organize),run_time=.5)
        # Reposition visibly with the full bordered input; then send a readable copy.
        self.play(m.animate.move_to([-4.55,-1.4,0]),run_time=.8)
        self.play(updated.animate.move_to([-4.8,1.4,0]).set_height(3.4),
                  req.animate.set_stroke(color='#766630'),res.animate.set_stroke(color='#347B80'),run_time=1.3)
        call=arrow(updated.get_bottom(),m.get_top())
        self.play(GrowArrow(call),run_time=.5)
        parcel=updated.copy()
        self.add(parcel)
        self.play(parcel.animate.scale(.65).move_to([-4.7,-.15,0]),run_time=1.2)
        self.play(parcel.animate.scale(.2).move_to(m).set_opacity(0),run_time=.8)
        self.remove(parcel)
        self.play(Transform(m,model().move_to(m)),run_time=.5)
        self.cue('03.9','调用后保留本次输入的缩略图，含请求与结果')
        self.play(Transform(updated,InputGroup(updated=True,compact=True).move_to([-5.5,2.2,0])),
                  FadeOut(call),FadeOut(req),FadeOut(res),p.animate.move_to([4.6,.35,0]),run_time=1.3)
        self.play(m.animate.move_to([-2.8,.35,0]),run_time=.8)
        connection=arrow(updated.get_bottom(),m.get_left())
        anchor_title=label('本次输入',23).next_to(updated,UP,buff=.15)
        self.play(FadeIn(anchor_title),GrowArrow(connection),run_time=.5)
        self.wait(1)
        # 03.10–11 Model answer goes via program to the user.
        self.cue('03.10','模型依据返回内容，生成给人的回答')
        a = answer().set_height(1.8).move_to([.1,.35,0])
        output = arrow(m.get_right(),a.get_left())
        self.play(GrowArrow(output),Write(a),run_time=2)
        output.add_updater(lambda line: line.become(arrow(m.get_right(),a.get_left())))
        self.wait(1)
        deliver = arrow(a.get_right(),p.get_left())
        self.play(GrowArrow(deliver),run_time=.6)
        deliver.add_updater(lambda line: line.become(arrow(a.get_right(),p.get_left())))
        self.play(a.animate.scale(.9).move_to([3,.35,0]),run_time=1.2)
        self.play(Indicate(p,color=INK),run_time=.6)
        self.cue('03.11','程序把回答交给用户阅读')
        user = source_icon(0).move_to([5.6,2.75,0])
        self.play(FadeIn(user),run_time=.4)
        outgoing = a.copy().set_height(.45).next_to(p,UP,buff=.25)
        self.play(TransformFromCopy(a,outgoing),run_time=.7)
        from_program = arrow(p.get_top(),outgoing.get_bottom())
        to_user = arrow(outgoing.get_top(),user.get_bottom())
        self.play(GrowArrow(from_program),GrowArrow(to_user),run_time=.5)
        from_program.add_updater(lambda line: line.become(arrow(p.get_top(),outgoing.get_bottom())))
        to_user.add_updater(lambda line: line.become(arrow(outgoing.get_top(),user.get_bottom())))
        self.play(outgoing.animate.set_height(.85).move_to([5.55,1.85,0]),run_time=1.2)
        self.wait(1.8)
        for line in [output,deliver,from_program,to_user]:
            line.clear_updaters()

    def comparison(self):
        # 03.12 Closing comparison, not an additional main shot.
        self.cue('03.12','用户问了一次，模型调用了两次。')
        self.play(*[FadeOut(mob) for mob in list(self.mobjects) if mob is not self.caption],run_time=.7)
        rows = VGroup()
        for y, updated, title in [(1.65,False,'第一次调用'),(-1.25,True,'第二次调用')]:
            inp = InputGroup(updated=updated).set_height(2.1).move_to([-4.3,y,0])
            mod = model().move_to([0,y,0])
            result = answer().set_height(1.65).move_to([4.05,y,0]) if updated else record().move_to([4.05,y,0])
            if not updated:
                result[0][1].become(label('工具请求',25,GOLD_IO).move_to(result[0][1]))
            tag = label('给人阅读' if updated else '给程序执行',25).next_to(result,DOWN,buff=.3)
            name = label(title+' · '+('更新后输入' if updated else '原有输入'),24).next_to(inp,UP,buff=.12)
            rows.add(VGroup(inp,mod,result,tag,name,arrow(inp.get_right(),mod.get_left()),arrow(mod.get_right(),result.get_left())))
        self.play(FadeIn(rows[0]),run_time=1)
        self.play(FadeIn(rows[1]),run_time=1)
        same = label('同一个模型',23).move_to([0,.25,0])
        self.play(FadeIn(same),run_time=.5)
        self.wait(4)


class ContinuityPreview(ReturnAnswer):
    """Bounded representative segment of six-part context shrinking/calling."""
    def build(self):
        updated = InputGroup(updated=True).scale(.82).move_to([-.5,.3,0])
        inputs,m,p,t,req,res = execution_state()
        title=label('下一次输入',28).next_to(updated,UP,buff=.2)
        organize=arrow(p.get_left(),updated.get_right())
        t.scale(.7).move_to([5.2,-2.15,0]).set_opacity(.4)
        self.add(updated,inputs,m,p,t,req,res,title,organize)
        self.second_call(updated,inputs,m,p,req,res,title,organize)
