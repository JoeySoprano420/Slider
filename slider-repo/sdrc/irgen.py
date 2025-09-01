
from llvmlite import ir
from . import ast as A

def parse_base12_int(text: str) -> int:
    raw = text
    base12 = False
    if text.endswith(".b12"):
        base12 = True; raw = text[:-4]
    if any(ch in "te" for ch in raw): base12 = True
    if base12:
        v = 0
        for ch in raw:
            d = 10 if ch=='t' else 11 if ch=='e' else int(ch,10)
            v = v*12 + d
        return v
    return int(raw,10)

class IRGen:
    def __init__(self, module_name="slider_module"):
        self.module = ir.Module(name=module_name)
        self.builder = None; self.func = None
        self.printf = self._declare_printf()
        self.globals = {}

    def _declare_printf(self):
        ty = ir.FunctionType(ir.IntType(32), [ir.IntType(8).as_pointer()], var_arg=True)
        return ir.Function(self.module, ty, name="printf")

    def cstr(self, s: str):
        if s in self.globals: return self.globals[s]
        b = bytearray(s.encode('utf8') + b'\x00')
        g = ir.GlobalVariable(self.module, ir.ArrayType(ir.IntType(8), len(b)), name=f".str{len(self.globals)}")
        g.global_constant = True; g.initializer = ir.Constant(g.type.pointee, b); g.linkage = 'internal'
        self.globals[s] = g; return g

    def gen_module(self, mod: A.Module) -> ir.Module:
        for f in mod.funcs: self.gen_func_decl(f)
        for f in mod.funcs: self.gen_func_body(f)
        return self.module

    def gen_func_decl(self, f: A.Func):
        params = [ir.IntType(64) for _ in f.params]
        rett = ir.IntType(64) if (f.ret_type == "i64") else ir.VoidType()
        fnty = ir.FunctionType(rett, params)
        irf = ir.Function(self.module, fnty, name=f.name)
        for i,(pname,_ptype) in enumerate(f.params): irf.args[i].name = pname

    def gen_func_body(self, f: A.Func):
        irf = self.module.get_global(f.name)
        block = irf.append_basic_block("entry")
        self.builder = ir.IRBuilder(block)
        env = {}
        for arg in irf.args:
            slot = self.builder.alloca(ir.IntType(64), name=arg.name)
            self.builder.store(arg, slot); env[arg.name] = slot
        for st in f.body: self.gen_stmt(st, env)
        if isinstance(irf.function_type.return_type, ir.VoidType): self.builder.ret_void()
        else: self.builder.ret(ir.Constant(ir.IntType(64), 0))

    def gen_stmt(self, st, env):
        ARef = A
        if isinstance(st, ARef.Let) or isinstance(st, ARef.Var):
            val = self.gen_expr(st.expr, env)
            slot = self.builder.alloca(ir.IntType(64), name=st.name)
            self.builder.store(val, slot); env[st.name] = slot; return
        if isinstance(st, ARef.Assign):
            val = self.gen_expr(st.expr, env); self.builder.store(val, env[st.name]); return
        if isinstance(st, ARef.Return):
            if st.expr is None: self.builder.ret_void()
            else: self.builder.ret(self.gen_expr(st.expr, env)); return
        if isinstance(st, ARef.ExprStmt): self.gen_expr(st.expr, env); return
        if isinstance(st, ARef.If): return self._gen_if(st, env)
        if isinstance(st, ARef.While): return self._gen_while(st, env)
        if isinstance(st, ARef.ForRange): return self._gen_for(st, env)
        raise NotImplementedError(type(st))

    def _gen_if(self, st, env):
        irf = self.builder.function
        then_bb = irf.append_basic_block("then"); else_bb = irf.append_basic_block("else"); end_bb = irf.append_basic_block("ifend")
        condv = self.gen_expr(st.cond, env)
        condz = self.builder.icmp_unsigned("!=", condv, ir.Constant(ir.IntType(64), 0))
        self.builder.cbranch(condz, then_bb, else_bb)
        self.builder.position_at_end(then_bb)
        for s in st.then_body: self.gen_stmt(s, env)
        if not self.builder.block.is_terminated: self.builder.branch(end_bb)
        self.builder.position_at_end(else_bb)
        for s in st.else_body: self.gen_stmt(s, env)
        if not self.builder.block.is_terminated: self.builder.branch(end_bb)
        self.builder.position_at_end(end_bb)

    def _gen_while(self, st, env):
        irf = self.builder.function
        cond_bb = irf.append_basic_block("while.cond"); body_bb = irf.append_basic_block("while.body"); end_bb = irf.append_basic_block("while.end")
        self.builder.branch(cond_bb)
        self.builder.position_at_end(cond_bb)
        condv = self.gen_expr(st.cond, env)
        condz = self.builder.icmp_unsigned("!=", condv, ir.Constant(ir.IntType(64), 0))
        self.builder.cbranch(condz, body_bb, end_bb)
        self.builder.position_at_end(body_bb)
        for s in st.body: self.gen_stmt(s, env)
        if not self.builder.block.is_terminated: self.builder.branch(cond_bb)
        self.builder.position_at_end(end_bb)

    def _gen_for(self, st, env):
        irf = self.builder.function
        cond_bb = irf.append_basic_block("for.cond"); body_bb = irf.append_basic_block("for.body"); inc_bb = irf.append_basic_block("for.inc"); end_bb = irf.append_basic_block("for.end")
        iv_slot = self.builder.alloca(ir.IntType(64), name=st.var); env[st.var] = iv_slot
        start = self.gen_expr(st.start, env); self.builder.store(start, iv_slot); self.builder.branch(cond_bb)
        self.builder.position_at_end(cond_bb)
        iv = self.builder.load(iv_slot); endv = self.gen_expr(st.end, env)
        cond = self.builder.icmp_signed("<", iv, endv); self.builder.cbranch(cond, body_bb, end_bb)
        self.builder.position_at_end(body_bb)
        for s in st.body: self.gen_stmt(s, env)
        if not self.builder.block.is_terminated: self.builder.branch(inc_bb)
        self.builder.position_at_end(inc_bb)
        iv = self.builder.load(iv_slot); one = ir.Constant(ir.IntType(64), 1)
        self.builder.store(self.builder.add(iv, one), iv_slot); self.builder.branch(cond_bb)
        self.builder.position_at_end(end_bb)

    def gen_expr(self, e, env):
        ARef = A
        if isinstance(e, ARef.IntLit): return ir.Constant(ir.IntType(64), parse_base12_int(e.text))
        if isinstance(e, ARef.FloatLit): return ir.Constant(ir.IntType(64), int(float(e.text)))
        if isinstance(e, ARef.StringLit): return ir.Constant(ir.IntType(64), 0)
        if isinstance(e, ARef.Name):
            slot = env.get(e.id); 
            if slot is None: 
                try:
                    callee = self.module.get_global(e.id)  # extern?
                    return callee
                except:
                    raise NameError(f"Undefined name: {e.id}")
            return self.builder.load(slot)
        if isinstance(e, ARef.BinOp):
            l = self.gen_expr(e.left, env); r = self.gen_expr(e.right, env)
            if e.op == '+': return self.builder.add(l, r)
            if e.op == '-': return self.builder.sub(l, r)
            if e.op == '*': return self.builder.mul(l, r)
            if e.op == '/': return self.builder.sdiv(l, r)
            raise NotImplementedError(e.op)
        if isinstance(e, ARef.Call):
            if isinstance(e.func, ARef.Name) and e.func.id == "say":
                return self._gen_say(e.args, env)
            # extern or user function
            fn_name = e.func.id if isinstance(e.func, ARef.Name) else None
            callee = self.module.globals.get(fn_name)
            if callee is None:
                # auto-declare extern with i64 params/void return for pack-style calls
                ft = ir.FunctionType(ir.IntType(64), [ir.IntType(64) for _ in e.args])
                callee = ir.Function(self.module, ft, name=fn_name)
            args = [self.gen_expr(a, env) for a in e.args]
            return self.builder.call(callee, args)
        raise NotImplementedError(type(e))

    def _gen_say(self, args, env):
        fmt_parts = []; vargs = []
        for a in args:
            if isinstance(a, A.StringLit):
                fmt_parts.append("%s"); c = self.cstr(a.value)
                zero = ir.Constant(ir.IntType(32), 0); ptr = self.builder.gep(c, [zero, zero], inbounds=True)
                vargs.append(ptr)
            else:
                fmt_parts.append("%lld"); vargs.append(self.gen_expr(a, env))
        fmt = " ".join(fmt_parts) + "\\n"
        g = self.cstr(fmt); zero = ir.Constant(ir.IntType(32), 0)
        ptr = self.builder.gep(g, [zero, zero], inbounds=True)
        return self.builder.call(self.printf, [ptr, *vargs])
