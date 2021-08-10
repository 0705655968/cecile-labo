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
import 'package:intl/intl.dart';
import 'package:share/share.dart';
import 'package:flutter/services.dart' show rootBundle;
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:fcm_config/fcm_config.dart';

// バックグラウンドの処理の実態
String newsId = '';

// WebViewコントローラー
late WebViewController _webViewController;
final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;

// トップレベルに定義
Future<void> _firebaseMessagingBackgroundHandler(
    RemoteMessage _notification) async {
  print("バックグラウンドでメッセージを受け取りました");
  var title = _notification.notification!.title;
  var body = _notification.notification!.body;
  print(title);
  print(body);
  try {
    newsId = _notification.data['news'];
    print(newsId);
  } catch(err){
    print(err);
  }
  FCMConfig.instance.displayNotification(title: title ?? '', body: body ?? '');
}

final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
FlutterLocalNotificationsPlugin();

const AndroidNotificationChannel channel = AndroidNotificationChannel(
  'high_importance_channel', // id
  'High Importance Notifications', // title
  'This channel is used for important notifications.', // description
  importance: Importance.high,
);

//void main() {
Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  //バックグラウンド用
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

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
  final bool _debug = true;
  bool _isLoading = false;
  bool _isActive = false;
  bool _isBar = true;
  int _saveImageMax = 10;
  int _selectedIndex = 0;

  List<String> _urlList = [
    'https://cecile-dev.prm.bz/home',
    'https://cecile-dev.prm.bz/catalog',
    'https://cecile-dev.prm.bz/similar',
    'https://cecile-dev.prm.bz/news',
    'https://cecile-dev.prm.bz/settings'
  ];
  final initialUrl = 'https://cecile-dev.prm.bz/home';
  final List<String> browserLinkList = [
    'www.cecile.co.jp','faq.cecile.co.jp'
  ];
  final _selectedItemColor = Colors.white;
  final _unselectedItemColor = Color.fromRGBO(99, 99, 99, 1.0);
  final _selectedBgColor = Color.fromRGBO(156, 20, 74, 1.0);
  final _unselectedBgColor = Colors.white;

  @override
  void initState() {
    super.initState();
    if (Platform.isAndroid) {
      WebView.platform = SurfaceAndroidWebView();
    }
    // 次の処理が無いと、フォアグラウンドでメッセージを受け取れないみたい
    _firebaseMessaging.getToken().then((token) {
      print("$token");
    });
    FirebaseMessaging.onMessageOpenedApp.listen((message) {
      print("フォアグラウンドオープンアプリでメッセージを受け取りました");
      _selectedIndex = 0;
      _isActive = true;
      _onItemTapped(_selectedIndex);
      _isActive = false;
      try {
        newsId = message.data['news'];
        _selectedIndex = 0;
        _webViewController.loadUrl(
            'https://cecile-dev.prm.bz/home?nid=' + newsId);
        print(newsId);
      } catch (err) {
        print(err);
      }
    });
    FirebaseMessaging.onMessage.listen((message) {
      print("フォアグラウンドでメッセージを受け取りました");
      _selectedIndex = 0;
      _isActive = true;
      _onItemTapped(_selectedIndex);
      _isActive = false;
      // ニュースIDがあれば取得
      try {
        newsId = message.data['news'];
        _webViewController.loadUrl(
            'https://cecile-dev.prm.bz/home?nid=' + newsId);
        if(_debug) print(newsId);
      } catch (err) {
        print(err);
      }
    });
  }

  // BottomNavigation 切り替えで動作
  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
      _webViewController.loadUrl(_urlList[index]);
    });
  }

  Future<void> _onRequestPermissions() async {
    _firebaseMessaging.getToken().then((token) async {
      // 取得したトークンを共有する
      await Share.share("$token");
    });
  }

  // 検索中画面の表示
  Future<void> _onFindingDisplay() async {
    _webViewController.loadUrl(Uri.dataFromString(
      await rootBundle.loadString('assets/html/wait.html'),
      mimeType: 'text/html',
      encoding: Encoding.getByName('utf-8')
    ).toString());
  }

  // 検索履歴画面
  Future<void> _onWebPageByErrMsg(String message, int index) async {
    showDialog(
        context: context,
        builder: (_) => AlertDialog(
          title :Text('お知らせ'),
          content: Text(message
              , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
          actions: <Widget>[
            FlatButton(
              child: Text('OK'),
              onPressed: () async {
                Navigator.of(context).pop(1);
                // 指定ページへ遷移
                if(index == 99){
                  // 検索履歴画面
                  _webViewController.loadUrl(Uri.dataFromString(
                    await _onHistoryList(),
                    mimeType: 'text/html',
                    encoding: Encoding.getByName('utf-8')
                  ).toString());
                }
                else _webViewController.loadUrl(_urlList[index]);
              },
            ),
          ],
        )
    );
  }


  // 画像検索処理
  Future<void> _onSimilar(String imgFile, bool history) async {
    try{
      final dio = Dio();
      dio.options.headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
      };
      var formData = FormData.fromMap({
        'file': await MultipartFile.fromFile(imgFile)
      });
      final response = await dio.post(
        _urlList[2],
        data: formData,
      );
      _webViewController.loadUrl(Uri.dataFromString(
          response.data,
          mimeType: 'text/html',
          encoding: Encoding.getByName('utf-8')
      ).toString());
    } catch (err) {
      _onWebPageByErrMsg(
        "カタログ画像検索処理に失敗しました。\nお手数ですが再度処理を行ってください。",
          (history) ? 99: 2
      );
    }
  }

  // 検索履歴画面
  Future<String> _onHistoryList() async {
    var userDirectory = await getApplicationDocumentsDirectory();
    var histories = "";
    List<FileSystemEntity> files = userDirectory.listSync(
        recursive: true, followLinks: false);
    files.sort((a, b) => a.toString().compareTo(b.toString()));
    for (var file in files.reversed) {
      if (file.path.contains('jpg')) {
        if (_debug) print(file.path);
        // 画像データをBASE64エンコードし、imgタグに直接指定
        String img64 = base64Encode(File(file.path).readAsBytesSync());
        String fileName = file.path
            .split('/')
            .last;
        histories += '<li><a href="https://cecile-dev.prm.bz/history_find/' + fileName + '"><img src="https://cecile-dev.prm.bz/static/images/s.gif" style="background:url(data:image/jpeg;base64,' + img64 + ');background-size:cover;"></a>';
      }
    }
    // HTMLの生成
    var historyPage = await rootBundle.loadString('assets/html/history.html');
    if (histories != '')
      historyPage = historyPage.replaceAll('<template>', '<ul class="search_history">' + histories + '</ul>');
    else
      historyPage = historyPage.replaceAll('<template>', '<div class="nodata">過去に撮影した写真はありません。</div>');
    return Future<String>.value(historyPage);
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
            initialUrl: initialUrl +'?nid='+newsId,
            // jsを有効化
            javascriptMode: JavascriptMode.unrestricted,
            // controllerを登録
            onWebViewCreated: (WebViewController webViewController) {
              _webViewController = webViewController;
              print('created');
            },
            // リソースの読み込みエラー
            onWebResourceError: (error) async {
              _webViewController.loadUrl(Uri.dataFromString(
                await rootBundle.loadString('assets/html/error.html'),
                mimeType: 'text/html',
                encoding: Encoding.getByName('utf-8')
              ).toString());
            },
            navigationDelegate: (request) async {
              // 初期URLやiFlameのURL、CSSのlink relの要素を除外する
              if ((!request.isForMainFrame) || (initialUrl == request.url)) {
                return NavigationDecision.navigate;
              }
              // ブラウザで開くリンクの判別
              final uri = Uri.parse(request.url);
              if(_debug) print(uri.path);
              if(uri.path == "/push_settings"){
                // アプリ設定画面へ移動
                openAppSettings();
                return NavigationDecision.prevent;
              }
              else if(uri.path.contains('share')) {
                // 共有処理

                // URLを正規の形に変更する
                String shareUrl = uri.toString().replaceAll('cecile-dev.prm.bz/share', 'cecile.co.jp');
                await Share.share(shareUrl);

                return NavigationDecision.prevent;
              }
              else if(uri.path.contains('history_find')) {
                // 過去の写真での再検索

                // ファイルパスの生成
                final userDirectory = await getApplicationDocumentsDirectory();
                String imgFile = userDirectory.path + '/' + uri.path.split('/').last;

                // 検索中画面の表示
                await _onFindingDisplay();

                // 画像検索処理
                _onSimilar(imgFile, true);
                return NavigationDecision.prevent;
              }
              else if(uri.path == "/history") {

                // 検索履歴
                try{
                  // 撮影履歴ページを表示
                  _webViewController.loadUrl(Uri.dataFromString(
                    await _onHistoryList(),
                    mimeType: 'text/html',
                    encoding: Encoding.getByName('utf-8')
                  ).toString());
                } catch (err) {
                  // ページ表示にエラーが発生したので、エラーメッセージを表示し、カタログ画像検索のメイン画面に遷移する
                  _onWebPageByErrMsg("検索履歴情報の取得時にエラーが発生しました。\nカタログ画像検索画面から再度処理を行ってください。", 2);
                }
                return NavigationDecision.prevent;

              }
              else if(uri.path == "/gallery"){
                // カメラを起動
                final _picker = ImagePicker();
                // ImageSource.camera / ImageSource.gallery
                final _pickedFile = await _picker.pickImage(source: ImageSource.camera, maxHeight: 640, maxWidth: 480, imageQuality: 80);
                final path = _pickedFile!.path;
                final ext = path.split('.').last;
                if(path != '') {
                  // 画像データの選択があれば処理を行う

                  // 画像データが指定数以上登録されている場合は、古い順に削除する
                  String deletePath = '';
                  int fileCnt = 0;
                  final userDirectory = await getApplicationDocumentsDirectory();
                  List<FileSystemEntity> files = userDirectory.listSync(recursive: true,followLinks: false);
                  for (var file in files) {
                    if(file.path.contains('jpg')) {
                      if(deletePath == '') deletePath = file.path;
                      fileCnt++;
                    }
                  }
                  // 保存画像が指定数以上なら、古いデータを削除する
                  if(fileCnt >= _saveImageMax) {
                    final dir = Directory(deletePath);
                    dir.deleteSync(recursive: true);
                  }
                  // 撮影した画像をユーザー領域へコピーする
                  String tmpPath = (await getApplicationDocumentsDirectory()).path + '/' + DateFormat('yyyyMMddHHmmss').format(DateTime.now()) + '.' + ext;
                  File(path).copy(tmpPath);
                  if(_debug) print(tmpPath);

                  // 検索中画面の表示
                  await _onFindingDisplay();

                  // 画像検索処理
                  _onSimilar(path, false);
                }
                return NavigationDecision.prevent;
              }
              else if(uri.path == "/data_reset"){
                // アプリ内のデータをリセット
                // 削除確認ダイアログを表示
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title :Text('データ削除確認'),
                    content: Text('アプリ内で保持しているデータを削除してもよろしいですか？'
                      , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
                    actions: <Widget>[
                      FlatButton(
                        child: Text('キャンセル'),
                        onPressed: () => Navigator.of(context).pop(1),
                      ),
                      FlatButton(
                        child: Text('削除'),
                        onPressed: () async {
                          Navigator.of(context).pop(1);
                          // WebViewのCookieを削除
                          await CookieManager().clearCookies();
                          // 画像検索履歴データの削除
                          final userDirectory = await getApplicationDocumentsDirectory();
                          List<FileSystemEntity> files = userDirectory.listSync(recursive: true,followLinks: false);
                          for (var file in files) {
                            if(file.path.contains('jpg')) {
                              Directory(file.path).deleteSync(recursive: true);
                            }
                          }
                          // 完了メッセージを表示
                          showDialog(
                            context: context,
                            builder: (_) => _buildDialog(
                              '削除完了', 'カタログ画像検索、デジタルカタログに関連するデータを削除しました。', 'OK'
                            )
                          );
                        },
                      ),
                    ],
                  )
                );
                return NavigationDecision.prevent;

              }
              else if(uri.path == "/firebase") {
                // プッシュ通知端末登録

                // プッシュ通知のトークンを取得する
                _onRequestPermissions();

                return NavigationDecision.prevent;
              }
              else if(uri.path == "/cache_reset") {
                // WebViewのキャッシュを削除(Androidのみ)

                // キャッシュクリア確認ダイアログを表示
                showDialog(
                  context: context,
                  builder: (_) => AlertDialog(
                    title :Text('キャッシュ削除確認'),
                    content: Text('キャッシュデータを削除してもよろしいですか？'
                      , style: TextStyle(fontSize: 14, color: _unselectedItemColor)),
                    actions: <Widget>[
                      FlatButton(
                        child: Text('キャンセル'),
                        onPressed: () => Navigator.of(context).pop(1),
                      ),
                      FlatButton(
                        child: Text('削除'),
                        onPressed: () async {
                          Navigator.of(context).pop(1);
                          // キャッシュデータの削除
                          await _webViewController.clearCache();
                          // 完了メッセージを表示
                          showDialog(
                            context: context,
                            builder: (_) => _buildDialog(
                              'クリア完了', 'アプリ内のキャッシュデータの削除が正常に完了しました。', 'OK'
                            )
                          );
                        },
                      ),
                    ],
                  )
                );
                return NavigationDecision.prevent;
              }
              else if (browserLinkList.indexOf(uri.host) >= 0) {
                if (await canLaunch(request.url)) {
                  // 外部ブラウザで遷移
                  await launch(
                    request.url,
                    forceSafariVC: false,
                  );
                }
                // 何もしない
                return NavigationDecision.prevent;
              }
              else if (uri.path == "/exit") {
                _isBar = true;
                _isActive = true;
                _onItemTapped(_selectedIndex);
                _isActive = false;
                // 何もしない
                return NavigationDecision.prevent;
              }
              // WebView内で遷移
              if(uri.path == "/settings"){
                _isBar = false;
                _isActive = true;
                _onItemTapped(_selectedIndex);
                _webViewController.loadUrl(_urlList[4]);
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
        child: _isBar
            ?BottomNavigationBar(
          // selectedFontSizeの値を0にする事でスペースが消える
          selectedFontSize: 0,
          items: [
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.home, 'ホーム', 12, 0),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.menu_book, 'デジタルカタログ', 12, 1),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.camera_enhance, 'カタログ画像検索', 12, 2),
              title: SizedBox.shrink(),
            ),
            BottomNavigationBarItem(
              icon: _buildIcon(Icons.verified, '新着情報', 12, 3),
              title: SizedBox.shrink(),
            ),
          ],
          currentIndex: _selectedIndex,
          selectedItemColor: _selectedItemColor,
          type: BottomNavigationBarType.fixed,
        ):Container(
          color: Colors.white,
          width: MediaQuery.of(context).size.width,
          height: 0,
        ),
      )
    );
  }

}
