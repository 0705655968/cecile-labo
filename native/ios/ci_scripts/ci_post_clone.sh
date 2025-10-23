#!/bin/bash

# ここに既存のスクリプト内容が続きます
echo "Starting post-clone operations..."
# ...

# Fail this script if any subcommand fails.
set -e
 
# The default execution directory of this script is the ci_scripts directory.
cd $CI_PRIMARY_REPOSITORY_PATH # change working directory to the root of your cloned repo.

echo "git clone https://github.com/flutter/flutter.git..."

# Install Flutter using git.
git clone https://github.com/flutter/flutter.git --depth 1 -b stable $HOME/flutter
export PATH="$PATH:$HOME/flutter/bin"

echo "flutter precache --ios..."

# Install Flutter artifacts for iOS (--ios), or macOS (--macos) platforms.
flutter precache --ios

echo "flutter pub get..."

echo "$HOME/flutter/bin"

flutter --version

cd "$HOME/flutter/bin"
ls -l

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