import streamlit as st
import google.generativeai as genai
import os
from datetime import datetime

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

# 🔹 占いロジック（詳細データを Gemini API に送信）
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
        return response.text
    except Exception as e:
        return f"⚠ エラーが発生しました: {str(e)}"

# 🎨 **Streamlit Web アプリ**
st.title("🔮 本格占いアプリ 🔮")

# 🎯 ユーザー入力フォーム
birth_date = st.text_input("生年月日を "20000220" の形式で入力してください", "")
gender_option = st.radio("性別を選択してください", ("男性", "女性"))

# 🔘 占いボタン
if st.button("今日の運勢を占う"):
    if birth_date.isdigit() and len(birth_date) == 8:
        fortune = generate_fortune(birth_date, gender_option)
        st.subheader("✨ 今日の運勢 ✨")
        st.write(fortune)
    else:
        st.error("⚠ 8桁の数字で入力してください (例: 19900515)")
