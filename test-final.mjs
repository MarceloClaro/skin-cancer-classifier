const GEMINI_API_KEY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_MODEL = "gemini-pro-latest";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const PROJECT_CONTEXT = `Você é um assistente técnico especializado no projeto "Classificador de Câncer de Pele K230".`;

async function testChat() {
  console.log("🧪 Teste FINAL com gemini-pro-latest\n");
  
  const userMessage = "Qual é a acurácia do modelo?";
  
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: `${PROJECT_CONTEXT}\n\nPergunta: ${userMessage}` }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
          topP: 0.95,
          topK: 40,
        }
      })
    });

    console.log("Status:", response.status);
    
    if (!response.ok) {
      console.error("❌ Erro:", await response.text());
      return;
    }

    const data = await response.json();
    const candidate = data.candidates[0];
    
    if (!candidate.content || !candidate.content.parts || !candidate.content.parts[0]) {
      console.error("❌ Sem content.parts (finishReason:", candidate.finishReason, ")");
      return;
    }
    
    console.log("\n✅ SUCESSO!");
    console.log("─".repeat(60));
    console.log(candidate.content.parts[0].text);
    console.log("─".repeat(60));
    
  } catch (error) {
    console.error("❌ ERRO:", error.message);
  }
}

testChat();
