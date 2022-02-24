#!/usr/bin/env bash

set -e

function usage {
    echo "Usage: $(basename $0) [-b INITIAL.blend] SCRIPT.py [... blender args]" 2>&1
    echo '   -b INITIAL.blend   initial blend file, defaults to algorist.blend'
    echo '   SCRIPT.py          python script to run'
    exit 1
}

if [[ ${#} -eq 0 ]]; then
    usage
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
export PYTHONPATH=$SCRIPT_DIR

if [[ "$OSTYPE" == "darwin"* ]]; then
    BLENDER=$(mdfind kMDItemCFBundleIdentifier=org.blenderfoundation.blender)/Contents/MacOS/Blender
else
    BLENDER=blender
fi

optstring=":b:"

while getopts ${optstring} arg; do
    case ${arg} in
        b)
            BLEND="$OPTARG"
            ;;
        :)
            echo "$0: Must supply an argument to -$arg." >&2
            exit 1
            ;;
        ?)
            echo "Invalid option: -${arg}."
            exit 1
            ;;
    esac
done
shift $(($OPTIND - 1))
if [[ ${#} -eq 0 ]]; then
    usage
fi
SOURCE_PATH="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
shift

"$BLENDER" "${BLEND:-$SCRIPT_DIR/algorist.blend}" --python "$SOURCE_PATH" "${@}"
