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

echo "flutter clean..."
flutter clean

# Install Flutter dependencies.
flutter pub get

# エラーが出たのでコメントアウト
cd /Volumes/workspace/repository/native/
rm -rf ios/Pods/ ios/Podfile.lock
#flutter build ios --no-codesign --no-tree-shake-icons

echo "HOMEBREW_NO_AUTO_UPDATE=1..."

# Install CocoaPods using Homebrew.
HOMEBREW_NO_AUTO_UPDATE=1 # disable homebrew's automatic updates.
brew install cocoapods

echo "cd ios && pod install..."

# 前にflutter pub getを実行しているが、iosの親ディレクトリで
# サイド処理しないと、Generated.xcconfigを生成しないらしいので
cd /Volumes/workspace/repository/native/
flutter pub get

# ビルド前に必要なファイルを生成
#flutter build ios --no-codesign

cd /Volumes/workspace/repository/native/ios/
pod deintegrate

# Install CocoaPods dependencies.
pod install--project-directory=ios

exit 0