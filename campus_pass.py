from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.document_loaders import WebBaseLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
load_dotenv()

# 定义URL为西安理工大学计算机学院的相关网页
WEB_URL = ["https://jsj.xaut.edu.cn/info/1046/1028.htm", "https://jsj.xaut.edu.cn/info/1046/1026.htm", "https://jsj.xaut.edu.cn/info/1046/1025.htm",
           "https://jsj.xaut.edu.cn/info/1046/1030.htm", "https://jsj.xaut.edu.cn/info/1046/1722.htm", "https://jsj.xaut.edu.cn/info/1046/1907.htm",
           "https://jsj.xaut.edu.cn/info/1046/3662.htm", "https://jsj.xaut.edu.cn/info/1046/3650.htm", "https://jsj.xaut.edu.cn/info/1046/3854.htm",
           "https://jsj.xaut.edu.cn/info/1046/3855.htm", "https://jsj.xaut.edu.cn/xygk/xyjs.htm", "https://jsj.xaut.edu.cn/szdw/jsjkxyjsx.htm",
           "https://jsj.xaut.edu.cn/info/1081/3241.htm", "https://jsj.xaut.edu.cn/info/1081/3243.htm"]
# 使用WebBaseLoader加载HTML
loader = WebBaseLoader(WEB_URL)
docs = loader.load()
# 使用Openai的嵌入模型"text-embedding-3-large"
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
# 导入递归字符文本分割器
text_splitter = RecursiveCharacterTextSplitter(chunk_size=384, chunk_overlap=0,
                                               separators=["\n\n", "\n", " ", "", "。", "，"])
# 导入文本
documents = text_splitter.split_documents(docs)
# 存入向量数据库
vectorstore = Chroma.from_documents(documents, embeddings)

# 创建提示词模板
prompt = ChatPromptTemplate.from_template("""使用下面的语料来回答本模板最末尾的问题。如果你不知道问题的答案，直接回答 "不好意思，
我并不清楚这方面的内容"，禁止随意编造答案。保证答案尽可能具体简洁。以下是语料：
<context>
{context}
</context>

Question: {input}""")
# 调用豆包大模型
llm = ChatOpenAI(
    # 环境变量中配置您的API Key
    openai_api_key=os.environ.get("ARK_API_KEY"),
    # 替换为您需要调用的模型服务Base Url
    openai_api_base="https://ark.cn-beijing.volces.com/api/v3/",
    # 替换为您创建推理接入点 ID
    model_name="ep-20241231122847-ksl5g" # 这里使用Doubao-pro-256k 通用大模型
)
# 我们设置一个链，该链接受一个问题和检索到的文档并生成一个答案。
document_chain = create_stuff_documents_chain(llm, prompt)
# 使用检索器动态选择最相关的文档并将其传递。
retriever = vectorstore.as_retriever()
retrieval_chain = create_retrieval_chain(retriever, document_chain)

# FastAPI部署app作为服务器
app = FastAPI(
    title="校园通",
    version="0.0.1",
    description="理工大教师信息助手"
)

# 配置跨域中间件
origins = ["*"]  # 这里允许所有来源的跨域请求，实际应用中可按需配置更精细的规则
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/", tags=["校园通"])
async def askQuestion(question: str):
    res = retrieval_chain.invoke(
        {"input": question}
    )
    return res.get("answer")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)