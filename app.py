import os
import logging
import json
import base64
import tempfile
import random
import re
from flask import Flask, render_template, request, jsonify, session
from gtts import gTTS
import uuid
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "spanish-learning-app-secret")

# Database setup
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Define language levels and topics
LANGUAGE_LEVELS = {
    "beginner": "beginner",
    "intermediate": "intermediate",
    "advanced": "advanced"
}

CONVERSATION_TOPICS = {
    "greetings": "greetings",
    "travel": "travel",
    "food": "food",
    "shopping": "shopping",
    "daily_life": "daily_life",
    "work": "work",
    "health": "health",
    "culture": "culture"
}

# Spanish responses based on patterns in user input
SPANISH_RESPONSES = {
    # Greetings
    "greetings": {
        "beginner": {
            "hello": ["¡Hola! ¿Cómo estás?", "Buenos días. Me llamo Juan. ¿Y tú?", "¡Hola! ¿Cómo te va?"],
            "how are you": ["Estoy bien, gracias. ¿Y tú?", "Muy bien, gracias. ¿Qué tal tú?", "Bien, gracias. ¿Qué tal tu día?"],
            "name": ["Me llamo Juan. Soy tu tutor de español. ¿Cómo te llamas?", "Mi nombre es María. ¿Cuál es tu nombre?"],
            "nice to meet": ["Encantado de conocerte también.", "Igualmente. Es un placer."],
            "goodbye": ["¡Adiós! Hasta luego.", "¡Hasta pronto!", "¡Nos vemos!"],
            "default": ["Hola, ¿cómo puedo ayudarte con tu español hoy?", "¿Quieres practicar más saludos en español?"]
        },
        "intermediate": {
            "hello": ["¡Hola! ¿Cómo has estado últimamente?", "¡Buenas! ¿Qué tal va todo?", "¡Hola! ¿Qué has hecho hoy?"],
            "how are you": ["Estoy bastante bien, gracias. ¿Y tú qué cuentas?", "Todo marcha bien por aquí. ¿Cómo van las cosas contigo?"],
            "name": ["Me llamo Carlos y seré tu compañero de conversación hoy. Cuéntame algo sobre ti.", "Soy Ana, tu tutora de español. ¿A qué te dedicas?"],
            "nice to meet": ["El placer es mío. Espero que podamos tener conversaciones interesantes.", "Encantado de conocerte. ¿Llevas mucho tiempo estudiando español?"],
            "goodbye": ["¡Hasta la próxima! Ha sido un placer charlar contigo.", "¡Nos vemos pronto! Sigue practicando tu español."],
            "default": ["Cuéntame más sobre lo que quieres practicar hoy.", "¿Hay algún tema específico del que te gustaría hablar?"]
        },
        "advanced": {
            "hello": ["¡Qué tal! Me alegra verte de nuevo por aquí. ¿Cómo se presenta el día?", "¡Hola! Es un placer poder conversar contigo nuevamente. ¿Qué novedades tienes?"],
            "how are you": ["Estoy estupendamente, gracias por preguntar. ¿Qué tal te ha ido desde nuestra última conversación?", "No me puedo quejar, la verdad. ¿Y tú qué tal llevas la semana?"],
            "name": ["Permíteme presentarme, soy Eduardo, lingüista y apasionado de la cultura hispana. ¿Cuál es tu trasfondo con el idioma español?"],
            "nice to meet": ["El sentimiento es mutuo. Siempre es enriquecedor conocer a personas interesadas en nuestra lengua y cultura.", "Igualmente. Espero que nuestras conversaciones te ayuden a perfeccionar tu dominio del español."],
            "goodbye": ["Ha sido un verdadero placer charlar contigo. Te deseo un excelente día y espero que continuemos pronto.", "Hasta la próxima oportunidad. No dudes en volver cuando quieras seguir practicando tu español."],
            "default": ["Estoy aquí para ayudarte a perfeccionar tu español. ¿Sobre qué te gustaría profundizar hoy?", "Tu nivel de español parece bastante avanzado. ¿Hay algún aspecto particular que te interese trabajar?"]
        }
    },
    
    # Travel
    "travel": {
        "beginner": {
            "where": ["¿Quieres ir a España? Es muy bonito.", "Madrid es la capital de España. Hay muchos museos.", "Barcelona tiene playas bonitas y buena comida."],
            "hotel": ["El hotel está cerca de la playa.", "¿Necesitas una habitación para dos personas?", "El hotel tiene piscina y restaurante."],
            "transport": ["Puedes tomar el autobús o el metro.", "El taxi es más caro pero más rápido.", "El tren sale cada hora desde la estación central."],
            "ticket": ["El boleto cuesta 10 euros.", "Puedes comprar los boletos en la taquilla o por internet.", "Necesitas tu pasaporte para comprar el boleto."],
            "default": ["¿Adónde te gustaría viajar?", "España y México son lugares populares para visitar.", "¿Has viajado a algún país donde se habla español?"]
        },
        "intermediate": {
            "where": ["Si te gusta la historia, te recomendaría visitar Andalucía, donde puedes ver la influencia árabe en la arquitectura.", "En Latinoamérica, Perú ofrece una combinación perfecta de cultura antigua y paisajes impresionantes.", "Las Islas Canarias tienen un clima perfecto durante todo el año y paisajes volcánicos espectaculares."],
            "hotel": ["He reservado un alojamiento en el centro histórico con vistas a la catedral.", "Muchos viajeros prefieren los apartamentos turísticos porque ofrecen más espacio y comodidades.", "Este hotel boutique está situado en un edificio histórico completamente renovado."],
            "transport": ["El sistema de trenes de alta velocidad conecta las principales ciudades y es bastante cómodo.", "Te recomiendo alquilar un coche si quieres explorar los pueblos pequeños fuera de las rutas turísticas.", "Las compañías de bajo coste ofrecen vuelos económicos, pero ten cuidado con las restricciones de equipaje."],
            "ticket": ["Puedes conseguir descuentos importantes si compras los boletos con antelación.", "Hay un pase especial que te permite visitar varios museos por un precio reducido.", "Te recomiendo la tarjeta turística que incluye transporte ilimitado y entradas a atracciones."],
            "default": ["¿Qué tipo de experiencias buscas cuando viajas?", "Viajar es una excelente manera de practicar un idioma. ¿Qué lugares te gustaría conocer?", "¿Prefieres las ciudades grandes o los pueblos pequeños cuando viajas?"]
        },
        "advanced": {
            "where": ["Si buscas una experiencia auténtica lejos del turismo masificado, te sugeriría explorar la región de Extremadura, con sus ciudades medievales y gastronomía excepcional.", "La ruta del Camino de Santiago no solo ofrece un recorrido espiritual, sino que también te permite descubrir la diversidad cultural y paisajística del norte de España.", "En lugar de los destinos convencionales, considera visitar la región vinícola de Mendoza en Argentina, donde podrás deleitarte con vinos de clase mundial mientras contemplas el impresionante telón de fondo de los Andes."],
            "hotel": ["En vez de cadenas hoteleras internacionales, te recomendaría hospedarte en paradores, antiguos castillos, monasterios y palacios convertidos en hoteles de lujo que preservan su carácter histórico.", "Para una experiencia inmersiva, considera un intercambio de casas con una familia local, lo que te permitirá no solo ahorrar en alojamiento sino también sumergirte completamente en la cultura local.", "Los alojamientos ecoturísticos en áreas naturales protegidas ofrecen una perspectiva única sobre la biodiversidad local y las iniciativas de conservación."],
            "transport": ["El sistema ferroviario español ha evolucionado considerablemente en las últimas décadas, con el AVE (Alta Velocidad Española) que rivaliza con los mejores trenes de alta velocidad del mundo en términos de puntualidad y comodidad.", "Para explorar la costa mediterránea, considera el alquiler de veleros con o sin patrón, una alternativa que te brinda libertad absoluta para descubrir calas recónditas inaccesibles por tierra.", "Los servicios de coche compartido están transformando la manera de viajar entre ciudades medianas, ofreciendo una alternativa económica y sostenible mientras facilitan encuentros con locales."],
            "ticket": ["Los sistemas de reserva anticipada en España funcionan bajo el modelo de 'yield management', lo que significa que los precios fluctúan constantemente según la demanda; por ello, es aconsejable utilizar alertas de precios en diversas plataformas.", "Existen abonos ferroviarios específicos para no residentes que permiten viajes ilimitados durante periodos determinados, representando un ahorro sustancial para quienes planean desplazarse extensivamente.", "Para los museos más emblemáticos como el Prado o el Guggenheim, es imprescindible adquirir entradas con fecha y hora específicas, pues han implementado sistemas de control de aforo que limitan el número de visitantes simultáneos."],
            "default": ["¿Qué aspectos de la idiosincrasia local te interesan más cuando viajas a un nuevo destino?", "El turismo sostenible está ganando relevancia en España y Latinoamérica. ¿Qué prácticas sostenibles incorporas en tus viajes?", "La gastronomía constituye un pilar fundamental en la experiencia cultural de cualquier viajero. ¿Qué platos regionales españoles o latinoamericanos has tenido oportunidad de degustar?"]
        }
    },
    
    # Food
    "food": {
        "beginner": {
            "hungry": ["Yo también tengo hambre. Vamos a comer algo.", "En España, la gente come tarde. La cena es a las 9 o 10 de la noche."],
            "restaurant": ["Me gusta este restaurante. La comida es muy buena.", "¿Prefieres un restaurante de comida española o mexicana?", "Este restaurante es famoso por su paella."],
            "menu": ["En el menú hay muchas opciones. Hay tapas, paella y postres.", "¿Quieres ver el menú en inglés o español?", "El menú del día incluye primer plato, segundo plato y postre."],
            "drink": ["¿Quieres agua, vino o cerveza?", "El vino tinto va bien con la carne.", "En España es común beber sangría en verano."],
            "default": ["La comida española es muy variada y deliciosa.", "¿Has probado la paella? Es un plato típico español con arroz y mariscos.", "En México, los tacos son muy populares."]
        },
        "intermediate": {
            "hungry": ["Se me ha abierto el apetito. ¿Conoces algún buen restaurante por esta zona?", "En España tenemos horarios de comida diferentes: desayunamos ligero, comemos fuerte a las 2 o 3, y cenamos tarde, sobre las 9 o 10."],
            "restaurant": ["Este restaurante familiar lleva tres generaciones sirviendo platos tradicionales.", "Te recomiendo reservar mesa con antelación, especialmente los fines de semana.", "Hay un restaurante de fusión que mezcla cocina española y japonesa que está ganando mucha popularidad."],
            "menu": ["La carta cambia según la temporada para utilizar los ingredientes más frescos.", "Te recomiendo probar el menú de degustación para experimentar diferentes sabores locales.", "Muchos restaurantes ahora ofrecen opciones vegetarianas y veganas adaptadas de recetas tradicionales."],
            "drink": ["España tiene varias regiones vinícolas importantes como Rioja, Ribera del Duero y Priorat.", "Un vermut antes de comer es una tradición en muchas partes de España.", "El tinto de verano es más ligero que la sangría y muy refrescante en días calurosos."],
            "default": ["La gastronomía española varía mucho según la región. ¿Hay alguna cocina regional que te interese especialmente?", "Las tapas son pequeñas porciones que permiten probar diferentes platos en una misma comida.", "¿Has tenido oportunidad de visitar algún mercado de alimentos en un país hispanohablante?"]
        },
        "advanced": {
            "hungry": ["El ritual de la comida en España trasciende la mera necesidad alimenticia; es un acto social que puede extenderse durante horas, especialmente durante los fines de semana cuando las sobremesas se alargan entre conversaciones y digestivos.", "La dicotomía entre la tradición culinaria y la vanguardia gastronómica es particularmente fascinante en ciudades como San Sebastián, donde los pintxos tradicionales conviven con establecimientos galardonados con estrellas Michelin."],
            "restaurant": ["Los 'gastrobares' han revolucionado el panorama culinario español, democratizando la alta cocina al ofrecer elaboraciones sofisticadas en ambientes informales y a precios más accesibles.", "La filosofía 'kilómetro cero' está ganando adeptos entre los restauradores más comprometidos, quienes abastecen sus cocinas exclusivamente con productos locales y de temporada, reduciendo así la huella ecológica y apoyando a productores locales.", "Algunos de los restaurantes más vanguardistas están recuperando técnicas ancestrales de conservación y fermentación, reinterpretándolas bajo prismas contemporáneos para crear experiencias gastronómicas que entrelazan pasado y presente."],
            "menu": ["Los menús degustación más innovadores juegan no solo con sabores y texturas, sino también con elementos multisensoriales que apelan a la memoria y las emociones, convirtiendo la comida en una experiencia narrativa completa.", "La incorporación de superalimentos autóctonos latinoamericanos como la quinoa, el amaranto o la chía en la cocina contemporánea española refleja un interesante diálogo culinario transatlántico que reinterpreta ingredientes precolombinos en contextos mediterráneos.", "Los restaurantes de vanguardia están implementando sistemas de trazabilidad total que permiten al comensal conocer con precisión el origen de cada ingrediente, las condiciones de cultivo o cría, e incluso el impacto medioambiental asociado a cada plato."],
            "drink": ["La revolución del vino natural está transformando el panorama vitivinícola español, con pequeños productores que elaboran vinos sin intervención química, recuperando variedades autóctonas casi olvidadas y métodos ancestrales de vinificación.", "Los 'vermuterías' especializadas están resucitando el arte del vermut artesanal, con maceraciones propias de hierbas y especias que resultan en perfiles aromáticos únicos, revitalizando así una tradición que parecía reservada a generaciones anteriores.", "La mixología contemporánea española está explorando la incorporación de destilados tradicionales como el pacharán, el licor de hierbas o el brandy de Jerez, creando cócteles de autor que reinterpretan la tradición licorera nacional desde perspectivas cosmopolitas."],
            "default": ["La dicotomía entre tradición e innovación en la gastronomía española genera debates apasionantes entre puristas y vanguardistas. ¿Dónde te sitúas tú en este espectro culinario?", "El concepto de 'patrimonio culinario inmaterial' ha cobrado relevancia en la preservación de recetas y técnicas ancestrales. ¿Consideras que la evolución gastronómica puede amenazar este legado o más bien enriquecerlo?", "La diplomacia gastronómica se ha convertido en una potente herramienta de soft power para países hispanohablantes. ¿Crees que la proyección internacional de estas cocinas refleja fidedignamente su diversidad regional?"]
        }
    },
    
    # Default responses for all topics
    "default": {
        "beginner": ["Lo siento, no entiendo. ¿Puedes decirlo de otra manera?", "Vamos a practicar más. ¿Qué quieres decir?", "Estoy aprendiendo también. ¿Puedes repetir eso?", "Vamos a hablar de algo sencillo. ¿Te gusta la comida española?"],
        "intermediate": ["Interesante. Cuéntame más sobre eso.", "No estoy seguro de entender completamente. ¿Podrías elaborar un poco más?", "Eso suena bien. ¿Hay algo específico sobre este tema que te gustaría discutir?", "Gracias por compartir eso. ¿Qué más te gustaría practicar hoy?"],
        "advanced": ["Tu punto de vista es fascinante. Me gustaría explorar esa idea con más profundidad.", "Esa es una observación perspicaz. ¿Has considerado también cómo esto se relaciona con otros aspectos culturales?", "Has planteado un tema complejo que tiene múltiples matices. Permíteme ofrecerte algunas reflexiones al respecto.", "Tu dominio del español es impresionante. Permíteme responder con algunos giros lingüísticos propios del español culto."]
    }
}

# In-memory conversation history
conversations = {}

@app.route('/')
def index():
    """Render the main page of the application."""
    # Create a session ID if it doesn't exist
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    
    # Initialize conversation history for this session if needed
    session_id = session['session_id']
    if session_id not in conversations:
        conversations[session_id] = []
    
    return render_template('index.html', 
                          language_levels=LANGUAGE_LEVELS.keys(),
                          topics=CONVERSATION_TOPICS.keys())

@app.route('/api/chat', methods=['POST'])
def chat():
    """Process user message and return AI response with audio."""
    try:
        data = request.json
        user_message = data.get('message', '')
        level = data.get('level', 'beginner')
        topic = data.get('topic', 'greetings')
        
        # Get session ID
        session_id = session.get('session_id')
        if not session_id:
            session['session_id'] = str(uuid.uuid4())
            session_id = session['session_id']
            conversations[session_id] = []
        
        # Get conversation history
        conversation_history = conversations.get(session_id, [])
        
        # Generate response based on pattern matching
        ai_message = generate_spanish_response(user_message, level, topic)
        
        # Generate speech from the AI message
        audio_base64 = text_to_speech(ai_message)
        
        # Store the conversation history
        conversation_history.append({'role': 'user', 'content': user_message})
        conversation_history.append({'role': 'assistant', 'content': ai_message})
        conversations[session_id] = conversation_history
        
        return jsonify({
            'message': ai_message,
            'audio': audio_base64
        })
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        return jsonify({
            'error': 'An error occurred while processing your request',
            'message': 'Lo siento, ha ocurrido un error.'
        }), 500

@app.route('/api/reset', methods=['POST'])
def reset_conversation():
    """Reset the conversation history for the current session."""
    session_id = session.get('session_id')
    if session_id and session_id in conversations:
        conversations[session_id] = []
    
    return jsonify({'status': 'success'})

def text_to_speech(text):
    """Convert text to speech using gTTS and return as base64 encoded string."""
    try:
        # Create a temporary file to store the audio
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=True) as temp_audio:
            # Generate the speech
            tts = gTTS(text=text, lang='es', slow=False)
            tts.save(temp_audio.name)
            
            # Read the file and convert to base64
            temp_audio.seek(0)
            audio_content = temp_audio.read()
            audio_base64 = base64.b64encode(audio_content).decode('utf-8')
            
            return audio_base64
    except Exception as e:
        logger.error(f"Error in text to speech conversion: {str(e)}")
        return ""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
