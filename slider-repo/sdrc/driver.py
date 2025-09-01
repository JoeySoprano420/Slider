
import argparse, os, sys
from .lexer import Lexer
from .parser import Parser
from .irgen import IRGen

def build(src_path: str, out_path: str):
    with open(src_path, "r", encoding="utf-8") as f:
        src = f.read()
    toks = Lexer(src).lex()
    mod = Parser(toks).parse()
    irg = IRGen(module_name=os.path.basename(src_path))
    module = irg.gen_module(mod)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(str(module))
    print(f"[sdrc] wrote {out_path}")

def main():
    ap = argparse.ArgumentParser(prog="sdrc", description="Slider compiler (scaffold)")
    sp = ap.add_subparsers(dest="cmd")

    b = sp.add_parser("build", help="Build a .sdr file to LLVM IR (.ll)")
    b.add_argument("source", help="path to .sdr file")
    b.add_argument("-o", "--out", default="build/out.ll", help="output .ll path")

    args = ap.parse_args()
    if args.cmd == "build":
        return build(args.source, args.out)
    ap.print_help()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[sdrc] error: {e}", file=sys.stderr)
        sys.exit(1)
