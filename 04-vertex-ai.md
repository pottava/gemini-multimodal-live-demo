# Gemini Multimodal Live API ハンズオン その 4

## 始めましょう

この手順では WebSocket と Web Audio API を使用使って Gemini Multimodal Live API と対話する、リアルタイムの音声対音声アプリケーションを構築していきます。

そして本章以降では、企業でも安心して利用できる **Vertex AI 経由での Gemini API** を使っていきます。

<walkthrough-tutorial-duration duration="20"></walkthrough-tutorial-duration>
<walkthrough-tutorial-difficulty difficulty="3"></walkthrough-tutorial-difficulty>

**[開始]** ボタンをクリックして次のステップに進みます。

## プロジェクトの設定

この手順の中で実際にリソースを構築する対象のプロジェクトを選択してください。

<walkthrough-project-setup></walkthrough-project-setup>

## 1. エディタの起動

[Cloud Shell エディタ](https://cloud.google.com/shell/docs/launching-cloud-shell-editor?hl=ja) を起動していなかった場合、以下のコマンドを実行しましょう。

```bash
cloudshell workspace gemini-multimodal-live-demo
```

## 2. CLI の初期設定

**ハンズオン その 1 を実施された方は読み飛ばしていただいて OK です。**

gcloud（[Google Cloud の CLI ツール](https://cloud.google.com/sdk/gcloud?hl=ja) のデフォルト プロジェクトを設定します。

```bash
export GOOGLE_CLOUD_PROJECT=<walkthrough-project-id/>
```

```bash
gcloud config set project "${GOOGLE_CLOUD_PROJECT}"
```

みなさんの権限でアプリケーションを動作させるため、アプリケーションのデフォルト認証情報（ADC）を作成します。  
表示される URL をブラウザの別タブで開き、認証コードをコピー、ターミナルに貼り付け Enter を押してください。

```bash
mkdir -p $HOME/.config/gcloud/
export GOOGLE_APPLICATION_CREDENTIALS=$HOME/.config/gcloud/application_default_credentials.json
```

```bash
gcloud auth application-default login --quiet
```

```bash
mv /tmp/*/application_default_credentials.json $HOME/.config/gcloud/ > /dev/null 2>&1
```

## 3. ファイル構成

これまでと異なり、双方向でライブ オーディオ ストリームを処理するため、コードは大幅に複雑になっていきます。  
例えば特徴的な変更点として、話者交代の検知はローカルのフラグを見るのではなく、API 側の機能を使うようになっています。

![システム アーキテクチャ](https://raw.githubusercontent.com/heiko-hotz/gemini-multimodal-live-dev-guide/main/assets/audio-to-audio-websocket.png)

本アプリケーションは次のファイル群で構成されています。

- **01-audio-to-audio.html**: ユーザー インターフェイス。全体的な流れや WebSocket 通信など、コアロジックを含んでいます。
- **audio-recorder.js**: マイクからオーディオをキャプチャし、必要な形式に変換、そののチャンクデータを送信します。
- **audio-recording-worklet.js**: 低レベルのオーディオ処理。float32 から int16 への変換やチャンク化など。
- **audio-streamer.js**: Web Audio API でオーディオを管理。Gemini から受信したチャンクデータのキューイング、バッファリング、再生など、スムーズで継続的な再生を保証します。
- **gemini-live-api.js**: WebSocket を使って Gemini API サーバーと通信し、リアルタイムな音声対話を実現するための機能を集約しています。

音声フォーマットの [現在の仕様](https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/multimodal-live?hl=ja#audio-formats) の通り、Multimodal Live API の入力音声形式は 16 kHz の 16 ビット PCM 形式となっており、その処理は `audio-recording-worklet.js` が担っています。各チャンクには 16 ビット PCM オーディオのサンプルが 2,048 個含まれており、結果として、オーディオ データは約 128 ミリ秒 (2,048 / 16,000 = 0.128 秒) ごとに送信される実装になっています。

## 4. システム構成

Web ブラウザ (JavaScript) から Vertex AI を安全に接続する方法はいくつか考えられますが、今回は以下の方法を採用します。

- JavaScript から Gemini Multimodal Live API には直接接続せず、プロキシを挟む
- Gemini (Vertex AI 版) への API 認証は、そのプロキシがサーバーサイドのサービスアカウントで代行する
- ブラウザからプロキシへのアクセスは、静的ファイルとプロキシが同一オリジンになるように配置し、IAP で保護する

ブラウザ -> IAP -> Cloud Run（Nginx）-> 同一コンテナ内のプロキシ -> Gemini API

## 5. コンテナのビルド

コードを読む前に、まずは動作確認を進めます。まずは 4. のシステム構成を実現するためのコンテナを作ります。

```bash
sed -e "s|<YOUR_PROJECT_ID>|${GOOGLE_CLOUD_PROJECT}|g" src/04/01-audio-to-audio.html > src/04/index.html
docker build -t app-0401 --build-arg SRC_DIR=04/ src
```

それを起動します。

```bash
docker rm -f app-0401 > /dev/null 2>&1
docker run --rm --name app-0401 -p 8080:8080 -e GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT} -e GOOGLE_APPLICATION_CREDENTIALS=/tmp/creds.json -v ${GOOGLE_APPLICATION_CREDENTIALS}:/tmp/creds.json app-0401
```

Web preview ボタンを押し、"ポート 8080 でプレビュー" を選びましょう。  
<walkthrough-web-preview-icon/>

マイクボタンをクリックして、何か話しかけてみてください！

## 6. Cloud Run へのデプロイ

本来 IAP で保護すべきですが、今回は認証なしのエンドポイントとして Cloud Run にサービスをデプロイしてみます。

まず、コンテナを保存するレジストリを作ります。

```bash
gcloud artifacts repositories create genai --repository-format docker --location asia-northeast1 --description "Docker repository for GenAI hands-on"
gcloud auth configure-docker asia-northeast1-docker.pkg.dev
docker tag app-0401 asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401
docker push asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401
```

そして Cloud Run サービスを作成しましょう。

```bash
gcloud run deploy genai-app-0401 --image asia-northeast1-docker.pkg.dev/${GOOGLE_CLOUD_PROJECT}/genai/app:0401 --region asia-northeast1 --platform managed --allow-unauthenticated --quiet
```

サービスがデプロイされたら、以下のコマンドで帰ってきた URL にアクセスしてみてください。

```bash
gcloud run services describe genai-app-0401 --region asia-northeast1 --format='value(status.address.url)'
```

## 7. リアルタイム音声チャットのコード確認

コードで確認してみます。  
<walkthrough-editor-open-file filePath="src/04/01-audio-to-audio.html">01-audio-to-audio.html</walkthrough-editor-open-file>

- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="33" endLine="36" startCharacterOffset="4" endCharacterOffset="100">L.34</walkthrough-editor-select-line> コードが複雑になってきたため、役割ごとにファイルを分割しています。
- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="53" endLine="53" startCharacterOffset="10" endCharacterOffset="150">L.54</walkthrough-editor-select-line> Vertex AI で利用するモデルは完全なパス形式で指定します。
- <walkthrough-editor-select-line filePath="src/04/01-audio-to-audio.html" startLine="128" endLine="130" startCharacterOffset="10" endCharacterOffset="100">L.129</walkthrough-editor-select-line> チャンクとなったオーディオデータは都度、Gemini API サーバーに送信されます。

ご興味があれば `audio-recorder.js` や `audio-streamer.js`、`gemini-live-api.js` の実装もぜひご覧ください。

## その 4 はこれで終わりです

<walkthrough-conclusion-trophy></walkthrough-conclusion-trophy>

では続けて、ハンズオン その 5 へ進みましょう！

```bash
teachme 05-video-and-audio.md
```
