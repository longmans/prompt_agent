# Prompt Optimizer Agent

> **English | [中文](README_CN.md)**

An intelligent Prompt optimization system based on multi-Agent collaboration, implementing workflow orchestration with LangGraph, supporting multiple large language models, and providing both A2A (Agent-to-Agent) service interfaces and Web UI.

## ✨ Core Features

- 🤖 **Multi-Agent Collaboration**: Professional Agent workflow based on LangGraph
- 🔄 **7-Step Optimization Process**: Complete prompt engineering optimization pipeline
- 🌐 **Multi-Model Support**: Support for Google Gemini and OpenAI GPT models
- 🚀 **A2A Service**: Standardized Agent-to-Agent interface
- 🌟 **Web Interface**: Gradio-based streaming interactive interface
- 📊 **Intelligent Evaluation**: Automatically generate evaluation metrics and improvement suggestions
- 🎯 **Role-Specific**: Customized optimization strategies for different user roles
- 🔒 **Proxy Support**: Built-in proxy configuration for network-restricted environments
- 📝 **Smart Parsing**: Support for JSON and natural language input
- 🛡️ **Robustness**: Comprehensive error handling and state management
- 🔍 **Example Validation**: Field name consistency checking and format validation
- 📋 **Session Management**: Intelligent state management and history tracking

## 🔧 Supported Models

| Provider | Model Name | Model Type ID | Configuration Required |
|----------|------------|---------------|----------------------|
| Google | Gemini 2.0 Flash | `gemini` | `GOOGLE_API_KEY` |
| OpenAI | GPT-4o-mini | `openai` | `OPENAI_API_KEY` |

## 🌐 Proxy Configuration

The system has built-in proxy support for convenient use in network-restricted environments:

### Environment Variable Configuration

```bash
# Configure proxy in .env file
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890

# Or set when starting
export HTTPS_PROXY=http://127.0.0.1:7890
export HTTP_PROXY=http://127.0.0.1:7890
python main.py
```

### Default Proxy Settings

If environment variables are not set, the system defaults to:
- HTTPS Proxy: `http://127.0.0.1:7890`
- HTTP Proxy: `http://127.0.0.1:7890`

### Common Proxy Software Ports

| Proxy Software | Default Port | Configuration Example |
|----------------|--------------|----------------------|
| Clash | 7890 | `http://127.0.0.1:7890` |
| V2Ray | 1081 | `http://127.0.0.1:1081` |
| SSR | 1080 | `http://127.0.0.1:1080` |

## 📋 7-Step Optimization Process

1. **Generate Engineering Guide** - Generate detailed prompt engineering guidelines for specific roles
2. **Analyze Role and Requirements** - Understand user roles and basic requirements
3. **Generate Initial Prompt** - Generate basic prompt based on role and requirements
4. **Create Evaluation Framework** - Create targeted prompt evaluation framework
5. **Execute Prompt Evaluation** - Comprehensive quality analysis of the prompt
6. **Generate Improvement Plans** - Provide 3 different optimization versions
7. **Select Best Version** - Automatically recommend or user-select final prompt

## 🚀 Quick Start

### Environment Setup

1. **Clone Project**
```bash
git clone <repository-url>
cd prompt_agent
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure API Keys and Server**
```bash
# Copy configuration template
cp config_example.env .env

# Edit .env file, add your API keys and server settings
GOOGLE_API_KEY=your_google_api_key_here
OPENAI_API_KEY=your_openai_api_key_here  # Optional

# Server configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=9999
LOG_LEVEL=info

# Proxy configuration (optional, defaults to http://127.0.0.1:7890)
HTTPS_PROXY=http://127.0.0.1:7890
HTTP_PROXY=http://127.0.0.1:7890

# Web interface configuration
WEB_HOST=0.0.0.0
WEB_PORT=7860
```

### Starting Services

#### A2A Service (Recommended)
```bash
python main.py
```
Service will start at http://localhost:9999

#### Web Interface
```bash
python web.py
```
Web interface will start at http://localhost:7860

#### Development Mode
```bash
# Enable hot reload and debug logging
export RELOAD=true
export LOG_LEVEL=debug
python main.py
```

## 🖥️ Web Interface Features

### 🚀 Prompt Optimization Page
- **Streaming Processing**: Real-time optimization progress display
- **Multi-Format Support**: JSON and text format example input
- **Real-time Validation**: Automatic input parameter validation
- **Result Display**: Formatted optimization result display

### 🔧 Manual Validation Page
- **Variable Management**: Automatic extraction and validation of prompt variables
- **Real-time Preview**: Preview of prompt after variable replacement
- **Error Messages**: Detailed validation error information
- **Variable Hints**: Intelligent variable definition suggestions

### 📖 Usage Guide Page
- **Complete Documentation**: Detailed usage guidelines
- **Example Showcase**: Multiple input format examples
- **Best Practices**: Prompt engineering best practice guidance

## 📖 Usage Methods

### Quick Start Example

The simplest way is to directly send keywords:

```json
{
  "messages": [
    {
      "role": "user",
      "content": "software developer"
    }
  ]
}
```

The system will automatically generate basic configuration for the software developer role.

### A2A Interface Call

Send POST request to `http://localhost:9999/` 

**Standard Request Format:**
```json
{
  "messages": [
    {
      "role": "user", 
      "content": {
        "role": "Target user role",
        "basic_requirements": "Basic task requirements",
        "examples": [...],  // Optional
        "additional_requirements": "Additional requirements",  // Optional
        "model_type": "Model type"  // Optional, defaults to openai
      }
    }
  ]
}
```

### 🤖 Gemini Model Example

```json
{
  "messages": [
    {
      "role": "user",
      "content": {
        "role": "software developers",
        "basic_requirements": "Write high-quality, maintainable Python code, including functions, classes, and API design",
        "model_type": "gemini",
        "examples": [
          {
            "input": "{\"function_name\": \"calculate_fibonacci\", \"input_type\": \"int\", \"output_type\": \"int\", \"description\": \"Calculate the nth Fibonacci number\"}",
            "output": "def calculate_fibonacci(n: int) -> int:\n    \"\"\"Calculate the nth Fibonacci number\n    Args:\n        n: Position to calculate\n    Returns:\n        int: Fibonacci number\n    \"\"\"\n    if n <= 1:\n        return n\n    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)"
          }
        ],
        "additional_requirements": "Include type hints and documentation"
      }
    }
  ]
}
```

### 🧠 OpenAI Model Example

```json
{
  "messages": [
    {
      "role": "user", 
      "content": {
        "role": "content creators",
        "basic_requirements": "Create engaging, well-structured blog articles and marketing copy",
        "model_type": "openai",
        "examples": [
          {
            "input": "{\"topic\": \"AI trends\", \"target_audience\": \"tech professionals\", \"tone\": \"professional\", \"word_count\": \"1000\"}",
            "output": "# The Future of AI: 5 Trends That Will Shape 2024\n\nArtificial Intelligence is revolutionizing how we work..."
          }
        ],
        "additional_requirements": "Engaging and accessible tone"
      }
    }
  ]
}
```

### 📝 Example Format Description

#### Field Name Consistency Requirements
Each example's input must be a JSON object, **all examples' input field names must be consistent**:

✅ **Correct Example** (consistent field names):
```json
[
  {
    "input": "{\"function_name\": \"validate_email\", \"input_type\": \"str\", \"output_type\": \"bool\"}",
    "output": "def validate_email(email: str) -> bool: ..."
  },
  {
    "input": "{\"function_name\": \"calculate_sum\", \"input_type\": \"list\", \"output_type\": \"int\"}",
    "output": "def calculate_sum(numbers: list) -> int: ..."
  }
]
```

❌ **Incorrect Example** (inconsistent field names):
```json
[
  {
    "input": "{\"function_name\": \"validate_email\", \"input_type\": \"str\"}",
    "output": "def validate_email(email: str) -> bool: ..."
  },
  {
    "input": "{\"method_name\": \"calculate_sum\", \"param_type\": \"list\"}",  // Different field names!
    "output": "def calculate_sum(numbers: list) -> int: ..."
  }
]
```

#### Supported Input Formats

**JSON Format** (recommended):
```json
[
  {
    "input": "{\"topic\": \"sustainability\", \"audience\": \"general public\", \"tone\": \"casual\"}",
    "output": "🌱 Small changes, BIG impact! ..."
  }
]
```

**Simple Text Format**:
```
Input:
topic=sustainability
audience=general public
tone=casual
Output:
🌱 Small changes, BIG impact! Here are 3 easy tips...

Input:
topic=AI trends
audience=tech professionals
tone=professional
Output:
# The Future of AI: 5 Trends That Will Shape 2024...
```

### Supported User Roles

- `software developers` - Software developers
- `content creators` - Content creators  
- `customer support representatives` - Customer service representatives
- `data scientists` - Data scientists
- `marketing professionals` - Marketing professionals
- `teachers` - Teachers
- Or any custom role

## 🛠️ Local Development and Testing

### Running Demo Scripts

```bash
# Complete feature demo
python demo.py

# Test Web interface components
python test_web.py

# Test proxy configuration and optimization
python test_proxy_optimization.py

# A2A client test
python test_client.py
```

### Development Environment Configuration

```bash
# Development mode environment variables
export RELOAD=true
export LOG_LEVEL=debug
export VERBOSE_LOGGING=true
export SERVER_PORT=8888
export WEB_PORT=7861

# Start development server
python main.py
```

## 📊 Output Format

```json
{
  "role": "Target user role",
  "basic_requirements": "Basic task requirements",
  "model_type": "Model used",
  "original_examples": [
    {
      "input": "Example input",
      "output": "Example output"
    }
  ],
  "generated_prompt": "Generated initial prompt",
  "evaluations": [
    "Evaluation result 1",
    "Evaluation result 2"
  ],
  "alternative_prompts": [
    "Improvement plan 1",
    "Improvement plan 2",
    "Improvement plan 3"
  ],
  "final_recommendation": "Final recommended prompt",
  "step": "completed"
}
```

## 🏗️ System Architecture

### Core Components
- **Multi-Agent System**: Specialized generator, evaluator, improver
- **LangGraph Workflow**: State management and process orchestration
- **Model Factory**: Unified model creation and management interface with instance caching
- **A2A Integration**: Standardized Agent service interface
- **Web Interface**: Gradio-based interactive interface with streaming support
- **Session State**: SessionState class for user session and history management

### New Features
- **Error Handling**: Classified error handling (input errors, connection errors, runtime errors)
- **Proxy Support**: Built-in proxy configuration with automatic network request handling
- **Logging System**: Complete logging with file output and different levels
- **Input Validation**: Comprehensive input validation including field name consistency checking
- **State Management**: Safe session state management avoiding global variables
- **Configuration Management**: Rich environment variable configuration options

## 🔧 Configuration Options

### Environment Variables

| Variable Name | Required | Default | Description |
|---------------|----------|---------|-------------|
| `GOOGLE_API_KEY` | Conditional* | - | Google Gemini API key |
| `OPENAI_API_KEY` | Conditional* | - | OpenAI API key |
| `SERVER_HOST` | No | `0.0.0.0` | Server host address |
| `SERVER_PORT` | No | `9999` | Server port |
| `WEB_HOST` | No | `0.0.0.0` | Web interface host address |
| `WEB_PORT` | No | `7860` | Web interface port |
| `LOG_LEVEL` | No | `info` | Log level (debug/info/warning/error) |
| `WORKERS` | No | `1` | Number of worker processes |
| `RELOAD` | No | `false` | Enable hot reload |
| `HTTPS_PROXY` | No | `http://127.0.0.1:7890` | HTTPS proxy address |
| `HTTP_PROXY` | No | `http://127.0.0.1:7890` | HTTP proxy address |
| `MODEL_TEMPERATURE` | No | `0.7` | Model temperature parameter |
| `REQUEST_TIMEOUT` | No | `60` | Request timeout (seconds) |
| `MAX_RETRIES` | No | `3` | Maximum retry attempts |

*At least one API key must be configured

### Performance Optimization

- **Model Instance Caching**: Avoid repeated model instance creation
- **Workflow Caching**: Reuse workflow instances for different model types
- **Error Recovery**: Graceful degradation when individual steps fail
- **Input Validation**: Early validation to avoid invalid requests
- **Logging**: Detailed performance and error logs
- **Session Management**: Intelligent state management and history tracking

## 🚨 Troubleshooting

### Common Issues

1. **ImportError: cannot import name 'StateGraph'**
   - Solution: Ensure correct langgraph version is installed: `pip install langgraph>=0.4.1`

2. **API Key Error**
   - Check API key configuration in .env file
   - Ensure at least one valid API key is configured
   - Verify key format is correct

3. **Port Occupied**
   - Modify port configuration in environment variables: `SERVER_PORT=8888`
   - Or stop processes occupying the port: `lsof -ti:9999 | xargs kill`

4. **Example Field Name Inconsistency Error**
   - Ensure all examples' input field names are exactly the same
   - Check JSON format is correct
   - Refer to example formats in documentation

5. **Proxy Connection Issues**
   - Check if proxy software is running normally
   - Verify proxy address and port configuration
   - Try different proxy ports

6. **Web Interface Inaccessible**
   - Check firewall settings
   - Confirm web server started normally
   - Check if port is occupied

### Logging and Debugging

```bash
# Enable verbose logging
export LOG_LEVEL=debug
export VERBOSE_LOGGING=true

# View log file
tail -f prompt_optimizer.log

# Check server status
curl http://localhost:9999/.well-known/agent.json
```

### Environment Check

The system automatically checks at startup:
- API key configuration status
- Proxy configuration status  
- Dependency package installation status
- Port availability

## 📚 More Documentation

- [System Architecture](ARCHITECTURE.md) - Detailed system architecture description
- [API Documentation](API.md) - A2A interface specifications
- [Development Guide](DEVELOPMENT.md) - Development and contribution guide
- [Changelog](CHANGELOG.md) - Version update records

## 🤝 Contributing

1. Fork the project
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Create Pull Request

## 📄 License

[MIT License](LICENSE) - See license file for details

## 🔗 Related Links

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [A2A Framework](https://github.com/a2a-dev/a2a)
- [Google Gemini API](https://ai.google.dev/)
- [OpenAI API](https://platform.openai.com/)
- [Gradio Documentation](https://gradio.app/docs/)

---

**Developer**: Multi-Agent prompt optimization system based on LangGraph  
**Version**: 1.2.0 - Enhanced Robustness and Web Interface Version  
**Last Updated**: December 2024

## 🎯 Version Features

### v1.2.0 New Features
- ✨ Complete Web interface support
- 🛡️ Enhanced error handling and state management
- 🔍 Example field name consistency validation
- 📋 Session state and history management
- 🔧 Rich environment variable configuration
- 📊 Detailed logging and monitoring
- 🚀 Streaming processing and real-time feedback
