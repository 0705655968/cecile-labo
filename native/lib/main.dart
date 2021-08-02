import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:dio/dio.dart';

void main() {
  runApp(CecileApp());
}

class CecileApp extends StatelessWidget {
  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      home: WebViewScreen(),
    );
  }
}

class WebViewScreen extends StatefulWidget {
  _WebViewScreenState createState() => _WebViewScreenState();
}

class _WebViewScreenState extends State<WebViewScreen> {
  late WebViewController _webViewController;
  bool _isLoading = false;
  bool _isActive = false;
  int _selectedIndex = 0;
  List<String> _urlList = [
    'https://cecile-dev.prm.bz/home',
    'https://cecile-dev.prm.bz/catalog',
    'https://cecile-dev.prm.bz/similar',
    'https://cecile-dev.prm.bz/news',
    'https://cecile-dev.prm.bz/settings'
  ];
  final initialUrl = 'https://cecile-dev.prm.bz/home';
  final appParam = '?device=app';
  final List<String> browserLinkList = [
    'www.cecile.co.jp'
  ];
  final _selectedItemColor = Colors.white;
  final _unselectedItemColor = Color.fromRGBO(99, 99, 99, 1.0);
  final _selectedBgColor = Color.fromRGBO(173, 32, 32, 1.0);
  final _unselectedBgColor = Colors.white;
  final _loadingPage = '<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1" /><link rel="stylesheet" href="https://cecile-dev.prm.bz/static/css/common.css?v=0002"></head><body><div id="contents"><header><h3>カタログ画像検索</h3></header><div class="loading"><i class="material-icons">image_search</i><br />商品検索中..</div></body></html>';

  @override
  void initState() {
    super.initState();
    if (Platform.isAndroid) {
      WebView.platform = SurfaceAndroidWebView();
    }
  }

  // BottomNavigation 切り替えで動作
  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _webViewController.loadUrl(_urlList[index]);
    });
  }

  // 背景色
  Color _getBgColor(int index) =>
      _selectedIndex == index ? _selectedBgColor : _unselectedBgColor;

  // テキスト色
  Color _getItemColor(int index) =>
      _selectedIndex == index ? _selectedItemColor : _unselectedItemColor;

  // アイコンに背景を設定する
  Widget _buildIcon(IconData iconData, String text, int fontsize, int index) => Container(
    width: double.infinity,
    height: kBottomNavigationBarHeight,
    child: Material(
      color: _getBgColor(index),
      child: InkWell(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Icon(iconData, size: 28.0, color: _getItemColor(index)),
            Text(text, style: TextStyle(fontSize: 9, color: _getItemColor(index))),
          ],
        ),
        onTap: () => _onItemTapped(index),
      ),
    ),
  );

  // ダイアログ
  Widget _buildDialog(String title, String message, String btn) => AlertDialog(
    title :Text(title),
    content: Text(message
        , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
    actions: <Widget>[
      FlatButton(
        child: Text(btn),
        onPressed: () => Navigator.of(context).pop(1),
      ),
    ],
  );

  Widget build(BuildContext context) {
    return Scaffold(
      appBar: PreferredSize(
        // appBarのサイズを0にし、バーを消す
        preferredSize: Size.fromHeight(0),
        child: AppBar(
          elevation: 0,
          backgroundColor: Colors.transparent,
        ),
      ),
      body: Stack(
          children: <Widget>[
            WebView(
              initialUrl: initialUrl,
              // jsを有効化
              javascriptMode: JavascriptMode.unrestricted,
              // controllerを登録
              onWebViewCreated: (WebViewController webViewController) {
                _webViewController = webViewController;
              },
              /*
            // ページの読み込み開始
            onPageStarted: (finish) {
              setState(() {
                _isLoading = true;
              });
            },
            // ページ読み込み終了
            onPageFinished: (finish) {
              setState(() {
                _isLoading = false;
              });
            },
            */
              navigationDelegate: (request) async {
                // 初期URLやiFlameのURL、CSSのlink relの要素を除外する
                if ((!request.isForMainFrame) || (initialUrl == request.url)) {
                  return NavigationDecision.navigate;
                }
                // ブラウザで開くリンクの判別
                final uri = Uri.parse(request.url);
                print(uri);
                if(uri.path == "/push_settings"){
                  // アプリ設定画面へ移動
                  openAppSettings();
                  return NavigationDecision.prevent;
                }
                else if(uri.path == "/camera"){
                  // カメラを起動
                  final _picker = ImagePicker();
                  final _pickedFile = await _picker.pickImage(source: ImageSource.camera);
                  final path = _pickedFile!.path;
                  if(path != '') {
                    _webViewController.loadUrl(Uri.dataFromString(
                        _loadingPage,
                        mimeType: 'text/html',
                        encoding: Encoding.getByName('utf-8')
                    ).toString());
                    // 画像データの選択があれば処理を行う
                    try{
                      final dio = Dio();
                      dio.options.headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                      };
                      var formData = FormData.fromMap({
                        'file': await MultipartFile.fromFile(path)
                      });
                      final response = await dio.post(
                        'https://cecile-dev.prm.bz/similar',
                        data: formData,
                      );
                      _webViewController.loadUrl(Uri.dataFromString(
                          response.data,
                          mimeType: 'text/html',
                          encoding: Encoding.getByName('utf-8')
                      ).toString());
                    } catch (err) {
                      print('uploading error: $err');
                    }
                  }
                  return NavigationDecision.prevent;
                }
                else if(uri.path == "/gallery"){
                  // ギャラリーを起動
                  final _picker = ImagePicker();
                  final _pickedFile = await _picker.pickImage(source: ImageSource.gallery);
                  final path = _pickedFile!.path;
                  if(path != '') {
                    _webViewController.loadUrl(Uri.dataFromString(
                        _loadingPage,
                        mimeType: 'text/html',
                        encoding: Encoding.getByName('utf-8')
                    ).toString());
                    // 画像データの選択があれば処理を行う
                    try{
                      final dio = Dio();
                      dio.options.headers = {
                        'Content-Type': 'application/x-www-form-urlencoded'
                      };
                      var formData = FormData.fromMap({
                        'file': await MultipartFile.fromFile(path)
                      });
                      final response = await dio.post(
                        'https://cecile-dev.prm.bz/similar',
                        data: formData,
                      );
                      _webViewController.loadUrl(Uri.dataFromString(
                          response.data,
                          mimeType: 'text/html',
                          encoding: Encoding.getByName('utf-8')
                      ).toString());
                    } catch (err) {
                      print('uploading error: $err');
                    }
                  }
                  return NavigationDecision.prevent;
                }
                else if(uri.path == "/data_reset"){
                  // アプリ内のデータをリセット
                  await CookieManager().clearCookies();
                  // 完了メッセージを表示
                  showDialog(
                      context: context,
                      builder: (_) => _buildDialog(
                          '削除完了', 'カタログ画像検索、デジタルカタログに関連するデータを削除しました。', 'OK'
                      )
                  );
                  return NavigationDecision.prevent;
                }
                else if(uri.path == "/cache_reset"){
                  // WebViewのキャッシュを削除(Androidのみ)
                  await _webViewController.clearCache();
                  // 完了メッセージを表示
                  showDialog(
                      context: context,
                      builder: (_) => _buildDialog(
                          'クリア完了', 'アプリ内のキャッシュデータの削除が正常に完了しました。', 'OK'
                      )
                  );
                  return NavigationDecision.prevent;
                }
                else if (browserLinkList.indexOf(uri.host) >= 0) {
                  if (await canLaunch(request.url)) {
                    // 外部ブラウザで遷移
                    await launch(
                      request.url,
//                    request.url + appParam,
                      forceSafariVC: false,
                    );
                  }
                  // 何もしない
                  return NavigationDecision.prevent;
                }
                // WebView内で遷移
                if(uri.path == "/settings"){
                  print("init");
                  print(_selectedIndex);
                  _isActive = true;
                  _onItemTapped(_selectedIndex);
                  _isActive = false;
                }
                return NavigationDecision.navigate;
              },
            ),
            // ページ読み込み中の時はIndicatorを出す
            _isLoading ? Center( child: CircularProgressIndicator())
                : Stack(),
          ]
      ),
      bottomNavigationBar: Container(
        margin: EdgeInsets.only(top: 0, bottom: 0),
        child: BottomNavigationBar(
          // selectedFontSizeの値を0にする事でスペースが消える
          selectedFontSize: 0,
          items: [
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.home, 'ホーム', 10, 0),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.menu_book, 'デジタルカタログ', 9, 1),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.camera_enhance, 'カタログ画像検索', 9, 2),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.verified, '新着情報', 10, 3),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.settings, '設定', 10, 4),
              title: SizedBox.shrink(),
            ),
          ],
          currentIndex: _selectedIndex,
          selectedItemColor: _selectedItemColor,
          type: BottomNavigationBarType.fixed,
        ),
      ),
    );
  }
}
