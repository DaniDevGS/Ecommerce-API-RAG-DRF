from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.contrib.auth.models import User
from rest_framework_simplejwt.authentication import JWTAuthentication
from chatbot.models import Conversacion
from chatbot.serializers import ConversacionSerializer
from chatbot.rag import generar_respuesta, limpiar_respuesta
from productos.models import Producto
from chatbot.vectors import buscar_productos_similares
from productos.utils.conversion import obtener_cambio
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated

class ChatbotView(APIView):
    serializer_class = ConversacionSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        engine = request.query_params.get('engine', "groq").lower()
        pregunta = serializer.validated_data["pregunta"].lower()

        resultados = buscar_productos_similares(pregunta, top_k=5)
        
        cambio_bolivar = obtener_cambio()
        if cambio_bolivar:
            cambio_bolivar = Decimal(str(cambio_bolivar))

        if resultados:
            contexto_lineas = []
            for res in resultados:
                p_nombre = res.metadata.get('nombre', 'Producto')
                p_precio = res.metadata.get('precio', 0)
                p_texto = res.data
                
                precio_bs_str = ""
                if cambio_bolivar:
                    precio_bs = round(Decimal(str(p_precio)) * cambio_bolivar, 2)
                    precio_bs_str = f" | Precio Bs: {precio_bs}"

                contexto_lineas.append(f"- {p_texto} | Precio USD: {p_precio}{precio_bs_str}")
            
            contexto = "\n".join(contexto_lineas)
        else:
            contexto = "No se encontraron productos específicos relacionados en el inventario."

        SYSTEM_PROMPT = (
            "Eres un asistente virtual del eCommerce de Triven Shop te llamas Trivenly, eres alguien amigable aunque también alguien profesional como un amigo dentro del sistema para el usuario. "
            "Usa solo la información provista en el 'CONTEXT' para responder sobre productos. "
            "Si te preguntan cosas básicas o saludos, sé amable y responde con naturalidad, no bloquees la conversación. "
            "Consultas sobre productos, disponibilidad, recomendaciones basadas en necesidades y gustos son tu especialidad. "
            "Si no puedes responder con la información del contexto, indícalo de forma amable, sin ser demasiado cerrado."
        )
        historial_usuario=Conversacion.objects.filter(usuario=request.user).order_by('-creado')[:3]
        historial_plano = "".join([
            f"\nPregunta: {h.pregunta.lower()}\nAsistente: {h.respuesta.lower()}" for h in historial_usuario]
        )
        prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"=== CONTEXT ===\n{contexto}\n\n"
            f"=== HISTORIAL RELEVANTE ===\n"
            f"{historial_plano}" if historial_plano else "Sin historial previo relevante.\n"
            f"\n=== INSTRUCCIÓN ===\n"
            "Responde solo con información del contexto pero tambien responde preguntas basicas de una manera amigable. Sé claro, conciso pero tambien algo creativo no seas alguien de pocas palabras y emite la respuesta en texto plano.\n"
        )
        temperatura = serializer.validated_data.get("temperatura", 0.7)
        modelo = serializer.validated_data.get("modelo", "modelo_base")
        try:
            print("Haciendo petición con el modelo:", modelo)
            print("Prompt:", prompt)
            print("Pregunta:", pregunta)
            print("Engine:", engine)
            respuesta = generar_respuesta(prompt,pregunta, temperatura=temperatura, engine=engine)
            print("Respuesta:", respuesta)
            LISTA_ERROR = ["No puedo responder a esa pregunta.",
                           "No puedo responder a tu pregunta.", "No puedo responder a tu pregunta", ""]
            if respuesta and respuesta not in LISTA_ERROR:
               respuesta_limpia = limpiar_respuesta(respuesta)
               print("Guardando conversacion")
               Conversacion.objects.create(pregunta=pregunta, respuesta=respuesta_limpia, usuario=request.user, temperatura=temperatura)
               return Response({"pregunta": pregunta, "respuesta": respuesta_limpia})
        except Exception as e:
            return Response({"error": str(e)}, status=500)

        return Response({"pregunta": pregunta, "respuesta": respuesta})
    
    def get(self, request):
        if request.user.is_authenticated:
            conversacion = Conversacion.objects.filter(
                usuario=request.user)
        else:
            conversacion = Conversacion.objects.all()[:10]
        serializer = ConversacionSerializer(conversacion, many=True)
        return Response(serializer.data)