import streamlit as st
import google.generativeai as genai
import os

# 🔹 Streamlit Cloud の Secrets から APIキー を取得
API_KEY = st.secrets["GEMINI_API_KEY"]

# APIキーの設定
if not API_KEY:
    st.error("⚠ APIキーが設定されていません。Streamlit Cloud の Secrets を確認してください。")
else:
    genai.configure(api_key=API_KEY)

# 🔹 Gemini API モデルの選択（モデル名を変更して試す）
MODEL_NAME = "gemini-1.5-pro"  # もしくは "gemini-pro"

# 🔹 占いロジック（四柱推命・六星占術・天星術を統合）
def generate_fortune(birth_date, gender):
    prompt = f"""
    あなたはプロの占い師です。
    以下の占術を組み合わせて、{birth_date} 生まれの {gender} の運勢を詳細に占ってください。

    1️⃣ **四柱推命**: 生年月日から命式を分析し、その人の基本的な性格や運勢の流れを説明。
    2️⃣ **六星占術**: 生年月日から運命星を導き、運気の流れ（好調期・低迷期）を診断。
    3️⃣ **天星術**: 生年月日を基に、12種類の天星タイプを特定し、適性や人間関係をアドバイス。

    **鑑定結果のフォーマット**
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
birth_date = st.text_input("生年月日を YYYYMMDD の形式で入力してください", "")
gender_option = st.radio("性別を選択してください", ("男性", "女性"))

# 🔘 占いボタン
if st.button("今日の運勢を占う"):
    if birth_date.isdigit() and len(birth_date) == 8:
        fortune = generate_fortune(birth_date, gender_option)
        st.subheader("✨ 今日の運勢 ✨")
        st.write(fortune)
    else:
        st.error("⚠ 8桁の数字で入力してください (例: 19900515)")
