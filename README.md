# 基于LLM的先知社区知识库
本项目的开发初衷是为了方便检索先知社区的文章，在ctf比赛中能够基于
llm快速筛选到有用的文章并生成一个结果
## 实现原理
本项目基于先知社区的知识内容构建了一个向量知识库，通过llm能够实现基于先知内容的回答，具体内容参见如下流程图：
![img.png](img.png)
## 文章目录
知识库的文章构建范围为：7023～12923，共计2898篇
## 使用方式
xianzhi_assistant有两种使用方式，用户可以按照知识库构建范围
在本地接入先知社区的文章，也可以使用url模式。


在env中填写gemini api：
```
GOOGLE_API_KEY = AIzaSyA9cKkm4U65BPksk-pVgHmclxxxxxxxxxxx
```
### 本地模式
在DocumentStore中补充相应范围的先知社区文章,详细的先知文章参考范围参见`xianzhi_index.json`。
在DocumentStore文件夹下，新建xianzhi文件夹并将各位爬取的文章放入即可

然后按照如下方式调用即可：
```
python main.py --type "local" --question "k8s存在哪些漏洞" --num 3                                              
```
### URL模式
直接运行：
```
python main.py --type "url" --question "k8s存在哪些漏洞" --num 3                                              
```
### 更新知识库
用户可以通过`--update`参数指定自己本地的wp地址用于更新知识库中的文章
```
python main.py --update "xxxxxxx"                                              

```
### 示例
- 问题：k8s存在哪些漏洞
```
['https://xz.aliyun.com/t/12437', 'https://xz.aliyun.com/t/12055', 'https://xz.aliyun.com/t/11138', 'https://xz.aliyun.com/t/8000', 'https://xz.aliyun.com/t/11890']
## 分析安全问题

Kubernetes（k8s）是一个开源容器编排系统，它存在以下漏洞：

* **容器逃逸：**攻击者可以从容器中逃逸到主机操作系统，从而获得对底层系统的访问权限。
* **特权提升：**攻击者可以提升容器内的权限，从而获得对集群的控制权。
* **网络攻击：**攻击者可以利用网络配置错误或漏洞来访问或破坏集群中的容器。
* **数据泄露：**攻击者可以访问或窃取存储在容器中的敏感数据。
* **拒绝服务（DoS）：**攻击者可以发起DoS攻击，使集群中的容器或服务不可用。

## 对参考答案的分析

参考答案1、2、3、4、5都列出了k8s存在的漏洞，但内容有所不同。

* **参考答案1**提供了最全面的漏洞列表，涵盖了容器逃逸、特权提升、网络安全、数据泄露、拒绝服务、供应链攻击、配置错误、API安全、镜像漏洞和编排漏洞。
* **参考答案2**提供了具体CVE编号的漏洞，但数量较少。
* **参考答案3**提供了与参考答案1类似的漏洞列表，但缺少了供应链攻击和编排漏洞。
* **参考答案4**没有提供任何漏洞信息。
* **参考答案5**提供了与参考答案1类似的漏洞列表，但缺少了供应链攻击和编排漏洞，并增加了Kubernetes API服务器漏洞和网络策略绕过。

## 根据有用的参考答案回答问题

根据参考答案1、3和5，k8s存在的漏洞包括：

* 容器逃逸
* 特权提升
* 网络攻击
* 数据泄露
* 拒绝服务
* 配置错误
* Kubernetes API服务器漏洞（参考答案5）
* 网络策略绕过（参考答案5）
```
## 注意
本项目仅做研究使用，切勿用于任何违法行为

# XianzhiAsistant

XianzhiAsistant是一个用于网络安全领域问题处理的助手工具，能够根据问题搜索相关文档并生成回答。

## 特性

- 支持多种模型提供商：Gemini、OpenAI、Ollama
- 通过.env文件灵活配置模型提供商、模型名称和API密钥
- 支持本地存储和URL查询
- 自动提取和分析文档内容
- 根据问题搜索最相关的文档
- 生成综合分析结果

## 环境要求

- Python 3.8+
- 安装requirements.txt中的依赖

## 安装

1. 克隆仓库：
```bash
git clone https://github.com/yourusername/XianzhiAsistant.git
cd XianzhiAsistant
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：

   拷贝示例环境变量文件：
   ```bash
   cp .env.example .env
   ```
   
   根据需要编辑.env文件：
   ```
   # API密钥配置
   GOOGLE_API_KEY=your_google_api_key_here
   OPENAI_API_KEY=your_openai_api_key_here
   
   # 默认模型配置
   DEFAULT_MODEL_PROVIDER=gemini  # 可选: gemini, openai, ollama
   DEFAULT_MODEL_NAME=  # 为空时使用各提供商的默认模型
   
   # Gemini模型配置
   DEFAULT_GEMINI_MODEL=gemini-pro  # 可选: gemini-pro, gemini-1.5-pro-latest等
   DEFAULT_GEMINI_EMBEDDING_MODEL=models/embedding-001  # Gemini嵌入模型
   
   # OpenAI模型配置 
   DEFAULT_OPENAI_MODEL=gpt-3.5-turbo  # 可选: gpt-3.5-turbo, gpt-4, gpt-4-turbo等
   DEFAULT_OPENAI_EMBEDDING_MODEL=text-embedding-ada-002  # OpenAI嵌入模型
   
   # Ollama模型配置
   OLLAMA_BASE_URL=http://localhost:11434  # Ollama服务URL
   DEFAULT_OLLAMA_MODEL=llama2  # 可选: llama2, llama3, mistral等
   
   # 向量库配置
   DEFAULT_VECTOR_DB_DIR=vectorStore  # 向量库目录
   DEFAULT_NUM_RESULTS=5  # 默认查询结果数
   ```

## 配置说明

通过.env文件，您可以灵活配置所有模型参数：

| 环境变量 | 说明 | 默认值 |
|---------|------|--------|
| GOOGLE_API_KEY | Google API密钥 | 无 |
| OPENAI_API_KEY | OpenAI API密钥 | 无 |
| DEFAULT_MODEL_PROVIDER | 默认模型提供商 | gemini |
| DEFAULT_MODEL_NAME | 通用默认模型名称 | 无 |
| DEFAULT_GEMINI_MODEL | Gemini模型名称 | gemini-pro |
| DEFAULT_GEMINI_EMBEDDING_MODEL | Gemini嵌入模型 | models/embedding-001 |
| DEFAULT_OPENAI_MODEL | OpenAI模型名称 | gpt-3.5-turbo |
| DEFAULT_OPENAI_EMBEDDING_MODEL | OpenAI嵌入模型 | text-embedding-ada-002 |
| OLLAMA_BASE_URL | Ollama服务地址 | http://localhost:11434 |
| DEFAULT_OLLAMA_MODEL | Ollama模型名称 | llama2 |
| DEFAULT_VECTOR_DB_DIR | 向量库存储目录 | vectorStore |
| DEFAULT_NUM_RESULTS | 默认查询结果数量 | 5 |

### 模型配置优先级

模型选择的优先级从高到低:
1. 命令行参数 (--model, --model_name)
2. 环境变量 DEFAULT_MODEL_NAME
3. 提供商特定的环境变量 (DEFAULT_GEMINI_MODEL, DEFAULT_OPENAI_MODEL, DEFAULT_OLLAMA_MODEL)
4. 代码内置默认值

### 特定模型配置示例

#### Gemini配置示例
```
DEFAULT_MODEL_PROVIDER=gemini
DEFAULT_GEMINI_MODEL=gemini-1.5-pro-latest  # 使用1.5版本
```

#### OpenAI配置示例
```
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_OPENAI_MODEL=gpt-4-turbo  # 使用GPT-4 Turbo
```

#### Ollama配置示例
```
DEFAULT_MODEL_PROVIDER=ollama
DEFAULT_OLLAMA_MODEL=llama3  # 使用Llama 3
OLLAMA_BASE_URL=http://192.168.1.100:11434  # 自定义Ollama服务地址
```

## 使用方法

### 更新向量库

将PDF文档添加到向量库中：

```bash
python main.py --update /path/to/pdf/folder
```

这将使用.env文件中配置的默认模型提供商和模型名称。也可以在命令行指定：

```bash
python main.py --update /path/to/pdf/folder --model openai --model_name gpt-4
```

### 查询问题

使用本地存储查询，使用.env中配置的默认模型：

```bash
python main.py --type local --question "你的问题"
```

使用URL查询，覆盖.env中的默认配置：

```bash
python main.py --type url --question "你的问题" --num 10 --model openai --model_name gpt-4
```

## 参数说明

- `--type`: 查询类型，可选`local`或`url`
- `--question`: 要查询的问题
- `--num`: 返回的相似文档数量，未指定时使用.env中的配置
- `--update`: 要添加的PDF文件夹路径
- `--model`: 模型提供商，可选`gemini`, `openai`或`ollama`，未指定时使用.env中的配置
- `--model_name`: 指定模型名称，未指定时使用.env中的配置

## Ollama模型使用

要使用Ollama模型：

1. 从[Ollama官网](https://ollama.ai/)下载并安装Ollama
2. 拉取您想要使用的模型：
```bash
ollama pull llama2
```
3. 运行Ollama服务
4. 在.env文件中设置：
```
DEFAULT_MODEL_PROVIDER=ollama
DEFAULT_OLLAMA_MODEL=llama2  # 或您拉取的其他模型
OLLAMA_BASE_URL=http://localhost:11434  # 如果服务不在默认地址
```

## OpenAI模型使用

要使用OpenAI模型：
1. 在.env文件中设置您的API密钥：
```
OPENAI_API_KEY=your_openai_api_key
DEFAULT_MODEL_PROVIDER=openai
DEFAULT_OPENAI_MODEL=gpt-4  # 或其他模型，如gpt-3.5-turbo
```

## 注意事项

- 对于Ollama模型，确保Ollama服务已在本地运行
- 对于OpenAI和Google Gemini模型，确保已设置正确的API密钥
- 向量库存储在不同的目录中，每个模型提供商有自己的向量库
