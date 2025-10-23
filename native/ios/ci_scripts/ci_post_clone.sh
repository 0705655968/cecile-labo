#!/bin/bash

# ここに既存のスクリプト内容が続きます
echo "Starting post-clone operations..."
# ...

# Fail this script if any subcommand fails.
set -e
 
# The default execution directory of this script is the ci_scripts directory.
cd $CI_PRIMARY_REPOSITORY_PATH # change working directory to the root of your cloned repo.

# Extract the Flutter version from fvm_config file
FLUTTER_VERSION=$(cat .fvm/fvm_config.json | grep "flutterSdkVersion" | cut -d '"' -f 4)

exho $FLUTTER_VERSION


echo "git clone https://github.com/flutter/flutter.git..."

# Install Flutter using git.
git clone https://github.com/flutter/flutter.git --depth 1 -b $FLUTTER_VERSION $HOME/flutter
export PATH="$PATH:$HOME/flutter/bin"

echo "flutter precache --ios..."

# Install Flutter artifacts for iOS (--ios), or macOS (--macos) platforms.
flutter precache --ios

echo "flutter --version..."

echo "flutter pub get..."

echo "$HOME/flutter/bin"

ls

# Install Flutter dependencies.
flutter pub get

echo "HOMEBREW_NO_AUTO_UPDATE=1..."

# Install CocoaPods using Homebrew.
HOMEBREW_NO_AUTO_UPDATE=1 # disable homebrew's automatic updates.
brew install cocoapods

echo "cd ios && pod install..."

# Install CocoaPods dependencies.
cd native/ios && pod install # run `pod install` in the `ios` directory.
 
exit 0