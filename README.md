# 🤖 AI智能伴侣 - Agent智能体版

基于 Python + DeepSeek 大模型 + Streamlit 打造的AI智能陪伴系统，支持Function Calling工具调用

## ✨ 六大特色功能

1. **情感识别与情绪适配** - 自动识别情绪，切换对应人设
2. **长期陪伴养成系统** - 等级经验、天数统计、SQLite持久化
3. **定时提醒功能** - APScheduler后台调度，支持单次/每日重复
4. **对话一键导出** - Markdown / TXT 两种格式
5. **多模态图文问答** - 接入DeepSeek-VL，上传图片提问
6. **🤖 Agent工具调用（新增）** - LLM自主判断调用工具，具备基础智能体能力

## 🔧 内置工具集

| 工具名称 | 功能 |
|---------|------|
| **计算器** | 加减乘除、括号运算，精准数学计算 |
| **时间查询** | 查询当前日期、时间、星期几 |
| **待办管理** | 添加/查看/完成/删除待办事项，本地持久化 |

## 🚀 快速启动

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置API Key
复制 `.env.example` 为 `.env`，填入你的DeepSeek API Key

### 3. 启动
- 双击 `启动.bat`
- 或命令行执行：`streamlit run app.py`

### 4. 开启Agent模式
左侧边栏打开「工具调用智能体」开关即可体验Agent能力

## 🌐 公网部署

### 方案一：Streamlit Community Cloud（免费）
1. 上传GitHub → share.streamlit.io关联部署
2. 配置环境变量DEEPSEEK_API_KEY

### 方案二：云服务器
```bash
nohup streamlit run app.py --server.port 8501 --server.address 0.0.0.0 &
```

## 📁 项目结构
```
ai_companion/
├── app.py              # 主入口
├── 启动.bat            # Windows一键启动
├── requirements.txt
├── .env.example
├── config/settings.py  # 配置
├── llm/                # 大模型封装（基类/对话/视觉）
├── features/           # 功能模块（情绪/提醒/导出）
├── tools/              # 工具集（计算器/时间/待办）
├── agent/              # Agent智能体核心
├── memory/database.py  # SQLite数据库
└── utils/              # 工具（日志/装饰器）
```

## 💡 Python高级语法应用

| 语法特性 | 应用场景 |
|---------|---------|
| **OOP面向对象+继承** | BaseLLM基类、BaseTool工具基类 |
| **装饰器** | 接口自动重试、执行日志统计 |
| **生成器yield** | 流式输出、Agent分步执行 |
| **ABC抽象基类** | 工具基类定义统一接口 |
| **@property** | 只读属性封装 |
| **魔术方法__call__** | LLM实例可直接函数调用 |
| **静态方法** | 图片编码、工具方法 |

## 📝 简历/Boss直聘话术

> 独立迭代开发AI智能陪伴系统，基于Python实现DeepSeek大模型对接；通过面向对象、装饰器、生成器等高级语法完成项目工程化封装；实现情绪识别自动切换人设、陪伴等级养成、定时任务提醒、对话导出、多模态图文问答五大特色功能；**新增LLM Function Calling工具调用能力，内置计算器、时间查询、待办管理等工具，具备基础AI Agent智能体自主执行能力**；使用SQLite做持久化存储，基于Streamlit搭建交互界面，支持Streamlit Cloud与Docker两种公网部署方案。

## 🔮 后续可拓展方向

- 新增更多工具：联网搜索、文件读写、邮件发送
- RAG私有知识库接入
- 多智能体协作系统
- FastAPI后端解耦，前后端分离
- Docker容器化部署
- Ollama本地大模型支持
