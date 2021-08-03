import 'dart:async';
import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:image_picker/image_picker.dart';
import 'package:dio/dio.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_image_compress/flutter_image_compress.dart';

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
  final _historyPageHeader = '<html lang="ja"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1" /><link rel="stylesheet" href="https://cecile-dev.prm.bz/static/css/common.css"></head><body><div id="contents"><header><h3>カタログ画像検索</h3></header><div class="search_history"><div class="title"><i class="material-icons submit">history</i>検索履歴</div>';
  final _historyPageFooter = '<br style="clear:both;"/><div class="title"><i class="material-icons submit">search</i>検索</div></div><div class="camera"><div class="select_photo"><div><div class="camera"><a href="https://cecile-dev.prm.bz/gallery"><i class="material-icons">add_a_photo</i><br />写真を撮る</a></div></div></div><div class="detail_re"><p>検索を行われる場合、上のカメラアイコンを選択し、検索する写真を撮影してください。</p></div></div></div></body></html>';

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
                print(uri.path);
                if(uri.path == "/push_settings"){
                  // アプリ設定画面へ移動
                  openAppSettings();
                  return NavigationDecision.prevent;
                }
                else if(uri.path.contains('history_find')) {
                  // 過去の写真での再検索
                  final userDirectory = await getApplicationDocumentsDirectory();
                  String imgFile = userDirectory.path + '/' + uri.path.split('/').last;

                  // 検索中画面の表示
                  _webViewController.loadUrl(Uri.dataFromString(
                      _loadingPage,
                      mimeType: 'text/html',
                      encoding: Encoding.getByName('utf-8')
                  ).toString());

                  // 画像データを転送する
                  try{
                    final dio = Dio();
                    dio.options.headers = {
                      'Content-Type': 'application/x-www-form-urlencoded'
                    };
                    var formData = FormData.fromMap({
                      'file': await MultipartFile.fromFile(imgFile)
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
                  return NavigationDecision.prevent;
                }
                else if(uri.path == "/history") {
                  // 検索履歴
                  final userDirectory = await getApplicationDocumentsDirectory();
                  var histories = "";
                  List<FileSystemEntity> files = userDirectory.listSync(recursive: true,followLinks: false);
                  for (var file in files.reversed) {
                    if(file.path.contains('jpg')) {
                      // 画像データをBASE64エンコードし、imgタグに直接指定
                      String img64 = base64Encode(File(file.path).readAsBytesSync());
                      String fileName = file.path.split('/').last;
                      histories += '<li><a href="https://cecile-dev.prm.bz/history_find/' +fileName+ '"><img src="data:image/jpeg;base64,'+img64+'"></a>';
                    }
                  }
                  // HTMLの生成
                  String historyPage = _historyPageHeader;
                  if(histories != '') {
                    historyPage += '<ul class="search_history">' + histories + '</ul>';
                  }
                  else{
                    historyPage += '<div class="nodata">過去に撮影した写真はありません。</div>';
                  }
                  historyPage += _historyPageFooter;
                  // 撮影履歴ページを表示
                  _webViewController.loadUrl(Uri.dataFromString(
                      historyPage,
                      mimeType: 'text/html',
                      encoding: Encoding.getByName('utf-8')
                  ).toString());
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
                  final _pickedFile = await _picker.pickImage(source: ImageSource.gallery, maxHeight: 640, maxWidth: 480, imageQuality: 80);
                  final path = _pickedFile!.path;
                  final ext = path.split('.').last;
                  if(path != '') {
                    // 画像データの選択があれば処理を行う

                    // 画像データが指定数以上登録されている場合は、古い順に削除する
                    String deletePath = '';
                    var fileCnt = 0;
                    for (var file in files) {
                      if(file.path.contains('jpg')) {
                        if(deletePath == '') deletePath = file.path;
                        fileCnt++;
                      }
                    }

                    // 撮影した画像をコピーする
                    String tmpPath = (await getApplicationDocumentsDirectory()).path + '/' + new DateTime.now().millisecondsSinceEpoch.toString() + '.' + ext;
                    File(path).copy(tmpPath);
//                    final dir = Directory('/data/user/0/com.example.cecile/app_flutter1627954836551.jpg');
//                    dir.deleteSync(recursive: true);

                    // 検索中画面の表示
                    _webViewController.loadUrl(Uri.dataFromString(
                        _loadingPage,
                        mimeType: 'text/html',
                        encoding: Encoding.getByName('utf-8')
                    ).toString());

                    // 画像データを転送する
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
