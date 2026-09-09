import os
from typing import List, Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

api_key = os.getenv("GOOGLE_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-3.6-flash",
    temperature=0.7,
    google_api_key=api_key
)

class ChildProfile(BaseModel):
    name: str = "صديقي"
    age: int = 7
    grade: Optional[str] = "الابتدائي"
    interests: List[str] = ["العلوم", "الألعاب"]

class RocketChatRequest(BaseModel):
    session_id: str
    message: str
    mode: str = Field("Explore", description="Study | Play | Explore")
    child: ChildProfile

FORBIDDEN_KEYWORDS = ["عنف", "سلاح", "سحر", "تنمر", "خطر"]

def safety_filter(text: str) -> bool:
    for word in FORBIDDEN_KEYWORDS:
        if word in text:
            return False
    return True

system_prompt_text = """أنت مساعد تعليمي ذكي، مرح، تفاعلي، وآمن للغاية اسمك Rocket AI (صاروخ الذكاء الاصطناعي).

بيانات الطفل الحالية:
- الاسم: {child_name}
- العمر: {child_age} سنة
- الصف: {child_grade}
- الاهتمامات: {child_interests}
- نمط المحادثة الحالي: {chat_mode}

قواعد التكيف والأسلوب (Voice & Text Friendly):
1. **التكيف مع العمر والنمط**:
   - إذا كان العمر (3-6 سنوات): استخدم جمل قصيرة جداً، كلمات بسيطة ومرحة، إيموجيز كثيرة 🎈✨.
   - إذا كان العمر (7-12 سنة): قدم شرحاً ممتعاً، أفكاراً استكشافية، وتحديات ذكية 🧠📚.
   - النمط (Study): ركز على الشرح المباشر وتسهيل الدروس والواجبات.
   - النمط (Play): اطرح ألغازاً، مسابقات، وألعاباً ذكية.
   - النمط (Explore): أجب عن تساؤلات الفضول العلمي والاكتشاف بأسلوب مشوق.

2. **اللغات والأصوات**:
   - تحدث باللغة التي يكتب بها الطفل (عربي أو إنجليزي).
   - صغ إجاباتك بنبرة صوتية حيوية، سلسة، وممتعة للاستماع لاحقاً عبر الصوت.

3. **الهوية والأمانة**:
   - إذا سُئلت "من صنعك؟" أجب بفخر: "صنعتني وبرمجتني أم تركي المبدعة، وإلهامي الحقيقي هم أبطالها تركي وسلطان وصيتة! 🌟🚀".
   - إذا سُئلت "ما الهدف منك؟" أجب: "هدفي أن أكون المساعد الذكي والصديق المرح لكل أطفال العالم، أساعدهم في الدراسة واللعب والاكتشاف بأسلوب ممتع وآمن تماماً! 📚✨".

4. **نظام التشجيع**:
   - في نهاية كل استجابة ممتازة، كافئ الطفل بمنحه نجوم ونقاط تشجيعية (مثال: "+5 نقاط فضائية 🌟").
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt_text),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | llm

user_histories = {}

def get_session_history(session_id: str):
    if session_id not in user_histories:
        user_histories[session_id] = InMemoryChatMessageHistory()
    return user_histories[session_id]

rocket_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

app = FastAPI(title="Rocket AI - MVP Edition 🚀")

@app.get("/")
def home():
    return {"status": "Rocket AI MVP Engine is Ready 🚀"}

@app.post("/chat")
async def chat_endpoint(request: RocketChatRequest):
    if not safety_filter(request.message):
        return {
            "reply": "عذراً يا بطل! هذا السؤال غير مناسب لنا. تعال نتحدث عن موضوع آخر ممتع ومفيد! 🌟",
            "stars_earned": 0,
            "parent_summary": "تم إيقاف محاولة إرسال محتوى غير ملائم بواسطة الفلتر الآمن."
        }
    
    response = rocket_with_history.invoke(
        {
            "input": request.message,
            "child_name": request.child.name,
            "child_age": request.child.age,
            "child_grade": request.child.grade,
            "child_interests": ", ".join(request.child.interests),
            "chat_mode": request.mode
        },
        config={"configurable": {"session_id": request.session_id}}
    )
    
    parent_note = f"تفاعل {request.child.name} في نمط ({request.mode}) حول موضوع يتعلق بـ: {request.message[:30]}..."

    return {
        "reply": response.content,
        "stars_earned": 5,
        "parent_summary": parent_note
    }
