import streamlit as st
import google.generativeai as genai
import re
from datetime import datetime

# 🔹 APIキーの取得
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
    genai.configure(api_key=API_KEY)
else:
    st.error("⚠ APIキーが設定されていません。Streamlit Cloud の Secrets を確認してください。")
    API_KEY = None

# 🔹 干支・五行（四柱推命）を計算
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

# 🔹 Gemini API を使用して占い結果を生成
def generate_fortune(birth_date, gender):
    if not API_KEY:
        return "⚠ APIキーが設定されていません。"

    birth_year = int(birth_date[:4])
    birth_month = int(birth_date[4:6])
    birth_day = int(birth_date[6:8])

    chinese_zodiac = calculate_chinese_zodiac(birth_year)
    six_star = calculate_six_star(birth_year)
    tensei_type = calculate_tensei_type(birth_year, birth_month, birth_day)

    prompt = f"""
    あなたはプロの占い師です。以下のデータを基に {birth_date} 生まれの {gender} の運勢を占ってください。

    - **四柱推命（干支・五行）:** {chinese_zodiac}
    - **六星占術（運命星）:** {six_star}
    - **天星術（天星タイプ）:** {tensei_type}

    **【ルール】**
    - 記号（*、■、●、◇、◆、○、◎、▶ など）を一切使用しない。
    - 改行を適切に使用し、リストは `-` を使用する。
    - 簡潔かつ明確な文章で、200文字以内でまとめる。

    **【出力フォーマット】**
    - **総合運:** ○○な運勢です。
    - **仕事運:** ○○な傾向があります。
    - **恋愛運:** ○○な特徴があります。
    - **金運:** ○○に注意してください。
    - **健康運:** ○○に気をつけましょう。
    - **ラッキーカラー:** ○○
    - **ラッキーアイテム:** ○○
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠ エラーが発生しました: {str(e)}"

# 🎨 **Streamlit Web アプリ**
st.title("🔮 本格占いアプリ 🔮")

birth_date = st.text_input("生年月日を YYYYMMDD の形式で入力してください", value="", placeholder="例: 19900515")
gender_option = st.radio("性別を選択してください", ("男性", "女性"))

if st.button("今日の運勢を占う"):
    if birth_date.isdigit() and len(birth_date) == 8:
        fortune = generate_fortune(birth_date, gender_option)

        # **念のため記号削除**
        fortune_cleaned = re.sub(r"[■●◇◆○◎▶☀️★☆━─□]", "", fortune)

        st.subheader("✨ 今日の運勢 ✨")
        st.write(fortune_cleaned)

        # **Twitter シェアボタン**
        tweet_text = f"🔮 今日の運勢 🔮\n{fortune_cleaned[:100]}...\n\nあなたも占ってみよう！"
        tweet_url = f"https://twitter.com/intent/tweet?text={tweet_text}&url=https://your-app-url.streamlit.app"
        st.markdown(f'[🐦 Twitter でシェア]({tweet_url})', unsafe_allow_html=True)

        # **LINE シェアボタン**
        line_url = f"https://social-plugins.line.me/lineit/share?url=https://your-app-url.streamlit.app"
        st.markdown(f'[💬 LINE でシェア]({line_url})', unsafe_allow_html=True)
    else:
        st.error("⚠ 8桁の数字で入力してください (例: 19900515)")
