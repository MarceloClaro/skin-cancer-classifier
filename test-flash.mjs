const GEMINI_API_KEY = "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs";
const GEMINI_MODEL = "gemini-1.5-flash";
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_MODEL}:generateContent`;

async function testChat() {
  console.log("🧪 Testando gemini-1.5-flash\n");
  
  try {
    const response = await fetch(`${GEMINI_API_URL}?key=${GEMINI_API_KEY}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: "Olá, você está funcionando?" }]
        }],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 2048,
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
    
    if (candidate.content && candidate.content.parts && candidate.content.parts[0]) {
      console.log("\n✅ SUCESSO!");
      console.log(candidate.content.parts[0].text);
    } else {
      console.error("❌ Sem content.parts");
    }
    
  } catch (error) {
    console.error("❌ ERRO:", error.message);
  }
}

testChat();
