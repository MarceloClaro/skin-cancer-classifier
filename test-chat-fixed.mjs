// Teste com modelo e configuração corrigidos
const GEMINI_API_KEY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_MODEL = "gemini-2.0-flash-exp";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const PROJECT_CONTEXT = `Você é um assistente técnico especializado no projeto "Classificador de Câncer de Pele K230".`;

async function testChat() {
  console.log("🧪 Testando chat bot com modelo corrigido...\n");
  
  const userMessage = "Como funciona o K230?";
  
  try {
    console.log("[TEST] Enviando mensagem:", userMessage);
    
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: `${PROJECT_CONTEXT}\n\nPergunta do usuário: ${userMessage}`
              }
            ]
          }
        ],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
          topP: 0.95,
          topK: 40,
        }
      })
    });

    console.log("[TEST] Status:", response.status, response.statusText);
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error("[TEST] ❌ Erro:", errorText);
      return;
    }

    const data = await response.json();
    console.log("[TEST] Estrutura da resposta:", JSON.stringify(data, null, 2));
    
    // Verificar estrutura
    if (!data.candidates || !data.candidates[0]) {
      console.error("❌ Sem candidates");
      return;
    }

    const candidate = data.candidates[0];
    console.log("[TEST] finishReason:", candidate.finishReason);
    
    if (!candidate.content || !candidate.content.parts || !candidate.content.parts[0]) {
      console.error("❌ Sem content.parts");
      return;
    }
    
    const botResponse = candidate.content.parts[0].text;
    console.log("\n✅ SUCESSO! Resposta do bot:");
    console.log("─".repeat(60));
    console.log(botResponse);
    console.log("─".repeat(60));
    
  } catch (error) {
    console.error("\n❌ ERRO:", error.message);
  }
}

testChat();
