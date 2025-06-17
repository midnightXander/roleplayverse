from openai import OpenAI
#from openai.types.chat import ChatCompletionRequest, ChatCompletionResponse
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY_TEST')
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")

client = OpenAI(api_key=api_key)
def generate_chat_completion(messages, model="gpt-3.5-turbo", temperature=0.7):
    """
    Generate a chat completion using OpenAI's API.

    :param messages: List of messages to send to the model.
    :param model: The model to use for generating the completion.
    :param temperature: Sampling temperature to use for the generation.
    :return: The response from the OpenAI API.
    """
    # request = ChatCompletionRequest(
    #     model=model,
    #     messages=messages,
    #     temperature=temperature
    # )
    
    # response: ChatCompletionResponse = client.chat.completions.create(request)
    
    #return response

def sample_response(content="Hello, how can you assist me today?", model="gpt-3.5-turbo", temperature=0.5):
    """
    Generate a sample response using the OpenAI API.
    
    :return: A sample response from the OpenAI API.
    """
    messages = [
        {"role": "system", "content": "Tu es arbitre pour un combat de roleplay dans l'univers Naruto. Donne un verdict sur chaque action en fonction des capacités du personnage et indique si le combat continue."},
        {"role": "user", "content": content}
    ]
    
    #response = generate_chat_completion(messages)
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=temperature
    )
    
    #return response.choices[0].message.content if response.choices else None
    return response.output_text



# client = OpenAI(
#   api_key="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"
# )

# def sample_response2():

#     completion = client.chat.completions.create(
#     model="gpt-4o-mini",
#     store=True,
#     messages=[
#         {"role": "user", "content": "write a haiku about ai"}
#     ]
#     )

#     print(completion.choices[0].message)



if __name__ == "__main__":
    # Example usage
    #sample_response2()
    #response = sample_response("GAI:  Dans le monde ninja, peu incarnent l’énergie et la passion comme **Might Guy**. Avec son sourire indéfectible et sa détermination inébranlable, il est le champion de la jeunesse et de l'esprit combatif. Entraîné avec acharnement, Gai a consacré sa vie à devenir le meilleur ninja, s'appuyant sur la force de ses techniques de taijutsu. Face à l'ancien Hokage **Hiruzen Sarutobi**, Gai se prépare à prouver que l'esprit et la volonté peuvent surmonter tous les obstacles. Avec la promesse d'un combat épique, il est prêt à démontrer que le véritable pouvoir réside dans le cœur et l'amitié. Séparé de son adversaire par une distance de 10 mètres, Gai scrute chaque mouvement de Hiruzen. D'un geste fluide, il laisse glisser un kunai de sa manche, le lançant avec une vitesse fulgurante de 5 m/s. La précision de son attaque ne laisse que 2 secondes à son adversaire pour réagir. Toujours en alerte, Gai reste attentif, guettant le moment opportun pour frapper de plus belle. La tension monte, et le combat promet d'être légendaire. ")
    response = sample_response("GAI: J'attaque avec un kunai, le lançant à une vitesse de 5 m/s vers Hiruzen, qui est à 10 mètres de distance. Je reste prêt à réagir à sa contre-attaque.")
    print("Sample Response:", response)