import os
import json
from pathlib import Path

from task3 import benchmark


def make_test_file(src_path: Path, dest_path: Path, target_size: int):
    content = src_path.read_text(encoding="utf-8", errors="ignore")
    if not content:
        content = "// sample\n"
    # Repeat content until target size
    multiplier = max(1, (target_size // max(1, len(content))))
    data = (content * (multiplier + 1))[:target_size]
    dest_path.write_text(data, encoding="utf-8")


def produce_report(results_list, task2_code: str, out_tex: Path):
    header = r"""
\documentclass[a4paper,11pt]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{lmodern}
\usepackage{hyperref}
\usepackage{parskip}
\usepackage{geometry}
\geometry{margin=1in}
\title{Lab 2 Report -- Double Buffering, Producer/Consumer, and Benchmarking (Generated)}
\author{Compiled by Student}
\date{\today}
\begin{document}
\maketitle
\section*{Summary}
This report contains source code for the multi-threaded buffer implementation, performance comparison results between single-buffer and double-buffer approaches, and test results on files of varying sizes.

"""

    footer = r"""
\section*{Conclusions}
Double buffering generally reduces pauses due to I/O and can improve throughput; results below quantify the effect for the tested files and configuration.
\end{document}
"""

    with out_tex.open("w", encoding="utf-8") as f:
        f.write(header)

        f.write("\section*{Source Code: Multi-threaded Buffer Implementation}\n")
        f.write("The following is the `task2.py` producer/consumer implementation used in this lab.\n\n")
        f.write("\\begin{verbatim}\n")
        f.write(task2_code)
        f.write("\\end{verbatim}\n\n")

        f.write("\section*{Benchmark Configuration and Results}\n")
        f.write("The benchmarks were run using `task3.py`'s `benchmark()` function with a buffer size of 4096 bytes. Results below list times (ms), average fill durations, and measured improvements.\n\n")

        f.write("\\begin{tabular}{lrrrrr}\n")
        f.write("\\hline\n")
        f.write("File & Size (bytes) & Single ms & Double ms & FillAvg single(ms) & FillAvg double(ms)\\\\\n")
        f.write("\\hline\n")
        for r in results_list:
            f.write(f"{r['filename']} & {r['total_file_size']} & {r['single_time_ms']:.3f} & {r['double_time_ms']:.3f} & {r['single_fill_avg_ms']:.4f} & {r['double_fill_avg_ms']:.4f}\\\\\n")
        f.write("\\hline\n")
        f.write("\\end{tabular}\n\n")

        f.write("\\section*{Detailed Results (JSON)}\n")
        f.write("\\begin{verbatim}\n")
        f.write(json.dumps(results_list, indent=2))
        f.write("\\end{verbatim}\n\n")

        f.write(footer)


def main():
    cwd = Path(__file__).parent
    src = cwd / "tasksampel.cpp"
    if not src.exists():
        print("Source sample file not found:", src)
        return

    # Define test targets: small (~1KB), medium (~50KB), large (~1MB)
    targets = [
        ("sample_small.cpp", 1024),
        ("sample_medium.cpp", 50 * 1024),
        ("sample_large.cpp", 1024 * 1024),
    ]

    generated = []
    for name, size in targets:
        path = cwd / name
        print(f"Creating {name} ({size} bytes)")
        make_test_file(src, path, size)
        generated.append(path)

    results = []
    for p in generated:
        print(f"Benchmarking: {p.name}")
        res = benchmark(str(p), buffer_size=4096)
        results.append(res)

    # Read task2 code to embed in report
    task2_path = cwd / "task2.py"
    task2_code = task2_path.read_text(encoding="utf-8") if task2_path.exists() else "(task2.py not found)"

    out_tex = cwd / "Lab2_report_generated.tex"
    produce_report(results, task2_code, out_tex)
    print("Wrote report:", out_tex)
    # Also write json
    with (cwd / "bench_results.json").open("w", encoding="utf-8") as jf:
        json.dump(results, jf, indent=2)


if __name__ == "__main__":
    main()
