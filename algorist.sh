#!/usr/bin/env bash

set -e
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
SOURCE_PATH="$(cd "$(dirname "$1")"; pwd -P)/$(basename "$1")"
open -b org.blenderfoundation.blender --stderr "$SCRIPT_DIR/blender-err.log" --stdout "$SCRIPT_DIR/blender-out.log" --env PYTHONPATH="$SCRIPT_DIR" --args algorist.blend --python "$SOURCE_PATH"
