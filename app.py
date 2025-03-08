import streamlit as st
import google.generativeai as genai
import re
from datetime import datetime, timedelta

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

# 🔹 Gemini API を使用して1週間の運勢を生成
def generate_weekly_fortune(birth_date, gender, extra_question=""):
    if not API_KEY:
        return "⚠ APIキーが設定されていません。"

    birth_year = int(birth_date[:4])
    birth_month = int(birth_date[4:6])
    birth_day = int(birth_date[6:8])
    
    start_date = datetime.now()
    week_dates = [(start_date + timedelta(days=i)).strftime("%m/%d (%a)") for i in range(7)]

    chinese_zodiac = calculate_chinese_zodiac(birth_year)
    six_star = calculate_six_star(birth_year)
    tensei_type = calculate_tensei_type(birth_year, birth_month, birth_day)

    prompt = f"""
    あなたはプロの占い師です。以下のデータを基に {birth_date} 生まれの {gender} の **1週間の運勢** をストーリー形式で占ってください。

    - **四柱推命（干支・五行）:** {chinese_zodiac}
    - **六星占術（運命星）:** {six_star}
    - **天星術（天星タイプ）:** {tensei_type}

    **【ルール】**
    - **1日ごとに異なる視点で運勢を記述する。（例: 仕事・恋愛・金運などバランスよく含める）**
    - 記号（*、■、●、◇、◆、○、◎、▶ など）を一切使用しない。
    - 改行を適切に使用し、リストは `-` を使用する。
    - 簡潔かつ明確な文章で、7日間分を記述する。
    - **週の終わりに「今週のアドバイス」を200字程度で提供する。（気をつけるべきことも含む）**

    **【出力フォーマット】**
    - **{week_dates[0]}:** ○○な運勢です。
    - **{week_dates[1]}:** ○○な傾向があります。
    - **{week_dates[2]}:** ○○な展開が予想されます。
    - **{week_dates[3]}:** ○○なチャンスが訪れそうです。
    - **{week_dates[4]}:** ○○なことに注意すると良いでしょう。
    - **{week_dates[5]}:** ○○な一日になりそうです。
    - **{week_dates[6]}:** ○○な気持ちで過ごすと良いでしょう。
    - **【今週のアドバイス】**（200字程度で詳細なアドバイス。運勢の良い点と、気をつけるべきポイントの両方を含める。）

    {"- **【追加質問】**" + extra_question if extra_question else ""}
    """

    try:
        model = genai.GenerativeModel("gemini-1.5-pro")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"⚠ エラーが発生しました: {str(e)}"

# 🎨 **Streamlit Web アプリ**
st.title("🔮 1週間の運勢ストーリー 🔮")

birth_date = st.text_input("生年月日を YYYYMMDD の形式で入力してください", value="", placeholder="例: 19900515")
gender_option = st.radio("性別を選択してください", ("男性", "女性"))

extra_question = st.text_area("特に知りたいことがあれば入力してください（例: 恋愛運を詳しく知りたい）", "")

if st.button("1週間の運勢を占う"):
    if birth_date.isdigit() and len(birth_date) == 8:
        fortune = generate_weekly_fortune(birth_date, gender_option, extra_question)
        st.subheader("✨ あなたの1週間の運勢 ✨")
        st.write(fortune)
    else:
        st.error("⚠ 8桁の数字で入力してください (例: 19900515)")
