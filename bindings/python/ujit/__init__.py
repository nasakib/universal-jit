"""
Universal JIT (ujit) Python Interface
High-performance algorithmic pseudocode to bare-metal native machine code compiler.
Seamlessly integrates with ClothOS, Ray clusters, and heterogenous runtime environments.
"""

import ctypes
import os
import sys
from typing import List, Optional, Callable, Any

def _find_library() -> str:
    possible_paths = [
        # Relative to package
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../lib/libujit.so")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../../lib/libujit.so")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "../lib/libujit.so")),
        os.path.abspath(os.path.join(os.path.dirname(__file__), "libujit.so")),
        # Absolute workspace path
        "/mnt/c/Users/natsa/Documents/universal-jit/lib/libujit.so",
        "C:\\Users\\natsa\\Documents\\universal-jit\\lib\\libujit.so",
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return p
    # Fallback to dynamic loader
    return "libujit.so"

_lib = None

def _get_lib():
    global _lib
    if _lib is None:
        lib_path = _find_library()
        try:
            _lib = ctypes.CDLL(lib_path)
        except OSError:
            raise RuntimeError(
                f"Could not load Universal JIT shared library. Checked path: {lib_path}. "
                "Ensure 'make' has been run in the universal-jit root directory."
            )

        # Function signatures
        _lib.ujit_create.restype = ctypes.c_void_p
        _lib.ujit_create.argtypes = []

        _lib.ujit_destroy.restype = None
        _lib.ujit_destroy.argtypes = [ctypes.c_void_p]

        _lib.ujit_compile_string.restype = ctypes.c_int
        _lib.ujit_compile_string.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        _lib.ujit_compile_file.restype = ctypes.c_int
        _lib.ujit_compile_file.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        _lib.ujit_get_fn.restype = ctypes.c_void_p
        _lib.ujit_get_fn.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        _lib.ujit_call.restype = ctypes.c_int64
        _lib.ujit_call.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.POINTER(ctypes.c_int64),
            ctypes.c_size_t,
        ]

        _lib.ujit_dump_ir.restype = None
        _lib.ujit_dump_ir.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

        _lib.ujit_dump_bytes.restype = None
        _lib.ujit_dump_bytes.argtypes = [ctypes.c_void_p, ctypes.c_char_p]

    return _lib


class JITFunction:
    """A callable compiled bare-metal native function."""
    def __init__(self, ctx: "Context", name: str):
        self.ctx = ctx
        self.name = name

    def __call__(self, *args: int) -> int:
        return self.ctx.call(self.name, *args)


class Context:
    """Universal JIT Compiler Context."""
    def __init__(self):
        lib = _get_lib()
        self._ctx = lib.ujit_create()
        if not self._ctx:
            raise MemoryError("Failed to allocate Universal JIT context")

    def __del__(self):
        if hasattr(self, "_ctx") and self._ctx:
            _get_lib().ujit_destroy(self._ctx)
            self._ctx = None

    def compile(self, source: str) -> "Context":
        lib = _get_lib()
        status = lib.ujit_compile_string(self._ctx, source.encode("utf-8"))
        if status != 0:
            raise ValueError(f"Universal JIT compilation error code: {status}")
        return self

    def compile_file(self, filepath: str) -> "Context":
        lib = _get_lib()
        status = lib.ujit_compile_file(self._ctx, filepath.encode("utf-8"))
        if status != 0:
            raise ValueError(f"Universal JIT compilation error code: {status}")
        return self

    def get_fn(self, name: str) -> JITFunction:
        lib = _get_lib()
        fn_ptr = lib.ujit_get_fn(self._ctx, name.encode("utf-8"))
        if not fn_ptr:
            raise KeyError(f"Function '{name}' not found in JIT context")
        return JITFunction(self, name)

    def call(self, name: str, *args: int) -> int:
        lib = _get_lib()
        c_args = (ctypes.c_int64 * len(args))(*args) if args else None
        return int(lib.ujit_call(self._ctx, name.encode("utf-8"), c_args, len(args)))

    def dump_ir(self, name: Optional[str] = None):
        lib = _get_lib()
        c_name = name.encode("utf-8") if name else None
        lib.ujit_dump_ir(self._ctx, c_name)

    def dump_bytes(self, name: Optional[str] = None):
        lib = _get_lib()
        c_name = name.encode("utf-8") if name else None
        lib.ujit_dump_bytes(self._ctx, c_name)


def compile(source: str) -> Context:
    """Compile a pseudocode snippet into a new JIT context."""
    ctx = Context()
    ctx.compile(source)
    return ctx


def kernel(source_code: str):
    """
    Decorator / Helper for defining native bare-metal ClothOS compute kernels.
    Example:
        @ujit.kernel('''
        fn solve(x: int) -> int {
            return x * 42 + 7
        }
        ''')
        def solve(x: int) -> int:
            ...
    """
    ctx = Context()
    ctx.compile(source_code)
    def decorator(fn):
        fn_name = fn.__name__
        return ctx.get_fn(fn_name)
    return decorator
