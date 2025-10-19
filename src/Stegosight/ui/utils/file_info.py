from __future__ import annotations


def format_file_size(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    value = float(size)
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.2f} {unit}"
        value /= 1024
    return f"{value:.2f} TB"


def estimate_capacity(size: int) -> str:
    approx = size * 0.15
    return f"~{format_file_size(int(approx))} ของข้อมูลลับ"


__all__ = ["format_file_size", "estimate_capacity"]
