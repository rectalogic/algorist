#!/usr/bin/env bash

set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SOURCE_PATH="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
export PYTHONPATH=$SCRIPT_DIR

if [[ "$OSTYPE" == "darwin"* ]]; then
    BLENDER=$(mdfind kMDItemCFBundleIdentifier=org.blenderfoundation.blender)/Contents/MacOS/Blender
else
    BLENDER=blender
fi

"$BLENDER" "$SCRIPT_DIR/algorist.blend" --python "$SOURCE_PATH"