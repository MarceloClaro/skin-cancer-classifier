const GEMINI_API_KEY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_MODEL = "models/gemini-2.5-flash";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/${GEMINI_MODEL}:generateContent`;

async function testChat() {
  console.log("🧪 Testando com modelo CORRETO: models/gemini-2.5-flash\n");
  
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: "Olá! Responda em português: qual é a acurácia do classificador de câncer de pele K230?" }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
        }
      })
    });

    console.log("✅ Status:", response.status, response.statusText);
    
    if (!response.ok) {
      const error = await response.text();
      console.error("❌ Erro:", error);
      return;
    }

    const data = await response.json();
    const candidate = data.candidates[0];
    
    if (candidate.content && candidate.content.parts && candidate.content.parts[0]) {
      console.log("\n🎉🎉🎉 SUCESSO TOTAL! CHAT BOT FUNCIONANDO! 🎉🎉🎉");
      console.log("═".repeat(60));
      console.log(candidate.content.parts[0].text);
      console.log("═".repeat(60));
    } else {
      console.error("❌ Sem content.parts (finishReason:", candidate.finishReason, ")");
    }
    
  } catch (error) {
    console.error("❌ ERRO:", error.message);
  }
}

testChat();
