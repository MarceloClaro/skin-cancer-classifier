// Script de teste da API Gemini
// Testa a conexão e resposta da API com as chaves fornecidas

const API_KEYS = [
  "AIzaSyCMsKvLqtAd6Sr4FvZ_ZrTIzZInMgwhVK0", // Chave primária
  "AIzaSyDVc5QnyhxvwoY1gqniVZ2jNCzeOEf4Nnc", // Chave fallback 1
  "AIzaSyBkD7xM8hcZ-3h1dNUumF6D401iXUVuWEs"  // Chave fallback 2
];

const MODEL = "gemini-pro-latest";
const TEST_MESSAGE = "Olá, você está funcionando?";

async function testGeminiAPI(apiKey, keyIndex) {
  console.log(`\n🔍 Testando chave ${keyIndex + 1}...`);
  console.log(`Chave: ${apiKey.substring(0, 20)}...`);
  
  const url = `https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${apiKey}`;
  
  const payload = {
    contents: [{
      parts: [{
        text: TEST_MESSAGE
      }]
    }]
  };

  try {
    console.log(`📤 Enviando requisição para: ${url.split('?')[0]}`);
    
    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    console.log(`📊 Status: ${response.status} ${response.statusText}`);
    
    const data = await response.json();
    
    if (!response.ok) {
      console.error(`❌ Erro na resposta:`, JSON.stringify(data, null, 2));
      return false;
    }

    if (data.candidates && data.candidates[0]?.content?.parts?.[0]?.text) {
      const responseText = data.candidates[0].content.parts[0].text;
      console.log(`✅ Sucesso! Resposta recebida:`);
      console.log(`📝 ${responseText.substring(0, 100)}...`);
      return true;
    } else {
      console.error(`❌ Formato de resposta inesperado:`, JSON.stringify(data, null, 2));
      return false;
    }
  } catch (error) {
    console.error(`❌ Erro na requisição:`, error.message);
    return false;
  }
}

async function main() {
  console.log('🚀 Iniciando teste da API Gemini...\n');
  console.log(`Modelo: ${MODEL}`);
  console.log(`Mensagem de teste: "${TEST_MESSAGE}"`);
  console.log(`Total de chaves a testar: ${API_KEYS.length}`);
  
  let workingKeyIndex = -1;
  
  for (let i = 0; i < API_KEYS.length; i++) {
    const success = await testGeminiAPI(API_KEYS[i], i);
    if (success) {
      workingKeyIndex = i;
      break;
    }
  }
  
  console.log('\n' + '='.repeat(60));
  if (workingKeyIndex >= 0) {
    console.log(`✅ SUCESSO! Chave ${workingKeyIndex + 1} está funcionando`);
    console.log(`Chave funcional: ${API_KEYS[workingKeyIndex].substring(0, 20)}...`);
  } else {
    console.log(`❌ FALHA! Nenhuma das ${API_KEYS.length} chaves está funcionando`);
    console.log(`\nPossíveis causas:`);
    console.log(`1. Chaves API inválidas ou expiradas`);
    console.log(`2. Limite de requisições excedido`);
    console.log(`3. Modelo "${MODEL}" não disponível`);
    console.log(`4. Problema de rede/firewall`);
  }
  console.log('='.repeat(60));
}

main();
