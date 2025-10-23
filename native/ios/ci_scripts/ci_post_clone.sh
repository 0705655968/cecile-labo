#!/bin/sh

# ビルドが失敗したときにスクリプトを終了させる
set -e

# 現在の作業ディレクトリをリポジトリのルートに移動
# Xcode Cloudはci_scriptsフォルダからスクリプトを実行するため
# cd $CI_WORKSPACE は既に実行されていることが多いですが、念のため
# Flutterプロジェクトがリポジトリのルートにあることを想定
cd $CI_WORKSPACE

# Flutterの依存関係を取得し、Generated.xcconfigを生成
flutter pub get

# iOSディレクトリに移動し、Podファイルをインストール
cd ios
pod install