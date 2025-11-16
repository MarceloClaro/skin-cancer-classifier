const GEMINI_API_KEY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_MODEL = "gemini-pro";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1/models/${GEMINI_MODEL}:generateContent`;

async function testChat() {
  console.log("🧪 Testando gemini-pro com API v1\n");
  
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: "Olá! Responda em português: você está funcionando?" }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
        }
      })
    });

    console.log("Status:", response.status);
    
    if (!response.ok) {
      const error = await response.text();
      console.error("❌ Erro:", error);
      return;
    }

    const data = await response.json();
    console.log("Resposta completa:", JSON.stringify(data, null, 2));
    
    const candidate = data.candidates[0];
    
    if (candidate.content && candidate.content.parts && candidate.content.parts[0]) {
      console.log("\n✅✅✅ SUCESSO TOTAL! gemini-pro (API v1) FUNCIONANDO! ✅✅✅");
      console.log("─".repeat(60));
      console.log(candidate.content.parts[0].text);
      console.log("─".repeat(60));
    } else {
      console.error("❌ Sem content.parts");
    }
    
  } catch (error) {
    console.error("❌ ERRO:", error.message);
  }
}

testChat();
