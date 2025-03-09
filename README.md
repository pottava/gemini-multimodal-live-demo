# Gemini Multimodal Live API ハンズオン

このリポジトリは、Google の [Gemini Multimodal Live API](https://developers.googleblog.com/ja/gemini-2-0-level-up-your-apps-with-real-time-multimodal-interactions/) をサンプル アプリケーションを通して体験するためのガイドです。ハンズオンを通し、見て、聴いて、人間と自然にやりとりできる Gemini の能力を活かしたリアルタイム アプリケーションを作ってみましょう！

## 作りながら学ぶ重要概念

- **リアルタイム コミュニケーション**

  - WebSocket ベース ストリーミング処理
  - 双方向のオーディオ チャット
  - リアルタイムビデオ処理
  - 話者交代と割り込み処理

- **オーディオ**

  - マイク入力キャプチャ
  - オーディオのチャンク化とストリーミング
  - 音声アクティビティ検出 (VAD)
  - リアルタイム オーディオ再生

- **ビデオ**

  - ウェブカメラとスクリーンのキャプチャ
  - フレーム処理とエンコード
  - オーディオとビデオの同時ストリーミング
  - 効率的なメディア処理

- **商用機能**

  - 関数呼び出し
  - System instructions
  - クラウドへのデプロイ
  - エンタープライズ セキュリティ

## ハンズオン

### 資材をダウンロード

```sh
git clone https://github.com/pottava/gemini-multimodal-live-demo.git
```

### 1. テキストとオーディオの基本

まずは Vertex AI の Gemini API を使ってテキストとオーディオを扱ってみましょう。

```sh
teachme 01-text-and-audio.md
```
