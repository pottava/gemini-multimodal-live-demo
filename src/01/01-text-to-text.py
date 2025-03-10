import asyncio
from google import genai
from google.genai import types

# Gemini モデルの指定
MODEL_ID = "gemini-2.0-flash-001"


async def main():
    """
    Gemini Multimodal Live API に対してテキストベースで一度だけやりとりする非同期関数です
    """
    # 生成 AI クライアントの初期化
    client = genai.Client()

    # Gemini モデルとのライブ接続を確立
    async with client.aio.live.connect(
        model=MODEL_ID,
        config=types.LiveConnectConfig(response_modalities=[types.Modality.TEXT]),
    ) as session:
        message = "こんにちは、よろしく Gemini! 日本語で話してね"
        print(f"> {message}")

        # プロンプトを Gemini モデルに送信、これがユーザーのターンの終わりであることを通知
        await session.send(input=message, end_of_turn=True)

        response = []

        # ライブセッションから非同期にメッセージを受信します
        async for message in session.receive():
            # 受信したメッセージにテキストが含まれていたら、テキストを応答リストに追加します
            if message.text:
                response.append(message.text)

        # Gemini から受信した完全な応答を結合してコンソールに出力
        print("".join(response))


if __name__ == "__main__":
    asyncio.run(main())
