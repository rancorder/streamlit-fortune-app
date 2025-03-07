import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# 🔹 今日の日付を取得（YYYYMMDD 形式）
today_date = datetime.today().strftime('%Y%m%d')

# 🔹 Streamlit Cloud の Secrets から APIキー を取得
API_KEY = st.secrets["GEMINI_API_KEY"]

# APIキーの設定
if not API_KEY:
    st.error("⚠ APIキーが設定されていません。Streamlit Cloud の Secrets を確認してください。")
else:
    genai.configure(api_key=API_KEY)

# 🔹 Gemini API モデルの選択
MODEL_NAME = "gemini-1.5-pro"

# 🔹 四柱推命の干支・五行を計算
def calculate_chinese_zodiac(birth_year):
    zodiacs = ["申", "酉", "戌", "亥", "子", "丑", "寅", "卯", "辰", "巳", "午", "未"]
    elements = ["金", "金", "土", "土", "水", "水", "木", "木", "火", "火", "土", "土"]
    index = birth_year % 12
    return f"{zodiacs[index]} ({elements[index]}の気質)"

# 🔹 六星占術の運命星を計算
def calculate_six_star(birth_year):
    stars = ["金星", "火星", "土星", "天王星", "木星", "水星"]
    return stars[(birth_year - 1900) % 6]

# 🔹 天星術の天星タイプを計算
def calculate_tensei_type(birth_year, birth_month, birth_day):
    base = (birth_year + birth_month + birth_day) % 12
    types = ["満月", "上弦の月", "新月", "下弦の月", "太陽", "夕焼け", "朝焼け", "月食", "日食", "流星", "銀河", "彗星"]
    return types[base]

# 🔹 画像生成関数（占い結果を画像化）
def generate_image(text):
    img = Image.new('RGB', (600, 400), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except:
        font = ImageFont.load_default()
    
    draw.text((20, 50), text, fill=(0, 0, 0), font=font)

    # 画像をバイナリ形式に変換
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    
    return buf

# 🔹 SNS 共有用の画像URLを作成
def get_image_download_link(img_buf):
    img_base64 = base64.b64encode(img_buf.getvalue()).decode()
    return f'<a href="data:image/png;base64,{img_base64}" download="fortune.png">📥 画像をダウンロード</a>'

# 🔹 占いロジック
def generate_fortune(birth_date, gender):
    birth_year = int(birth_date[:4])
    birth_month = int(birth_date[4:6])
    birth_day = int(birth_date[6:8])

    chinese_zodiac = calculate_chinese_zodiac(birth_year)
    six_star = calculate_six_star(birth_year)
    tensei_type = calculate_tensei_type(birth_year, birth_month, birth_day)

    prompt = f"""
    あなたはプロの占い師です。以下のデータを基に {birth_date} 生まれの {gender} の運勢を詳細に占ってください。

    🔹 四柱推命（干支・五行）: {chinese_zodiac}
    🔹 六星占術（運命星）: {six_star}
    🔹 天星術（天星タイプ）: {tensei_type}

    **占い結果のフォーマット**
    - **総合運:** ○○な運勢です。
    - **仕事運:** ○○な傾向があります。
    - **恋愛運:** ○○な特徴があります。
    - **金運:** ○○に注意してください。
    - **健康運:** ○○に気をつけましょう。
    - **ラッキーカラー:** ○○
    - **ラッキーアイテム:** ○○

    ⚠ **具体的なアドバイスを200文字以内でまとめてください。**
    """

    try:
        model = genai.GenerativeModel(MODEL_NAME)
        response = model.generate_content(prompt)
        return response.text.replace("\n", "\n\n")  # ✅ 改行を適切に処理
    except Exception as e:
        return f"⚠ エラーが発生しました: {str(e)}"

# 🎨 **Streamlit Web アプリ**
st.title("🔮 本格占いアプリ 🔮")

# 🎯 ユーザー入力フォーム（デフォルト値を今日の日付に設定）
birth_date = st.text_input("生年月日を YYYYMMDD の形式で入力してください", today_date)
gender_option = st.radio("性別を選択してください", ("男性", "女性"))

# 🔘 占いボタン
if st.button("今日の運勢を占う"):
    if birth_date.isdigit() and len(birth_date) == 8:
        fortune = generate_fortune(birth_date, gender_option)
        st.subheader("✨ 今日の運勢 ✨")
        st.write(fortune)

        # **画像生成**
        img_buf = generate_image(fortune)
        st.image(img_buf, caption="📷 あなたの占い結果", use_container_width=True)  # ✅ 修正

        # **ダウンロードリンク**
        st.markdown(get_image_download_link(img_buf), unsafe_allow_html=True)

        # 🔹 Twitter シェアボタン
        tweet_text = f"🔮 今日の運勢 🔮\n{fortune[:100]}...\n\nあなたも占ってみよう！"
        tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text}&url=https://your-app-url.streamlit.app"
        st.markdown(f'[🐦 Twitter でシェア]({tweet_url})', unsafe_allow_html=True)

        # 🔹 LINE シェアボタン
        line_url = f"https://social-plugins.line.me/lineit/share?url=https://your-app-url.streamlit.app"
        st.markdown(f'[💬 LINE でシェア]({line_url})', unsafe_allow_html=True)
    else:
        st.error("⚠ 8桁の数字で入力してください (例: 19900515)")
