import streamlit as st
import google.generativeai as genai
import toml

# 🔹 secrets.toml から APIキー を読み込む
with open("secrets.toml", "r") as f:
    secrets = toml.load(f)
API_KEY = secrets.get("GEMINI_API_KEY", "")

# APIキーの設定
if not API_KEY:
    st.error("⚠ APIキーが設定されていません。secrets.toml を確認してください。")
else:
    genai.configure(api_key=API_KEY)

# 最新のモデルを指定
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# 🔹 占いロジック
def generate_fortune(birth_date, gender):
    prompt = f"""
    あなたはプロの占い師です。
    生年月日 {birth_date} の {gender} の運勢を占ってください。
    200文字以内で、ポジティブなアドバイスを含めてください。
    """
    response = model.generate_content(prompt)
    return response.text

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
