# Modelo TFLite para K230 - Classificação de Câncer de Pele

## 📦 Arquivos Gerados

### 1. Modelo Float32
- **Arquivo:** `skin_cancer_k230.tflite`
- **Tamanho:** 9.08 MB
- **Precisão:** Float32 (máxima acurácia)
- **Uso:** Dispositivos com recursos suficientes

### 2. Modelo Quantizado INT8
- **Arquivo:** `skin_cancer_k230_quantized.tflite`
- **Tamanho:** 2.74 MB
- **Compressão:** 69.8% menor
- **Precisão:** INT8 (otimizado para edge)
- **Uso:** K230 e dispositivos embarcados

## 🚀 Uso no K230

### Python (TensorFlow Lite)

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Carregar modelo
interpreter = tf.lite.Interpreter(model_path="skin_cancer_k230_quantized.tflite")
interpreter.allocate_tensors()

# Obter detalhes de entrada/saída
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Preprocessar imagem
img = Image.open("lesion.jpg").resize((224, 224))
img_array = np.array(img) / 255.0
img_array = np.expand_dims(img_array, axis=0).astype(np.uint8)  # Para modelo quantizado

# Inferência
interpreter.set_tensor(input_details[0]['index'], img_array)
interpreter.invoke()
output = interpreter.get_tensor(output_details[0]['index'])

# Interpretar resultado
classes = ["BENIGNO", "MALIGNO"]
predicted_class = classes[np.argmax(output)]
confidence = np.max(output) * 100

print(f"Diagnóstico: {predicted_class} ({confidence:.1f}%)")
```

### C++ (K230 SDK)

```cpp
#include <tensorflow/lite/interpreter.h>
#include <tensorflow/lite/kernels/register.h>
#include <tensorflow/lite/model.h>

// Carregar modelo
auto model = tflite::FlatBufferModel::BuildFromFile("skin_cancer_k230_quantized.tflite");
tflite::ops::builtin::BuiltinOpResolver resolver;
tflite::InterpreterBuilder builder(*model, resolver);
std::unique_ptr<tflite::Interpreter> interpreter;
builder(&interpreter);

// Alocar tensores
interpreter->AllocateTensors();

// Preprocessar e executar inferência
// ... (código de preprocessamento)

interpreter->Invoke();

// Obter resultado
float* output = interpreter->typed_output_tensor<float>(0);
```

## 📊 Especificações Técnicas

### Entrada
- **Shape:** (1, 224, 224, 3)
- **Tipo:** UINT8 (quantizado) ou FLOAT32
- **Range:** [0, 255] (quantizado) ou [0.0, 1.0] (float)
- **Formato:** RGB

### Saída
- **Shape:** (1, 2)
- **Tipo:** UINT8 (quantizado) ou FLOAT32
- **Classes:** [BENIGNO, MALIGNO]
- **Interpretação:** Probabilidades (softmax)

### Preprocessamento
1. Redimensionar imagem para 224×224
2. Normalizar pixels: `pixel / 255.0`
3. Converter para RGB (se necessário)
4. Expandir dimensões: `(224, 224, 3) → (1, 224, 224, 3)`

### Pós-processamento
1. Aplicar argmax para obter índice da classe
2. Mapear índice: 0=BENIGNO, 1=MALIGNO
3. Calcular confiança: `max(output) * 100`

## ⚙️ Otimizações para K230

### Modelo Quantizado
- **Redução de tamanho:** ~75% menor
- **Velocidade:** ~4x mais rápido
- **Precisão:** ~1-2% de perda aceitável
- **Memória:** ~4x menos RAM

### Recomendações
1. Use modelo quantizado para produção
2. Implemente cache de inferências
3. Processe imagens em batch (se possível)
4. Use aceleração de hardware (NPU do K230)

## 📚 Referências

- [TensorFlow Lite Guide](https://www.tensorflow.org/lite/guide)
- [K230 SDK Documentation](https://github.com/kendryte/k230_sdk)
- [Model Optimization](https://www.tensorflow.org/lite/performance/model_optimization)

## ⚠️ Nota Importante

Este modelo é uma ferramenta auxiliar de estudo para residentes em dermatologia. **NÃO substitui avaliação clínica presencial** por dermatologista qualificado. Sempre correlacione com achados clínicos e história do paciente.

---
*Gerado automaticamente pelo Sistema de Classificação de Câncer de Pele K230*
