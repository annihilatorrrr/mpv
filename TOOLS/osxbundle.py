#!/usr/bin/env python3
import os
import shutil
import sys
import fileinput
from optparse import OptionParser

def sh(command):
    return os.popen(command).read().strip()

def bundle_path(binary_name):
    return f"{binary_name}.app"

def bundle_name(binary_name):
    return os.path.basename(bundle_path(binary_name))

def target_plist(binary_name):
    return os.path.join(bundle_path(binary_name), 'Contents', 'Info.plist')

def target_directory(binary_name):
    return os.path.join(bundle_path(binary_name), 'Contents', 'MacOS')

def target_binary(binary_name):
    return os.path.join(target_directory(binary_name),
                        os.path.basename(binary_name))

def copy_bundle(binary_name):
    if os.path.isdir(bundle_path(binary_name)):
        shutil.rmtree(bundle_path(binary_name))
    shutil.copytree(
        os.path.join('TOOLS', 'osxbundle', bundle_name(binary_name)),
        bundle_path(binary_name))

def copy_binary(binary_name):
    shutil.copy(binary_name, target_binary(binary_name))

def apply_plist_template(plist_file, version):
    for line in fileinput.input(plist_file, inplace=1):
        print(line.rstrip().replace('${VERSION}', version))

def create_bundle_symlink(binary_name, symlink_name):
    os.symlink(os.path.basename(binary_name),
               os.path.join(target_directory(binary_name), symlink_name))

def bundle_version():
    if os.path.exists('VERSION'):
        with open('VERSION') as x:
            version = x.read()
    else:
        version = sh("./version.sh").strip()
    return version

def main():
    version = bundle_version().rstrip()

    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-s", "--skip-deps", action="store_false", dest="deps",
                      default=True,
                      help="don't bundle the dependencies")

    (options, args) = parser.parse_args()

    if len(args) != 1:
        parser.error("incorrect number of arguments")
    else:
        binary_name = args[0]

    print(f"Creating Mac OS X application bundle (version: {version})...")
    print("> copying bundle skeleton")
    copy_bundle(binary_name)
    print("> copying binary")
    copy_binary(binary_name)
    print("> create bundle symlink")
    create_bundle_symlink(binary_name, "mpv-bundle")
    print("> generating Info.plist")
    apply_plist_template(target_plist(binary_name), version)

    if options.deps:
        print("> bundling dependencies")
        print(sh(" ".join(["TOOLS/dylib-unhell.py", target_binary(binary_name)])))

    print("done.")

if __name__ == "__main__":
    main()
