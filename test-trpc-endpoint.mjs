// Teste do endpoint tRPC para chat
const API_URL = "http://localhost:3000/trpc/chat.sendMessage";

async function testTRPCEndpoint() {
  console.log("🧪 Testando endpoint tRPC...\n");
  
  const payload = {
    message: "Olá, você está funcionando?",
    sessionId: "test-session-123"
  };
  
  console.log("📤 Enviando payload:", JSON.stringify(payload, null, 2));
  
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(payload)
    });
    
    console.log(`\n📊 Status: ${response.status} ${response.statusText}`);
    
    const data = await response.json();
    console.log("\n📥 Resposta:", JSON.stringify(data, null, 2));
    
    if (response.ok && data.result?.data?.response) {
      console.log("\n✅ SUCESSO! Resposta do bot:");
      console.log(data.result.data.response);
    } else {
      console.log("\n❌ FALHA! Resposta inesperada");
    }
  } catch (error) {
    console.error("\n❌ Erro na requisição:", error.message);
  }
}

testTRPCEndpoint();
