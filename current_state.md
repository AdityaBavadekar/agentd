# Where are Google Technologies?

- `google_search` - ADK Tool
- Google Cloud Storage - Upload/Download/Generate link
- Text Generation: Using Gemini models
- Image Generation: Using Gemini models (but using Imagen is also supported just kept disable due to pricing)


# TODOs:
1. Once the image is generated and uploaded to Cloud Storage, since the url is signed and has complex pattern the
   the agent ends up adding wrong charachter to the url generated response. Which leads to invalid image url.
   Solution A: create json file and store all urls belonging to the state to it and then retrieve accordingly.
   Solution B: create a shortner that will register this signed url path and will delete after timeout. and then return smaller identifier <8 charachters.


# What is not working?

2. [SEVERE] There is not a "Advanced usage" of Google Cloud/Any Cloud


## Implemented but "NEEDS TESTING"
<!--  -->

## FIXED

1. Solution Analysis agent flow ends up asking user Two times
3. Images, Files and Reports should be generated and saved to cloud not locally as this will run on a server.
4. The output of Posts agents is not Structured, we need to parse it and add rules.
5. [REMOVED][SEVERE] Images Generation Agent does not do anything right now [TODO]
6. Key Things From ADK To be used:
    - Agent
    - Sequential
    - Parelell
    - Tools
    - State
    - Callbacks
    - Sub Agents
7. Fill "Add your description" in pyptoject.toml 