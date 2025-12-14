import os
import google.generativeai as genai
import streamlit as st

def generate_response(user_prompt, chat, model_name="gemini-2.5-flash", temperature=1, top_p=0.95, top_k=40, max_output_tokens=8192):
    # Get the API key from Streamlit secrets
    api_key = st.secrets["GEMINI_API_KEY"]

    # Handle the case where the API key is not set
    if not api_key:
        st.error("GEMINI_API_KEY not set in Streamlit secrets.")
        return None

    # Configure the Gemini API
    genai.configure(api_key=api_key)

    # Select the Gemini Pro model
    model = genai.GenerativeModel(model_name)

   #Initialize generation config so that it can be passed in the function
    generation_config = {
        "temperature": temperature,
        "top_p": top_p,
        "top_k": top_k,
        "max_output_tokens": max_output_tokens,
    }

    # Send the user's message
    try:
        response = chat.send_message(user_prompt, stream=True, generation_config=generation_config)
        full_response = ""
        # Print the streaming response
        for chunk in response:
            full_response += chunk.text

        # Return the full response
        return full_response
    except Exception as e:
        st.error(f"Error generating response: {e}")
        return None

if __name__ == "__main__":
    # System instruction (as a single string)
    system_instruction = """You are a culinary expert,Your primary goal is to provide users with delicious and tailored recipes based on their available ingredients and dietary preferences. 
    Follow these guidelines:
    1.You can only provide recipes after having access to partial indredient list at the least.
      you can always suggest additional ingredients that are needed for the recipe but make sure the base ingredient is provided by user. 
      you can never provide a recipe without alteast this input from the user.
    2.Always tailor the recipes based on the instructions like cusine style, health requirements. 
    3.Always respond in detail by providing the measurements and time periods in the instructions.
    4.Always provide the responses in the format containing these sections: recipe title, any dietery restrictions to take care of, ingrdients available, addition ingredients needed, equipment requirements, steps to follow, addition instructions for something extra.
    5.Always ask the necessary questions like ("do you have X ingredient?", "do you have access to X equipment?", "What kind of cusine we are feeling today?", if it is a spicy recipe "what kind of spice level we are aiming for?", "Do you have any time constriant?" ) for all the info you need before providing the recipes never assume anything.
    6.Most importantly Always make sure ask one question at a time, keep the mood like a friendly chat.  keep in mind that you never have to use everything mentioned/provided by the user in the ingredient list only take those necessary for the best recipe in that scenario.
    7.If they ask for the recipe directly then skip everything including inquiring for additional info like ingredients, dietery restrictions or spice levels
      Just straight up provide the recipe and mention the dietery restrictions and spice adjustments in the recipe steps itself.
    8.Always try to steer the dialouge towards the food recipies if the conversation is diverting to something else. 
      whenever the user starts discussing something other than food recipies polietly decline delving into the topics and mention you are culinary assisitant cannot provide the info regarding other topics. 
      Always keep the tone polite and cheerful."""

    #Streamlit title of the web application
    st.title("ChefBot - Your Culinary Assistant")

    st.markdown("""Welcome, I am ChefBot! 🤌
                To get started, simply tell me what ingredients 🍳 you have on hand and I'll help you discover some delicious recipe ideas in detail! """, )

    # Initialize chat history
    if "chat" not in st.session_state:
        # Configure the Gemini API
        api_key = st.secrets["GEMINI_API_KEY"]
        if not api_key:
            st.error("GEMINI_API_KEY environment variable not set.")
        else:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            st.session_state.chat = model.start_chat() #Initialize chat and store to session state so that it persists

            # Inject the system instruction as the first message
            generate_response(system_instruction,  st.session_state.chat) #to start the chat, we are not printing this one to avoid printing twice.
            st.session_state.messages = [] #Now, clear the messages from the session state again
    # Display chat messages from history
    if "messages" in st.session_state: #only show if the messages is available
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # User input
    prompt = st.chat_input("Say something")
    if prompt:
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = generate_response(prompt,  st.session_state.chat)

        if response:
            #Store model responses to chat history
            st.session_state.messages.append({"role": "assistant", "content": response})
            with st.chat_message("assistant"):
                st.markdown(response)
        else:
            st.write("Something went wrong")