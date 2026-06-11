#!/usr/bin/env bash
set -euo pipefail

[ -n "${SOURCE_DATE_EPOCH:-}" ] || unset SOURCE_DATE_EPOCH
: "${SANITIZER_FLAGS=-fsanitize=address,undefined -fno-sanitize-recover=all -fno-omit-frame-pointer -g}"
: "${CC:=clang}" ; : "${CXX:=clang++}"
: "${MAYHEM_JOBS:=$(nproc)}"
export CC CXX MAYHEM_JOBS

cd "$SRC"

# Test oracle: clean venv (no sanitizers).
python3 -m venv /mayhem/test-venv
/mayhem/test-venv/bin/pip install --upgrade pip setuptools wheel
(
  export CC=clang CXX=clang++
  unset CFLAGS CXXFLAGS LDFLAGS
  /mayhem/test-venv/bin/pip install -e ".[dev]"
)

# Fuzz build: separate venv with atheris + PyInstaller ELF.
python3 -m venv /mayhem/fuzz-venv
/mayhem/fuzz-venv/bin/pip install --upgrade pip setuptools wheel
export CFLAGS="$SANITIZER_FLAGS" CXXFLAGS="$SANITIZER_FLAGS" LDFLAGS="$SANITIZER_FLAGS"
/mayhem/fuzz-venv/bin/pip install atheris pyinstaller
/mayhem/fuzz-venv/bin/pip install -e .

$CC -shared -fPIC -o /mayhem/asan_defaults.so "$SRC/mayhem/asan_defaults.c"

/mayhem/fuzz-venv/bin/pyinstaller \
  --distpath /tmp/pyinst-out \
  --workpath /tmp/pyinst-work \
  --specpath /tmp/pyinst-spec \
  --onefile \
  --name fuzz-lang \
  --paths "$SRC/mayhem" \
  --collect-all sqlglot \
  --hidden-import fuzz_helpers \
  --hidden-import difflib \
  --hidden-import importlib \
  --hidden-import json \
  --hidden-import re \
  --hidden-import decimal \
  --hidden-import datetime \
  --hidden-import collections \
  --hidden-import functools \
  --hidden-import itertools \
  --hidden-import typing \
  --hidden-import enum \
  --hidden-import copy \
  --hidden-import dataclasses \
  --hidden-import abc \
  --hidden-import logging \
  --hidden-import textwrap \
  --hidden-import statistics \
  --hidden-import heapq \
  --hidden-import math \
  --hidden-import numbers \
  --hidden-import sys \
  --hidden-import os \
  --add-binary /mayhem/asan_defaults.so:. \
  "$SRC/mayhem/fuzz_lang.py"

install -m 0755 /tmp/pyinst-out/fuzz-lang /mayhem/fuzz-lang
