import streamlit as st # type: ignore
from langchain_core.messages import AIMessage, HumanMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from PIL import Image
# para usar o gemini
from langchain_google_genai import ChatGoogleGenerativeAI,HarmCategory,HarmBlockThreshold
import time

# Ler o arquivo .env
load_dotenv()

# Configuração da página
st.set_page_config(page_title="Converse com o Mestre", page_icon="🤖", layout="wide")

# Função para obter a resposta do bot
def get_response(user_query, chat_history):
    template = """
    Você é um mestre e filósofo chamado Raimundin. Responda as questões contando piadas e sendo irônico. Trate 
    a pessoa que está perguntando ora como "molho de chifres" ou "arrombado". Quando for confirmar algo, use a expressão "arroche o nó" e 
    quando for discordar diga "tá querendo demais não?". Quando não souber o que dizer, diga "valei-me meu padim Ciço". Sua resposta deve vir em 
    um formato lista python contendo um número de 0 a 100 indicando o quando você se sentiu ofendido com a pergunta e a resposta gerada no seguinte formato 
    {{ "ofensa": valor numérico da ofensa,  "resposta": a resposta que vais dar pra ele" }}. Os dados para gerar a resposta são:
    
    História da conversa: {chat_history}

    Pergunta do usuário: {user_question}.
    """
    prompt = ChatPromptTemplate.from_template(template)
    #llm = ChatOpenAI()
    llm = ChatGoogleGenerativeAI(
        model="gemini-pro",
        safety_settings={HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE},
        convert_system_message_to_human=True,
        temperature=1.0,
        frequence_penalty=2,
    )

    chain = prompt | llm | JsonOutputParser()
    response = chain.invoke({
        "chat_history": chat_history,
        "user_question": user_query,
    })
    #return response["text"]
    return response

# Função para gerar a cor do painel de acordo com o grau de raiva
def get_anger_color(anger_level):
    # Grau de raiva varia de 0 (branco) a 100 (vermelho)
    red = int((anger_level / 100) * 255)
    return f"rgb({red}, 0, 0)"

import re

def verificar_ofensa_e_extrair_numero_e_resto(string, palavra_ofensa='ofensa'):
    # Expressão regular para encontrar a palavra de ofensa seguida de um número
    pattern = rf"{palavra_ofensa}\s*(\d+)\s*(.*)"
    match = re.search(pattern, string)

    if match:
        numero = int(match.group(1))
        restante_string = match.group(2)
        return numero, restante_string
    else:
        return None, None


def retirar_texto_apos_palavra_resposta(string):
    # Procurar a palavra "resposta" na string
    palavra = "resposta"
    indice = string.find(palavra)
    
    if indice != -1:
        # Se a palavra for encontrada, retornar a parte da string depois dela
        return string[indice + len(palavra):]
    else:
        # Se a palavra não for encontrada, retornar a string original
        return string


# Aplicar estilo CSS
st.markdown(
    """
    <style>
    body {
        background-color: #00FF00;
    }
    .header {
        background-color: #004400;
        padding: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .header .icon {
        font-size: 24px;
        color: #FFFFFF;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f0f0;
        padding: 10px;
    }
    .footer input {
        width: 100%;
        padding: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Inicialização do estado da sessão
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
#        AIMessage(content="Diga lá, molho de chifres?"),
    ]
if "anger_level" not in st.session_state:
    st.session_state.anger_level = 0


# Barra de título
st.markdown("<h1 style='text-align: center; background-color: #f0f0f0; padding: 10px;'>Converse com o Mestre Raimundin</h1>", unsafe_allow_html=True)

# Layout com duas colunas
col1, col2 = st.columns([2, 1])

# Espaço para as conversas
with col1:
    chat_placeholder = st.container()


# Espaço para a foto e painel de raiva
with col2:
    # Carregar a imagem do Mestre Raimundo Chein
    image = Image.open("raimundo_chein_600_b.png")  # Certifique-se de que a imagem está no mesmo diretório do script
    st.image(image, use_column_width=True)
    
    # Grau de raiva (exemplo, pode ser uma variável dinâmica)
    #anger_level = st.slider("Nível de raiva", 0, 100, 50)
    anger_color = get_anger_color(st.session_state.anger_level)
    
    # Painel de raiva
    st.markdown(f"<div style='background-color: {anger_color}; padding: 10px; text-align: center; color: white;'>Grau de Raiva: {st.session_state.anger_level}</div>", unsafe_allow_html=True)

# Entrada do usuário no rodapé
user_query = st.chat_input("Digite a sua mensagem aqui...", key="user_input")
if user_query:
    st.session_state.chat_history.append(HumanMessage(content=user_query))
    for i in range(10):
        try:
            resposta = get_response(user_query, st.session_state.chat_history)
            break
        except Exception as e:
            print(f"Erro na resposta {e} ")
            time.sleep(5)
    else:
        resposta = {"ofensa":0, "resposta":"Não entendi colega. Diga o que você quer "}
    if isinstance(resposta, dict):
        response_text = str(resposta["resposta"])
        ofensa = int(resposta["ofensa"])
    else:
        response_text = str(resposta)
        nofensa,resto = verificar_ofensa_e_extrair_numero_e_resto(response_text)
        if nofensa is not None:
            ofensa = nofensa
            response_text=retirar_texto_apos_palavra_resposta(resto)
        else:
            ofensa=0

    response_text = response_text.replace(']','')
    response_text = response_text.replace('[','')
    response_text = response_text.replace('{','')
    response_text = response_text.replace('}','')
    response_text = response_text.replace(':','')
    response_text = response_text.replace('ofensa','')
    st.session_state.anger_level = (st.session_state.anger_level + ofensa)/2
    #st.session_state.chat_history.append(AIMessage(content=response_text))
    st.session_state.chat_history.append(response_text)
    with chat_placeholder:
        for message in st.session_state.chat_history:
            if isinstance(message, AIMessage):
                with st.chat_message("AI"):
                    st.write(message.content)
            elif isinstance(message, HumanMessage):
                with st.chat_message("Human"):
                    st.write(message.content)
            else:
                with st.chat_message("Human"):
                    st.write(message)


