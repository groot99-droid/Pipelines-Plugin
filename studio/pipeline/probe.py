"""What the machine is doing right now, as one JSON object. Standard library only.

    python studio/pipeline/probe.py [--out FILE]

Reads the host kind, the machine model, the GPU, memory, power, thermal
readings and disk headroom, and prints them for compute_gate.py. A reading it
cannot take is null, never a made-up zero. It changes nothing on the machine.

On Windows and WSL the readings come from one PowerShell call (CIM classes);
on Linux from /proc and /sys. macOS is reported as host.kind "unknown": the
studio does not run there.

Rewritten from Creative-Headquarters' bash probe, whose Windows branch never
ran on the laptop. This one is a single file with no extraction step.
"""

import argparse
import json
import math
import os
import platform
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent

POWERSHELL_QUERY = r"""
$ErrorActionPreference = 'SilentlyContinue'
$out = @{}
$cs = Get-CimInstance Win32_ComputerSystem
$os = Get-CimInstance Win32_OperatingSystem
$out.model = $cs.Model
$out.total_kb = $os.TotalVisibleMemorySize
$out.free_kb = $os.FreePhysicalMemory
$out.pagefile_mb = (Get-CimInstance Win32_PageFileUsage | Measure-Object -Property CurrentUsage -Sum).Sum
$out.gpu = (Get-CimInstance Win32_VideoController | Select-Object -First 1).Name
$bat = Get-CimInstance Win32_Battery
$out.battery_count = @($bat).Count
$out.battery_status = if ($bat) { @($bat)[0].BatteryStatus } else { $null }
$out.battery_pct = if ($bat) { @($bat)[0].EstimatedChargeRemaining } else { $null }
$tz = Get-CimInstance -Namespace root/wmi MSAcpi_ThermalZoneTemperature | Select-Object -First 1
$out.thermal_tenths_k = if ($tz) { $tz.CurrentTemperature } else { $null }
$perf = Get-CimInstance Win32_PerfFormattedData_Counters_ProcessorInformation | Where-Object { $_.Name -eq '_Total' }
$out.cpu_perf_pct = if ($perf) { $perf.PercentProcessorPerformance } else { $null }
$out.system_free_bytes = (Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'").FreeSpace
$out | ConvertTo-Json -Compress
"""


def host_kind():
    system = platform.system()
    if system == "Windows":
        return "windows"
    if system == "Linux":
        if os.environ.get("WSL_DISTRO_NAME"):
            return "wsl"
        try:
            if "microsoft" in Path("/proc/version").read_text(encoding="utf-8").lower():
                return "wsl"
        except OSError:
            pass
        return "linux"
    return "unknown"


def number(value):
    """A float, or None for anything that is not a number."""
    try:
        if value is None or isinstance(value, bool):
            return None
        out = float(value)
        return out if math.isfinite(out) else None
    except (TypeError, ValueError):
        return None


def read_first(*paths):
    for path in paths:
        try:
            return Path(path).read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return None


def run(command, timeout=20):
    try:
        done = subprocess.run(command, capture_output=True, text=True, timeout=timeout, encoding="utf-8",
                              errors="replace")
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def windows_readings():
    """One PowerShell call. Everything null when the bridge is missing."""
    shell = next((name for name in ("powershell.exe", "pwsh.exe", "pwsh") if shutil.which(name)), None)
    if not shell:
        return {}
    text = run([shell, "-NoProfile", "-NonInteractive", "-Command", POWERSHELL_QUERY], timeout=40)
    if not text:
        return {}
    try:
        return json.loads(text.strip().splitlines()[-1])
    except (json.JSONDecodeError, IndexError):
        return {}


def probe_windows(kind):
    r = windows_readings()
    total = number(r.get("total_kb"))
    free = number(r.get("free_kb"))
    total_gb = round(total / 1048576, 1) if total else None
    available_gb = round(free / 1048576, 1) if free else None
    status = r.get("battery_status")
    count = number(r.get("battery_count"))
    if isinstance(status, (int, float)) and not isinstance(status, bool):
        source = "battery" if int(status) == 1 else "ac"
    elif count == 0:
        source = "ac"
    else:
        source = None
    tenths = number(r.get("thermal_tenths_k"))
    temp_c = round(tenths / 10 - 273.15, 1) if tenths else None
    system_free = number(r.get("system_free_bytes"))
    gpu_name = r.get("gpu") if isinstance(r.get("gpu"), str) else None
    return {
        "host": {"kind": kind, "machine": r.get("model") if isinstance(r.get("model"), str) else None},
        "gpu": gpu_block(gpu_name),
        "memory": memory_block(total_gb, available_gb, number(r.get("pagefile_mb"))),
        "power": {"source": source, "battery_pct": number(r.get("battery_pct"))},
        "thermal": {"cpu_temp_c": temp_c, "cpu_perf_pct": number(r.get("cpu_perf_pct"))},
        "disk": disk_block(round(system_free / 1073741824, 1) if system_free else None),
    }


def probe_linux(kind):
    meminfo = {}
    text = read_first("/proc/meminfo") or ""
    for line in text.splitlines():
        key, _, rest = line.partition(":")
        value = number(rest.split()[0]) if rest.split() else None
        meminfo[key.strip()] = value
    total_gb = round(meminfo["MemTotal"] / 1048576, 1) if meminfo.get("MemTotal") else None
    available_gb = round(meminfo["MemAvailable"] / 1048576, 1) if meminfo.get("MemAvailable") else None
    swap_used = None
    if meminfo.get("SwapTotal") is not None and meminfo.get("SwapFree") is not None:
        swap_used = round((meminfo["SwapTotal"] - meminfo["SwapFree"]) / 1024)
    machine = read_first("/sys/class/dmi/id/product_version", "/sys/class/dmi/id/product_name")
    gpu_name = None
    lspci = run(["lspci"], timeout=5)
    if lspci:
        gpu_name = next((line.split(":", 2)[-1].strip() for line in lspci.splitlines()
                         if "VGA" in line or "3D controller" in line), None)
    source = None
    for supply in sorted(Path("/sys/class/power_supply").glob("A*")) if Path("/sys/class/power_supply").is_dir() else []:
        online = read_first(supply / "online")
        if online in ("0", "1"):
            source = "ac" if online == "1" else "battery"
            break
    batteries = list(Path("/sys/class/power_supply").glob("BAT*")) if Path("/sys/class/power_supply").is_dir() else []
    if source is None and not batteries and Path("/sys/class/power_supply").is_dir():
        source = "ac"
    battery_pct = number(read_first(*[b / "capacity" for b in batteries])) if batteries else None
    temp = number(read_first("/sys/class/thermal/thermal_zone0/temp"))
    temp_c = round(temp / 1000, 1) if temp else None
    perf = None
    cur = number(read_first("/sys/devices/system/cpu/cpu0/cpufreq/scaling_cur_freq"))
    top = number(read_first("/sys/devices/system/cpu/cpu0/cpufreq/cpuinfo_max_freq"))
    if cur and top:
        perf = round(100 * cur / top)
    system_free = None
    try:
        system_free = round(shutil.disk_usage("/").free / 1073741824, 1)
    except OSError:
        pass
    return {
        "host": {"kind": kind, "machine": machine},
        "gpu": gpu_block(gpu_name),
        "memory": memory_block(total_gb, available_gb, swap_used),
        "power": {"source": source, "battery_pct": battery_pct},
        "thermal": {"cpu_temp_c": temp_c, "cpu_perf_pct": perf},
        "disk": disk_block(system_free),
    }


def gpu_block(name):
    discrete = shutil.which("nvidia-smi") is not None
    status = "discrete" if discrete else ("integrated" if name else "none")
    return {"status": status, "name": name, "vram_total_gb": None, "memory_shared_with_system": not discrete}


def memory_block(total_gb, available_gb, swap_used_mb):
    claim = None
    if total_gb is not None and available_gb is not None:
        claim = max(0, min(math.floor(available_gb * 0.6), math.floor(total_gb - 4)))
    free_pct = round(100 * available_gb / total_gb) if total_gb and available_gb is not None else None
    return {"total_gb": total_gb, "available_gb": available_gb, "free_pct": free_pct,
            "swap_used_mb": swap_used_mb, "dynamic_claim_limit_gb": claim}


def disk_block(system_free_gb):
    free = None
    try:
        free = round(shutil.disk_usage(HERE).free / 1073741824, 1)
    except OSError:
        pass
    return {"free_gb": free, "system_free_gb": system_free_gb}


def probe():
    kind = host_kind()
    if kind in ("windows", "wsl"):
        found = probe_windows(kind)
    elif kind == "linux":
        found = probe_linux(kind)
    else:
        found = {"host": {"kind": kind, "machine": platform.machine() or None}, "gpu": gpu_block(None),
                 "memory": memory_block(None, None, None), "power": {"source": None, "battery_pct": None},
                 "thermal": {"cpu_temp_c": None, "cpu_perf_pct": None}, "disk": disk_block(None)}
    found["host"]["name"] = platform.node() or None
    found["ts_epoch"] = int(time.time())
    found["probe"] = "rosw/probe/v1"
    return found


def main(argv=None):
    parser = argparse.ArgumentParser(prog="probe.py", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", help="write here instead of stdout")
    args = parser.parse_args(argv)
    text = json.dumps(probe(), indent=2)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
