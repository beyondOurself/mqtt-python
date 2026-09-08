# -*- coding: utf-8 -*-
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from mqtt_tool.version import APP_NAME, bump_build, exe_basename, format_full, save_version_data

BUILD_OUT = os.path.join(ROOT, ".build_out.txt")
VERSION_INFO = os.path.join(ROOT, "version_info.txt")
DATA_SEP = ";" if os.name == "nt" else ":"


def _write_version_info(data, exe_name):
    major = int(data["major"])
    minor = int(data["minor"])
    patch = int(data["patch"])
    build = int(data["build"])
    full = format_full(data)
    content = """# UTF-8
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(%d, %d, %d, %d),
    prodvers=(%d, %d, %d, %d),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'080404b0',
        [StringStruct(u'CompanyName', u''),
        StringStruct(u'FileDescription', u'%s'),
        StringStruct(u'FileVersion', u'%s'),
        StringStruct(u'InternalName', u'MQTTTool'),
        StringStruct(u'LegalCopyright', u''),
        StringStruct(u'OriginalFilename', u'%s.exe'),
        StringStruct(u'ProductName', u'%s'),
        StringStruct(u'ProductVersion', u'%s')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [2052, 1200])])
  ]
)
""" % (
        major,
        minor,
        patch,
        build,
        major,
        minor,
        patch,
        build,
        APP_NAME,
        full,
        exe_name,
        APP_NAME,
        full,
    )
    with open(VERSION_INFO, "w", encoding="utf-8") as f:
        f.write(content)


def _copy_if_exists(name, dist_dir):
    src = os.path.join(ROOT, name)
    if os.path.isfile(src):
        import shutil

        shutil.copy2(src, os.path.join(dist_dir, name))


def _prune_spec_files(keep=2):
    prefix = APP_NAME + "_"
    specs = []
    for name in os.listdir(ROOT):
        if name.startswith(prefix) and name.endswith(".spec"):
            path = os.path.join(ROOT, name)
            if os.path.isfile(path):
                specs.append(path)
    specs.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    for path in specs[keep:]:
        try:
            os.remove(path)
            print("已删除旧 spec:", os.path.basename(path))
        except OSError as e:
            print("删除 spec 失败 %s: %s" % (path, e), file=sys.stderr)


def main():
    os.chdir(ROOT)
    version_path = os.path.join(ROOT, "version.json")
    data = bump_build(version_path)
    exe_name = exe_basename(data)
    _write_version_info(data, exe_name)

    data_src = os.path.join("mqtt_tool", "data", "templates.default.json")
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--windowed",
        "--onefile",
        "--name",
        exe_name,
        "--version-file",
        VERSION_INFO,
        "--paths",
        ROOT,
        "--add-data",
        "%s%s%s" % (data_src, DATA_SEP, os.path.join("mqtt_tool", "data")),
        "launch.py",
    ]
    subprocess.run(cmd, check=True)
    _prune_spec_files(keep=2)

    dist_dir = os.path.join(ROOT, "dist")
    _copy_if_exists("templates.json", dist_dir)
    save_version_data(data, os.path.join(dist_dir, "version.json"))

    out_exe = os.path.join(dist_dir, exe_name + ".exe")
    with open(BUILD_OUT, "w", encoding="utf-8") as f:
        f.write(out_exe)
    print(out_exe)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except subprocess.CalledProcessError as e:
        print("PyInstaller 失败: %s" % e, file=sys.stderr)
        raise SystemExit(1)
