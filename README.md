# agentd

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)

Built for the ["Agent Development Kit Hackathon with Google Cloud"](https://googlecloudmultiagents.devpost.com/)

> "`agentd` orchestrates the complex processes of idea development, much like `systemd` manages a Linux system's operations."


<html>
  <body>
    <h2 align="center">
      <img src="assets/logo.png" width="256" />
    </h2>
    <h4 align="center">
      An open-source, Multi-agent system that automates idea development
      using AI agents built using Google ADK. <br />
      <a href="http://www.youtube.com/watch?v=hfshqC7B1zM">Watch demo</a>
    </h4>
  </body>
</html>


## Overview

### The Problem

Transforming a raw idea into a well-structured plan is often challenging. Whether you are an entrepreneur, innovator, or part of a product team, the journey from concept to actionable strategy involves multiple steps:

* Identifying a meaningful problem
* Analyzing potential solutions
* Understanding competitors and target users
* Creating reports, technical insights, and marketing materials

This process can be time-consuming, fragmented, and overwhelming, especially without the right tools or guidance.

---

### The Solution: `agentd`

**agentd** is a multi-agent system designed to automate and orchestrate the entire ideation-to-initial-plan workflow.
Built on **Google Cloud's Agent Development Kit (ADK)**, `agentd` acts as an intelligent assistant that:

* Analyzes raw ideas
* Identifies problems and viable solutions
* Studies competitors and target users
* Generates structured reports, technical advice, cost estimates, and initial marketing content

`agentd` helps innovators and teams accelerate early-stage planning with data-driven insights and AI-generated collateral.

---

## Agents Architecture

`agentd` is composed of orchestrated pipelines of agents, each responsible for a specific phase in the idea development process.

```
Root Agent
 ├── Topic Analysis Pipeline (Sequential)
 │     ├── Topic Analysis Agent
 │     ├── Problem Identification Agent (uses Google Search)
 │     ├── Solution Analysis Agent
 │     └── User selects a problem & solution
 │
 ├── Solution Analysis Pipeline (Sequential)├──
 │     ├── Target Users Analysis Agent (uses Google Search)
 │     ├── Competitor Analysis Agent (uses Google Search)
 │     ├── Report Generation Agent (generates images, saves to Cloud Storage)
 │     └── User decision: proceed or not
 │
 ├── Detailing Pipeline (Parallel)
 │     ├── Idea Value Identifier Agent
 │     └── Technical Pipeline (Sequential)
 │           ├── Technical Advisor Agent
 │           └── Architecht Agent (uses Google Search)
 │
 ├── Social Media Post Generation Agent (image + text)
 │
 └── Finalization Pipeline
```

Each pipeline is modular and can be adapted or extended.

### Diagram
<!-- TODO -->
<!-- - Detailed and a better explaination to be added. -->

![flow](/assets/AGENTD_ARCH_DIAGRAM.excalidraw(1).png)


## Requirements

Before running `agentd`, ensure you have:

- Python 3.9
- Google Cloud Account and a Gemini API Key
- Google Cloud Storage Configured with a Storage Bucket (If you would like to use a different storage option see [Extending Guide](#extending-cloud-storage))


## How to Run

1. **Clone the repository**

   ```bash
   git clone https://github.com/AdityaBavadekar/agentd
   cd agentd
   ```

2. **Install `uv` (if not already installed)**

   ```bash
   curl -Ls https://astral.sh/uv/install.sh | sh
   ```

3. **(recommended) Create a virtual environment**

   ```bash
   uv venv .venv
   source .venv/bin/activate
   ```

4. **Install dependencies**

   ```bash
   uv pip sync
   ```


3. **Set up environment variables**

   - Create a `.env` file as per the provided `.env.sample`

   - Go to https://aistudio.google.com/apikey and generate and API Key, this key will be use to generate the main Gemini AI responses. Now update the .env with the API Key.
    - Google Cloud Storage Configuration:
        - After creating a Bucket, create a Service Account with the ` Storage Admin` permission
        - After downloading the JSON file, update the .env with its path .env

   
4. **Start the application**

   * **Web interface:**

     ```bash
     adk web
     ```
   * **CLI version:**

     ```bash
     adk run agentd
     ```


## Extending Cloud Storage

`agentd` is designed to be cloud-agnostic. If you prefer to use a different cloud provider or your own custom storage solution, you can easily extend the storage system:

1. **Implement your storage class**
Create a class that inherits from `CloudStorage` (found in `agentd/utils/cloud_storage_base.py`) and implements the the required methods.
Each method defines basic file operations your storage service must provide.

2. **Update the factory method**
In `agentd/utils/__init__.py`, modify:

```python
def get_cloud_storage():
    """
    Returns an instance of the default Cloud Storage implementation.
    This function is a wrapper so it remains independent of the specific cloud storage used.
    """
    return GCPStorage()  # Replace with `return YourCustomStorage()`
```


- This design ensures that `agentd` remains independent of any specific cloud provider.



## Acknowledgements / External Libraries Used

`agentd` is built with the help of several excellent open-source libraries:

* **[google-adk](https://github.com/google/adk-python/)** - Framework for building and orchestrating multi-agent systems using Google Cloud’s Agent Development Kit.
* **[graphviz](https://graphviz.org/)** - Graph visualization software for rendering agent workflows and relationships.
* **[markdown2](https://github.com/trentm/python-markdown2)** - Fast and complete Markdown parser for generating reports.
* **[matplotlib](https://matplotlib.org/)** - Library for creating static, animated, and interactive visualizations.
* **[networkx](https://networkx.org/)** - Library for creating, manipulating, and analyzing complex networks.
* **[weasyprint](https://weasyprint.org/)** - Library for generating PDF documents from HTML and CSS.
* **[wordcloud](https://github.com/amueller/word_cloud)** - Simple library for creating word cloud visualizations.


## Formatting

The codebase uses **Black** and **isort** for consistent Python formatting.
Run following before committing changes:
```
black . && isort .
```

* **[Black](https://black.readthedocs.io/)** - for automatic Python code formatting
* **[isort](https://pycqa.github.io/isort/)** - for import sorting


## License

This project is licensed under the Apache License 2.0. See the [LICENSE](/LICENSE.md) file for details.



```
Copyright 2025 Aditya Bavadekar

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```