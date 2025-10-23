#!/bin/bash

# ここに既存のスクリプト内容が続きます
echo "Starting post-clone operations..."
# ...

# Fail this script if any subcommand fails.
set -e

# このスクリプトは、リポジトリがクローンされた直後に実行されます。
# Xcodeプロジェクトファイル（.xcodeproj）のパスを設定します
PROJECT_FILE="./ios/Pods/Pods.xcodeproj"
TARGET_NAME="firebase_messaging"
SETTING_NAME="CLANG_ALLOW_NON_MODULAR_INCLUDES_IN_FRAMEWORK_MODULES"
SETTING_VALUE="YES"

# Firebase Messaging ターゲットのビルド設定を強制的に YES に上書きする
echo "Setting '$SETTING_NAME' to '$SETTING_VALUE' for target '$TARGET_NAME' in '$PROJECT_FILE'"

# 'Pods' プロジェクト内の 'firebase_messaging' ターゲットに対して設定を適用
# Debug (デバッグ) および Release (リリース) の両方の構成に適用
/usr/bin/xcrun xcodebuild -project "$PROJECT_FILE" -target "$TARGET_NAME" -configuration Debug       -type buildsetting ONLY_ACTIVE_ARCH=NO GCC_PRECOMPILE_PREFIX_HEADER=NO -json | /usr/bin/plutil -convert json -r -o /dev/stdout - | grep -q '"'"$SETTING_NAME"'"' || /usr/bin/xcrun xcodebuild -project "$PROJECT_FILE" -target "$TARGET_NAME" -configuration Debug       -type buildsetting ONLY_ACTIVE_ARCH=NO GCC_PRECOMPILE_PREFIX_HEADER=NO "$SETTING_NAME"="$SETTING_VALUE"
/usr/bin/xcrun xcodebuild -project "$PROJECT_FILE" -target "$TARGET_NAME" -configuration Release      -type buildsetting ONLY_ACTIVE_ARCH=NO GCC_PRECOMPILE_PREFIX_HEADER=NO -json | /usr/bin/plutil -convert json -r -o /dev/stdout - | grep -q '"'"$SETTING_NAME"'"' || /usr/bin/xcrun xcodebuild -project "$PROJECT_FILE" -target "$TARGET_NAME" -configuration Release      -type buildsetting ONLY_ACTIVE_ARCH=NO GCC_PRECOMPILE_PREFIX_HEADER=NO "$SETTING_NAME"="$SETTING_VALUE"

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

# エラーが出たのでコメントアウト
cd /Volumes/workspace/repository/native/
rm -rf ios/Pods/ ios/Podfile.lock
#flutter build ios --no-codesign --no-tree-shake-icons

cd "$HOME/flutter/bin"

# Install Flutter dependencies.
flutter pub get

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

cd /Volumes/workspace/repository/native/

# Install CocoaPods dependencies.
pod install --project-directory=ios

exit 0