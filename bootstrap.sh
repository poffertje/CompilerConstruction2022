#!/usr/bin/env bash
set -e

realcd() {
    builtin cd "$1"
}

root="$(realcd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exec 5> "$root/bootstrap.log"
run() {
    echo "====== Exec \"$*\"" >&5
    set +e
    out=$("$@" 2>&1)
    ret=$?
    set -e
    echo "$out" >&5
    if [ $ret -ne 0 ]; then
        echo "Error during command $*:"
        echo "$out"
        echo
        echo "See bootstrap.log for full installation log"
        exit 1
    fi
    echo "====== Done" >&5
}


sudocmd=sudo
tarextractopts=()
if [ $UID -eq 0 ]; then
    # We're already root, no need for sudo
    sudocmd=
    # Instruct tar to extract and not preserve files owner, effectively changing
    # it to root. This allows to extract files in a bind-mount folder e.g.
    # inside a container.
    tarextractopts=(--no-same-owner)
fi

if [[ "$OSTYPE" == "linux-gnu" ]]; then
    DEPS=(build-essential wget git cmake ninja-build python3 virtualenv libtinfo-dev libtinfo5 zlib1g-dev libxml2-dev)
    echo "[+] Installing dependencies: " "${DEPS[@]}"
    DEBIAN_FRONTEND=noninteractive run $sudocmd apt-get install --assume-yes "${DEPS[@]}"
    jobs=$(nproc)
    [ "$jobs" -eq 0 ] && jobs=1
elif [[ "$OSTYPE" == "darwin"* ]]; then
    if ! [ -x "$(command -v brew)" ]; then
        # Install xcode cli: xcode-select --install
        echo "[+] Installing homebrew"
        /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
    fi
    DEPS=(wget git cmake ninja python3)
    echo "[+] Installing dependencies: " "${DEPS[@]}"
    brew install "${DEPS[@]}" || true
    pip3 install virtualenv || true
    jobs=$(sysctl -n hw.ncpu)
    [ "$jobs" -eq 0 ] && jobs=1
fi


pathsrc="$root/lib/src"
pathbuild="$root/lib/build"
pathinstall="$root/lib/install"

versionllvm=10.0.1
llvmurl=https://github.com/llvm/llvm-project/releases/download/llvmorg-$versionllvm
llvm=llvm-$versionllvm
clang=clang-$versionllvm
versionllvmlite=0.34.0
commitllvmlite=c5889c9
llvmlite=llvmlite-$versionllvmlite
frontend=frontend
optalias=myopt

case $(uname -m) in
    x86[-_]64|amd64|AMD64)
        if [[ "$OSTYPE" == "linux-gnu" ]]; then
            llvmbindist="clang+llvm-$versionllvm-x86_64-linux-gnu-ubuntu-16.04.tar.xz"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            llvmbindist="clang+llvm-$versionllvm-x86_64-apple-darwin.tar.xz"
        fi
        ;;
    arm64|ARM64|aarch64|AARCH64)
        if [[ "$OSTYPE" == "linux-gnu" ]]; then
            llvmbindist="clang+llvm-$versionllvm-aarch64-linux-gnu.tar.xz"
        fi
        ;;
esac

mkdir -p "$pathsrc" "$pathbuild" "$pathinstall"

# get LLVM core
echo "[+] Downloading LLVM core"
if [ ! -d "$pathsrc/$llvm" ]; then
    realcd "$pathsrc"
    run wget $llvmurl/$llvm.src.tar.xz
    run tar -xf $llvm.src.tar.xz "${tarextractopts[@]}"
    run mv $llvm.src $llvm
    run rm $llvm.src.tar.xz
fi

# get Clang
echo "[+] Downloading Clang"
if [ ! -d "$pathsrc/$llvm/tools/clang" ]; then
    realcd "$pathsrc"
    run wget $llvmurl/$clang.src.tar.xz
    run tar -xf $clang.src.tar.xz "${tarextractopts[@]}"
    run mv $clang.src $llvm/tools/clang
    run rm $clang.src.tar.xz
fi

# get llvmlite
echo "[+] Downloading llvmlite"
if [ ! -d "$pathsrc/$llvmlite" ]; then
    realcd "$pathsrc"
    run git clone https://github.com/numba/llvmlite.git $llvmlite
    realcd "$llvmlite"
    run git checkout --detach $commitllvmlite
    run patch -p1 < "$root/support/${llvmlite}-spaces.patch"
fi

# build & install LLVM
echo "[+] Installing LLVM"
if [ -n "$llvmbindist" ]; then
    # Try using the prebuilt LLVM which saves 1-2 hours of compiling

    if [ ! -f "$pathinstall/bin/clang" ]; then
        realcd "$pathinstall"
        if [ ! -f "$pathinstall/$llvmbindist" ]; then
            echo "[+] Fetching LLVM bindist"
            run wget "$llvmurl/$llvmbindist"
        fi
        echo "[+] Unpacking LLVM bindist"
        run tar --strip-components=1 -xf "$llvmbindist" "${tarextractopts[@]}"

        # Test to see if the clang is compatible with this system
        if ! echo "" | bin/clang -xc -S -o- - 2>&5 >/dev/null; then
            echo "[+] LLVM bindist not compatible with this system, removing "
            echo "    and falling back to building LLVM"
            realcd ..
            rm -rf "$pathinstall"
            mkdir -p "$pathinstall"
        fi
    fi
fi

if [ ! -d "$pathbuild/$llvm" ]; then
    mkdir -p "$pathbuild/$llvm"
    realcd "$pathbuild/$llvm"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        mkdir -p "$pathinstall/include"
        ln -s "$(dirname "$(xcrun -find clang)")/../include/c++" "$pathinstall/include/c++"
    fi
    [ -f rules.ninja ] || run cmake -G Ninja \
        -DCMAKE_BUILD_TYPE=Release -DLLVM_ENABLE_ASSERTIONS=On \
        -DCMAKE_INSTALL_PREFIX="$pathinstall" "$pathsrc/$llvm"
fi

if [ -f "$pathinstall/bin/clang" ]; then
    # LLVM is installed but FileCheck might be missing
    echo "[+] Installing FileCheck"
    if [ ! -f "$pathinstall/bin/FileCheck" ]; then
        realcd "$pathbuild/$llvm"
        run cmake --build . --target FileCheck
        cp "$pathbuild/$llvm/bin/FileCheck" "$pathinstall/bin/FileCheck"
    fi
else
    echo "[+] Building LLVM (takes a long time and a lot of system resources)"
    realcd "$pathbuild/$llvm"
    run cmake --build . --target install

    # install FileCheck binary from LLVM - it's normally only used internally
    echo "[+] Installing FileCheck"
    if [ ! -f "$pathinstall/bin/FileCheck" ]; then
        cp "$pathbuild/$llvm/bin/FileCheck" "$pathinstall/bin/FileCheck"
    fi
fi

# create python3 virtualenv
echo "[+] Creating virtualenv"
if [ ! -f "$pathinstall/bin/python" ]; then
    run virtualenv --python="$(which python3)" --prompt="(coco) " --no-wheel \
        "$pathinstall"

    # patch pip to fix shebang without spaces issue
    realcd "$pathinstall/bin"
    for pip in pip pip3 pip3.*
    do
        mv "$pip" "$pip.old"
        echo "#!/usr/bin/env bash" > "$pip"
        echo "exec \"$pathinstall/bin/python3\" \"$pathinstall/bin/$pip.old\" \"\$@\"" >> "$pip"
        run chmod +x "$pip"
    done
fi

# load virtualenv to have python/pip available below
# shellcheck disable=SC1090
source "$pathinstall/bin/activate"

# install PLY
echo "[+] Installing PLY"
if ! python -c "import ply" 2>/dev/null; then
    run pip install ply
fi

# install termcolor
echo "[+] Installing termcolor"
if ! python -c "import termcolor" 2>/dev/null; then
    run pip install termcolor
fi

# build & install llvmlite
echo "[+] Building and installing llvmlite"
if ! python -c "import llvmlite" 2>/dev/null; then
    realcd "$pathsrc/$llvmlite"
    run python setup.py build
    run python runtests.py
    run python setup.py install
fi

# install our frontend as a binary
echo "[+] Installing frontend"
if [ ! -f "$pathinstall/bin/$frontend" ]; then
    cat <<- EOF > "$pathinstall/bin/$frontend"
#!/usr/bin/env bash
exec "$pathinstall/bin/python" "$root/frontend/main.py" "\$@"
EOF
    run chmod +x "$pathinstall/bin/$frontend"
fi

# install an alias to opt
echo "[+] Installing opt alias"
if [ ! -f "$pathinstall/bin/$optalias" ]; then
    cat <<- EOF > "$pathinstall/bin/$optalias"
#!/usr/bin/env bash
exec "$pathinstall/bin/opt" -load "$root/llvm-passes/obj/libllvm-passes.so" -S "\$@"
EOF
    run chmod +x "$pathinstall/bin/$optalias"
fi

# touch stamp for build script
touch "$root/lib/.bootstrapped"

echo "All done! Source the virtualenv script to use the installed tools:"
echo "  $ source \"$root/shrc\""
echo "To get out of the virtualenv, run:"
echo "  $ deactivate"
