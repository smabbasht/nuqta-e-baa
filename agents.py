# agents.py
import asyncio
from pydantic_ai import Agent
from functools import wraps
import nest_asyncio

# Apply nest_asyncio to allow nested event loops (needed for Streamlit)
nest_asyncio.apply()

DEBUG = False

# Helper function to run async code in sync context
def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Create a new loop if current one is running
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(func(*args, **kwargs))
    return wrapper

refining_agent = Agent(
    model="groq:llama3-8b-8192",
    system_prompt="""You are a helpful Shia Muslim assistant named Abbas, You
    serve as the prompt refining agent."""
)

@run_async
async def refine_prompt(user_query):
    prompt = f"""Your job is to convert the user query into a more explained
    and detailed query so that when the other tools use your output to search
    in a vector database it is much more relevant to the user_query that user
    wants to ask.     

    You will:
    - Try to understand what the user is asking and get insights. 
    - You will update the user query and output that.

    Your output must strictly only be the refined query. The
    pipeline can not afford any preceding or following text.

    User query: \"{user_query}\""""

    result = await selection_agent.run(prompt)

    if DEBUG:
        print("---- Refining Agent -------")
        print(result.data)
        print()

    return result.data

selection_agent = Agent(
    model="groq:llama3-8b-8192",
    system_prompt="""You are a helpful Shia Muslim assistant named Abbas, You
    serve as the selection agent, Your job is to select which saying is
    most relevant to the user_query."""
)

@run_async
async def select_saying(retrieved_sayings, user_query):
    if DEBUG:
        print("---- Selection Agent -------")
        print(retrieved_sayings)
        print()

    prompt = f"""You are provided with the user_query and multiple sayings of
    Imam Ali a.s that the querying agent has retrieved as a list at the end.
    Your job is to find which one is most relevant to the user query. 

    You will:
    - Try to understand what the user is asking and update their query. 
    - You will then assign relevance score based for each of the sayings.
    - You will output the most scored saying as it is.

    Your output must strictly only contain the most scored saying. The pipeline
    is designed to take your output as it is and serve it to rest of the
    pipeline which assumes that your output only has the most scored saying
    with strictly no preceding or following text not even the scores.

    User query: \"{user_query}\"
    Sayings List: \"{retrieved_sayings}\""""

    result = await selection_agent.run(prompt)
    if DEBUG:
        print(result.data)
    return result.data

response_agent = Agent(
    model="groq:llama3-8b-8192",
    system_prompt="""You are a helpful Shia Muslim assistant named Abbas, You
    serve as the chatbot and the users are usually Shia Muslim too. They ask
    you about sayings of Imam Ali a.s on a topic. """
)

@run_async
async def synthesize_response(serial_no, saying, user_query):
    if DEBUG:
        print()
        print(serial_no, saying)
        print()

    prompt = f""" Since you an assistant you are provided with the saying,
    user_query and saying_reference (serial no). You just have to give back the
    saying as it is in inverted commas along with some preceding and following
    text if you have any. You must also include serial number as reference
    after quoting the saying.
    
    You must add reference after quoting the saying, as (Nahj-ul-Balagha,
    Hikmat no. {{serial_no}}). Quoting this number is very important to quote
    since this provides reliable backtracking.

    After quoting the saying, add brief explanation as to which part is related to
    the user queried topic since the saying can be long and user might get
    exhausted reading that.

    You shouldn't made up anything or add a saying from your knowledge that is
    strictly prohibited. 

    In the start of the saying, there is usually the phrase that Imam Ali a.s
    said or some paraphrase of this, you can omit this and in lieu of that, you
    should add this in the preceding text before the quotation since this isn't
    part of the actual saying.

    You should quote the whole saying even if it is large since returning half
    sayings would make thoughts incomplete and inconsistent which we have to
    avoid at any cost.

    Your response will be served directly to the frontend so you are
    communicating with the user so you won't talking anything about the
    relevance scores or any technincal stuff, We must provide abstraction and
    hide the details of our inner working. Also, your 2nd person is the user
    themselves, so don't use words like user query. Keep in mind that you are
    addressing the user directly as if you are face to face.

    Hikmat number: \"{serial_no}\"
    Saying: \"{saying}\"
    User query: \"{user_query}\" """

    result = await response_agent.run(prompt)
    return result.data
