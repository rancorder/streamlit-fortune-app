import streamlit as st
import google.generativeai as genai

# 🔹 APIキーを設定（実際のキーに変更する）
API_KEY = "YOUR_GEMINI_API_KEY"
genai.configure(api_key=API_KEY)

# 最新のモデルを指定
model = genai.GenerativeModel("gemini-1.5-pro-latest")

# 🔹 占いロジック（仮）
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
