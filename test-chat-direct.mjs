// Teste direto do chat bot com a mesma lógica do servidor
const GEMINI_API_KEY_PRIMARY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_API_KEY_FALLBACK = "AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0";
const GEMINI_MODEL = "gemini-pro-latest";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

const PROJECT_CONTEXT = `Você é um assistente técnico especializado no projeto "Classificador de Câncer de Pele K230".`;

async function testChat() {
  console.log("🧪 Testando chat bot...\n");
  
  const userMessage = "Olá, como funciona o projeto?";
  
  try {
    console.log("[CHAT] Recebida mensagem:", userMessage);
    console.log("[CHAT] Tentando API Gemini com chave primária...");
    
    let response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY_PRIMARY}`, {
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
          maxOutputTokens: 1024,
        }
      })
    });

    console.log("[CHAT] Resposta primária - Status:", response.status, response.statusText);
    
    if (!response.ok) {
      console.log("[CHAT] Chave primária falhou, tentando fallback...");
      response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY_FALLBACK}`, {
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
            maxOutputTokens: 1024,
          }
        })
      });
      console.log("[CHAT] Resposta fallback - Status:", response.status, response.statusText);
    }

    if (!response.ok) {
      const errorText = await response.text();
      console.error("[CHAT] ❌ Erro na API Gemini:", response.status, errorText);
      throw new Error(`Erro ao comunicar com a API Gemini: ${response.status}`);
    }

    const data = await response.json();
    console.log("[CHAT] Resposta da API:", JSON.stringify(data, null, 2));
    
    if (!data.candidates || !data.candidates[0] || !data.candidates[0].content) {
      console.error("[CHAT] ❌ Formato de resposta inválido:", data);
      throw new Error("Formato de resposta inválido da API Gemini");
    }
    
    const botResponse = data.candidates[0].content.parts[0].text;
    console.log("\n✅ [CHAT] Resposta do bot:");
    console.log(botResponse);
    
  } catch (error) {
    console.error("\n❌ [CHAT] ERRO COMPLETO:", error);
    console.error("[CHAT] Stack trace:", error.stack);
  }
}

testChat();
