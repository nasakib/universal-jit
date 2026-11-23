# Universal JIT (`ujit`)

Universal JIT (`ujit`) is a lightweight C99 just-in-time compiler that transforms algorithmic pseudocode into native machine code (x86-64 / RV64) at runtime.

It was designed to provide fast kernel synthesis for ClothOS distributed computing nodes, language virtual machines (such as MiniVM, LuaJIT, and YJIT), and dynamic execution engines.

## Key Capabilities

- Low Compilation Latency: In-memory parsing, IR creation, and native code emission take under 0.1 ms per routine.
- Direct Executable Memory: Emits x86-64 machine instructions into executable memory pages allocated via `mmap` (POSIX) or `VirtualAlloc` (Windows).
- Standalone C Architecture: Zero third-party dependencies; written in modular C99.
- Multi-Language Accessibility:
  - C ABI interface (`include/ujit.h`)
  - Python ctypes wrapper (`bindings/python/ujit/`)
  - Integration adapters for MiniVM (`adapters/minivm/`) and ClothOS (`adapters/clothos/`)

## Pseudocode Syntax

The parser accepts structured algorithmic pseudocode:

```text
fn collatz(n: int) -> int {
    let steps = 0
    while n > 1 {
        if n % 2 == 0 {
            n = n / 2
        } else {
            n = 3 * n + 1
        }
        steps = steps + 1
    }
    return steps
}
```

Supported elements:
- Functions: `fn name(param: type, ...) -> type { ... }`
- Variables: `let var = expr` and assignments `var = expr`
- Control flow: `if cond { ... } else { ... }`, `while cond { ... }`
- Binary operations: `+`, `-`, `*`, `/`, `%`, `&`, `|`, `^`, `==`, `!=`, `<`, `<=`, `>`, `>=`
- Comments: `#` (Python), `//` (C), `--` (Lua)

## Build Instructions

Using standard `make` (via GCC or Clang):

```bash
make
make test
make bench
```

Outputs:
- `lib/libujit.a`: Static library
- `lib/libujit.so`: Dynamic shared library
- `bin/ujit`: Command line executable runner
- `bin/test_ujit`: Test harness
- `bin/bench_ujit`: Performance benchmark suite

## Command-Line Usage

```bash
# Run a specific function with arguments
./bin/ujit run examples/collatz.pseudo collatz 27

# Dump Intermediate Representation and hex machine code
./bin/ujit dump examples/collatz.pseudo collatz

# Evaluate an inline expression
./bin/ujit eval "fn f(x: int) -> int { return x * 10 }" f 5
```

## Python and ClothOS Example

```python
import ujit

ctx = ujit.compile("""
fn compute(power: int, rate: int) -> int {
    let raw = power * rate
    return (raw * 92) / 100
}
""")
fn = ctx.get_fn("compute")
print(fn(100, 50))
```
